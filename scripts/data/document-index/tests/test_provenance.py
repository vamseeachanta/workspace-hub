"""Tests for the multi-source provenance tracking layer."""

import json
import os
from copy import deepcopy
from pathlib import Path

import pytest

# Allow running from repo root via `python -m pytest` or with PYTHONPATH set.
import sys

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from provenance import (
    DEFAULT_SOURCE_PRIORITY,
    apply_provenance_to_pipeline,
    merge_provenance,
    merge_provenance_streaming,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _rec(
    path: str,
    source: str,
    content_hash: str = "sha256:aaa111",
    host: str = "dev-primary",
    **extra,
) -> dict:
    """Build a minimal index record."""
    base = {
        "path": path,
        "host": host,
        "source": source,
        "ext": "pdf",
        "size_mb": 1.0,
        "mtime": "2025-01-01",
        "content_hash": content_hash,
        "is_cad": False,
        "domain": None,
        "summary": None,
    }
    base.update(extra)
    return base


# ---------------------------------------------------------------------------
# merge_provenance — in-memory
# ---------------------------------------------------------------------------

class TestMergeProvenance:
    def test_single_record_gets_provenance_array(self):
        records = [_rec("/a/doc.pdf", "og_standards")]
        merged = merge_provenance(records)
        assert len(merged) == 1
        assert "provenance" in merged[0]
        assert len(merged[0]["provenance"]) == 1
        assert merged[0]["provenance"][0]["source"] == "og_standards"
        assert merged[0]["provenance"][0]["path"] == "/a/doc.pdf"

    def test_two_sources_merge_into_one_record(self):
        records = [
            _rec("/mnt/ace/standards/doc.pdf", "og_standards", content_hash="sha256:abc"),
            _rec("/mnt/ace/docs/doc.pdf", "ace_project", content_hash="sha256:abc"),
        ]
        merged = merge_provenance(records)
        assert len(merged) == 1
        assert len(merged[0]["provenance"]) == 2

    def test_primary_chosen_by_source_priority(self):
        records = [
            _rec("/mnt/low/doc.pdf", "ace_project", content_hash="sha256:abc"),
            _rec("/mnt/high/doc.pdf", "og_standards", content_hash="sha256:abc"),
        ]
        merged = merge_provenance(records)
        # og_standards has higher priority, so its path should be the primary
        assert merged[0]["path"] == "/mnt/high/doc.pdf"
        assert merged[0]["source"] == "og_standards"

    def test_provenance_sorted_by_priority(self):
        records = [
            _rec("/c.pdf", "dde_project", content_hash="sha256:x"),
            _rec("/a.pdf", "og_standards", content_hash="sha256:x"),
            _rec("/b.pdf", "ace_standards", content_hash="sha256:x"),
        ]
        merged = merge_provenance(records)
        sources = [p["source"] for p in merged[0]["provenance"]]
        assert sources == ["og_standards", "ace_standards", "dde_project"]

    def test_different_hashes_stay_separate(self):
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:aaa"),
            _rec("/b.pdf", "og_standards", content_hash="sha256:bbb"),
        ]
        merged = merge_provenance(records)
        assert len(merged) == 2

    def test_no_hash_records_pass_through(self):
        records = [
            _rec("/cad.dwg", "ace_project", content_hash=None, is_cad=True),
        ]
        # content_hash=None should be treated as falsy
        records[0]["content_hash"] = None
        merged = merge_provenance(records)
        assert len(merged) == 1
        assert merged[0]["provenance"][0]["source"] == "ace_project"

    def test_duplicate_of_field_removed(self):
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:dup"),
            _rec("/b.pdf", "ace_project", content_hash="sha256:dup", duplicate_of="/a.pdf"),
        ]
        merged = merge_provenance(records)
        assert "duplicate_of" not in merged[0]

    def test_enrichments_merged_from_secondary(self):
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:enr", domain=None),
            _rec(
                "/b.pdf", "ace_project", content_hash="sha256:enr",
                domain="structural", summary="A structural doc",
            ),
        ]
        merged = merge_provenance(records)
        # Primary is og_standards (None domain), but secondary has enrichment
        assert merged[0]["domain"] == "structural"
        assert merged[0]["summary"] == "A structural doc"

    def test_primary_enrichments_not_overwritten(self):
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:enr2", domain="pipeline"),
            _rec("/b.pdf", "ace_project", content_hash="sha256:enr2", domain="structural"),
        ]
        merged = merge_provenance(records)
        # Primary's domain should NOT be overwritten
        assert merged[0]["domain"] == "pipeline"

    def test_list_fields_merged(self):
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:lst",
                 target_repos=["digitalmodel"]),
            _rec("/b.pdf", "ace_project", content_hash="sha256:lst",
                 target_repos=["digitalmodel", "doris"]),
        ]
        merged = merge_provenance(records)
        assert "doris" in merged[0]["target_repos"]
        assert "digitalmodel" in merged[0]["target_repos"]

    def test_custom_source_priority(self):
        records = [
            _rec("/a.pdf", "ace_project", content_hash="sha256:cust"),
            _rec("/b.pdf", "og_standards", content_hash="sha256:cust"),
        ]
        # Reverse priority: ace_project first
        merged = merge_provenance(records, source_priority=["ace_project", "og_standards"])
        assert merged[0]["source"] == "ace_project"

    def test_provenance_entry_preserves_og_db_id(self):
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:ogid", og_db_id=42),
        ]
        merged = merge_provenance(records)
        assert merged[0]["provenance"][0]["og_db_id"] == 42

    def test_provenance_entry_preserves_old_path(self):
        records = [
            _rec("/new/path.pdf", "og_standards", content_hash="sha256:remap",
                 old_path="/old/path.pdf"),
        ]
        merged = merge_provenance(records)
        assert merged[0]["provenance"][0]["old_path"] == "/old/path.pdf"

    def test_three_sources_for_same_document(self):
        h = "sha256:triple"
        records = [
            _rec("/og/doc.pdf", "og_standards", content_hash=h),
            _rec("/ace/doc.pdf", "ace_standards", content_hash=h),
            _rec("/dde/doc.pdf", "dde_project", content_hash=h, host="dev-secondary"),
        ]
        merged = merge_provenance(records)
        assert len(merged) == 1
        assert len(merged[0]["provenance"]) == 3
        hosts = {p["host"] for p in merged[0]["provenance"]}
        assert "dev-secondary" in hosts

    def test_empty_input(self):
        merged = merge_provenance([])
        assert merged == []

    def test_does_not_mutate_input(self):
        original = _rec("/a.pdf", "og_standards", content_hash="sha256:mut")
        records = [original]
        original_copy = deepcopy(original)
        merge_provenance(records)
        assert original == original_copy


