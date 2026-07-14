"""Retained-dirfd and key-source adversarial tests."""

from __future__ import annotations

import base64
import importlib
import os
import socket
import sys
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, KEY_B64

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))


def private_fs():
    return importlib.import_module("rule_authority.private_fs")


def write_key(parent: Path, payload: str = KEY_B64 + "\n") -> Path:
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = parent / "key.b64"
    path.write_text(payload, encoding="ascii")
    path.chmod(0o600)
    return path


def test_key_selectors_are_mutually_exclusive_even_if_env_absent(tmp_path):
    fs = private_fs()
    key_file = write_key(tmp_path / "private")
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=key_file, env_name="ABSENT", environ={})


def test_symlinked_ancestor_rejects(tmp_path):
    fs = private_fs()
    target = tmp_path / "target"
    key_file = write_key(target / "nested")
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=link / "nested" / key_file.name, env_name=None, environ={})


def test_parent_mode_and_key_symlink_reject(tmp_path):
    fs = private_fs()
    parent = tmp_path / "private"
    key_file = write_key(parent)
    parent.chmod(0o750)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=key_file, env_name=None, environ={})
    parent.chmod(0o700)
    link = parent / "link.b64"
    link.symlink_to(key_file)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=link, env_name=None, environ={})


def test_non_regular_and_oversized_key_reject(tmp_path):
    fs = private_fs()
    parent = tmp_path / "private"
    key_file = write_key(parent, "A" * 1025)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=key_file, env_name=None, environ={})
    socket_path = parent / "key.sock"
    sock = socket.socket(socket.AF_UNIX)
    try:
        sock.bind(str(socket_path))
        socket_path.chmod(0o600)
        with pytest.raises(fs.PrivateFilesystemError):
            fs.load_key(key_file=socket_path, env_name=None, environ={})
    finally:
        sock.close()


def test_wrong_owner_and_noncanonical_key_encodings_reject(tmp_path, monkeypatch):
    fs = private_fs()
    key_file = write_key(tmp_path / "private")
    real_uid = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: real_uid + 1)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=key_file, env_name=None, environ={})
    monkeypatch.setattr(os, "getuid", lambda: real_uid)
    bad = (
        base64.b64encode(KEY[:-1]).decode(),
        KEY_B64 + "=",
        KEY_B64 + "\r",
        KEY_B64 + "\n",
    )
    for value in bad:
        with pytest.raises(fs.PrivateFilesystemError):
            fs.load_key(key_file=None, env_name="AUTH", environ={"AUTH": value})


def test_errors_withhold_key_and_locator(tmp_path):
    fs = private_fs()
    key_file = tmp_path / "private" / "sensitive-locator-name"
    try:
        fs.load_key(key_file=key_file, env_name=None, environ={})
    except fs.PrivateFilesystemError as error:
        message = str(error)
        assert "sensitive-locator-name" not in message
        assert KEY_B64 not in message
    else:
        pytest.fail("missing key unexpectedly loaded")


def test_parent_namespace_swap_rejects(tmp_path, monkeypatch):
    fs = private_fs()
    parent = tmp_path / "private"
    key_file = write_key(parent)
    original_read = fs._read_key_at

    def swapping_read(parent_fd, name):
        raw = original_read(parent_fd, name)
        parent.rename(tmp_path / "moved")
        replacement = tmp_path / "private"
        write_key(replacement)
        return raw

    monkeypatch.setattr(fs, "_read_key_at", swapping_read)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=key_file, env_name=None, environ={})


def test_ancestor_reparent_with_same_final_parent_inode_rejects(tmp_path, monkeypatch):
    fs = private_fs()
    ancestor = tmp_path / "private"
    final_parent = ancestor / "nested"
    key_file = write_key(final_parent)
    ancestor.chmod(0o700)
    original_read = fs._read_key_at
    reparented = []

    def reparenting_read(parent_fd, name):
        raw = original_read(parent_fd, name)
        moved = tmp_path / "moved"
        ancestor.rename(moved)
        ancestor.mkdir(mode=0o700)
        (moved / "nested").rename(ancestor / "nested")
        reparented.append(True)
        return raw

    monkeypatch.setattr(fs, "_read_key_at", reparenting_read)
    with pytest.raises(fs.PrivateFilesystemError):
        fs.load_key(key_file=key_file, env_name=None, environ={})
    assert reparented == [True]
