#!/usr/bin/env python3
"""GitHub Actions workflow contract linter.

Validates every workflow in .github/workflows against the RS Windows Cloud
Workspace contract: valid YAML with name/jobs, allowlisted runners, timeouts,
least-privilege permissions, concurrency groups, no pull_request_target, pinned
action versions, and artifact-upload hygiene. Exit code 1 on any ERROR finding.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REQUIRED_WORKFLOWS = (
    "audit.yml", "build.yml", "test.yml", "gui.yml",
    "screenshots.yml", "xlite-inspection.yml", "cleanup.yml",
)
ALLOWED_RUNNERS = {
    "windows-latest", "windows-2022", "windows-2025",
    "ubuntu-latest", "ubuntu-24.04", "macos-latest",
}
PINNED_ACTION = re.compile(r"^[\w.-]+/[\w.-]+@v\d+(?:\.\d+)*$")
MATRIX_RUNNER = re.compile(r"^\$\{\{\s*matrix\.(\w+)\s*\}\}$")
MAX_TIMEOUT = 360  # GitHub-hosted free-tier job limit (minutes)


def finding(rule: str, severity: str, location: str, message: str) -> dict:
    return {"rule": rule, "severity": severity, "location": location, "message": message}


def triggers_of(data: dict):
    """YAML 1.1 quirk: PyYAML loads a bare `on:` key as boolean True (D-009)."""
    return data.get("on", data.get(True))


def lint_workflow(path: Path) -> list[dict]:
    findings: list[dict] = []
    loc = str(path)
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except (OSError, yaml.YAMLError) as exc:
        return [finding("R1", "error", loc, f"cannot parse workflow: {exc}")]

    if not isinstance(data, dict):
        return [finding("R1", "error", loc, "workflow must be a YAML mapping")]
    if not data.get("name"):
        findings.append(finding("R1", "error", loc, "missing top-level 'name'"))
    trig = triggers_of(data)
    if trig in (None, {}):
        findings.append(finding("R1", "error", loc, "missing 'on' triggers"))
    jobs = data.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        findings.append(finding("R1", "error", loc, "missing or empty 'jobs'"))
        return findings
    if "pull_request_target" in (trig or {}):
        findings.append(finding("R6", "error", loc, "pull_request_target trigger is forbidden"))

    # R10: branch/tag filters must be lists — a plain string parses silently
    # in YAML and silently breaks trigger filtering (regression from the
    # AGENT-03 audit round)
    for event in ("push", "pull_request", "pull_request_target", "workflow_run"):
        event_cfg = (trig or {}).get(event)
        if isinstance(event_cfg, dict):
            for filter_key in ("branches", "branches-ignore", "tags", "tags-ignore", "paths"):
                value = event_cfg.get(filter_key)
                if value is not None and not isinstance(value, list):
                    findings.append(finding(
                        "R10", "error", loc,
                        f"'{event}.{filter_key}' must be a list, got "
                        f"{type(value).__name__}: {value!r}"))
                if isinstance(value, list):
                    for item in value:
                        if not isinstance(item, str) or not item.strip():
                            findings.append(finding(
                                "R10", "error", loc,
                                f"'{event}.{filter_key}' contains invalid entry {item!r}"))

    perms = data.get("permissions")
    if not isinstance(perms, dict):
        findings.append(finding("R4", "error", loc, "missing top-level 'permissions' mapping"))
    else:
        for scope, value in perms.items():
            if value not in ("read", "write"):
                findings.append(finding("R4", "error", loc,
                                        f"invalid permission value {scope}: {value}"))
            if scope == "contents" and value == "write":
                findings.append(finding("R4", "error", loc,
                                        "top-level contents:write forbidden (use job-scoped in build.yml)"))

    conc = data.get("concurrency")
    if not (isinstance(conc, dict) and conc.get("group")):
        findings.append(finding("R5", "error", loc, "missing concurrency.group"))
    elif conc.get("cancel-in-progress") is not True:
        findings.append(finding("R5", "warn", loc, "concurrency.cancel-in-progress should be true"))

    for job_id, job in jobs.items():
        jloc = f"{loc}#{job_id}"
        if not isinstance(job, dict):
            findings.append(finding("R1", "error", jloc, "job must be a mapping"))
            continue
        runner = job.get("runs-on")
        matrix_match = MATRIX_RUNNER.match(str(runner)) if runner else None
        if matrix_match:
            key = matrix_match.group(1)
            matrix = (job.get("strategy") or {}).get("matrix") or {}
            values = matrix.get(key) if isinstance(matrix, dict) else None
            if not isinstance(values, list) or not values:
                findings.append(finding("R2", "error", jloc,
                                        f"matrix runner key '{key}' has no values"))
            else:
                bad = [v for v in values if v not in ALLOWED_RUNNERS]
                if bad:
                    findings.append(finding("R2", "error", jloc,
                                            f"matrix runner values not allowlisted: {bad}"))
        elif runner not in ALLOWED_RUNNERS:
            findings.append(finding("R2", "error", jloc, f"runner not allowlisted: {runner!r}"))
        timeout = job.get("timeout-minutes")
        if not isinstance(timeout, (int, float)) or timeout < 1:
            findings.append(finding("R3", "error", jloc, "missing/invalid timeout-minutes"))
        elif timeout > MAX_TIMEOUT:
            findings.append(finding("R3", "error", jloc,
                                    f"timeout-minutes {timeout} exceeds free-tier max {MAX_TIMEOUT}"))
        jperms = job.get("permissions")
        if jperms is not None:
            if not isinstance(jperms, dict):
                findings.append(finding("R4", "error", jloc, "job permissions must be a mapping"))
            else:
                for scope, value in jperms.items():
                    if value not in ("read", "write"):
                        findings.append(finding("R4", "error", jloc,
                                                f"invalid job permission {scope}: {value}"))
        for step in job.get("steps", []) or []:
            uses = step.get("uses")
            if uses and not PINNED_ACTION.match(str(uses)):
                findings.append(finding("R7", "error", jloc, f"action not version-pinned: {uses!r}"))
            if uses and str(uses).startswith("actions/upload-artifact"):
                cond = str(step.get("if", ""))
                if "always()" not in cond:
                    findings.append(finding("R8", "warn", jloc,
                                            "artifact upload should use if: always()"))
        if runner and str(runner).startswith("windows"):
            has_powershell_step = any(
                isinstance(s.get("run"), str) and "$env:" in s["run"]
                for s in job.get("steps", []) or [])
            if has_powershell_step:
                for s in job.get("steps", []) or []:
                    if isinstance(s.get("run"), str) and "$env:" in s["run"] and s.get("shell") != "pwsh":
                        findings.append(finding("R9", "warn", jloc,
                                                "windows steps using $env: should declare shell: pwsh"))
    return findings


def check_required_files(workflows_dir: Path, required=REQUIRED_WORKFLOWS) -> list[dict]:
    findings = []
    for name in required:
        if not (workflows_dir / name).is_file():
            findings.append(finding("R0", "error", str(workflows_dir / name),
                                    "required workflow file missing"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GitHub Actions workflow contract linter")
    parser.add_argument("--workflows-dir", default=".github/workflows")
    parser.add_argument("--json", action="store_true", help="emit JSON findings")
    args = parser.parse_args(argv)

    workflows_dir = Path(args.workflows_dir)
    findings = check_required_files(workflows_dir)
    for path in sorted(workflows_dir.glob("*.yml")) + sorted(workflows_dir.glob("*.yaml")):
        findings.extend(lint_workflow(path))

    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"workflows_dir": str(workflows_dir), "findings": findings,
                          "errors": len(errors)}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['rule']} {f['location']}: {f['message']}")
        print(f"-- {len(findings)} findings ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
