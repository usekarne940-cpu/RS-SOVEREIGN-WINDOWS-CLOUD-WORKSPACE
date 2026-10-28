"""Integration tests: CLI entrypoints + config/task wiring across modules."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

MODULES = [
    "xlite_inspector.py", "workflow_lint.py", "ps_validator.py",
    "secret_scanner.py", "artifact_manager.py", "report_generator.py",
    "run_task.py", "run_all_checks.py",
]


@pytest.mark.integration
@pytest.mark.parametrize("module", MODULES)
def test_cli_help_exit_zero(repo_root, module):
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / module), "--help"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, f"{module} --help failed: {proc.stderr}"
    assert "usage" in proc.stdout.lower()


@pytest.mark.integration
def test_report_generator_render_cli(repo_root, tmp_path):
    """CLI render flow: records JSON -> markdown report file."""
    records = [{
        "test_id": "T-001", "suite": "cli", "name": "cli render",
        "command": "report_generator render", "expected": "file written",
        "actual": "file written", "status": "PASS", "evidence": "out file",
        "error": "",
    }]
    src = tmp_path / "records.json"
    src.write_text(json.dumps(records), encoding="utf-8")
    out = tmp_path / "report.md"
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / "report_generator.py"),
         "render", "--records", str(src), "--out", str(out), "--title", "CLI Render"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    text = out.read_text(encoding="utf-8")
    assert "# CLI Render" in text and "T-001" in text and "**PASS**" in text


@pytest.mark.integration
def test_inspector_metadata_cli_on_repo_config(repo_root):
    """The CLI must load the real repository config and reach a definite
    outcome (metadata or a typed BLOCKED error) without hanging. Note: this
    makes a live endpoint attempt when network is reachable, but every
    outcome — including offline BLOCKED — is a pass; it never hangs because
    every read is size-capped (see docs/TESTING.md)."""
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / "xlite_inspector.py"),
         "--config", str(repo_root / "config" / "xlite.json"), "metadata"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1, 2), "unexpected exit code"
    assert "Traceback" not in proc.stderr, "unhandled crash"


@pytest.mark.integration
def test_task_dispatcher_lists_repo_tasks(repo_root):
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / "run_task.py"),
         "--tasks-dir", str(repo_root / "automation" / "tasks"), "--list"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0
    for task in ("audit", "gui-test", "xlite-probe", "cleanup", "package"):
        assert task in proc.stdout


@pytest.mark.integration
def test_workflow_lint_cli_on_repo_workflows(repo_root):
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / "workflow_lint.py"),
         "--workflows-dir", str(repo_root / ".github" / "workflows")],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, f"workflow lint errors: {proc.stdout}"


@pytest.mark.integration
def test_ps_validator_cli_on_repo(repo_root):
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / "ps_validator.py"),
         "--dir", str(repo_root / "scripts" / "powershell"), "--no-real-parse"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, f"ps validation errors: {proc.stdout}"


@pytest.mark.integration
def test_secret_scanner_cli_on_repo(repo_root):
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "python" / "secret_scanner.py"),
         "--root", str(repo_root)],
        capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, f"secret findings: {proc.stdout}"


@pytest.mark.integration
def test_artifact_manager_manifest_verify_roundtrip(repo_root, tmp_path):
    module = repo_root / "scripts" / "python" / "artifact_manager.py"
    manifest_path = tmp_path / "manifest.json"
    proc = subprocess.run(
        [sys.executable, str(module), "manifest",
         "--root", str(repo_root / "config"), "--out", str(manifest_path)],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0
    assert manifest_path.exists()
    verify = subprocess.run(
        [sys.executable, str(module), "verify",
         "--root", str(repo_root / "config"), "--manifest", str(manifest_path)],
        capture_output=True, text=True, timeout=120)
    assert verify.returncode == 0
    assert json.loads(verify.stdout)["ok"] is True


@pytest.mark.integration
def test_all_repo_json_parses(repo_root):
    """Every JSON file in the repository must be parseable."""
    json_files = [p for p in repo_root.rglob("*.json")
                  if ".git" not in p.parts and "__pycache__" not in p.parts]
    assert len(json_files) >= 15
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))
