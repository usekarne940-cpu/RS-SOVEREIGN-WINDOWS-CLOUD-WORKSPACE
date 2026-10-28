#!/usr/bin/env python3
"""Artifact manifest manager — content-addressed file inventory with SHA-256.

`manifest` builds a full manifest of a directory tree (excluding VCS/cache
dirs); `verify` recomputes and reports mismatches/missing/extra files.
Exit code 1 when verification fails.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db"}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in EXCLUDE_NAMES:
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def build_manifest(root: Path) -> dict:
    root = root.resolve()
    files = []
    total = 0
    for path in iter_files(root):
        size = path.stat().st_size
        total += size
        files.append({"path": path.relative_to(root).as_posix(),
                      "size": size, "sha256": _sha256(path)})
    return {"manifest_version": 1, "generated_utc": utc_now(), "root": str(root),
            "file_count": len(files), "total_bytes": total, "files": files}


def verify_manifest(root: Path, manifest: dict) -> dict:
    root = root.resolve()
    recorded = {f["path"]: f for f in manifest["files"]}
    actual = {p.relative_to(root).as_posix(): p for p in iter_files(root)}
    mismatches, missing = [], []
    for rel, info in recorded.items():
        if rel not in actual:
            missing.append(rel)
            continue
        digest = _sha256(actual[rel])
        if digest != info["sha256"]:
            mismatches.append({"path": rel, "expected": info["sha256"], "actual": digest})
    extra = sorted(set(actual) - set(recorded))
    ok = not mismatches and not missing and not extra
    return {"ok": ok, "verified": len(recorded) - len(missing), "missing": missing,
            "mismatches": mismatches, "extra": extra}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="artifact manifest manager")
    sub = parser.add_subparsers(dest="command", required=True)
    p_man = sub.add_parser("manifest", help="build a manifest for a directory")
    p_man.add_argument("--root", required=True)
    p_man.add_argument("--out", required=True)
    p_ver = sub.add_parser("verify", help="verify a directory against a manifest")
    p_ver.add_argument("--root", required=True)
    p_ver.add_argument("--manifest", required=True)

    args = parser.parse_args(argv)
    if args.command == "manifest":
        manifest = build_manifest(Path(args.root))
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"root": manifest["root"], "file_count": manifest["file_count"],
                          "total_bytes": manifest["total_bytes"],
                          "manifest_file_sha256": _sha256(Path(args.out))}, indent=2))
        return 0
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = verify_manifest(Path(args.root), manifest)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
