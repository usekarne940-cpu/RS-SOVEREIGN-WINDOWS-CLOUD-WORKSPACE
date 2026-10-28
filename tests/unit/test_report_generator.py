"""Unit tests for report_generator (record schema + rendering)."""
import pytest

import report_generator as rg

VALID_RECORD = {
    "test_id": "T-001", "suite": "local", "name": "sample test",
    "command": "python -m pytest", "expected": "exit 0", "actual": "exit 0",
    "status": "PASS", "evidence": "reports/x.xml", "error": "",
}
ALL_FIELDS = ("test_id", "suite", "name", "command", "expected", "actual",
              "status", "evidence", "error")


def test_validate_record_accepts_valid():
    rg.validate_record(VALID_RECORD)


@pytest.mark.parametrize("missing_field", [f for f in rg.REQUIRED_FIELDS])
def test_validate_record_rejects_missing(missing_field):
    record = {k: v for k, v in VALID_RECORD.items() if k != missing_field}
    with pytest.raises(rg.RecordError, match="missing fields"):
        rg.validate_record(record)


@pytest.mark.parametrize("status", ["pass", "SKIPPED", "ERROR", "ok"])
def test_validate_record_rejects_bad_status(status):
    record = dict(VALID_RECORD, status=status)
    with pytest.raises(rg.RecordError, match="not in"):
        rg.validate_record(record)


def test_validate_record_rejects_empty_status_as_missing():
    """An empty status fails the required-fields gate first."""
    record = dict(VALID_RECORD, status="")
    with pytest.raises(rg.RecordError, match="missing fields"):
        rg.validate_record(record)


@pytest.mark.parametrize("status", rg.ALLOWED_STATUSES)
def test_all_statuses_accepted(status):
    rg.validate_record(dict(VALID_RECORD, status=status))


def test_summarize_counts():
    records = [dict(VALID_RECORD, status=s)
               for s in ("PASS", "PASS", "FAIL", "BLOCKED", "NOT_RUN")]
    assert rg.summarize(records) == {"PASS": 2, "FAIL": 1, "BLOCKED": 1, "NOT_RUN": 1}


def test_render_markdown_structure():
    records = [VALID_RECORD,
               dict(VALID_RECORD, test_id="T-002", suite="other", status="FAIL",
                    error="boom | pipe")]
    md = rg.render_markdown(records, title="Results")
    assert md.startswith("# Results")
    assert "## Suite: local" in md
    assert "## Suite: other" in md
    assert "**PASS**" in md and "**FAIL**" in md
    assert "T-001" in md and "T-002" in md
    assert "boom \\| pipe" in md  # pipe escaped


RELEASE_DATA = {
    "project_status": "LOCAL DEVELOPMENT COMPLETE",
    "rs_memory_status": "ACTIVE (local implementation)",
    "plan_read_status": "COMPLETE — 3 analytical passes",
    "agent_count": "4 (1 orchestrator + 3 parallel review subagents)",
    "waves_completed": "30/30 (6 wave groups)",
    "files_created": "123",
    "files_modified": "4",
    "features_completed": "see REQUIREMENTS-MATRIX",
    "features_blocked": "GitHub push (awaiting owner approval)",
    "tests_passed": "88",
    "tests_failed": "0",
    "security_status": "clean",
    "source_archive": "download/rs-windows-cloud-workspace-v1.0.0.zip",
    "source_sha256": "ab" * 32,
    "release_readiness": "READY (pending approval)",
    "next_required_action": "approve GitHub deployment",
}


def test_render_release_report_full():
    text = rg.render_release_report(RELEASE_DATA)
    assert text.startswith("RS SOVEREIGN WINDOWS CLOUD WORKSPACE")
    assert "FOUNDER: RAJSARASWATI JATAV (RS)" in text
    assert "GITHUB STATUS: NOT DEPLOYED" in text
    assert "SOURCE SHA-256: " + "ab" * 32 in text


def test_render_release_report_missing_field():
    data = {k: v for k, v in RELEASE_DATA.items() if k != "agent_count"}
    with pytest.raises(rg.RecordError, match="agent_count"):
        rg.render_release_report(data)
