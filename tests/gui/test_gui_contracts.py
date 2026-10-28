"""GUI contract tests (Linux-executable tier).

The GUI automation itself runs ONLY on real Windows (gui.yml). These tests
verify the wiring that makes that possible: the app spec, the driver script,
the workflow and the best-effort policy. No Windows results are invented
here (PLAN.md §9: Windows execution happens on the runners).
"""
import json

import ps_validator as psv


def test_gui_spec_present_and_shape(repo_root):
    spec = json.loads((repo_root / "applications" / "applications.json")
                     .read_text(encoding="utf-8"))
    apps = spec["apps"]
    assert len(apps) >= 3
    assert any(a["name"] == "notepad" and a["send_keys"] for a in apps)
    assert any(a["name"] == "calculator" for a in apps)
    assert any(a["name"] == "explorer" and a["close"] == "none" for a in apps)


def test_gui_driver_reads_spec_and_uses_real_automation(repo_root):
    text = (repo_root / "scripts" / "powershell" / "Invoke-GuiTest.ps1") \
        .read_text(encoding="utf-8")
    assert "applications\\applications.json" in text
    assert "AppActivate" in text
    assert "SendKeys" in text or "SendWait" in text
    assert "CloseMainWindow" in text
    assert "Capture-RsScreen" in text
    assert "D-005" in text  # best-effort policy is documented in the script
    assert "gui-test-results.json" in text


def test_gui_driver_passes_static_validation(repo_root):
    results = psv.validate_dir(repo_root / "scripts" / "powershell", real_parse=False)
    for path, findings in results.items():
        errors = [f for f in findings if f["severity"] == "error"]
        assert errors == [], f"{path}: {errors}"


def test_screenshot_helper_implemented(repo_root):
    module = (repo_root / "scripts" / "powershell" / "Common.psm1") \
        .read_text(encoding="utf-8")
    assert "CopyFromScreen" in module
    assert "VirtualScreen" in module
    assert "ImageFormat]::Png" in module
    driver = (repo_root / "scripts" / "powershell" / "Capture-Screenshots.ps1") \
        .read_text(encoding="utf-8")
    assert "Capture-RsScreen" in driver
    assert "screenshots.json" in driver


def test_gui_workflow_runs_driver(repo_root):
    text = (repo_root / ".github" / "workflows" / "gui.yml").read_text(encoding="utf-8")
    assert "Invoke-GuiTest.ps1" in text
    assert "Install-Applications.ps1" in text
    assert "artifacts/screenshots" in text


def test_windows_execution_explicitly_not_faked_locally(repo_root):
    """The docs must state that GUI results come from Windows runners only."""
    testing_doc = (repo_root / "docs" / "TESTING.md")
    if testing_doc.exists():
        text = testing_doc.read_text(encoding="utf-8")
        assert "NOT_RUN" in text and "Windows" in text
