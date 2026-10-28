#!/usr/bin/env python3
"""Secret/credential scanner for the RS Windows Cloud Workspace repository.

Detects GitHub tokens, AWS/Google keys, private key blocks, Slack tokens and
suspicious credential assignments. Rule patterns are constructed via string
concatenation so the scanner source never self-matches (D-010).
Exit code 1 on any ERROR finding.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
EXCLUDE_FILES = {"secret_scanner.py"}  # rule definitions live here by construction
EXCLUDE_SUFFIXES = (".zip", ".png", ".jpg", ".7z", ".iso", ".gz", ".whl", ".exe")


def _rules() -> list[tuple[str, str, re.Pattern]]:
    gh_token = re.compile("gh" + "p_[A-Za-z0-9]{30,}")
    gh_fine = re.compile("github_pat_" + "[A-Za-z0-9_]{30,}")
    private_key = re.compile("-----BEGIN " + r"[A-Z ]*PRIVATE KEY-----")
    slack = re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")
    aws = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
    google = re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")
    generic = re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*[\"'][^\"'\s]{10,}[\"']")
    return [
        ("github-classic-token", "error", gh_token),
        ("github-fine-grained-token", "error", gh_fine),
        ("private-key-block", "error", private_key),
        ("slack-token", "error", slack),
        ("aws-access-key", "error", aws),
        ("google-api-key", "error", google),
        ("hardcoded-credential", "warn", generic),
    ]


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in EXCLUDE_FILES:
            continue
        yield path


def scan_file(path: Path) -> list[dict]:
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for rule, severity, pattern in _rules():
        for m in pattern.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            snippet = m.group(0)
            preview = snippet[:6] + "..." if len(snippet) > 12 else snippet
            findings.append({"rule": rule, "severity": severity,
                             "location": f"{path}:{line_no}", "match": preview})
    return findings


def scan_repo(root: Path) -> dict:
    findings: list[dict] = []
    files_scanned = 0
    for path in iter_files(root):
        files_scanned += 1
        findings.extend(scan_file(path))
    errors = [f for f in findings if f["severity"] == "error"]
    return {"root": str(root), "files_scanned": files_scanned,
            "findings": findings, "errors": len(errors)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="repository secret scanner")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    result = scan_repo(root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for f in result["findings"]:
            print(f"[{f['severity'].upper()}] {f['rule']} {f['location']}: {f['match']}")
        print(f"-- scanned {result['files_scanned']} files, "
              f"{len(result['findings'])} findings ({result['errors']} errors)")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
