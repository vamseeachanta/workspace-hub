import hashlib, os, posixpath
import json
from verify_rule_authority_genesis_approval import parse_canonical_approval
from pathlib import Path

def _member(path: Path, role: str) -> dict:
    raw = path.read_bytes()
    rel = posixpath.normpath(str(path))
    if rel.startswith("/") or rel != str(path):
        raise ValueError("noncanonical path")
    return {"path": rel, "blob_oid": hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(), "sha256": hashlib.sha256(raw).hexdigest(), "role": role}

def build_fixture_manifest(verifier: Path, entry: Path, expected=None) -> dict:
    manifest = {"schema_id":"legal-rule-genesis-execution-manifest-v1", "members": sorted([_member(verifier,"verifier"), _member(entry,"internal_entry")], key=lambda m:m["path"])}
    roles = [m["role"] for m in manifest["members"]]
    if roles.count("verifier") != 1 or roles.count("internal_entry") != 1:
        raise ValueError("invalid roles")
    if expected is not None and expected != manifest:
        raise ValueError("member identity or digest changed")
    return manifest

def build_genesis_fixture(approval, contract, manifest, verifier, entry):
    raw = Path(approval).read_bytes()
    approval_doc = parse_canonical_approval(raw)
    def ident(path):
        data = Path(path).read_bytes()
        return {"path": str(path), "blob_oid": hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest(), "sha256": hashlib.sha256(data).hexdigest()}
    if approval_doc.get("contract") != ident(contract) or approval_doc.get("execution_manifest") != ident(manifest):
        raise ValueError("approval identity mismatch")
    try:
        doc = json.loads(Path(manifest).read_text())
    except Exception as exc:
        raise ValueError("invalid execution manifest") from exc
    if doc.get("schema_id") != "legal-rule-genesis-execution-manifest-v1" or not doc.get("members"):
        raise ValueError("manifest identity missing")
    built = build_fixture_manifest(Path(verifier), Path(entry))
    if doc != built:
        raise ValueError("manifest identity mismatch")
    return {"approval_sha256": hashlib.sha256(raw).hexdigest(), "manifest": built}
