#!/usr/bin/env python3
# ABOUTME: TDD tests 29-31 for #1878 — Phase C/E rewrites and full A→enrich→C→E
# ABOUTME: chain preserve content_type / summary_done.

"""Integration tests proving enriched-field survival through pipeline rewrites."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)


def _write_index(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _read_index(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ───────────────────── Test 29: Phase C writeback ─────────────────────
def test_phase_c_writeback_preserves_enriched_fields(tmp_path):
    """Phase C bounded writeback on allowlisted records must keep content_type + summary_done."""
    phase_c = importlib.import_module("phase-c-classify")

    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {
                "path": "/target.pdf",
                "ext": "pdf",
                "content_hash": "sha256:aaaa",
                "domain": "other",
                "status": "gap",
                "target_repos": [],
                "readability": "machine",
                "content_type": "document",  # must survive
                "summary_done": True,  # must survive
            },
            {
                "path": "/other.pdf",
                "ext": "pdf",
                "content_hash": "sha256:bbbb",
                "domain": "marine",
                "status": "done",
                "target_repos": ["x"],
                "content_type": "document",
                "summary_done": False,
            },
        ],
    )

    report = phase_c.apply_bounded_writeback(
        index_path=idx,
        target_hashes={"sha256:aaaa"},
        repo_domain_map={"marine": ["digitalmodel"]},
    )
    assert report["updated"] == 1

    out = _read_index(idx)
    by_path = {r["path"]: r for r in out}
    # Allowlisted record updated its classification but enriched fields survive
    assert by_path["/target.pdf"]["content_type"] == "document"
    assert by_path["/target.pdf"]["summary_done"] is True
    # Non-target record passed through unchanged (byte-for-byte)
    assert by_path["/other.pdf"]["content_type"] == "document"
    assert by_path["/other.pdf"]["summary_done"] is False


# ───────────────────── Test 30: Phase E backpopulate ─────────────────────
def test_phase_e_backpopulate_preserves_enriched_fields(tmp_path):
    """Phase E backpopulate_index() reads/mutates/writes each rec — enriched fields round-trip."""
    phase_e = importlib.import_module("phase-e-backpopulate")

    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {
                "path": "/a.pdf",
                "ext": "pdf",
                "domain": None,  # triggers classification
                "content_type": "document",
                "summary_done": True,
            },
            {
                "path": "/b.pdf",
                "ext": "pdf",
                "domain": "marine",  # already populated — skip
                "content_type": "document",
                "summary_done": False,
            },
        ],
    )

    # Exercise the real Phase E function with a deterministic classify_fn
    report = phase_e.backpopulate_index(
        index_path=idx,
        repo_domain_map={"other": ["testrepo"], "marine": ["digitalmodel"]},
        classify_fn=lambda _rec: ("other", "gap"),
    )
    assert report["processed"] == 2

    out = _read_index(idx)
    by_path = {r["path"]: r for r in out}
    # Enriched fields round-tripped through backpopulation
    assert by_path["/a.pdf"]["content_type"] == "document"
    assert by_path["/a.pdf"]["summary_done"] is True
    assert by_path["/a.pdf"]["domain"] == "other"  # newly classified
    assert by_path["/b.pdf"]["content_type"] == "document"
    assert by_path["/b.pdf"]["summary_done"] is False
    assert by_path["/b.pdf"]["domain"] == "marine"  # untouched


# ───────────────────── Test 31: full A → enrich → C → E chain ─────────────────────
def test_pipeline_chain_A_enrich_C_E_preserves_fields(tmp_path):
    """End-to-end: Phase A rebuild → enrichment → Phase C writeback → Phase E backpop.
    Enriched fields must survive the full chain."""
    phase_a = importlib.import_module("phase-a-index")
    phase_c = importlib.import_module("phase-c-classify")
    enrich = importlib.import_module("enrich-summary-metadata")

    idx = tmp_path / "index.jsonl"
    summaries = tmp_path / "summaries"
    summaries.mkdir()

    # Seed summary files (four-pattern coverage)
    import hashlib

    path_a = "/corpus/a.pdf"
    path_b = "/corpus/b.pdf"
    key_a = hashlib.sha256(path_a.encode()).hexdigest()[:16]
    (summaries / f"{key_a}.json").write_text(json.dumps({"summary": "real summary text"}))

    # Phase A: synthetic initial index build
    # (we skip scanning — just produce the merged_index dict directly)
    merged = {
        path_a: {"path": path_a, "ext": "pdf", "content_hash": None, "domain": "other", "status": "gap"},
        path_b: {"path": path_b, "ext": "pdf", "content_hash": "sha256:bbbb", "domain": "other", "status": "gap"},
    }
    phase_a.write_merged_index_with_carryover(
        index_path=idx,
        merged_index=merged,
        preserve_metadata=True,
        today="2026-04-16",
    )

    # Enrichment step
    enrich.enrich_index(
        index_path=idx,
        summaries_dir=summaries,
        workers=1,
        resume=False,
        dry_run=False,
        today="2026-04-16",
    )

    # Assert enrichment succeeded
    after_enrich = {r["path"]: r for r in _read_index(idx)}
    assert after_enrich[path_a]["content_type"] == "document"
    assert after_enrich[path_a]["summary_done"] is True
    assert after_enrich[path_b]["summary_done"] is False

    # Phase C bounded writeback on path_b
    phase_c.apply_bounded_writeback(
        index_path=idx,
        target_hashes={"sha256:bbbb"},
        repo_domain_map={"pipeline": ["digitalmodel"]},
    )

    # Phase E backpopulate via the real function
    phase_e = importlib.import_module("phase-e-backpopulate")
    phase_e.backpopulate_index(
        index_path=idx,
        repo_domain_map={"marine": ["digitalmodel"], "other": ["other-repo"]},
        classify_fn=lambda _rec: ("marine", "gap"),
    )

    # Phase A re-run (simulated rebuild) with carryover to prove round-trip safety
    rebuild = {
        path_a: {"path": path_a, "ext": "pdf", "content_hash": None, "domain": "marine"},
        path_b: {"path": path_b, "ext": "pdf", "content_hash": "sha256:bbbb", "domain": "marine"},
    }
    phase_a.write_merged_index_with_carryover(
        index_path=idx,
        merged_index=rebuild,
        preserve_metadata=True,
        today="2026-04-16",
    )

    final = {r["path"]: r for r in _read_index(idx)}
    # content_type + summary_done survived A → enrich → C → E → A
    assert final[path_a]["content_type"] == "document"
    assert final[path_a]["summary_done"] is True
    assert final[path_b]["content_type"] == "document"
    assert final[path_b]["summary_done"] is False
    # #2309: summary_file_exists also survives the full chain
    assert final[path_a]["summary_file_exists"] is True   # summary exists with content
    assert final[path_b]["summary_file_exists"] is False  # no summary file


# ═════════════ #2309 tests 15, 16: mixed-schema Phase C/E ═════════════

def test_phase_c_writeback_preserves_both_summary_fields(tmp_path):
    """Phase C bounded writeback on a record with both summary fields keeps both."""
    phase_c = importlib.import_module("phase-c-classify")

    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {
                "path": "/t.pdf",
                "ext": "pdf",
                "content_hash": "sha256:aaaa",
                "domain": "other",
                "status": "gap",
                "target_repos": [],
                "content_type": "document",
                "summary_done": False,
                "summary_file_exists": True,  # file exists, content empty — #2309 case
            }
        ],
    )

    phase_c.apply_bounded_writeback(
        index_path=idx,
        target_hashes={"sha256:aaaa"},
        repo_domain_map={"marine": ["digitalmodel"]},
    )
    out = _read_index(idx)[0]
    assert out["content_type"] == "document"
    assert out["summary_done"] is False
    assert out["summary_file_exists"] is True  # survived writeback


def test_phase_e_backpopulate_preserves_both_summary_fields(tmp_path):
    """Phase E backpopulate on a record with both summary fields keeps both."""
    phase_e = importlib.import_module("phase-e-backpopulate")

    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {
                "path": "/e.pdf",
                "ext": "pdf",
                "domain": None,  # triggers classification
                "content_type": "document",
                "summary_done": False,
                "summary_file_exists": True,  # file exists, content empty
            }
        ],
    )

    phase_e.backpopulate_index(
        index_path=idx,
        repo_domain_map={"marine": ["digitalmodel"]},
        classify_fn=lambda _rec: ("marine", "gap"),
    )
    out = _read_index(idx)[0]
    assert out["content_type"] == "document"
    assert out["summary_done"] is False
    assert out["summary_file_exists"] is True  # survived backpop
    assert out["domain"] == "marine"  # Phase E classification applied
