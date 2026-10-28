"""Unit tests for xlite_inspector (network calls fully mocked)."""
import hashlib
import json
import urllib.error

import pytest

import xlite_inspector as xi


class FakeResponse:
    def __init__(self, status=200, headers=None, body=b""):
        self.status = status
        self.headers = headers or {}
        self._body = body

    def read(self, n=-1):
        """Consuming read (like a real socket): each read returns at most n
        bytes and advances the stream — an infinite source would hang the
        download loop, so the fake must consume too."""
        if n is None or n < 0:
            data, self._body = self._body, b""
            return data
        data = self._body[:n]
        self._body = self._body[len(data):]
        return data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def http_error(code):
    return urllib.error.HTTPError("https://pixeldrain.com/api/file/TEST", code,
                                  "reason", None, None)


# ---------------------------------------------------------------- magic / sizes
def test_seven_zip_magic_positive():
    assert xi.SEVEN_ZIP_MAGIC == b"7z\xbc\xaf\x27\x1c"
    assert xi.SEVEN_ZIP_MAGIC[:6] == b"7z\xbc\xaf\x27\x1c"


def test_human_size():
    assert xi.human_size(0) == "0.0 B"
    assert xi.human_size(1024) == "1.0 KiB"
    assert xi.human_size(2555783617) == "2.4 GiB"


