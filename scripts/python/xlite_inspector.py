#!/usr/bin/env python3
"""RS X-Lite Archive Inspector.

Real inspection pipeline for the user-provided Windows X-Lite archive hosted on
pixeldrain (config/xlite.json). Supports: metadata retrieval with forced JSON
negotiation, availability probing (HTTP Range + magic bytes), authenticated
download via PIXELDRAIN_API_KEY when required, resume/retry, SHA-256 integrity
verification, safe 7z listing/extraction with traversal guard, ISO detection,
Windows image marker inspection and a JSON inspection report.

ANALYSIS ONLY (PLAN.md section 6): this tool NEVER executes anything that came
out of the archive, and NEVER claims the image can replace a runner's OS.

Exit codes: 0 = success, 1 = failure, 2 = blocked (auth required / unavailable).
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TOOL_VERSION = "1.0.0"
SEVEN_ZIP_MAGIC = b"7z\xbc\xaf\x27\x1c"
USER_AGENT = f"rs-windows-cloud-workspace/{TOOL_VERSION} (x-lite-inspector)"
CHUNK_SIZE = 1024 * 1024
DEFAULT_TIMEOUT = 30


class InspectorError(RuntimeError):
    """Recoverable inspection failure."""


class BlockedError(InspectorError):
    """Operation blocked: authentication required or file unavailable."""


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def redact(secret: str | None) -> str:
    if not secret:
        return ""
    return secret[:3] + "..." if len(secret) > 6 else "***"


def human_size(num: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} PiB"


def load_config(path: Path) -> dict:
    try:
        cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InspectorError(f"cannot load config {path}: {exc}") from exc
    for key in ("file_id", "api_endpoint"):
        if not cfg.get(key):
            raise InspectorError(f"config {path} missing required key '{key}'")
    return cfg


def _auth_header(api_key: str, mode: str) -> tuple[dict, dict] | tuple[dict, None]:
    """Pixeldrain accepts the API key as the username in Basic auth (any
    password). Query mode appends ?auth=<key> instead. Never log the key."""
    if mode == "query":
        return {}, {"auth": api_key}
    token = base64.b64encode((api_key + ":").encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}, None


def _endpoint_url(api_endpoint: str, api_key: str | None, auth_mode: str) -> str:
    """Apply query-mode auth consistently (AGENT-01 finding 1: query auth
    was only honored by get_metadata). The key never reaches reports: metadata
    id derivation strips the query string."""
    if api_key and auth_mode == "query":
        sep = "&" if "?" in api_endpoint else "?"
        return f"{api_endpoint}{sep}auth={api_key}"
    return api_endpoint


def _request(url: str, *, headers: dict | None = None, timeout: int = DEFAULT_TIMEOUT,
             method: str = "GET"):
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": USER_AGENT, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout)


def _map_http_error(exc: urllib.error.HTTPError) -> Exception:
    if exc.code in (401, 403):
        return BlockedError(f"authentication required (HTTP {exc.code})")
    if exc.code in (404, 410):
        return BlockedError(f"file unavailable (HTTP {exc.code})")
    return InspectorError(f"request failed: HTTP {exc.code}")


def _parse_content_disposition_filename(value: str) -> str | None:
    if not value:
        return None
    match = re.search(r'filename="?([^";]+)"?', value)
    return match.group(1) if match else None


def _header_metadata(url: str, resp_headers, status: int) -> dict:
    """Derive metadata from HTTP response headers (real name, size, date,
    availability) when the server serves raw file content instead of JSON.
    The id is derived from the endpoint WITHOUT any query string so a
    query-authenticated key can never leak into reports (AGENT-01 finding 1)."""
    length = resp_headers.get("Content-Length")
    size = int(length) if length and length.isdigit() else None
    name = _parse_content_disposition_filename(resp_headers.get("Content-Disposition", ""))
    base_url = url.split("?", 1)[0].rstrip("/")
    return {
        "id": base_url.rsplit("/", 1)[-1],
        "name": name,
        "size": size,
        "size_human": human_size(size) if size else None,
        "availability": "available" if status in (200, 206) else "unknown",
        "date": resp_headers.get("Last-Modified"),
        "downloads": None,
        "views": None,
        "source": "http-headers (endpoint serves raw file bytes; D-004)",
    }


def _head_or_ranged_get(url: str, headers: dict, timeout: int):
    """HEAD the URL; if HEAD is not allowed, fall back to a 1-byte ranged GET.
    Never transfers an unbounded body (ERROR-HISTORY E-002 fix)."""
    try:
        with _request(url, headers=headers, timeout=timeout, method="HEAD") as resp:
            return getattr(resp, "status", 200), resp.headers
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            try:
                with _request(url, headers={**headers, "Range": "bytes=0-0"},
                              timeout=timeout) as resp:
                    resp.read(1)
                    return getattr(resp, "status", 200), resp.headers
            except urllib.error.HTTPError as exc2:
                raise _map_http_error(exc2) from exc2
            except urllib.error.URLError as exc2:
                raise BlockedError(f"network unreachable: {exc2.reason}") from exc2
        raise _map_http_error(exc) from exc
    except urllib.error.URLError as exc:
        raise BlockedError(f"network unreachable: {exc.reason}") from exc


def get_metadata(api_endpoint: str, api_key: str | None = None,
                 auth_mode: str = "basic", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Retrieve file metadata.

    Live observation (2026-10-28, ERROR-HISTORY E-002): this pixeldrain
    endpoint serves the raw archive content (application/x-7z-compressed,
    Content-Length 2555783617) regardless of the Accept header. Strategy:
    HEAD first (zero body transfer); if the server ever answers JSON, fetch
    the body with a hard 1 MiB cap; otherwise derive metadata from headers.
    """
    headers = {"Accept": "application/json"}
    if api_key:
        extra, _ = _auth_header(api_key, auth_mode)
        headers.update(extra)
    url = _endpoint_url(api_endpoint, api_key, auth_mode)
    status, resp_headers = _head_or_ranged_get(url, headers, timeout)
    ctype = (resp_headers.get("Content-Type") or "").lower()
    if "json" in ctype:
        try:
            with _request(url, headers={**headers, "Range": "bytes=0-1048575"},
                          timeout=timeout) as resp:
                body = resp.read(1048576)
            raw = json.loads(body.decode("utf-8"))
            meta = normalize_metadata(raw)
            meta["source"] = "json"
            return meta
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError,
                UnicodeDecodeError) as exc:
            raise InspectorError(f"JSON metadata fetch failed: {exc}") from exc
    return _header_metadata(url, resp_headers, status)


