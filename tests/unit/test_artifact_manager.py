"""Unit tests for artifact_manager."""
import hashlib
import json

import artifact_manager as am


def make_tree(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "sub" / "b.txt").write_text("beta" * 1000, encoding="utf-8")
    hidden = tmp_path / ".git"
    hidden.mkdir()
    (hidden / "index").write_text("git internals", encoding="utf-8")


def test_build_manifest(tmp_path):
    make_tree(tmp_path)
    manifest = am.build_manifest(tmp_path)
    assert manifest["file_count"] == 2  # .git excluded
    paths = [f["path"] for f in manifest["files"]]
    assert "a.txt" in paths and "sub/b.txt" in paths
    expected = hashlib.sha256(b"beta" * 1000).hexdigest()
    by_path = {f["path"]: f for f in manifest["files"]}
    assert by_path["sub/b.txt"]["sha256"] == expected
    assert by_path["sub/b.txt"]["size"] == 4000


def test_verify_manifest_ok(tmp_path):
    make_tree(tmp_path)
    manifest = am.build_manifest(tmp_path)
    result = am.verify_manifest(tmp_path, manifest)
    assert result["ok"] is True
    assert result["verified"] == 2


def test_verify_detects_tamper(tmp_path):
    make_tree(tmp_path)
    manifest = am.build_manifest(tmp_path)
    (tmp_path / "a.txt").write_text("tampered", encoding="utf-8")
    result = am.verify_manifest(tmp_path, manifest)
    assert result["ok"] is False
    assert len(result["mismatches"]) == 1
    assert result["mismatches"][0]["path"] == "a.txt"


def test_verify_detects_missing_and_extra(tmp_path):
    make_tree(tmp_path)
    manifest = am.build_manifest(tmp_path)
    (tmp_path / "a.txt").unlink()
    (tmp_path / "new.txt").write_text("new", encoding="utf-8")
    result = am.verify_manifest(tmp_path, manifest)
    assert result["ok"] is False
    assert result["missing"] == ["a.txt"]
    assert result["extra"] == ["new.txt"]


def test_manifest_json_roundtrip(tmp_path):
    """Manifest must live OUTSIDE the scanned tree, else it becomes an
    unexpected 'extra' file during verification."""
    tree = tmp_path / "tree"
    tree.mkdir()
    make_tree(tree)
    out = tmp_path / "manifest.json"
    manifest = am.build_manifest(tree)
    out.write_text(json.dumps(manifest), encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert am.verify_manifest(tree, loaded)["ok"] is True