def test_sha256_file(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(b"rs-windows-cloud-workspace" * 100)
    expected = hashlib.sha256(b"rs-windows-cloud-workspace" * 100).hexdigest()
    assert xi.sha256_file(path) == expected


def test_redact():
    assert xi.redact(None) == ""
    assert xi.redact("abcdef") == "***"
    assert xi.redact("abcdefgh") == "abc..."


# ---------------------------------------------------------------- metadata
def test_normalize_metadata_bool_availability():
    meta = xi.normalize_metadata({"id": "X", "name": "a.7z", "size": 10,
                                  "availability": True})
    assert meta["availability"] == "available"
    assert meta["size_human"] == "10.0 B"


def test_normalize_metadata_string_availability_unknown():
    meta = xi.normalize_metadata({"id": "X", "name": "a.7z", "size": None})
    assert meta["availability"] == "unknown"
    assert meta["size_human"] is None


def test_parse_content_disposition_filename():
    parse = xi._parse_content_disposition_filename
    assert parse('inline; filename="[Windows X-Lite] Optimum 11 26H1 Pro v2.7z"') == \
        "[Windows X-Lite] Optimum 11 26H1 Pro v2.7z"
    assert parse('attachment; filename=plain.7z') == "plain.7z"
    assert parse("") is None
    assert parse(None) is None


def test_header_metadata_derivation():
    headers = {
        "Content-Length": "2555783617",
        "Content-Type": "application/x-7z-compressed",
        "Content-Disposition": 'inline; filename="x-lite.7z"',
        "Last-Modified": "Sun, 30 Nov 2025 03:10:55 GMT",
    }
    meta = xi._header_metadata("https://pixeldrain.com/api/file/ZdPxkVmH", headers, 200)
    assert meta["name"] == "x-lite.7z"
    assert meta["size"] == 2555783617
    assert meta["size_human"] == "2.4 GiB"
    assert meta["availability"] == "available"
    assert meta["id"] == "ZdPxkVmH"
    assert meta["source"].startswith("http-headers")


def test_get_metadata_json_path(monkeypatch):
    payload = {"id": "ZdPxkVmH", "name": "x.7z", "size": 123,
               "availability": True, "date": "2025-11-30T03:10:55Z"}
    calls = []

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        calls.append((method, url))
        if method == "HEAD":
            return FakeResponse(200, {"Content-Type": "application/json"})
        return FakeResponse(206, {"Content-Type": "application/json"},
                            json.dumps(payload).encode())

    monkeypatch.setattr(xi, "_request", fake_request)
    meta = xi.get_metadata("https://pixeldrain.com/api/file/ZdPxkVmH")
    assert meta["id"] == "ZdPxkVmH"
    assert meta["availability"] == "available"
    assert meta["source"] == "json"
    assert ("HEAD", "https://pixeldrain.com/api/file/ZdPxkVmH") in calls


def test_get_metadata_header_path_when_server_serves_bytes(monkeypatch):
    """Live-observed behavior: endpoint serves raw 7z bytes, not JSON."""
    resp_headers = {"Content-Type": "application/x-7z-compressed",
                    "Content-Length": "2555783617",
                    "Content-Disposition": 'inline; filename="x-lite.7z"'}

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        return FakeResponse(200, resp_headers)

    monkeypatch.setattr(xi, "_request", fake_request)
    meta = xi.get_metadata("https://pixeldrain.com/api/file/ZdPxkVmH")
    assert meta["name"] == "x-lite.7z"
    assert meta["size"] == 2555783617
    assert meta["availability"] == "available"


def test_get_metadata_unavailable(monkeypatch):
    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        raise http_error(404)

    monkeypatch.setattr(xi, "_request", fake_request)
    with pytest.raises(xi.BlockedError, match="unavailable"):
        xi.get_metadata("https://pixeldrain.com/api/file/TEST")


def test_get_metadata_auth_required(monkeypatch):
    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        raise http_error(401)

    monkeypatch.setattr(xi, "_request", fake_request)
    with pytest.raises(xi.BlockedError, match="authentication"):
        xi.get_metadata("https://pixeldrain.com/api/file/TEST")


def test_head_fallback_on_405(monkeypatch):
    resp_headers = {"Content-Length": "10",
                    "Content-Disposition": 'inline; filename="y.7z"'}
    seen = []

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        seen.append(method)
        if method == "HEAD":
            raise http_error(405)
        return FakeResponse(206, resp_headers)

    monkeypatch.setattr(xi, "_request", fake_request)
    meta = xi.get_metadata("https://pixeldrain.com/api/file/TEST")
    assert meta["size"] == 10
    assert "HEAD" in seen and "GET" in seen


def test_auth_header_basic():
    header, params = xi._auth_header("K", "basic")
    assert "Authorization" in header
    assert params is None
    assert header["Authorization"].startswith("Basic ")


def test_auth_header_query():
    header, params = xi._auth_header("K", "query")
    assert header == {}
    assert params == {"auth": "K"}


# ---------------------------------------------------------------- probe
def test_probe_magic_and_range(monkeypatch):
    body = xi.SEVEN_ZIP_MAGIC + b"\x00" * 4096
    resp_headers = {"Content-Type": "application/x-7z-compressed",
                    "Content-Range": "bytes 0-65535/2555783617",
                    "Content-Disposition": 'inline; filename="x.7z"'}

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        assert headers["Range"] == "bytes=0-65535"
        return FakeResponse(206, resp_headers, body)

    monkeypatch.setattr(xi, "_request", fake_request)
    result = xi.probe("https://pixeldrain.com/api/file/TEST", nbytes=65536)
    assert result["http_status"] == 206
    assert result["range_honored"] is True
    assert result["is_7z_archive"] is True
    assert result["total_size_bytes"] == 2555783617
    assert result["filename"] == "x.7z"
    assert result["first_bytes_hex"].startswith("377abcaf271c")


def test_probe_range_ignored(monkeypatch):
    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        return FakeResponse(200, {}, b"not-7z-data" * 100)

    monkeypatch.setattr(xi, "_request", fake_request)
    result = xi.probe("https://pixeldrain.com/api/file/TEST", nbytes=1000)
    assert result["range_honored"] is False
    assert result["is_7z_archive"] is False


def test_probe_auth_required(monkeypatch):
    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        raise http_error(403)

    monkeypatch.setattr(xi, "_request", fake_request)
    with pytest.raises(xi.BlockedError, match="authentication"):
        xi.probe("https://pixeldrain.com/api/file/TEST")


# ---------------------------------------------------------------- download
def test_download_resume_with_tmp(tmp_path, monkeypatch):
    dest = tmp_path / "archive.7z"
    dest.write_bytes(b"abc")  # partial download already on disk
    seen = []

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        seen.append(dict(headers))
        return FakeResponse(206, {}, b"def")

    monkeypatch.setattr(xi, "_request", fake_request)
    info = xi.download("https://pixeldrain.com/api/file/TEST", dest, resume=True)
    assert seen[0].get("Range") == "bytes=3-"
    assert dest.read_bytes() == b"abcdef"
    assert info["resumed_from"] == 3
    assert info["bytes"] == 6


def test_download_restarts_on_full_200(tmp_path, monkeypatch):
    dest = tmp_path / "archive.7z"
    dest.write_bytes(b"stale")

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        return FakeResponse(200, {}, b"fresh")

    monkeypatch.setattr(xi, "_request", fake_request)
    xi.download("https://pixeldrain.com/api/file/TEST", dest, resume=True)
    assert dest.read_bytes() == b"fresh"


def test_download_retries_then_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(xi.time, "sleep", lambda s: None)
    attempts = []

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        attempts.append(1)
        raise urllib.error.URLError("connection reset")

    monkeypatch.setattr(xi, "_request", fake_request)
    with pytest.raises(xi.InspectorError, match="attempts"):
        xi.download("https://pixeldrain.com/api/file/TEST",
                    tmp_path / "a.7z", retries=2)
    assert len(attempts) == 3  # initial + 2 retries


# ---------------------------------------------------------------- 7z parsing
SLT_OUTPUT = """
Path = [Windows X-Lite] Optimum 11 26H1 Pro v2.7z
Type = C
Size = 2555783617

Path = Windows X-Lite Optimum 11.iso
Type = File
Size = 5368709120
Attributes = A

Path = sources
Type = Folder
Attributes = D_ 

Path = sources/install.wim
Type = File
Size = 4294967296
Attributes = A
"""


def test_list_archive_parses_slt(monkeypatch):
    monkeypatch.setattr(xi, "_run_seven_zip", lambda *a, **k: SLT_OUTPUT)
    entries = xi.list_archive("archive.7z")
    files = [e for e in entries if not e.get("is_dir")]
    assert len(entries) == 4
    assert len(files) == 3
    isos = xi.detect_iso_entries(entries)
    assert len(isos) == 1
    assert isos[0]["Path"] == "Windows X-Lite Optimum 11.iso"
    markers = xi.detect_windows_image_markers(entries)
    assert "sources/install.wim" in markers


def test_find_unsafe_entries():
    entries = [{"Path": "ok/file.txt"}, {"Path": "../escape.txt"},
               {"Path": "/absolute.txt"}]
    unsafe = xi.find_unsafe_entries(entries)
    assert "../escape.txt" in unsafe
    assert "/absolute.txt" in unsafe


def test_traversal_guard_hardened():
    """AGENT-01 finding 3 regression: drive-absolute paths, backslash
    traversal, NTFS ADS colons and symlink entries must all be rejected."""
    entries = [
        {"Path": "ok/file.txt"},
        {"Path": "C:/evil/x.txt"},
        {"Path": "C:\\evil\\y.txt"},
        {"Path": "..\\..\\escape.txt"},
        {"Path": "file:stream.txt"},
        {"Path": "link", "Symbolic Link": "target"},
        {"Path": "posix-link", "Type": "PosixLink"},
    ]
    bad = xi.find_unsafe_entries(entries)
    assert "ok/file.txt" not in bad
    for path in ("C:/evil/x.txt", "C:\\evil\\y.txt", "..\\..\\escape.txt",
                 "file:stream.txt", "link", "posix-link"):
        assert path in bad, f"guard missed: {path}"


def test_query_auth_key_never_leaks_into_metadata(monkeypatch):
    """AGENT-01 finding 1 regression: in query-auth mode the key travels in
    the URL but must NEVER appear in the metadata report (id derivation
    strips the query string)."""
    resp_headers = {"Content-Type": "application/x-7z-compressed",
                    "Content-Length": "10",
                    "Content-Disposition": 'inline; filename="y.7z"'}
    seen_urls = []

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        seen_urls.append(url)
        return FakeResponse(200, resp_headers)

    monkeypatch.setattr(xi, "_request", fake_request)
    meta = xi.get_metadata("https://pixeldrain.com/api/file/TEST",
                           api_key="SECRETKEY123", auth_mode="query")
    assert any("auth=SECRETKEY123" in u for u in seen_urls)  # mode applied
    assert "SECRETKEY123" not in json.dumps(meta)  # never in the report
    assert meta["id"] == "TEST"  # query stripped from id derivation


def test_download_size_ceiling_aborts(tmp_path, monkeypatch):
    """AGENT-01 finding 7 regression: exceeding the expected-size ceiling
    aborts the download instead of filling the disk."""
    body = b"x" * 5000

    def fake_request(url, *, headers=None, timeout=30, method="GET"):
        return FakeResponse(200, {}, body)

    monkeypatch.setattr(xi, "_request", fake_request)
    with pytest.raises(xi.InspectorError, match="exceeded"):
        xi.download("https://pixeldrain.com/api/file/TEST",
                    tmp_path / "a.7z", max_bytes=1000)


def test_extract_refuses_non_empty_dest(tmp_path, monkeypatch):
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "existing.txt").write_text("x")
    with pytest.raises(xi.InspectorError, match="not empty"):
        xi.extract_archive(tmp_path / "a.7z", dest)


def test_run_seven_zip_missing_binary():
    import shutil as _sh
    if _sh.which("7z") is not None:
        pytest.skip("7z installed: the missing-binary path cannot be exercised here")
    with pytest.raises(xi.BlockedError, match="not found"):
        xi._run_seven_zip("7z", ["l", "x.7z"])


# ---------------------------------------------------------------- report
def test_build_report_contains_disclaimer():
    report = xi.build_report([], config_path="config/xlite.json")
    assert report["analysis_only"] is True
    assert "CANNOT replace" in report["disclaimer"]
    assert "NEVER booted" in report["disclaimer"]


def test_write_report_roundtrip(tmp_path):
    report = xi.build_report([{"step": "probe", "status": "PASS"}],
                             config_path="config/xlite.json",
                             extra={"sha256": "ab" * 32})
    out = tmp_path / "report.json"
    xi.write_report(report, out)
    loaded = json.loads(out.read_text())
    assert loaded["sha256"] == "ab" * 32
    assert loaded["steps"][0]["step"] == "probe"


def test_load_config_validates(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"filename": "x"}')
    with pytest.raises(xi.InspectorError, match="missing required key"):
        xi.load_config(bad)