# ---------------------------------------------------------------------------
# merge_provenance_streaming — file-based
# ---------------------------------------------------------------------------

class TestMergeProvenanceStreaming:
    def test_streaming_basic(self, tmp_path):
        input_path = tmp_path / "input.jsonl"
        output_path = tmp_path / "output.jsonl"

        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:s1"),
            _rec("/b.pdf", "ace_project", content_hash="sha256:s1"),
            _rec("/c.pdf", "og_standards", content_hash="sha256:s2"),
        ]
        with open(input_path, "w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")

        stats = merge_provenance_streaming(input_path, output_path)
        assert stats["input_count"] == 3
        assert stats["output_count"] == 2
        assert stats["merged_groups"] == 1

        # Verify output
        with open(output_path) as f:
            out_records = [json.loads(line) for line in f if line.strip()]
        assert len(out_records) == 2
        for rec in out_records:
            assert "provenance" in rec

    def test_streaming_atomic_write(self, tmp_path):
        """No .tmp files should remain after a successful run."""
        input_path = tmp_path / "input.jsonl"
        output_path = tmp_path / "output.jsonl"

        with open(input_path, "w") as f:
            f.write(json.dumps(_rec("/a.pdf", "og_standards")) + "\n")

        merge_provenance_streaming(input_path, output_path)
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0

    def test_streaming_handles_no_hash(self, tmp_path):
        input_path = tmp_path / "input.jsonl"
        output_path = tmp_path / "output.jsonl"

        rec = _rec("/cad.dwg", "ace_project", content_hash=None)
        rec["content_hash"] = None
        with open(input_path, "w") as f:
            f.write(json.dumps(rec) + "\n")

        stats = merge_provenance_streaming(input_path, output_path)
        assert stats["no_hash_count"] == 1
        assert stats["output_count"] == 1

    def test_streaming_in_place(self, tmp_path):
        """Writing output to the same path as input should work (atomic replace)."""
        path = tmp_path / "index.jsonl"
        records = [
            _rec("/a.pdf", "og_standards", content_hash="sha256:inp"),
            _rec("/b.pdf", "ace_project", content_hash="sha256:inp"),
        ]
        with open(path, "w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")

        stats = merge_provenance_streaming(path, path)
        assert stats["input_count"] == 2
        assert stats["output_count"] == 1

        with open(path) as f:
            out = [json.loads(line) for line in f if line.strip()]
        assert len(out) == 1
        assert len(out[0]["provenance"]) == 2


# ---------------------------------------------------------------------------
# apply_provenance_to_pipeline — integration hook
# ---------------------------------------------------------------------------

class TestApplyProvenanceToPipeline:
    def test_merges_existing_and_new(self):
        existing = {
            "/a.pdf": _rec("/a.pdf", "og_standards", content_hash="sha256:pip"),
        }
        new_records = [
            _rec("/b.pdf", "ace_project", content_hash="sha256:pip"),
        ]
        merged = apply_provenance_to_pipeline(existing, new_records)
        # Should merge into one record keyed by content_hash
        assert "sha256:pip" in merged
        assert len(merged["sha256:pip"]["provenance"]) == 2

    def test_new_unique_record_added(self):
        existing = {
            "/a.pdf": _rec("/a.pdf", "og_standards", content_hash="sha256:old"),
        }
        new_records = [
            _rec("/c.pdf", "ace_project", content_hash="sha256:new"),
        ]
        merged = apply_provenance_to_pipeline(existing, new_records)
        assert "sha256:old" in merged
        assert "sha256:new" in merged

    def test_does_not_mutate_existing(self):
        existing = {
            "/a.pdf": _rec("/a.pdf", "og_standards", content_hash="sha256:safe"),
        }
        original = deepcopy(existing)
        apply_provenance_to_pipeline(existing, [])
        assert existing == original