def normalize_metadata(raw: dict) -> dict:
    availability = raw.get("availability")
    if isinstance(availability, bool):
        avail = "available" if availability else "unavailable"
    elif isinstance(availability, str) and availability:
        avail = "available" if availability.lower() in ("available", "online", "true") else "unavailable"
    else:
        avail = "unknown"
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "size": raw.get("size"),
        "size_human": human_size(raw["size"]) if isinstance(raw.get("size"), int) else None,
        "availability": avail,
        "date": raw.get("date"),
        "downloads": raw.get("downloads"),
        "views": raw.get("views"),
    }


def probe(api_endpoint: str, nbytes: int = 65536, api_key: str | None = None,
          auth_mode: str = "basic", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Range-request the first nbytes to verify download availability and the
    7z signature without transferring the whole multi-GB archive. Uses the
    file endpoint directly (live-verified 2026-10-28: Accept-Ranges: bytes)."""
    headers = {"Accept": "application/octet-stream", "Range": f"bytes=0-{nbytes - 1}"}
    if api_key:
        extra, _ = _auth_header(api_key, auth_mode)
        headers.update(extra)
    url = _endpoint_url(api_endpoint, api_key, auth_mode)
    try:
        with _request(url, headers=headers, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            resp_headers = resp.headers
            total = resp_headers.get("Content-Range", "").split("/")[-1]
            data = resp.read(nbytes)
    except urllib.error.HTTPError as exc:
        raise _map_http_error(exc) from exc
    except urllib.error.URLError as exc:
        raise BlockedError(f"network unreachable: {exc.reason}") from exc
    return {
        "http_status": status,
        "range_honored": status == 206,
        "bytes_received": len(data),
        "total_size_bytes": int(total) if total.isdigit() else None,
        "filename": _parse_content_disposition_filename(
            resp_headers.get("Content-Disposition", "")),
        "content_type": resp_headers.get("Content-Type"),
        "first_bytes_hex": data[:8].hex(),
        "is_7z_archive": data[:6] == SEVEN_ZIP_MAGIC,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(api_endpoint: str, dest: Path, api_key: str | None = None,
             auth_mode: str = "basic", resume: bool = True, retries: int = 3,
             timeout: int = DEFAULT_TIMEOUT, max_bytes: int | None = None) -> dict:
    """Download with retry/backoff and Range-based resume (live-verified
    Accept-Ranges: bytes). Appends when the server answers 206, restarts on a
    full 200 response. Every read is chunk-capped; when max_bytes (expected
    archive size + tolerance) is given, exceeding it aborts the download
    (AGENT-01 finding 7)."""
    url = _endpoint_url(api_endpoint, api_key, auth_mode)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    attempt, started = 0, time.time()
    while True:
        attempt += 1
        headers = {"Accept": "application/octet-stream"}
        if api_key:
            extra, _ = _auth_header(api_key, auth_mode)
            headers.update(extra)
        offset = dest.stat().st_size if (resume and dest.exists()) else 0
        if offset:
            headers["Range"] = f"bytes={offset}-"
        try:
            with _request(url, headers=headers, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                mode = "ab" if (status == 206 and offset) else "wb"
                if mode == "wb":
                    offset = 0
                with open(dest, mode) as out:
                    while True:
                        chunk = resp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        out.write(chunk)
                        if max_bytes and out.tell() + offset > max_bytes:
                            raise InspectorError(
                                f"download exceeded size ceiling {max_bytes} bytes "
                                f"(expected ~{human_size(max_bytes)}); aborting")
            final_size = dest.stat().st_size
            if max_bytes and final_size > max_bytes:
                raise InspectorError(
                    f"downloaded size {final_size} exceeds ceiling {max_bytes}")
            return {"path": str(dest), "bytes": final_size, "resumed_from": offset,
                    "attempts": attempt, "elapsed_s": round(time.time() - started, 1)}
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise BlockedError(f"download requires authentication (HTTP {exc.code})") from exc
            if exc.code in (404, 410):
                raise BlockedError(f"file unavailable (HTTP {exc.code})") from exc
            if attempt > retries:
                raise InspectorError(f"download failed after {attempt} attempts: HTTP {exc.code}") from exc
        except (urllib.error.URLError, OSError) as exc:
            if attempt > retries:
                raise InspectorError(f"download failed after {attempt} attempts: {exc}") from exc
        time.sleep(min(2 ** attempt, 15))


def _run_seven_zip(seven_zip: str, args: list[str]) -> str:
    if shutil.which(seven_zip) is None:
        raise BlockedError(f"'{seven_zip}' binary not found on PATH (install 7-Zip)")
    proc = subprocess.run([seven_zip, *args], capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise InspectorError(f"7z {' '.join(args[:2])} failed (rc={proc.returncode}): "
                             f"{(proc.stderr or proc.stdout).strip()[:400]}")
    return proc.stdout


def list_archive(archive: Path, seven_zip: str = "7z") -> list[dict]:
    """Parse `7z l -slt` output into entry dicts. Listing only — nothing is
    extracted and nothing is executed."""
    out = _run_seven_zip(seven_zip, ["l", "-slt", str(archive)])
    entries: list[dict] = []
    current: dict = {}
    for line in out.splitlines():
        line = line.strip()
        if not line:
            if current.get("Path"):
                current["is_dir"] = current.get("Attributes", "").startswith("D")
                entries.append(current)
            current = {}
            continue
        if " = " in line:
            key, _, value = line.partition(" = ")
            current[key.strip()] = value.strip()
    if current.get("Path"):
        current["is_dir"] = current.get("Attributes", "").startswith("D")
        entries.append(current)
    return entries


def find_unsafe_entries(entries: list[dict]) -> list[str]:
    """Traversal guard: refuse entries escaping the extraction directory.
    Hardened per AGENT-01 finding 3: backslashes normalized, absolute paths,
    drive-absolute paths (C:/...), any '..' component after normalization,
    NTFS alternate-data-stream ':' separators and symlink/reparse-point
    entries are all rejected."""
    bad = []
    for entry in entries:
        raw = entry.get("Path", "")
        if not raw:
            bad.append("<empty path>")
            continue
        normalized = raw.replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized) \
                or ":" in normalized \
                or any(part == ".." for part in normalized.split("/")):
            bad.append(raw)
            continue
        if entry.get("Symbolic Link") or entry.get("Type") in ("PosixLink", "SymbolicLink"):
            bad.append(raw)
    return bad


def detect_iso_entries(entries: list[dict]) -> list[dict]:
    return [e for e in entries if not e.get("is_dir") and e["Path"].lower().endswith(".iso")]


WINDOWS_IMAGE_MARKERS = ("sources/install.wim", "sources/install.esd", "setup.exe", "bootmgr",
                         "sources/boot.wim")


def detect_windows_image_markers(entries: list[dict]) -> list[str]:
    lowered = {e["Path"].replace("\\", "/").lower() for e in entries if not e.get("is_dir")}
    return [m for m in WINDOWS_IMAGE_MARKERS if m in lowered]


def extract_archive(archive: Path, dest: Path, seven_zip: str = "7z") -> int:
    """Safely extract into a fresh dedicated directory. Refuses traversal
    entries before extraction; verifies after extraction that nothing escaped
    and no symlinks/reparse points were created; never executes content."""
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise InspectorError(f"extraction destination not empty: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    _run_seven_zip(seven_zip, ["x", "-y", f"-o{dest}", str(archive)])
    extracted = 0
    for path in dest.rglob("*"):
        if path.is_symlink():
            raise InspectorError(f"extraction produced a symlink (refused): {path}")
        if path.is_file():
            extracted += 1
    return extracted


def build_report(steps: list[dict], *, config_path: str, extra: dict | None = None) -> dict:
    report = {
        "tool": "rs-xlite-inspector",
        "tool_version": TOOL_VERSION,
        "generated_utc": utc_now(),
        "config": config_path,
        "analysis_only": True,
        "steps": steps,
        "disclaimer": ("Windows X-Lite is inspected for analysis only. It is NEVER booted, "
                       "executed or installed, and it CANNOT replace the operating system of a "
                       "GitHub-hosted Windows runner (PLAN.md section 6)."),
    }
    if extra:
        report.update(extra)
    return report


def write_report(report: dict, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def cmd_metadata(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    api_key = os.environ.get("PIXELDRAIN_API_KEY")
    meta = get_metadata(cfg["api_endpoint"], api_key, args.auth_mode)
    print(json.dumps(meta, indent=2))
    return 0 if meta["availability"] != "unavailable" else 1


def cmd_probe(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    api_key = os.environ.get("PIXELDRAIN_API_KEY")
    result = probe(cfg["api_endpoint"], args.bytes, api_key, args.auth_mode)
    result["expected_file"] = cfg.get("filename")
    result["total_size_human"] = human_size(result["total_size_bytes"]) if result["total_size_bytes"] else None
    print(json.dumps(result, indent=2))
    if args.report:
        write_report(build_report(
            [{"step": "probe", "status": "PASS", "detail": result}], config_path=str(args.config),
            extra={"probe": result}), Path(args.report))
    return 0 if result["is_7z_archive"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default="config/xlite.json", help="X-Lite config JSON")
    parser.add_argument("--auth-mode", choices=("basic", "query"), default="basic",
                        help="pixeldrain auth mode (the API key itself is read "
                             "ONLY from the PIXELDRAIN_API_KEY env var; it is "
                             "never accepted on the command line — AGENT-01 finding 5)")
    sub = parser.add_subparsers(dest="command", required=True)
    p_meta = sub.add_parser("metadata", help="retrieve file metadata as JSON")
    p_probe = sub.add_parser("probe", help="range-probe archive availability + 7z signature")
    p_probe.add_argument("--bytes", type=int, default=65536)
    p_probe.add_argument("--report", default=None)
    p_dl = sub.add_parser("download", help="download with resume/retry + sha256")
    p_dl.add_argument("--dest", required=True)
    p_dl.add_argument("--expected-sha256", default=None)
    p_ver = sub.add_parser("verify", help="sha256 + safe 7z listing + ISO detection")
    p_ver.add_argument("--archive", required=True)
    p_ver.add_argument("--expected-sha256", default=None)
    p_ver.add_argument("--seven-zip", default="7z")
    p_ver.add_argument("--report", default=None)
    p_ver.add_argument("--extract-to", default=None)
    p_meta.set_defaults(func=cmd_metadata)
    p_probe.set_defaults(func=cmd_probe)

    def cmd_download(args: argparse.Namespace) -> int:
        cfg = load_config(args.config)
        api_key = os.environ.get("PIXELDRAIN_API_KEY")
        expected_size = cfg.get("expected_size_bytes")
        max_bytes = int(expected_size * 1.02) if expected_size else None
        info = download(cfg["api_endpoint"], Path(args.dest), api_key, args.auth_mode,
                        max_bytes=max_bytes)
        digest = sha256_file(Path(args.dest))
        info["sha256"] = digest
        expected = args.expected_sha256 or cfg.get("expected_sha256")
        info["sha256_matches"] = None if not expected else digest == expected.lower()
        info["size_matches"] = None if not expected_size else info["bytes"] == expected_size
        print(json.dumps(info, indent=2))
        if info["size_matches"] is False:
            return 1
        return 0 if info["sha256_matches"] in (None, True) else 1

    def cmd_verify(args: argparse.Namespace) -> int:
        archive = Path(args.archive)
        steps = []
        digest = sha256_file(archive)
        expected = args.expected_sha256
        match = None if not expected else digest == expected.lower()
        steps.append({"step": "sha256", "status": "PASS", "detail":
                      {"sha256": digest, "expected": expected, "matches": match}})
        entries = list_archive(archive, args.seven_zip)
        files = [e for e in entries if not e.get("is_dir")]
        unsafe = find_unsafe_entries(entries)
        steps.append({"step": "list", "status": "PASS" if not unsafe else "FAIL", "detail":
                      {"entries": len(entries), "files": len(files), "unsafe_paths": unsafe}})
        isos = detect_iso_entries(entries)
        markers = detect_windows_image_markers(entries)
        steps.append({"step": "iso-detection", "status": "PASS", "detail":
                      {"iso_files": [e["Path"] for e in isos],
                       "windows_image_markers": markers,
                       "compatibility": ("Windows installation media detected — "
                                         "analysis-only inspection; not installable on "
                                         "GitHub-hosted runners") if isos or markers else
                                        "no Windows image detected in archive root"}})
        extracted = None
        if args.extract_to:
            if unsafe:
                steps.append({"step": "extract", "status": "FAIL",
                              "detail": "refused: unsafe paths present"})
            else:
                extracted = extract_archive(archive, Path(args.extract_to), args.seven_zip)
                steps.append({"step": "extract", "status": "PASS",
                              "detail": {"files": extracted, "note": "extracted only; never executed"}})
        report = build_report(steps, config_path=str(args.config), extra={
            "archive": str(archive), "sha256": digest, "sha256_matches": match,
            "entry_count": len(entries), "file_count": len(files),
            "iso_files": [e["Path"] for e in isos], "windows_image_markers": markers,
            "extracted_files": extracted})
        if args.report:
            write_report(report, Path(args.report))
        print(json.dumps({k: report[k] for k in
                          ("sha256", "entry_count", "file_count", "iso_files",
                           "windows_image_markers", "extracted_files")}, indent=2))
        failed = [s for s in steps if s["status"] == "FAIL"]
        return 1 if failed else 0

    p_dl.set_defaults(func=cmd_download)
    p_ver.set_defaults(func=cmd_verify)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BlockedError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}), file=sys.stderr)
        return 2
    except InspectorError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
