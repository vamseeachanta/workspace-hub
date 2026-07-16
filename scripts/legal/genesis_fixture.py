import hashlib, os, posixpath
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
