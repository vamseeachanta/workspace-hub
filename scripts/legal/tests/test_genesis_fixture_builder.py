"""RED fixture-builder contract reusing the canonical approval factory."""
import hashlib, json, sys
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from test_rule_authority_genesis_approval import canonical_record, canonical_bytes
from genesis_fixture import build_genesis_fixture, build_fixture_manifest

def test_build_genesis_fixture_rejects_inconsistent_inputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    record = canonical_record()
    approval = Path("approval.json"); approval.write_bytes(canonical_bytes(record)); approval.chmod(0o600)
    contract = Path("contract.md"); contract.write_text("contract\n"); contract.chmod(0o400)
    manifest = Path("manifest.json"); manifest.write_text("{}\n"); manifest.chmod(0o400)
    verifier = Path("verifier.py"); verifier.write_text("# verifier\n"); verifier.chmod(0o400)
    entry = Path("entry.py"); entry.write_text("# entry\n"); entry.chmod(0o400)
    with pytest.raises(ValueError):
        build_genesis_fixture(approval, contract, manifest, verifier, entry)

def test_build_genesis_fixture_positive_identity_bound(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    record = canonical_record()
    contract = Path("contract.md"); contract.write_text("contract\n"); contract.chmod(0o400)
    verifier = Path("verifier.py"); verifier.write_text("# verifier\n"); verifier.chmod(0o400)
    entry = Path("entry.py"); entry.write_text("# entry\n"); entry.chmod(0o400)
    def ident(path):
        data = path.read_bytes()
        return {"path": str(path), "blob_oid": hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest(), "sha256": hashlib.sha256(data).hexdigest()}
    record["contract"] = ident(contract)
    manifest_doc = build_fixture_manifest(verifier, entry)
    manifest = Path("manifest.json"); manifest.write_text(json.dumps(manifest_doc, separators=(",", ":"))+"\n"); manifest.chmod(0o400)
    record["execution_manifest"] = ident(manifest)
    approval = Path("approval.json"); approval.write_bytes(canonical_bytes(record)); approval.chmod(0o600)
    result = build_genesis_fixture(approval, contract, manifest, verifier, entry)
    assert result["manifest"] == manifest_doc
