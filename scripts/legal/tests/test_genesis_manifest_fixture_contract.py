"""RED contract for canonical internal verifier/entry fixture handoff."""
import hashlib
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
from genesis_fixture import build_fixture_manifest  # noqa: F401


def test_fixture_manifest_binds_roles_and_digests(tmp_path):
    verifier = tmp_path / "verifier.py"
    entry = tmp_path / "entry.py"
    verifier.write_bytes(b"# verifier\n")
    entry.write_bytes(b"# entry\n")
    manifest = build_fixture_manifest(verifier, entry)
    assert manifest["schema_id"] == "legal-rule-genesis-execution-manifest-v1"
    assert {m["role"] for m in manifest["members"]} == {"verifier", "internal_entry"}
    assert manifest["members"]
    assert [m["path"] for m in manifest["members"]] == sorted(m["path"] for m in manifest["members"])
    for member in manifest["members"]:
        assert set(member) == {"path", "blob_oid", "sha256", "role"}
        assert len(member["blob_oid"]) == 40 and all(c in "0123456789abcdef" for c in member["blob_oid"])
        assert member["sha256"] == hashlib.sha256(Path(member["path"]).read_bytes()).hexdigest()


def test_fixture_manifest_rejects_path_replacement(tmp_path):
    verifier = tmp_path / "verifier.py"
    entry = tmp_path / "entry.py"
    verifier.write_bytes(b"v")
    entry.write_bytes(b"e")
    manifest = build_fixture_manifest(verifier, entry)
    verifier.write_bytes(b"replaced")
    with pytest.raises(ValueError, match="digest|identity|member"):
        build_fixture_manifest(verifier, entry, expected=manifest)
