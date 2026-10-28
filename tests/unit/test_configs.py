"""Unit tests for repository configuration files (schemas + values)."""
import json

import pytest


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_xlite_config_schema(repo_root):
    cfg = load(repo_root / "config" / "xlite.json")
    for key in ("file_id", "filename", "page_url", "api_endpoint",
                "min_free_disk_gb", "analysis_only", "never_execute"):
        assert key in cfg, f"config/xlite.json missing {key}"
    assert cfg["file_id"] == "ZdPxkVmH"
    assert cfg["api_endpoint"].endswith(cfg["file_id"])
    assert cfg["analysis_only"] is True
    assert cfg["never_execute"] is True
    assert cfg["expected_sha256"] is None  # no hardcoded secret-like values


def test_winget_config_schema(repo_root):
    cfg = load(repo_root / "config" / "applications.json")
    apps = cfg["applications"]
    assert len(apps) >= 5
    for app in apps:
        for key in ("id", "name", "category", "required"):
            assert key in app, f"app {app.get('id')} missing {key}"
    ids = [a["id"] for a in apps]
    assert len(ids) == len(set(ids))
    assert "7zip.7zip" in ids and "Git.Git" in ids and "Python.Python.3.12" in ids


def test_gui_apps_config_schema(repo_root):
    cfg = load(repo_root / "applications" / "applications.json")
    apps = cfg["apps"]
    assert len(apps) >= 3
    allowed_close = {"window", "process", "none"}
    for app in apps:
        for key in ("name", "enabled", "launch", "process", "launch_wait_s", "close"):
            assert key in app, f"gui app {app.get('name')} missing {key}"
        assert app["close"] in allowed_close
        assert isinstance(app["enabled"], bool)
        assert app["launch_wait_s"] > 0
    names = [a["name"] for a in apps]
    assert "notepad" in names


def test_settings_config_schema(repo_root):
    cfg = load(repo_root / "config" / "settings.json")
    assert cfg["version"] == "1.0.0"
    timeouts = cfg["timeouts"]
    for key in ("default_job_minutes", "gui_job_minutes", "xlite_job_minutes"):
        assert isinstance(timeouts[key], int) and timeouts[key] > 0
    assert timeouts["xlite_job_minutes"] >= 60


def test_version_file(repo_root):
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    assert version == "1.0.0"


def test_requirements_pinned(repo_root):
    lines = [l.strip() for l in
             (repo_root / "scripts" / "python" / "requirements.txt")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any(l.startswith("pytest") for l in lines)
    assert any(l.startswith("PyYAML") for l in lines)


def test_no_placeholder_only_files(repo_root):
    """PLAN.md §7: no empty placeholder files. Every .py/.ps1/.psm1/.sh/.json
    in the tree must be non-trivial (>1 line)."""
    targets = []
    for pattern in ("scripts/**/*.py", "scripts/**/*.ps1", "scripts/**/*.psm1",
                    "scripts/**/*.sh", "config/*.json", "applications/*.json",
                    "automation/tasks/*.json", ".github/workflows/*.yml"):
        targets += list(repo_root.glob(pattern))
    assert len(targets) >= 30
    for path in targets:
        content = path.read_text(encoding="utf-8").strip()
        assert len(content.splitlines()) >= 2, f"placeholder-like file: {path}"
