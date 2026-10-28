#!/usr/bin/env python3
"""PowerShell script validator.

Two tiers of validation:
1. REAL parse: when `pwsh` is on PATH, every file is parsed with the PowerShell
   AST parser (System.Management.Automation.Language.Parser::ParseFile) — this
   runs on GitHub Windows runners via Test-Syntax.ps1 / test.yml.
2. Heuristic static validation (always available, Linux included): UTF-8 and
   null-byte checks, delimiter balance scanner aware of strings, escapes,
   here-strings and block comments, forbidden patterns (Invoke-Expression etc.)
   and required best-practice markers.

Exit code 1 on any ERROR finding. Heuristic findings are clearly labelled.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAIRS = {")": "(", "]": "[", "}": "{"}
OPENERS = "([{"


def finding(rule: str, severity: str, location: str, message: str) -> dict:
    return {"rule": rule, "severity": severity, "location": location, "message": message}


def _forbidden_patterns() -> list[tuple[str, str, re.Pattern]]:
    return [
        ("PS-EXEC-001", "error", re.compile(r"\bInvoke-Expression\b")),
        ("PS-EXEC-002", "error", re.compile(r"(?<![\w-])iex(?![\w-])")),
        ("PS-POLICY", "error",
         re.compile(r"Set-ExecutionPolicy\s+[^#\n]*?(Unrestricted|Bypass)", re.IGNORECASE)),
        ("PS-RM", "warn", re.compile(r"(?<![\w-])rm\s+(-Recurse|-r\b)", re.IGNORECASE)),
        ("PS-ENCODEDCMD", "warn", re.compile(r"-EncodedCommand\b")),
    ]


def _required_patterns() -> list[tuple[str, re.Pattern]]:
    return [
        ("PS-REQ-STRICT", re.compile(r"Set-StrictMode")),
        ("PS-REQ-CMDLET", re.compile(r"\[CmdletBinding\(\)\]")),
        ("PS-REQ-PARAM", re.compile(r"\bparam\s*\(")),
    ]


def check_balance(text: str, location: str) -> list[dict]:
    """Heuristic delimiter balance outside strings/comments/here-strings."""
    findings: list[dict] = []
    stack: list[tuple[str, int]] = []
    in_block = False
    in_here_close: str | None = None  # expected closer line ("'@" or '"@')
    for line_no, raw in enumerate(text.splitlines(), start=1):
        if in_block:
            if "#>" in raw:
                in_block = False
                raw = raw.split("#>", 1)[1]
            else:
                continue
        if in_here_close is not None:
            if raw.strip() == in_here_close:
                in_here_close = None
            continue
        stripped = raw.strip()
        if stripped.startswith("<#"):
            if "#>" not in stripped:
                in_block = True
            continue
        opener = None
        if stripped in ("@'", '@"'):
            opener = stripped
        else:
            match = re.search(r'[=(\s](@["\'])\s*$', raw)
            if match:
                opener = match.group(1)
        if opener is not None:
            # here-string opens; its closer is the reversed quote-at marker
            in_here_close = "'@" if opener == "@'" else '"@'
            continue
        out: list[str] = []
        i = 0
        while i < len(raw):
            ch = raw[i]
            if ch == "`":
                i += 2
                continue
            if ch == "'":
                i += 1
                while i < len(raw):
                    if raw[i] == "'":
                        if i + 1 < len(raw) and raw[i + 1] == "'":
                            i += 2
                            continue
                        break
                    i += 1
                i += 1
                continue
            if ch == '"':
                i += 1
                while i < len(raw):
                    if raw[i] == "`":
                        i += 2
                        continue
                    if raw[i] == '"':
                        break
                    i += 1
                i += 1
                continue
            if ch == "#":
                break
            out.append(ch)
            i += 1
        for ch in "".join(out):
            if ch in OPENERS:
                stack.append((ch, line_no))
            elif ch in PAIRS:
                if not stack or stack[-1][0] != PAIRS[ch]:
                    findings.append(finding("PS-BALANCE", "error",
                                            f"{location}:{line_no}",
                                            f"unbalanced '{ch}' (heuristic scanner)"))
                    if len(findings) > 20:
                        return findings
                else:
                    stack.pop()
    if stack:
        ch, line_no = stack[-1]
        findings.append(finding("PS-BALANCE", "error", f"{location}:{line_no}",
                                f"unclosed '{ch}' (heuristic scanner)"))
    return findings


def validate_text(text: str, location: str) -> list[dict]:
    findings: list[dict] = []
    if "\x00" in text:
        findings.append(finding("PS-ENCODING", "error", location, "null byte in script body"))
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        findings.append(finding("PS-ENCODING", "error", location, "not valid UTF-8"))
    findings.extend(check_balance(text, location))
    for rule, severity, pattern in _forbidden_patterns():
        for m in pattern.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append(finding(rule, severity, f"{location}:{line_no}",
                                    f"forbidden pattern: {m.group(0)!r}"))
    if "Invoke-WebRequest" in text and "UseBasicParsing" in text:
        findings.append(finding("PS-LEGACY", "warn", location,
                                "-UseBasicParsing is a no-op on PowerShell 6+"))
    return findings


def check_required(text: str, location: str) -> list[dict]:
    findings = []
    for rule, pattern in _required_patterns():
        if not pattern.search(text):
            findings.append(finding(rule, "warn", location,
                                    "missing recommended marker "
                                    f"'{pattern.pattern}'"))
    return findings


def pwsh_parse(path: Path) -> list[dict]:
    """REAL parse via the PowerShell AST parser when pwsh is available."""
    if shutil.which("pwsh") is None:
        return [finding("PS-REAL-PARSE", "info", str(path),
                        "pwsh not on PATH — heuristic validation only (real parse runs on Windows runners)")]
    ps_script = (
        "$errs = $null; $toks = $null;"
        "[System.Management.Automation.Language.Parser]::ParseFile("
        f"'{str(path).replace(chr(39), chr(39)*2)}', [ref]$toks, [ref]$errs) | Out-Null;"
        "if ($errs) { $errs | ForEach-Object { Write-Output ($_.Extent.StartLineNumber.ToString() + '|' + $_.Message) } }"
    )
    encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
    proc = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                          capture_output=True, text=True, timeout=120)
    findings = []
    for line in (proc.stdout or "").splitlines():
        if "|" not in line:
            continue
        line_no, _, message = line.partition("|")
        findings.append(finding("PS-REAL-PARSE", "error", f"{path}:{line_no}", message.strip()))
    if proc.returncode != 0 and not findings:
        findings.append(finding("PS-REAL-PARSE", "error", str(path),
                                f"pwsh exited rc={proc.returncode}: {proc.stderr.strip()[:300]}"))
    return findings


def validate_file(path: Path, real_parse: bool = True) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        return [finding("PS-ENCODING", "error", str(path), f"cannot read: {exc}")]
    findings = validate_text(text, str(path))
    findings.extend(check_required(text, str(path)))
    if real_parse:
        findings.extend(pwsh_parse(path))
    return findings


def validate_dir(directory: Path, real_parse: bool = True) -> dict:
    results = {}
    for path in sorted(list(directory.glob("*.ps1")) + list(directory.glob("*.psm1"))):
        results[str(path)] = validate_file(path, real_parse=real_parse)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PowerShell static/AST validator")
    parser.add_argument("--dir", default="scripts/powershell")
    parser.add_argument("--no-real-parse", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"error: directory not found: {directory}", file=sys.stderr)
        return 1
    results = validate_dir(directory, real_parse=not args.no_real_parse)
    errors = sum(1 for fnds in results.values() for f in fnds if f["severity"] == "error")
    if args.json:
        print(json.dumps({"dir": str(directory), "files": results, "errors": errors}, indent=2))
    else:
        for path, fnds in results.items():
            for f in fnds:
                if f["severity"] != "info":
                    print(f"[{f['severity'].upper()}] {f['rule']} {f['location']}: {f['message']}")
        print(f"-- {len(results)} files validated, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
