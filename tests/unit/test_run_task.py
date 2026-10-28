"""Unit tests for run_task dispatcher."""
import json

import pytest

import run_task as rt


def write_task(tmp_path, name, **overrides):
    task = {
        "name": name,
        "description": f"task {name}",
        "os": ["windows", "linux"],
        "commands": {"windows": "echo win", "linux": "echo linux"},
    }
    task.update(overrides)
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(task), encoding="utf-8")
    return path


def test_load_task_valid(tmp_path):
    task = rt.load_task(write_task(tmp_path, "alpha"))
    assert task["name"] == "alpha"


def test_load_task_missing_keys(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"name": "bad"}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing keys"):
        rt.load_task(path)


def test_load_task_bad_commands(tmp_path):
    with pytest.raises(ValueError, match="commands"):
        rt.load_task(write_task(tmp_path, "bad", commands={}))


def test_load_tasks_registry(tmp_path):
    write_task(tmp_path, "alpha")
    write_task(tmp_path, "beta")
    tasks = rt.load_tasks(tmp_path)
    assert set(tasks) == {"alpha", "beta"}


def test_select_command_platform_specific():
    task = {"name": "t", "os": ["windows", "linux"],
            "commands": {"windows": "w", "linux": "l"}}
    command, reason = rt.select_command(task, "windows")
    assert command == "w"
    command, reason = rt.select_command(task, "linux")
    assert command == "l"


def test_select_command_any_fallback():
    task = {"name": "t", "os": ["windows", "linux"], "commands": {"any": "python x.py"}}
    command, reason = rt.select_command(task, "linux")
    assert command == "python x.py"
    assert "agnostic" in reason


def test_select_command_os_mismatch_blocks():
    task = {"name": "t", "os": ["windows"], "commands": {"windows": "w"}}
    command, reason = rt.select_command(task, "linux")
    assert command is None
    assert "does not support platform 'linux'" in reason


def test_select_command_missing_platform_entry():
    task = {"name": "t", "os": ["windows"], "commands": {"linux": "l"}}
    command, reason = rt.select_command(task, "windows")
    assert command is None


def test_main_list(tmp_path, capsys):
    write_task(tmp_path, "alpha")
    write_task(tmp_path, "beta")
    code = rt.main(["--tasks-dir", str(tmp_path), "--list"])
    out = capsys.readouterr().out
    assert code == 0
    assert "alpha" in out and "beta" in out


def test_main_unknown_task(tmp_path):
    write_task(tmp_path, "alpha")
    code = rt.main(["--tasks-dir", str(tmp_path), "--run", "nope"])
    assert code == 1


def test_main_missing_task_arg_errors(tmp_path):
    with pytest.raises(SystemExit):
        rt.main(["--tasks-dir", str(tmp_path)])


def test_main_dry_run_current_platform(tmp_path, capsys):
    write_task(tmp_path, "alpha",
               commands={"any": "python scripts/python/run_all_checks.py"})
    code = rt.main(["--tasks-dir", str(tmp_path), "--run", "alpha", "--dry-run"])
    out = capsys.readouterr().out
    assert code == 0
    assert '"status": "DRY_RUN"' in out
    assert "run_all_checks" in out


def test_main_windows_only_task_blocks_on_linux(tmp_path, capsys):
    """GUI task is Windows-only: on a Linux host it must BLOCK (exit 2),
    never silently pass."""
    write_task(tmp_path, "gui", os=["windows"],
               commands={"windows": "powershell -File Invoke-GuiTest.ps1"})
    code = rt.main(["--tasks-dir", str(tmp_path), "--run", "gui", "--dry-run"])
    err = capsys.readouterr().err
    assert code == 2
    assert "BLOCKED" in err


def test_repo_task_registry_valid(repo_root):
    """The repository automation/tasks registry must be valid and non-empty."""
    tasks = rt.load_tasks(repo_root / "automation" / "tasks")
    assert len(tasks) >= 10
    expected = {"audit", "install-apps", "gui-test", "screenshots", "windows-tests",
                "xlite-probe", "xlite-inspect-full", "cleanup", "local-checks", "package"}
    assert expected <= set(tasks)
