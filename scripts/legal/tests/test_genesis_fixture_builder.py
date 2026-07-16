"""RED fixture-builder contract reusing the canonical approval factory."""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from test_rule_authority_genesis_approval import canonical_record, canonical_bytes
from genesis_fixture import build_genesis_fixture  # noqa: F401

def test_build_genesis_fixture_emits_matching_identities(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    record = canonical_record()
    approval = Path("approval.json"); approval.write_bytes(canonical_bytes(record)); approval.chmod(0o600)
    contract = Path("contract.md"); contract.write_text("contract\n"); contract.chmod(0o400)
    manifest = Path("manifest.json"); manifest.write_text("{}\n"); manifest.chmod(0o400)
    verifier = Path("verifier.py"); verifier.write_text("# verifier\n"); verifier.chmod(0o400)
    entry = Path("entry.py"); entry.write_text("# entry\n"); entry.chmod(0o400)
    result = build_genesis_fixture(approval, contract, manifest, verifier, entry)
    assert result["approval_sha256"] == hashlib.sha256(approval.read_bytes()).hexdigest()
    assert result["manifest"]["schema_id"] == "legal-rule-genesis-execution-manifest-v1"
    assert json.loads(approval.read_text()) == record
