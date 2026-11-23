#!/usr/bin/env python3
# ABOUTME: TDD tests for _summary_lookup.py — multi-pattern summary filename resolver (#1878)
# ABOUTME: Four filename conventions coexist on disk; lookup must try each in order.

"""Tests for scripts/data/document-index/_summary_lookup.py."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)


@pytest.fixture
def summaries_dir(tmp_path: Path) -> Path:
    d = tmp_path / "summaries"
    d.mkdir()
    return d


def _write_summary(dir_: Path, name: str, summary_text: str | None = "x") -> Path:
    import json

    p = dir_ / name
    p.write_text(json.dumps({"summary": summary_text, "title": "t", "discipline": "d"}))
    return p


# ─────────────────────────── Test 5 ───────────────────────────
def test_lookup_prefers_full_prefixed_hash(summaries_dir: Path):
    """content_hash='sha256:<64hex>' should match '<sha256:64hex>.json' file first."""
    from _summary_lookup import find_summary

    hex64 = "a" * 64
    full = f"sha256:{hex64}"
    _write_summary(summaries_dir, f"{full}.json")

    record = {"path": "/irrelevant/path.pdf", "content_hash": full}
    p = find_summary(record, summaries_dir)
    assert p is not None
    assert p.name == f"{full}.json"


# ─────────────────────────── Test 6 ───────────────────────────
def test_lookup_falls_back_to_bare_sha256(summaries_dir: Path):
    """If the prefixed file does not exist, strip 'sha256:' and try bare hex."""
    from _summary_lookup import find_summary

    hex64 = "b" * 64
    _write_summary(summaries_dir, f"{hex64}.json")  # only the bare form exists

    record = {"path": "/irrelevant/path.pdf", "content_hash": f"sha256:{hex64}"}
    p = find_summary(record, summaries_dir)
    assert p is not None
    assert p.name == f"{hex64}.json"


# ─────────────────────────── Test 7 ───────────────────────────
def test_lookup_md5_prefix_and_bare_both_tried(summaries_dir: Path):
    """Legacy og_standards: try 'md5:<32hex>.json' first, then bare '<32hex>.json'."""
    from _summary_lookup import find_summary

    hex32 = "c" * 32
    _write_summary(summaries_dir, f"{hex32}.json")  # bare md5 exists only

    record = {"path": "/irrelevant/path.xls", "content_hash": f"md5:{hex32}"}
    p = find_summary(record, summaries_dir)
    assert p is not None
    assert p.name == f"{hex32}.json"


# ─────────────────────────── Test 8 ───────────────────────────
def test_lookup_falls_back_to_path_sha256_16(summaries_dir: Path):
    """No content_hash → use sha256(path.encode())[:16] as filename stem."""
    from _summary_lookup import find_summary

    path = "/mnt/ace/some/document.pdf"
    path_key = hashlib.sha256(path.encode()).hexdigest()[:16]
    _write_summary(summaries_dir, f"{path_key}.json")

    record = {"path": path, "content_hash": None}
    p = find_summary(record, summaries_dir)
    assert p is not None
    assert p.name == f"{path_key}.json"


# ─────────────────────────── Test 9 ───────────────────────────
def test_lookup_returns_none_when_no_file_matches(summaries_dir: Path):
    """All candidate filenames missing → return None (not raise)."""
    from _summary_lookup import find_summary

    record = {"path": "/nowhere/to/be/found.pdf", "content_hash": "sha256:" + "0" * 64}
    assert find_summary(record, summaries_dir) is None


# ───────────────────── Bonus: ordered candidate list is observable ─────────
def test_candidate_filenames_ordering_for_prefixed_hash():
    """candidate_filenames() yields: prefixed → bare → path-fallback (per pseudocode)."""
    from _summary_lookup import candidate_filenames

    hex64 = "d" * 64
    record = {"path": "/x/y.pdf", "content_hash": f"sha256:{hex64}"}
    cands = candidate_filenames(record)
    # prefixed first, bare second, path-fallback last
    assert cands[0] == f"sha256:{hex64}.json"
    assert cands[1] == f"{hex64}.json"
    path_key = hashlib.sha256("/x/y.pdf".encode()).hexdigest()[:16]
    assert cands[-1] == f"{path_key}.json"


def test_candidate_filenames_no_content_hash_only_path_fallback():
    """No content_hash → single candidate, the path-derived 16-hex."""
    from _summary_lookup import candidate_filenames

    record = {"path": "/only/path.pdf", "content_hash": None}
    cands = candidate_filenames(record)
    path_key = hashlib.sha256("/only/path.pdf".encode()).hexdigest()[:16]
    assert cands == [f"{path_key}.json"]


def test_candidate_filenames_empty_string_content_hash_treated_as_missing():
    """Phase-A sometimes writes '' rather than None for no-hash records."""
    from _summary_lookup import candidate_filenames

    record = {"path": "/empty/hash.pdf", "content_hash": ""}
    cands = candidate_filenames(record)
    path_key = hashlib.sha256("/empty/hash.pdf".encode()).hexdigest()[:16]
    assert cands == [f"{path_key}.json"]
