"""Unit tests for run_all_checks (JUnit parsing and record mapping)."""
import run_all_checks as rac

JUNIT_SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="tests" tests="4" failures="1" errors="1" skipped="1">
  <testcase classname="tests.unit.test_x" name="test_pass"/>
  <testcase classname="tests.unit.test_x" name="test_fail">
    <failure message="assert 1 == 2">assert 1 == 2</failure>
  </testcase>
  <testcase classname="tests.unit.test_x" name="test_error">
    <error message="boom">boom traceback</error>
  </testcase>
  <testcase classname="tests.unit.test_x" name="test_skip">
    <skipped message="no network">skipped: no network</skipped>
  </testcase>
</testsuite>
"""


def test_parse_junit_statuses(tmp_path):
    path = tmp_path / "junit.xml"
    path.write_text(JUNIT_SAMPLE, encoding="utf-8")
    records = rac.parse_junit(path)
    by_name = {r["name"]: r for r in records}
    assert len(records) == 4
    assert by_name["test_pass"]["status"] == "PASS"
    assert by_name["test_fail"]["status"] == "FAIL"
    assert "assert 1 == 2" in by_name["test_fail"]["error"]
    assert by_name["test_error"]["status"] == "FAIL"
    assert "boom" in by_name["test_error"]["error"]
    assert by_name["test_skip"]["status"] == "NOT_RUN"


def test_parse_junit_record_schema(tmp_path):
    """Every parsed record must satisfy the PLAN.md §9 8-field schema."""
    import report_generator as rg

    path = tmp_path / "junit.xml"
    path.write_text(JUNIT_SAMPLE, encoding="utf-8")
    for record in rac.parse_junit(path):
        rg.validate_record(record)  # raises on any schema violation


def test_parse_junit_empty_file(tmp_path):
    path = tmp_path / "empty.xml"
    path.write_text(
        '<?xml version="1.0"?><testsuite name="t" tests="0"></testsuite>',
        encoding="utf-8")
    assert rac.parse_junit(path) == []


def test_records_counts_helper():
    records = rac.Records("test-run")
    for status in ("PASS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"):
        records.add(f"T-{status}", "n", "c", "e", "a", status, "ev")
    assert records.counts() == {"PASS": 2, "FAIL": 1, "BLOCKED": 1, "NOT_RUN": 1}
    assert len(records.records) == 5
