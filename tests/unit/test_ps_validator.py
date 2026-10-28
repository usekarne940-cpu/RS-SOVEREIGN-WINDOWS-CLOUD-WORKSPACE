"""Unit tests for ps_validator (heuristic tier; pwsh AST tier runs on Windows)."""
import ps_validator as psv


def errors(findings):
    return [f for f in findings if f["severity"] == "error"]


GOOD_SCRIPT = """#Requires -Version 5.1
[CmdletBinding()]
param([string]$Path)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Write-Host "hello { world"
Get-ChildItem -Path $Path | ForEach-Object { Write-Host $_.Name }
"""


def test_good_script_no_errors():
    assert errors(psv.validate_text(GOOD_SCRIPT, "good.ps1")) == []


def test_unbalanced_brace_is_error():
    bad = "foreach ($x in 1..3) {\n  Write-Host $x\n"  # missing }
    assert any(f["rule"] == "PS-BALANCE" for f in errors(psv.validate_text(bad, "bad.ps1")))


def test_unbalanced_paren_is_error():
    assert any(f["rule"] == "PS-BALANCE"
               for f in errors(psv.validate_text("Write-Host ('unclosed", "bad.ps1")))


def test_braces_inside_strings_ignored():
    text = "$s = '}{ not counted'\nWrite-Host $s\n"
    assert errors(psv.validate_text(text, "s.ps1")) == []


def test_braces_inside_double_quoted_with_escapes_ignored():
    text = '$msg = "literal `{ brace and }{ pair"\nWrite-Host $msg\n'
    assert errors(psv.validate_text(text, "s.ps1")) == []


def test_here_string_content_ignored():
    text = "$h = @'\nunbalanced { braces everywhere )(\n'@\nWrite-Host $h\n"
    assert errors(psv.validate_text(text, "s.ps1")) == []


def test_scanning_resumes_after_here_string():
    """Regression: the scanner must resume normal scanning after a
    here-string closes (previously everything after the opener was skipped
    forever)."""
    text = "$h = @'\njunk { )(\n'@\nWrite-Host 'ok'\nforeach ($x in 1..2) {\n"
    findings = errors(psv.validate_text(text, "s.ps1"))
    assert any(f["rule"] == "PS-BALANCE" for f in findings), \
        "unclosed brace after here-string must be detected"
    text_ok = "$h = @'\njunk { )(\n'@\nWrite-Host 'ok'\nforeach ($x in 1..2) { Write-Host $x }\n"
    assert errors(psv.validate_text(text_ok, "s.ps1")) == []


def test_double_quoted_here_string_resumes():
    text = '$h = @"\njunk { )(\n"@\nWrite-Host (unclosed\n'
    findings = errors(psv.validate_text(text, "s.ps1"))
    assert any(f["rule"] == "PS-BALANCE" for f in findings)


def test_block_comment_content_ignored():
    text = "<#\nunbalanced { in comment\n#>\nWrite-Host 'ok'\n"
    assert errors(psv.validate_text(text, "s.ps1")) == []


def test_line_comment_brace_ignored():
    text = "Write-Host 'ok' # trailing comment with {\n"
    assert errors(psv.validate_text(text, "s.ps1")) == []


def test_invoke_expression_is_error():
    assert any(f["rule"] == "PS-EXEC-001"
               for f in errors(psv.validate_text("Invoke-Expression $cmd", "bad.ps1")))


def test_iex_alias_is_error():
    assert any(f["rule"] == "PS-EXEC-002"
               for f in errors(psv.validate_text("iex 'Get-Date'", "bad.ps1")))


def test_execution_policy_bypass_is_error():
    text = "Set-ExecutionPolicy -Scope Process Bypass"
    assert any(f["rule"] == "PS-POLICY"
               for f in errors(psv.validate_text(text, "bad.ps1")))


def test_rm_recurse_alias_warns():
    findings = psv.validate_text("rm -Recurse ./stuff", "warn.ps1")
    assert any(f["rule"] == "PS-RM" and f["severity"] == "warn" for f in findings)
    assert errors(findings) == []


def test_null_byte_is_error():
    findings = psv.validate_text("Write-Host 'x'\x00", "bad.ps1")
    assert any(f["rule"] == "PS-ENCODING" for f in errors(findings))


def test_required_markers_missing_warns():
    findings = psv.check_required("Write-Host 'no markers here'", "plain.ps1")
    assert findings
    assert all(f["severity"] == "warn" for f in findings)


def test_required_markers_present():
    assert psv.check_required(GOOD_SCRIPT, "good.ps1") == []


def test_check_balance_reports_line_number():
    findings = psv.check_balance("Write-Host 'a'\nforeach ($x in 1..2) {\n", "bad.ps1")
    assert findings
    assert ":2" in findings[0]["location"]


def test_validate_dir_repo_powershell(repo_root):
    """The repository PowerShell suite must be error-free (static tier)."""
    results = psv.validate_dir(repo_root / "scripts" / "powershell", real_parse=False)
    assert results, "no PowerShell files found"
    for path, findings in results.items():
        assert errors(findings) == [], f"unexpected errors in {path}: {findings}"
