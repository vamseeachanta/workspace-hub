"""Hash regressions for byte capture feeding the existing pointer repair.

Git show DESCRIPTION specifies plain blob contents:
https://git-scm.com/docs/git-show
Python 3.11 subprocess, Frequently Used Arguments, specifies newline conversion:
https://docs.python.org/3.11/library/subprocess.html#frequently-used-arguments
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OLD = b'../AGENTS.md'
NEW = b'../workspace-hub/AGENTS.md'
# Hand calculation: only the pointer token on the middle line changes. CR/LF,
# BOM EF BB BF (UTF-8 signature), and absent terminators are literal fixture data.
# Signature source: Python 3.11 codecs, UTF-8 signature encoding:
# https://docs.python.org/3.11/library/codecs.html#module-encodings.utf_8_sig
CASES = [
    b'# Notes\r\nContract: ../AGENTS.md\r\nTail\r\n',
    b'# Notes\r\nContract: ../AGENTS.md\nTail\r',
    b'# Notes\r\nContract: ../AGENTS.md\r\nTail',
    b'\xef\xbb\xbf# Notes\r\nContract: ../AGENTS.md\r\nTail\r\n',
]


def load_repair():
    spec = importlib.util.spec_from_file_location(
        'byte_capture_pointer', ROOT / 'scripts/readiness/repair-sibling-sso-flow.py',
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def blob_repo(tmp_path):
    """Disposable Git objects require no index, commit or configured identity."""
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    repo = tmp_path / 'objects.git'
    subprocess.run(['git', 'init', '--bare', '--quiet', str(repo)], env=env, check=True)
    return repo, env


@pytest.mark.parametrize('before', CASES, ids=['crlf', 'mixed', 'unterminated', 'bom'])
def test_blob_capture_and_pointer_repair_preserve_unrelated_hashes(blob_repo, tmp_path, before):
    """Independent expected output: concatenate prefix + new token + suffix.

    SHA-256(before excluding old token) must equal SHA-256(after excluding new
    token). Neither expected bytes nor expected hashes use repair code.
    """
    repo, env = blob_repo
    oid = subprocess.run(
        ['git', '-C', str(repo), 'hash-object', '-w', '--stdin'],
        input=before, capture_output=True, env=env, check=True,
    ).stdout.decode('ascii').strip()
    command = ['git', '-C', str(repo), 'show', oid]
    captured = subprocess.run(command, capture_output=True, env=env, check=True).stdout
    assert hashlib.sha256(captured).digest() == hashlib.sha256(before).digest()
    prefix, suffix = before.split(OLD)
    expected = prefix + NEW + suffix
    path = tmp_path / 'contract.md'
    path.write_bytes(captured)
    load_repair().rewrite_agents_pointer(path, OLD.decode('ascii'), NEW.decode('ascii'))
    actual = path.read_bytes()
    assert actual == expected
    assert hashlib.sha256(actual.replace(NEW, b'')).digest() == hashlib.sha256(prefix + suffix).digest()
    # Negative control: Python text capture loses CR in each literal fixture.
    wrong = subprocess.run(command, capture_output=True, env=env, check=True, text=True).stdout.encode('utf-8')
    assert wrong == before.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    assert hashlib.sha256(wrong).digest() != hashlib.sha256(before).digest()


def test_documented_three_line_example(blob_repo):
    """Hand calculation: 41=A, 6f6c64=old, 6e6577=new, 5a=Z, 0d0a=CRLF.

    The wrong path drops the CR of every terminator as specified by Python
    subprocess docs. Each expected hex string is written out in scripts/README.md.
    """
    before = b'A\r\nold\r\nZ\r\n'
    repo, env = blob_repo
    oid = subprocess.run(
        ['git', '-C', str(repo), 'hash-object', '-w', '--stdin'], input=before,
        capture_output=True, env=env, check=True,
    ).stdout.decode('ascii').strip()
    command = ['git', '-C', str(repo), 'show', oid]
    raw = subprocess.run(command, capture_output=True, env=env, check=True).stdout
    wrong = subprocess.run(command, capture_output=True, env=env, check=True, text=True).stdout
    right = raw.decode('utf-8', errors='surrogateescape').replace('old', 'new').encode('utf-8', errors='surrogateescape')
    hex_values = [
        '41 0d 0a 6f 6c 64 0d 0a 5a 0d 0a',
        '41 0a 6e 65 77 0a 5a 0a',
        '41 0d 0a 6e 65 77 0d 0a 5a 0d 0a',
    ]
    assert [raw.hex(' '), wrong.replace('old', 'new').encode('utf-8').hex(' '), right.hex(' ')] == hex_values
    guidance = (ROOT / 'scripts/README.md').read_text()
    assert all(value in guidance for value in hex_values)
