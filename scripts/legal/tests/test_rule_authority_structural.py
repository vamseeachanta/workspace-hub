"""Structural-secret and private-filesystem contract tests."""

from __future__ import annotations

import base64
import importlib
import os
import sys
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, KEY_B64

LEGAL = Path(__file__).resolve().parents[1]
ROOT = LEGAL.parents[1]
PACKAGE = LEGAL / "rule_authority"


def load_module(name: str):
    path = PACKAGE / f"{name}.py"
    assert path.is_file(), f"missing Phase A module: {path.relative_to(ROOT)}"
    sys.path.insert(0, str(LEGAL))
    return importlib.import_module(f"rule_authority.{name}")


@pytest.mark.parametrize(
    "payload",
    [
        b"legal-rule-map-v1",
        b"legal-rule-authority-manifest-v1",
        b"legal-rule-active-anchor-v1",
        b"legal-rule-generation-ledger-v1",
        b"legal-rule-complete-v1",
        b"PACK\x00\x00\x00\x02",
        KEY,
        KEY_B64.encode("ascii"),
        base64.b64encode(b"synthetic-block-token"),
    ],
)
def test_structural_secret_artifacts_reject_under_arbitrary_names(payload):
    structural = load_module("structural")
    sensitive = structural.SensitiveArtifacts(
        key=KEY,
        decoded_patterns=(b"synthetic-block-token",),
        exact_artifacts=(),
        prohibited_basenames=frozenset(),
    )
    findings = structural.scan_blobs({"arbitrary/name.bin": b"prefix" + payload + b"suffix"}, sensitive)
    assert findings == ["arbitrary/name.bin"]


def test_public_markers_are_allowlisted_only_at_canonical_paths():
    structural = load_module("structural")
    sensitive = structural.SensitiveArtifacts(KEY, (), (), frozenset())
    marker = b"legal-rule-registry-v1"
    assert structural.scan_blobs({"config/legal-rule-registry.json": marker}, sensitive) == []
    assert structural.scan_blobs({"notes/registry-copy.json": marker}, sensitive) == ["notes/registry-copy.json"]


def test_key_file_requires_0600_under_current_uid_0700_parent(tmp_path):
    private_fs = load_module("private_fs")
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    key_file = parent / "key.b64"
    key_file.write_text(KEY_B64 + "\n", encoding="ascii")
    key_file.chmod(0o600)
    assert private_fs.load_key(key_file=key_file, env_name=None, environ={}) == KEY
    key_file.chmod(0o640)
    with pytest.raises(private_fs.PrivateFilesystemError):
        private_fs.load_key(key_file=key_file, env_name=None, environ={})


def test_key_source_is_exactly_one_and_environment_is_canonical(tmp_path):
    private_fs = load_module("private_fs")
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    key_file = parent / "key.b64"
    key_file.write_text(KEY_B64 + "\n", encoding="ascii")
    key_file.chmod(0o600)
    with pytest.raises(private_fs.PrivateFilesystemError):
        private_fs.load_key(key_file=key_file, env_name="AUTH", environ={"AUTH": KEY_B64})
    with pytest.raises(private_fs.PrivateFilesystemError):
        private_fs.load_key(key_file=None, env_name="AUTH", environ={"AUTH": KEY_B64 + "\n"})
    assert private_fs.load_key(key_file=None, env_name="AUTH", environ={"AUTH": KEY_B64}) == KEY


def test_parent_symlink_and_wrong_owner_reject(tmp_path, monkeypatch):
    private_fs = load_module("private_fs")
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    key_file = parent / "key.b64"
    key_file.write_text(KEY_B64 + "\n", encoding="ascii")
    key_file.chmod(0o600)
    link = tmp_path / "linked"
    link.symlink_to(parent, target_is_directory=True)
    with pytest.raises(private_fs.PrivateFilesystemError):
        private_fs.load_key(key_file=link / "key.b64", env_name=None, environ={})
    monkeypatch.setattr(os, "getuid", lambda: os.stat(key_file).st_uid + 1)
    with pytest.raises(private_fs.PrivateFilesystemError):
        private_fs.load_key(key_file=key_file, env_name=None, environ={})
