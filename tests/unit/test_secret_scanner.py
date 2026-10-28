"""Unit tests for secret_scanner.

Real-looking secrets in these tests are synthetic (constructed) and written
only to tmp_path (outside the repository) so the repo-wide scan stays clean.
"""
import secret_scanner as ss


def test_github_classic_token_detected(tmp_path):
    target = tmp_path / "leak.txt"
    # constructed so this test source does not itself contain a live pattern
    token = ("gh" + "p_") + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    target.write_text(f"token = {token}\n", encoding="utf-8")
    findings = ss.scan_file(target)
    assert any(f["rule"] == "github-classic-token" for f in findings)
    assert all(f["severity"] == "error" for f in findings if f["rule"] == "github-classic-token")
    # the reported match is redacted
    reported = [f["match"] for f in findings if f["rule"] == "github-classic-token"][0]
    assert token not in reported


def test_private_key_block_detected(tmp_path):
    target = tmp_path / "key.txt"
    target.write_text("-----BEGIN " + "RSA PRIVATE KEY-----\nabc\n", encoding="utf-8")
    findings = ss.scan_file(target)
    assert any(f["rule"] == "private-key-block" for f in findings)


def test_aws_key_detected(tmp_path):
    target = tmp_path / "aws.txt"
    # constructed so this test source does not itself contain a live pattern
    key = ("AK" + "IA") + "IOSFODNN7EXAMPLE"
    target.write_text(f"aws_access_key_id = {key}\n", encoding="utf-8")
    findings = ss.scan_file(target)
    assert any(f["rule"] == "aws-access-key" for f in findings)


def test_hardcoded_password_warns(tmp_path):
    target = tmp_path / "cfg.txt"
    target.write_text('password = "SuperSecret123!"\n', encoding="utf-8")
    findings = ss.scan_file(target)
    assert any(f["rule"] == "hardcoded-credential" and f["severity"] == "warn"
               for f in findings)
    assert all(f["severity"] != "error" for f in findings)


def test_benign_file_clean(tmp_path):
    target = tmp_path / "clean.txt"
    target.write_text("The password policy is documented in SECURITY.md.\n", encoding="utf-8")
    assert ss.scan_file(target) == []


def test_scan_repo_excludes_scanner_itself(tmp_path):
    # a copy of the scanner file (contains rule patterns by construction) must
    # be excluded from scanning entirely
    scanner_src = __import__("pathlib").Path(ss.__file__).read_text(encoding="utf-8")
    (tmp_path / "secret_scanner.py").write_text(scanner_src, encoding="utf-8")
    result = ss.scan_repo(tmp_path)
    assert result["files_scanned"] == 0
    assert result["findings"] == []


def test_scan_repo_excludes_git_and_caches(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("gh" + "p_" + "Z9y8X7w6V5u4T3s2R1q0P9o8N7m6L5k4",
                                    encoding="utf-8")
    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "mod.cpython-312.pyc").write_text("binary", encoding="utf-8")
    result = ss.scan_repo(tmp_path)
    assert result["files_scanned"] == 0
    assert result["errors"] == 0
