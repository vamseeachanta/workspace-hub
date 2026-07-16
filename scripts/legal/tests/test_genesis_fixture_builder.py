"""RED fixture-builder contract reusing the canonical approval factory."""
import hashlib, json, sys
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from test_rule_authority_genesis_approval import canonical_record, canonical_bytes
from genesis_fixture import build_genesis_fixture  # noqa: F401

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
