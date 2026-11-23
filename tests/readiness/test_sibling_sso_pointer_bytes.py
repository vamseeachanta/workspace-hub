"""Byte-level regressions for the bounded contract-pointer repair."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def load_repair():
    path = Path(__file__).resolve().parents[2] / "scripts/readiness/repair-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("pointer_bytes_repair", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("ending", [b"\n", b"\r\n", b"\r"])
@pytest.mark.parametrize("prefix", [b"", b"\xef\xbb\xbf"])
@pytest.mark.parametrize("final_ending", [b"", b"\r\n"])
def test_pointer_repair_preserves_file_bytes(tmp_path, ending, prefix, final_ending):
    """Hand calculation: substitute the pointer on the Contract line only.

    All other literal byte segments, including a BOM and the final ending,
    concatenate unchanged. Python 3.11 open() documents newline translation:
    https://docs.python.org/3.11/library/functions.html#open
    """
    repair = load_repair()
    path = tmp_path / "contract.md"
    before = prefix + ending.join([
        b"# Notes",
        b"Contract: ../AGENTS.md | Source: src/",
        b"Notes: literal ../AGENTS.md stays here.",
    ]) + final_ending
    expected = prefix + ending.join([
        b"# Notes",
        b"Contract: ../workspace-hub/AGENTS.md | Source: src/",
        b"Notes: literal ../AGENTS.md stays here.",
    ]) + final_ending
    path.write_bytes(before)

    repair.rewrite_agents_pointer(path, "../AGENTS.md", "../workspace-hub/AGENTS.md")

    assert path.read_bytes() == expected
    repair.rewrite_agents_pointer(path, "../AGENTS.md", "../workspace-hub/AGENTS.md")
    assert path.read_bytes() == expected


def test_pointer_repair_preserves_mixed_endings_and_undecodable_bytes(tmp_path):
    """Hand calculation: change only the three marked pointer occurrences.

    The explicit expected literal retains CRLF, LF, CR, valid UTF-8, invalid
    UTF-8 and an unterminated final line. Python 3.11 open() documents that
    surrogateescape round trips undecodable bytes with the same handler:
    https://docs.python.org/3.11/library/functions.html#open
    """
    repair = load_repair()
    path = tmp_path / "contract.md"
    path.write_bytes(
        b"# Caf\xc3\xa9 \xff\r\n"
        b"Contract: ../AGENTS.md | note: \xfe\n"
        b"Legacy contract: ../AGENTS.md\r"
        b"This repository inherits the canonical contract from:\r\n"
        b"../AGENTS.md\n"
        b"Notes: ../AGENTS.md \x80"
    )
    expected = (
        b"# Caf\xc3\xa9 \xff\r\n"
        b"Contract: ../workspace-hub/AGENTS.md | note: \xfe\n"
        b"Legacy contract: ../workspace-hub/AGENTS.md\r"
        b"This repository inherits the canonical contract from:\r\n"
        b"../workspace-hub/AGENTS.md\n"
        b"Notes: ../AGENTS.md \x80"
    )

    repair.rewrite_agents_pointer(path, "../AGENTS.md", "../workspace-hub/AGENTS.md")

    assert path.read_bytes() == expected


def test_pointer_repair_without_matching_lines_is_byte_identical(tmp_path):
    """Hand calculation: no eligible line means the expected bytes equal input.

    Python 3.11 open(), errors and newline, defines the lossy text defaults:
    https://docs.python.org/3.11/library/functions.html#open
    """
    repair = load_repair()
    path = tmp_path / "contract.md"
    original = b"# Notes\r\nNotes: ../AGENTS.md \xff\r\nTail\r"
    path.write_bytes(original)

    repair.rewrite_agents_pointer(path, "../AGENTS.md", "../workspace-hub/AGENTS.md")

    assert path.read_bytes() == original
