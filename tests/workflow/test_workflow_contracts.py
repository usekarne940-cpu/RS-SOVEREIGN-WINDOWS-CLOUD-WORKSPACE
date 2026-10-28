"""Workflow contract tests: the 7 GitHub Actions workflows must exist, be
structurally valid, and wire the real scripts with the right runners,
permissions, timeouts and artifact uploads."""
from pathlib import Path

import yaml

REQUIRED = ("audit.yml", "build.yml", "test.yml", "gui.yml",
            "screenshots.yml", "xlite-inspection.yml", "cleanup.yml")


def load(repo_root, name):
    data = yaml.safe_load((repo_root / ".github" / "workflows" / name)
                          .read_text(encoding="utf-8"))
    data["__triggers__"] = data.get("on", data.get(True))  # YAML 1.1 `on` gotcha
    return data


def job_uses(job, needle):
    for step in job.get("steps", []):
        if needle in str(step.get("uses", "")):
            return step
    return None


def test_all_required_workflows_exist(repo_root):
    for name in REQUIRED:
        assert (repo_root / ".github" / "workflows" / name).is_file(), f"missing {name}"
    workflows = list((repo_root / ".github" / "workflows").glob("*.yml"))
    assert len(workflows) == 7


def test_all_workflows_least_privilege(repo_root):
    for name in REQUIRED:
        data = load(repo_root, name)
        perms = data.get("permissions")
        assert isinstance(perms, dict), f"{name}: missing permissions mapping"
        assert perms.get("contents") == "read", f"{name}: contents must be read"
        assert data.get("concurrency", {}).get("group"), f"{name}: missing concurrency"
        for job_id, job in data["jobs"].items():
            timeout = job.get("timeout-minutes")
            assert isinstance(timeout, (int, float)) and 0 < timeout <= 360, \
                f"{name}#{job_id}: bad timeout"


def test_no_pull_request_target_anywhere(repo_root):
    for name in REQUIRED:
        triggers = load(repo_root, name)["__triggers__"] or {}
        assert "pull_request_target" not in triggers, f"{name} uses pull_request_target"


def test_audit_wiring(repo_root):
    data = load(repo_root, "audit.yml")
    win = data["jobs"]["windows-audit"]
    linux = data["jobs"]["linux-audit"]
    assert win["runs-on"] == "windows-latest"
    assert linux["runs-on"] == "ubuntu-latest"
    win_text = (repo_root / ".github" / "workflows" / "audit.yml").read_text()
    assert "Get-SystemAudit.ps1" in win_text
    assert "audit.sh" in win_text
    for job in (win, linux):
        assert job_uses(job, "actions/upload-artifact"), "audit must upload reports"


def test_test_workflow_matrix_both_os(repo_root):
    data = load(repo_root, "test.yml")
    job = data["jobs"]["run-tests"]
    os_values = job["strategy"]["matrix"]["os"]
    assert "windows-latest" in os_values and "ubuntu-latest" in os_values
    text = (repo_root / ".github" / "workflows" / "test.yml").read_text()
    assert "Test-Syntax.ps1" in text, "Windows job must run the real AST syntax gate"
    assert "-m \"not network\"" in text
    assert job_uses(job, "actions/setup-python")


def test_build_workflow_packaging_and_release(repo_root):
    data = load(repo_root, "build.yml")
    package = data["jobs"]["validate-and-package"]
    release = data["jobs"]["github-release"]
    assert package["runs-on"] == "ubuntu-latest"
    needs = release["needs"]
    assert needs == "validate-and-package" or needs == ["validate-and-package"]
    assert release["if"] == "startsWith(github.ref, 'refs/tags/v')"
    assert release["permissions"]["contents"] == "write"  # job-scoped only
    assert data["permissions"]["contents"] == "read"  # workflow-level stays read
    text = (repo_root / ".github" / "workflows" / "build.yml").read_text()
    assert "run_tests.sh" in text and "package_release.sh" in text


def test_gui_workflow_wiring(repo_root):
    data = load(repo_root, "gui.yml")
    job = data["jobs"]["windows-gui"]
    assert job["runs-on"] == "windows-latest"
    text = (repo_root / ".github" / "workflows" / "gui.yml").read_text()
    assert "Install-Applications.ps1" in text
    assert "Invoke-GuiTest.ps1" in text
    assert job_uses(job, "actions/upload-artifact")


def test_screenshots_workflow_wiring(repo_root):
    data = load(repo_root, "screenshots.yml")
    job = data["jobs"]["windows-screenshots"]
    assert job["runs-on"] == "windows-latest"
    text = (repo_root / ".github" / "workflows" / "screenshots.yml").read_text()
    assert "Capture-Screenshots.ps1" in text


def test_xlite_workflow_contract(repo_root):
    data = load(repo_root, "xlite-inspection.yml")
    triggers = data["__triggers__"]
    assert "workflow_dispatch" in triggers
    mode_input = triggers["workflow_dispatch"]["inputs"]["mode"]
    assert mode_input["options"] == ["probe", "full"]
    job = data["jobs"]["windows-xlite-inspection"]
    assert job["runs-on"] == "windows-latest"
    assert job["timeout-minutes"] >= 60
    env = job["env"]
    assert env["PIXELDRAIN_API_KEY"] == "${{ secrets.PIXELDRAIN_API_KEY }}"
    text = (repo_root / ".github" / "workflows" / "xlite-inspection.yml").read_text()
    assert "Invoke-XliteInspection.ps1" in text
    # analysis-only guarantees
    assert "ANALYSIS ONLY" in text
    assert "cannot replace the runner OS" in text
    # never executes anything extracted from the archive
    for banned in ("setup.exe", "dism /apply", "Start-Process", "bcdboot"):
        assert banned not in text, f"xlite workflow must not reference {banned}"


def test_cleanup_workflow_scheduled(repo_root):
    data = load(repo_root, "cleanup.yml")
    triggers = data["__triggers__"]
    assert "schedule" in triggers
    assert "workflow_dispatch" in triggers
    assert "windows-cleanup" in data["jobs"]
    assert "linux-cleanup" in data["jobs"]
    text = (repo_root / ".github" / "workflows" / "cleanup.yml").read_text()
    assert "Invoke-Cleanup.ps1" in text and "cleanup.sh" in text


def test_actions_version_pinned(repo_root):
    for name in REQUIRED:
        text = (repo_root / ".github" / "workflows" / name).read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("- uses:") or line.startswith("uses:"):
                ref = line.split("uses:", 1)[1].strip().strip('"')
                assert "@" in ref and ref.split("@")[-1].startswith("v"), \
                    f"{name}: action not pinned: {ref}"


def test_branch_filters_are_exact_main_lists(repo_root):
    """Byte-verified reality: all push/pull_request branch filters are exact
    ['main'] lists. (During the AGENT-03 audit round a display-layer artifact
    made the on-disk [main] appear corrupted as 'ain]'; od -c proved the disk
    content correct. This contract pins the true content so any real future
    corruption fails loudly.)"""
    checked = 0
    for name in REQUIRED:
        data = load(repo_root, name)
        for event in ("push", "pull_request"):
            cfg = (data["__triggers__"] or {}).get(event)
            if isinstance(cfg, dict) and "branches" in cfg:
                assert cfg["branches"] == ["main"], \
                    f"{name} {event}: bad branch filter {cfg['branches']!r}"
                assert isinstance(cfg["branches"], list)
                checked += 1
    assert checked >= 6, f"expected >=6 branch filters, checked {checked}"
    build = load(repo_root, "build.yml")
    assert build["__triggers__"]["push"]["tags"] == ["v*"]
