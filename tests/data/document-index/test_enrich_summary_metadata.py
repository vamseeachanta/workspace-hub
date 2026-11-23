#!/usr/bin/env python3
# ABOUTME: TDD tests for enrich-summary-metadata.py — content_type mapping,
# ABOUTME: summary_done derivation, corrupt-input robustness (#1878).

"""Tests for scripts/data/document-index/enrich-summary-metadata.py."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)


def _load_enrich():
    return importlib.import_module("enrich-summary-metadata")


@pytest.fixture
def summaries_dir(tmp_path: Path) -> Path:
    d = tmp_path / "summaries"
    d.mkdir()
    return d


# ─────────────────────────── Tests 1–4: content_type ───────────────────────────
def test_content_type_pdf_maps_to_document():
    mod = _load_enrich()
    assert mod.content_type_for_ext("pdf") == "document"


def test_content_type_dwg_maps_to_cad():
    mod = _load_enrich()
    assert mod.content_type_for_ext("dwg") == "cad"


def test_content_type_unknown_ext_maps_to_other():
    mod = _load_enrich()
    assert mod.content_type_for_ext("xyz") == "other"
    # Must always return a string, never None
    assert mod.content_type_for_ext("xyz") is not None


def test_content_type_case_insensitive():
    mod = _load_enrich()
    assert mod.content_type_for_ext("PDF") == "document"
    assert mod.content_type_for_ext(".PDF") == "document"  # tolerates leading dot
    assert mod.content_type_for_ext(".pdf") == "document"


# ─────────────────────────── Tests 10–15: summary_done ───────────────────────────
def _write(dir_: Path, name: str, obj: dict) -> Path:
    p = dir_ / name
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_summary_done_true_when_summary_nonempty(summaries_dir: Path):
    mod = _load_enrich()
    p = _write(summaries_dir, "k.json", {"summary": "This is a real summary."})
    assert mod.summary_done_from_file(p) is True


def test_summary_done_false_when_summary_empty_string(summaries_dir: Path):
    mod = _load_enrich()
    p = _write(summaries_dir, "k.json", {"summary": "   "})
    assert mod.summary_done_from_file(p) is False


def test_summary_done_false_when_summary_key_absent(summaries_dir: Path):
    mod = _load_enrich()
    p = _write(summaries_dir, "k.json", {"title": "t", "word_count": 0})
    assert mod.summary_done_from_file(p) is False


def test_summary_done_false_on_corrupt_json(summaries_dir: Path):
    mod = _load_enrich()
    p = summaries_dir / "bad.json"
    p.write_text("{not valid json", encoding="utf-8")
    assert mod.summary_done_from_file(p) is False


def test_summary_done_false_on_unicode_decode_error(summaries_dir: Path):
    mod = _load_enrich()
    p = summaries_dir / "bin.json"
    p.write_bytes(b"\xff\xfe\x00\x01 not utf-8")
    assert mod.summary_done_from_file(p) is False


def test_summary_done_false_when_file_missing(tmp_path: Path):
    mod = _load_enrich()
    missing = tmp_path / "does-not-exist.json"
    assert mod.summary_done_from_file(missing) is False


def test_summary_done_false_when_summary_is_null(summaries_dir: Path):
    """Real production summaries often have `"summary": null` (e.g. CAD skipped)."""
    mod = _load_enrich()
    p = _write(summaries_dir, "k.json", {"summary": None})
    assert mod.summary_done_from_file(p) is False


# ─────────────────────────── enrich_one() composition ──────────────────────────
def test_enrich_one_adds_both_fields_with_summary_present(summaries_dir: Path):
    mod = _load_enrich()
    _write(summaries_dir, f"{'0' * 16}.json", {"summary": "hello"})

    import hashlib

    path = "/some/doc.pdf"
    # Force path_key to match our fixture filename
    expected_key = hashlib.sha256(path.encode()).hexdigest()[:16]
    # Rename fixture file to expected_key
    (summaries_dir / f"{'0' * 16}.json").rename(summaries_dir / f"{expected_key}.json")

    record = {"path": path, "ext": "pdf", "content_hash": None}
    out = mod.enrich_one(record, summaries_dir)
    assert out["content_type"] == "document"
    assert out["summary_done"] is True
    assert out["path"] == path  # original fields preserved


def test_enrich_one_summary_done_false_when_no_file(summaries_dir: Path):
    mod = _load_enrich()
    record = {"path": "/x/y.pdf", "ext": "pdf", "content_hash": None}
    out = mod.enrich_one(record, summaries_dir)
    assert out["content_type"] == "document"
    assert out["summary_done"] is False


def test_enrich_one_preserves_all_prior_fields(summaries_dir: Path):
    mod = _load_enrich()
    record = {
        "path": "/x/y.pdf",
        "ext": "pdf",
        "content_hash": None,
        "domain": "marine",
        "org": "DNV",
        "status": "gap",
        "readability": "machine",
    }
    out = mod.enrich_one(record, summaries_dir)
    # Nothing lost
    for k in ("domain", "org", "status", "readability"):
        assert out[k] == record[k]


# ═══════════════════ #2309 field split: summary_file_exists ═══════════════════
# The single summary_done field in #1878 conflated file-existence with content-quality.
# #2309 splits the signal: summary_file_exists is True iff find_summary returns non-None.

def test_summary_file_exists_true_when_file_present(summaries_dir):
    """Non-empty summary file present → summary_file_exists=True AND summary_done=True."""
    mod = _load_enrich()
    import hashlib

    path = "/p.pdf"
    key = hashlib.sha256(path.encode()).hexdigest()[:16]
    _write(summaries_dir, f"{key}.json", {"summary": "real text"})
    out = mod.enrich_one({"path": path, "ext": "pdf", "content_hash": None}, summaries_dir)
    assert out["summary_file_exists"] is True
    assert out["summary_done"] is True


def test_summary_file_exists_true_when_file_empty_content(summaries_dir):
    """File present with empty summary → summary_file_exists=True, summary_done=False. DIVERGENCE."""
    mod = _load_enrich()
    import hashlib

    path = "/empty.pdf"
    key = hashlib.sha256(path.encode()).hexdigest()[:16]
    _write(summaries_dir, f"{key}.json", {"summary": ""})
    out = mod.enrich_one({"path": path, "ext": "pdf", "content_hash": None}, summaries_dir)
    assert out["summary_file_exists"] is True
    assert out["summary_done"] is False


def test_summary_file_exists_true_when_file_has_no_summary_key(summaries_dir):
    """File present with no `summary` key → summary_file_exists=True, summary_done=False. DIVERGENCE."""
    mod = _load_enrich()
    import hashlib

    path = "/nokey.pdf"
    key = hashlib.sha256(path.encode()).hexdigest()[:16]
    _write(summaries_dir, f"{key}.json", {"title": "t", "word_count": 0})
    out = mod.enrich_one({"path": path, "ext": "pdf", "content_hash": None}, summaries_dir)
    assert out["summary_file_exists"] is True
    assert out["summary_done"] is False


def test_summary_file_exists_false_when_file_missing(summaries_dir):
    """No file on disk → both fields False."""
    mod = _load_enrich()
    out = mod.enrich_one({"path": "/missing.pdf", "ext": "pdf", "content_hash": None}, summaries_dir)
    assert out["summary_file_exists"] is False
    assert out["summary_done"] is False


def test_enrich_one_populates_both_summary_fields(summaries_dir):
    """Every enriched record gets both keys present (never missing)."""
    mod = _load_enrich()
    out = mod.enrich_one({"path": "/x.pdf", "ext": "pdf", "content_hash": None}, summaries_dir)
    assert "summary_file_exists" in out
    assert "summary_done" in out


def test_summary_file_exists_true_summary_done_false_on_corrupt_json(summaries_dir):
    """File present but malformed JSON → summary_file_exists=True, summary_done=False. DIVERGENCE (Claude F2)."""
    mod = _load_enrich()
    import hashlib

    path = "/corrupt.pdf"
    key = hashlib.sha256(path.encode()).hexdigest()[:16]
    (summaries_dir / f"{key}.json").write_text("{not valid json", encoding="utf-8")
    out = mod.enrich_one({"path": path, "ext": "pdf", "content_hash": None}, summaries_dir)
    assert out["summary_file_exists"] is True
    assert out["summary_done"] is False


def test_summary_file_exists_true_summary_done_false_on_unicode_decode(summaries_dir):
    """File present but non-UTF-8 bytes → summary_file_exists=True, summary_done=False. DIVERGENCE (Claude F2)."""
    mod = _load_enrich()
    import hashlib

    path = "/unicode.pdf"
    key = hashlib.sha256(path.encode()).hexdigest()[:16]
    (summaries_dir / f"{key}.json").write_bytes(b"\xff\xfe\x00\x01 not utf-8")
    out = mod.enrich_one({"path": path, "ext": "pdf", "content_hash": None}, summaries_dir)
    assert out["summary_file_exists"] is True
    assert out["summary_done"] is False
