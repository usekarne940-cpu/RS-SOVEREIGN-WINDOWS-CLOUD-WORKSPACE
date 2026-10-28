#!/usr/bin/env python3
"""Local validation orchestrator.

Runs every locally executable gate in the Linux/Windows dev environment and
writes evidence: reports/local-validation.json (records in the PLAN.md §9
schema) and reports/LOCAL-VALIDATION.md (rendered). Windows-executable-only
checks are NOT run here — they run on GitHub Windows runners (test.yml,
gui.yml, ...); nothing is faked as passing.

Exit code: 1 if any gate FAILs; 0 otherwise (BLOCKED gates are reported but do
not fail the run — they represent environment limitations, per zero-fake
policy they are always visible in the report).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS_PY = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_PY.parents[1]
sys.path.insert(0, str(SCRIPTS_PY))

import ps_validator  # noqa: E402
import workflow_lint  # noqa: E402
import secret_scanner  # noqa: E402
from report_generator import render_markdown  # noqa: E402


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Records:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.records: list[dict] = []

    def add(self, test_id: str, name: str, command: str, expected: str, actual: str,
            status: str, evidence: str, error: str = "", suite: str = "local") -> None:
        self.records.append({"test_id": test_id, "suite": suite, "name": name,
                             "command": command, "expected": expected, "actual": actual,
                             "status": status, "evidence": evidence, "error": error})

    def counts(self) -> dict:
        out = {"PASS": 0, "FAIL": 0, "BLOCKED": 0, "NOT_RUN": 0}
        for record in self.records:
            out[record["status"]] += 1
        return out


def run(cmd: list[str], cwd: Path, timeout: int = 900, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                          env=env)


def gate_import_smoke(records: Records) -> None:
    modules = ["xlite_inspector", "workflow_lint", "ps_validator", "secret_scanner",
               "artifact_manager", "report_generator", "run_task", "run_all_checks"]
    env = {**os.environ,
           "PYTHONPATH": str(SCRIPTS_PY) + os.pathsep + os.environ.get("PYTHONPATH", "")}
    for module in modules:
        proc = run([sys.executable, "-c", f"import {module}"], cwd=REPO_ROOT, env=env)
        records.add(
            f"IMP-{module[:12].upper()}",
            f"Import smoke: {module}",
            f"{sys.executable} -c 'import {module}'",
            "exit code 0",
            f"exit code {proc.returncode}",
            "PASS" if proc.returncode == 0 else "FAIL",
            (proc.stdout or "").strip()[:200],
            (proc.stderr or "").strip()[:300],
            suite="imports")


def gate_json_configs(records: Records) -> None:
    targets = sorted(REPO_ROOT.glob("config/*.json")) + \
        sorted(REPO_ROOT.glob("applications/*.json")) + \
        sorted(REPO_ROOT.glob("automation/tasks/*.json"))
    if not targets:
        records.add("CFG-000", "JSON config files exist", "glob config/ applications/ automation/tasks/",
                    ">=1 config file", "0 found", "FAIL", "no config files", suite="configs")
        return
    for path in targets:
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            ok = isinstance(data, dict)
        except (OSError, json.JSONDecodeError) as exc:
            records.add(f"CFG-{rel.upper()[:20]}", f"Valid JSON: {rel}",
                        f"json.loads({rel})", "parses as JSON object",
                        f"parse error: {exc}", "FAIL", str(exc)[:300], suite="configs")
            continue
        records.add(f"CFG-{rel.upper()[:20]}", f"Valid JSON: {rel}",
                    f"json.loads({rel})", "parses as JSON object",
                    "parsed" if ok else "not an object",
                    "PASS" if ok else "FAIL", f"{rel} OK", suite="configs")


def gate_bash_syntax(records: Records) -> None:
    if shutil.which("bash") is None:
        records.add("SH-BASH", "bash available", "which bash", "present", "missing",
                    "BLOCKED", "bash not on PATH", suite="shell")
        return
    scripts = sorted((REPO_ROOT / "scripts" / "linux").glob("*.sh"))
    for path in scripts:
        rel = path.relative_to(REPO_ROOT).as_posix()
        proc = run(["bash", "-n", str(path)], cwd=REPO_ROOT)
        records.add(f"SH-{path.stem.upper()[:16]}", f"bash -n: {rel}",
                    f"bash -n {rel}", "exit code 0", f"exit code {proc.returncode}",
                    "PASS" if proc.returncode == 0 else "FAIL",
                    (proc.stderr or "syntax OK").strip()[:200],
                    (proc.stderr or "").strip()[:300], suite="shell")


def gate_shellcheck(records: Records) -> None:
    if shutil.which("shellcheck") is None:
        records.add("SH-CHK", "shellcheck external linter", "shellcheck -S warning scripts/linux/*.sh",
                    "0 findings", "shellcheck not installed in this environment "
                    "(release downloads blocked: BLOCKERS B-05)",
                    "BLOCKED", "executes for real in CI: test.yml job lint-external "
                    "(ubuntu runner, shellcheck preinstalled)",
                    suite="shell")
        return
    scripts = sorted((REPO_ROOT / "scripts" / "linux").glob("*.sh"))
    failed = []
    for path in scripts:
        proc = run(["shellcheck", "-S", "error", str(path)], cwd=REPO_ROOT)
        if proc.returncode != 0:
            failed.append(path.name)
    records.add("SH-CHK", "shellcheck (error severity)", "shellcheck -S error scripts/linux/*.sh",
                "0 findings", f"{len(failed)} scripts with findings: {', '.join(failed) or 'none'}",
                "PASS" if not failed else "FAIL", "see command output", suite="shell")


def gate_powershell(records: Records) -> None:
    results = ps_validator.validate_dir(REPO_ROOT / "scripts" / "powershell")
    total_errors = 0
    for path, findings in sorted(results.items()):
        errors = [f for f in findings if f["severity"] == "error"]
        total_errors += len(errors)
        records.add(
            f"PS-{Path(path).stem.upper()[:16]}",
            f"PowerShell validation: {Path(path).name}",
            f"ps_validator.validate_file({Path(path).name})",
            "0 error-severity findings",
            f"{len(errors)} error-severity findings",
            "PASS" if not errors else "FAIL",
            "; ".join(f"{f['rule']}@{f['location']}" for f in errors)[:200] or "clean",
            "; ".join(f["message"] for f in errors)[:300], suite="powershell")
    if not results:
        records.add("PS-000", "PowerShell files exist", "glob scripts/powershell/*.ps1",
                    ">=1 script", "0 found", "FAIL", "no PowerShell files", suite="powershell")


def gate_workflows(records: Records) -> None:
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    required = workflow_lint.check_required_files(workflows_dir)
    missing = [f["location"] for f in required]
    records.add("WF-REQ", "Required workflow files present",
                "workflow_lint.check_required_files(.github/workflows)",
                "all 7 required workflows present",
                f"missing: {', '.join(missing) or 'none'}",
                "PASS" if not missing else "FAIL", "audit/build/test/gui/screenshots/xlite/cleanup",
                suite="workflows")
    for path in sorted(workflows_dir.glob("*.yml")):
        findings = workflow_lint.lint_workflow(path)
        errors = [f for f in findings if f["severity"] == "error"]
        records.add(
            f"WF-{path.stem.upper()[:18]}",
            f"Workflow contract: {path.name}",
            f"workflow_lint.lint_workflow({path.name})",
            "0 error findings", f"{len(errors)} errors, {len(findings)} total",
            "PASS" if not errors else "FAIL",
            "; ".join(f"{f['rule']}: {f['message']}" for f in errors)[:200] or "clean",
            "; ".join(f["message"] for f in errors)[:300], suite="workflows")


def gate_secrets(records: Records) -> None:
    result = secret_scanner.scan_repo(REPO_ROOT)
    errors = result["errors"]
    records.add("SEC-SCAN", "Repository secret scan", "secret_scanner.scan_repo(<repo>)",
                "0 error findings", f"{errors} error findings "
                f"({len(result['findings'])} total, {result['files_scanned']} files)",
                "PASS" if errors == 0 else "FAIL",
                "; ".join(f"{f['location']}: {f['match']}" for f in result["findings"])[:200]
                or "clean", suite="security")


def parse_junit(path: Path) -> list[dict]:
    records = []
    tree = ET.parse(path)
    for case in tree.iter("testcase"):
        classname = case.get("classname", "tests")
        name = case.get("name", "unknown")
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if error is not None:
            status, detail = "FAIL", (error.get("message") or error.text or "")[:300]
        elif failure is not None:
            status, detail = "FAIL", (failure.get("message") or failure.text or "")[:300]
        elif skipped is not None:
            status, detail = "NOT_RUN", (skipped.get("message") or "skipped")[:300]
        else:
            status, detail = "PASS", ""
        records.append({"test_id": f"PY-{classname}.{name}"[:80], "suite": f"pytest:{classname}",
                        "name": name, "command": "python -m pytest (see reports/pytest-local.xml)",
                        "expected": "test passes", "actual": status.lower(),
                        "status": status, "evidence": f"junit: reports/pytest-local.xml",
                        "error": detail})
    return records


def gate_pytest(records: Records, extra_args: list[str] | None = None) -> None:
    junit = REPO_ROOT / "reports" / "pytest-local.xml"
    junit.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "pytest", "tests/unit", "tests/integration",
           "tests/workflow", "tests/security", "tests/gui",
           "-m", "not network", f"--junitxml={junit}", "-q"]
    if extra_args:
        cmd += extra_args
    proc = run(cmd, cwd=REPO_ROOT, timeout=1800)
    if not junit.exists():
        records.add("PY-000", "pytest local suite", " ".join(cmd), "junit report written",
                    f"exit code {proc.returncode}, no junit file", "FAIL",
                    (proc.stderr or proc.stdout)[-400:], suite="pytest")
        return
    parsed = parse_junit(junit)
    records.records.extend(parsed)
    if proc.returncode != 0 and not any(r["status"] == "FAIL" for r in parsed):
        records.add("PY-EXIT", "pytest exit code", " ".join(cmd), "exit code 0",
                    f"exit code {proc.returncode}", "FAIL",
                    (proc.stderr or proc.stdout)[-400:], suite="pytest")


def gate_actionlint(records: Records) -> None:
    if shutil.which("actionlint") is None:
        records.add("WF-ACTIONLINT", "actionlint external linter",
                    "actionlint", "no findings",
                    "actionlint not installed in this environment "
                    "(release downloads blocked: BLOCKERS B-05)", "BLOCKED",
                    "executes for real in CI: test.yml job lint-external "
                    "(ubuntu runner, pinned v1.7.12)", suite="workflows")
        return
    proc = run(["actionlint"], cwd=REPO_ROOT)
    ok = proc.returncode == 0
    records.add("WF-ACTIONLINT", "actionlint external linter", "actionlint",
                "exit code 0", f"exit code {proc.returncode}",
                "PASS" if ok else "FAIL", (proc.stdout or "clean")[:200],
                (proc.stdout or proc.stderr)[:300], suite="workflows")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="local validation orchestrator")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--skip-pytest", action="store_true")
    args = parser.parse_args(argv)

    run_id = args.run_id or f"local-{utc_now()}"
    records = Records(run_id)

    gate_import_smoke(records)
    gate_json_configs(records)
    gate_bash_syntax(records)
    gate_shellcheck(records)
    gate_powershell(records)
    gate_workflows(records)
    gate_actionlint(records)
    gate_secrets(records)
    if not args.skip_pytest:
        gate_pytest(records)

    report = {
        "run_id": run_id, "generated_utc": utc_now(), "repo_root": str(REPO_ROOT),
        "counts": records.counts(), "total": len(records.records),
        "notes": ("BLOCKED gates are environment limitations, honestly reported (PLAN.md §9). "
                  "Windows-executable checks run on GitHub Windows runners after push; they are "
                  "never marked PASS from Linux."),
        "records": records.records,
    }
    reports_dir = REPO_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "local-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (reports_dir / "LOCAL-VALIDATION.md").write_text(
        render_markdown(records.records, title=f"Local Validation — {run_id}"), encoding="utf-8")

    counts = report["counts"]
    print(json.dumps({"run_id": run_id, "total": report["total"], "counts": counts}, indent=2))
    print(f"evidence: reports/local-validation.json + reports/LOCAL-VALIDATION.md")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
