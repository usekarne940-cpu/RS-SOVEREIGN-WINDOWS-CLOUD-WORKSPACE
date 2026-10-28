#!/usr/bin/env python3
"""Cross-platform task dispatcher.

Tasks are defined as JSON files in automation/tasks/*.json:

    {"name": "audit", "description": "...", "os": ["windows", "linux"],
     "commands": {"windows": "powershell ...", "linux": "bash ..."},
     "timeout_seconds": 600}

`--list` shows tasks; `--run NAME [--dry-run]` selects the command for the
current platform. Windows tasks refuse to run on non-Windows hosts with exit
code 2 (BLOCKED semantics), never silently skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REQUIRED_KEYS = ("name", "description", "os", "commands")


def current_platform() -> str:
    if os.name == "nt":
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    return sys.platform


def load_task(path: Path) -> dict:
    try:
        task = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid task file {path}: {exc}") from exc
    missing = [key for key in REQUIRED_KEYS if key not in task]
    if missing:
        raise ValueError(f"task file {path} missing keys: {missing}")
    if not isinstance(task["commands"], dict) or not task["commands"]:
        raise ValueError(f"task file {path}: 'commands' must be a non-empty mapping")
    if not isinstance(task["os"], list):
        raise ValueError(f"task file {path}: 'os' must be a list")
    return task


def load_tasks(tasks_dir: Path) -> dict[str, dict]:
    tasks = {}
    for path in sorted(tasks_dir.glob("*.json")):
        task = load_task(path)
        tasks[task["name"]] = task
    return tasks


def select_command(task: dict, platform: str) -> tuple[str | None, str]:
    """Return (command, reason). Refuses OS-mismatched tasks explicitly."""
    if platform not in task["os"]:
        return None, (f"task '{task['name']}' does not support platform '{platform}' "
                      f"(supports: {', '.join(task['os'])})")
    commands = task["commands"]
    if platform in commands:
        return commands[platform], "platform-specific command"
    if "any" in commands:
        return commands["any"], "platform-agnostic command"
    return None, f"task '{task['name']}' has no command for platform '{platform}'"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RS task dispatcher")
    parser.add_argument("--tasks-dir", default=None,
                        help="default: <repo>/automation/tasks")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--run", metavar="TASK")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    tasks_dir = Path(args.tasks_dir) if args.tasks_dir else \
        Path(__file__).resolve().parents[2] / "automation" / "tasks"
    if not tasks_dir.is_dir():
        print(f"error: tasks directory not found: {tasks_dir}", file=sys.stderr)
        return 1
    tasks = load_tasks(tasks_dir)

    if args.list:
        print(f"{len(tasks)} tasks in {tasks_dir} (platform: {current_platform()})")
        for name in sorted(tasks):
            task = tasks[name]
            print(f"  {name:20s} [{','.join(task['os'])}] {task['description']}")
        return 0

    if not args.run:
        parser.error("nothing to do: use --list or --run TASK")
    if args.run not in tasks:
        print(f"error: unknown task '{args.run}' (available: {', '.join(sorted(tasks))})",
              file=sys.stderr)
        return 1

    platform = current_platform()
    command, reason = select_command(tasks[args.run], platform)
    if command is None:
        print(json.dumps({"task": args.run, "status": "BLOCKED", "reason": reason}),
              file=sys.stderr)
        return 2

    if args.dry_run:
        print(json.dumps({"task": args.run, "status": "DRY_RUN", "platform": platform,
                          "reason": reason, "command": command}, indent=2))
        return 0

    timeout = int(tasks[args.run].get("timeout_seconds", 900))
    print(f"[run_task] {args.run} on {platform}: {command}")
    proc = subprocess.run(command, shell=True, timeout=timeout)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
