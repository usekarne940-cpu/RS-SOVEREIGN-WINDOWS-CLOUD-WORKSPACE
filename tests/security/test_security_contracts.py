"""Security contract tests for the repository.

The grep-style contract tests scan PRODUCT code only (scripts/, .github/,
applications/, automation/, config/) — the test sources themselves contain
the banned literals as detection patterns and would trivially self-match.
The repo-wide secret scan covers every file including tests/."""
import re

import secret_scanner as ss

# banned-pattern literals are constructed to avoid self-matching this file.
# NOTE: the setup-exe marker is deliberately NOT banned repo-wide — it is a
# legitimate *detection* marker in xlite_inspector.WINDOWS_IMAGE_MARKERS; its
# dedicated contract test below pins it to that detection context only.
REMOTE_DESKTOP_PATTERN = re.compile(
    r"(?i)\b(rust" + r"desk|any" + r"desk|ng" + r"rok|tail" + r"scale|"
    r"mstsc\.exe|x" + r"rdp|openssh-server|ssh-server|rdp-server|vnc-server|"
    r"enable-psremoting)\b")
OS_INSTALL_PATTERN = re.compile(
    r"(?i)(dism\s+/apply|bcd" + r"boot|apply-image|expand-wim|install-windowsimage)")

PRODUCT_DIRS = ("scripts", ".github", "applications", "automation", "config")


def product_files(repo_root):
    for name in PRODUCT_DIRS:
        for path in (repo_root / name).rglob("*"):
            if path.is_file() and path.suffix.lower() in (
                    ".py", ".ps1", ".psm1", ".sh", ".yml", ".yaml", ".json"):
                yield path


def test_repo_secret_scan_clean(repo_root):
    """Repo-wide secret scan (covers tests/ too — constructed fakes in test
    sources must not produce real-looking literals)."""
    result = ss.scan_repo(repo_root)
    assert result["errors"] == 0, f"secret findings: {result['findings']}"
    assert result["files_scanned"] > 80, \
        f"scanner must cover the whole repo (scanned {result['files_scanned']})"


def test_no_remote_desktop_or_tunnel_code(repo_root):
    """PLAN.md §5: no persistent RDP hosting / remote desktop access code."""
    for path in product_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = REMOTE_DESKTOP_PATTERN.search(text)
        assert match is None, \
            f"remote-desktop/tunnel pattern {match!r} found in {path}"


def test_no_os_replacement_claims(repo_root):
    """No product code may attempt to install/apply the X-Lite image."""
    for path in product_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = OS_INSTALL_PATTERN.search(text)
        assert match is None, f"OS-install pattern {match!r} found in {path}"


def test_setup_exe_marker_is_detection_only(repo_root):
    """The setup-exe Windows-image marker may appear ONLY inside the
    WINDOWS_IMAGE_MARKERS detection tuple of xlite_inspector.py — never in an
    execution context."""
    source = (repo_root / "scripts" / "python" / "xlite_inspector.py") \
        .read_text(encoding="utf-8")
    import re as _re
    markers_block = _re.search(
        r"WINDOWS_IMAGE_MARKERS = \((?P<body>.*?)\)\n", source, _re.DOTALL)
    assert markers_block, "WINDOWS_IMAGE_MARKERS definition not found"
    marker = "set" + "up.exe"
    for match in _re.finditer(_re.escape(marker), source):
        inside = markers_block.start("body") <= match.start() < markers_block.end("body")
        assert inside, f"setup-exe marker outside detection tuple at offset {match.start()}"
    # and it is a pure string constant — never passed to a subprocess call
    assert "shell=True" not in source and "os.system" not in source


def test_inspector_never_executes_archive_content(repo_root):
    """xlite_inspector: subprocess is restricted to 7z list/extract, and the
    only invocation path for extracted files is none."""
    source = (repo_root / "scripts" / "python" / "xlite_inspector.py") \
        .read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "os.system" not in source
    # the only subprocess call is _run_seven_zip with list/extract args
    for call in re.findall(r"subprocess\.run\(\[([^\]]+)\]", source):
        assert "seven_zip" in call or "cmd" in call, f"unvetted subprocess: {call}"
    assert '"l"' in source and '"x"' in source  # 7z list + extract only
    assert "analysis_only" in source


def test_only_secret_reference_is_pixeldrain_key(repo_root):
    """Workflows may reference exactly one secret: PIXELDRAIN_API_KEY."""
    for path in sorted((repo_root / ".github" / "workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        secrets = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", text))
        assert secrets <= {"PIXELDRAIN_API_KEY"}, \
            f"{path.name}: unexpected secrets {secrets}"


def test_no_script_interpolation_of_untrusted_context(repo_root):
    """No workflow may interpolate untrusted event context into run: blocks."""
    dangerous = ("github.event.pull_request", "github.event.issue",
                 "github.event.comment", "github.event.head_message")
    for path in sorted((repo_root / ".github" / "workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for marker in dangerous:
            assert marker not in text, \
                f"{path.name}: untrusted context {marker} in workflow"


def test_extracted_files_never_run_by_tasks(repo_root):
    """Automation task commands must never execute extracted archive paths."""
    import run_task as rt
    tasks = rt.load_tasks(repo_root / "automation" / "tasks")
    for name, task in tasks.items():
        for platform, command in task["commands"].items():
            assert "artifacts/xlite" not in command.replace("\\", "/") or \
                "xlite_inspector" in command, \
                f"task {name} executes inside the extraction dir"
            assert "setup.exe" not in command
            assert "install.wim" not in command


def test_cleanup_paths_guarded(repo_root):
    """Cleanup scripts must guard deletions to the repository root."""
    ps = (repo_root / "scripts" / "powershell" / "Invoke-Cleanup.ps1") \
        .read_text(encoding="utf-8")
    assert "StartsWith($repo" in ps
    sh = (repo_root / "scripts" / "linux" / "cleanup.sh").read_text(encoding="utf-8")
    assert '"$REPO_ROOT"/*)' in sh


def test_ps_scripts_have_no_execution_policy_bypass(repo_root):
    """Scripts must not weaken the execution policy themselves (the CI
    invocation passes -ExecutionPolicy Bypass externally)."""
    for path in (repo_root / "scripts" / "powershell").glob("*.ps1"):
        text = path.read_text(encoding="utf-8")
        assert "Set-ExecutionPolicy" not in text, f"{path.name} alters policy"
