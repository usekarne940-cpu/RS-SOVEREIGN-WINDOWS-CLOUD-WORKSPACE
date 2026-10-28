#!/usr/bin/env python3
"""Test-record renderer and release-report generator.

Renders test records (PLAN.md section 9 schema: TEST ID / NAME / COMMAND /
EXPECTED / ACTUAL / STATUS / EVIDENCE / ERROR DETAILS) into grouped Markdown
tables with summary counts, and renders the PLAN.md section 12 final report
format from measured data. Invalid records are surfaced, never hidden.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("test_id", "name", "command", "expected", "actual", "status", "evidence")
ALLOWED_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN")


class RecordError(ValueError):
    pass


def validate_record(record: dict) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in record or record[f] in (None, "")]
    if missing:
        raise RecordError(f"record {record.get('test_id', '<unknown>')}: missing fields {missing}")
    if record["status"] not in ALLOWED_STATUSES:
        raise RecordError(
            f"record {record['test_id']}: status {record['status']!r} not in {ALLOWED_STATUSES}")


def escape(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def summarize(records: list[dict]) -> dict:
    counts = {status: 0 for status in ALLOWED_STATUSES}
    for record in records:
        counts[record["status"]] += 1
    return counts


def render_markdown(records: list[dict], title: str = "Test Results") -> str:
    lines = [f"# {title}", "", f"Total records: {len(records)}", ""]
    counts = summarize(records)
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    for status in ALLOWED_STATUSES:
        lines.append(f"| {status} | {counts[status]} |")
    lines.append("")
    suites: dict[str, list[dict]] = {}
    for record in records:
        suites.setdefault(record.get("suite", "default"), []).append(record)
    for suite in sorted(suites):
        lines.append(f"## Suite: {suite}")
        lines.append("")
        lines.append("| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |")
        lines.append("|---------|------|---------|----------|--------|--------|----------|-------|")
        for record in sorted(suites[suite], key=lambda r: r["test_id"]):
            error = escape(record.get("error", "") or "")
            lines.append(
                f"| {escape(record['test_id'])} | {escape(record['name'])} "
                f"| `{escape(record['command'])}` | {escape(record['expected'])} "
                f"| {escape(record['actual'])} | **{record['status']}** "
                f"| {escape(record['evidence'])} | {error} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_release_report(data: dict) -> str:
    """PLAN.md section 12 format — values must be measured, never invented."""
    fields = [
        "project_status", "rs_memory_status", "plan_read_status", "agent_count",
        "waves_completed", "files_created", "files_modified", "features_completed",
        "features_blocked", "tests_passed", "tests_failed", "security_status",
        "source_archive", "source_sha256", "release_readiness", "next_required_action",
    ]
    missing = [f for f in fields if f not in data]
    if missing:
        raise RecordError(f"release report data missing: {missing}")
    lines = [
        "RS SOVEREIGN WINDOWS CLOUD WORKSPACE",
        f"FOUNDER: {data.get('founder', 'RAJSARASWATI JATAV (RS)')}",
        f"PROJECT STATUS: {data['project_status']}",
        f"RS MEMORY STATUS: {data['rs_memory_status']}",
        f"PLAN.MD READ STATUS: {data['plan_read_status']}",
        f"ACTUAL AGENT COUNT: {data['agent_count']}",
        f"WAVES COMPLETED: {data['waves_completed']}",
        f"FILES CREATED: {data['files_created']}",
        f"FILES MODIFIED: {data['files_modified']}",
        f"FEATURES COMPLETED: {data['features_completed']}",
        f"FEATURES BLOCKED: {data['features_blocked']}",
        f"TESTS PASSED: {data['tests_passed']}",
        f"TESTS FAILED: {data['tests_failed']}",
        f"SECURITY STATUS: {data['security_status']}",
        f"SOURCE ARCHIVE: {data['source_archive']}",
        f"SOURCE SHA-256: {data['source_sha256']}",
        "GITHUB STATUS: NOT DEPLOYED",
        f"RELEASE READINESS: {data['release_readiness']}",
        f"NEXT REQUIRED ACTION: {data['next_required_action']}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="test-record / release report renderer")
    sub = parser.add_subparsers(dest="command", required=True)
    p_md = sub.add_parser("render", help="render records JSON to Markdown")
    p_md.add_argument("--records", required=True)
    p_md.add_argument("--out", required=True)
    p_md.add_argument("--title", default="Test Results")
    p_rel = sub.add_parser("release", help="render release report from data JSON")
    p_rel.add_argument("--data", required=True)
    p_rel.add_argument("--out", required=True)

    args = parser.parse_args(argv)
    if args.command == "render":
        records = json.loads(Path(args.records).read_text(encoding="utf-8"))
        if isinstance(records, dict):
            records = records.get("records", [])
        for record in records:
            validate_record(record)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(render_markdown(records, args.title), encoding="utf-8")
        print(f"rendered {len(records)} records -> {args.out}")
        return 0
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(render_release_report(data), encoding="utf-8")
    print(f"rendered release report -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
