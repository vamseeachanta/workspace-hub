#!/usr/bin/env python3
# ABOUTME: TDD tests for bounded classification writeback (#2247)
# ABOUTME: Validates that targeted runs update only allowlisted index records

"""Tests for bounded authoritative domain writeback in phase-c-classify.py."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

# Import phase-c-classify.py (hyphenated module name requires importlib)
_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)
_mod = importlib.import_module("phase-c-classify")

load_target_list = _mod.load_target_list
apply_bounded_writeback = _mod.apply_bounded_writeback
classify_heuristic = _mod.classify_heuristic


# ---------------------------------------------------------------------------
# Fixtures — reusable temporary index data
# ---------------------------------------------------------------------------

def _make_index(tmp_path: Path, records: list[dict]) -> Path:
    """Write records to a temporary index.jsonl and return its path."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    index_path = tmp_path / "index.jsonl"
    with open(index_path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return index_path


def _read_index(index_path: Path) -> list[dict]:
    """Read all records from a jsonl file."""
    records = []
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


SAMPLE_RECORDS = [
    {
        "path": "/mnt/ace/docs/pipeline/dnv-st-f101-guide.pdf",
        "content_hash": "aaa111",
        "source": "ace_standards",
        "doc_number": "DNV-ST-F101",
    },
    {
        "path": "/mnt/ace/docs/structural/iso-19902.pdf",
        "content_hash": "bbb222",
        "source": "ace_standards",
        "doc_number": "ISO 19902",
    },
    {
        "path": "/mnt/ace/docs/mooring/calm-buoy-analysis.pdf",
        "content_hash": "ccc333",
        "source": "ace_project",
        "doc_number": "",
    },
    {
        "path": "/mnt/ace/docs/misc/readme.txt",
        "content_hash": "ddd444",
        "source": "ace_project",
        "doc_number": "",
        "domain": "other",
        "status": "reference",
    },
]

REPO_DOMAIN_MAP = {
    "digitalmodel": ["structural", "cathodic-protection", "pipeline", "marine", "installation", "materials"],
    "worldenergydata": ["energy-economics", "regulatory"],
}


# ---------------------------------------------------------------------------
# (a) No writeback without explicit bounded mode
# ---------------------------------------------------------------------------

class TestNoWritebackWithoutBoundedMode:
    """Default classification run must NOT mutate the index."""

    def test_empty_target_set_leaves_index_unchanged(self, tmp_path):
        """apply_bounded_writeback with empty targets must not touch index."""
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        original_bytes = index_path.read_bytes()

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=set(),
            repo_domain_map=REPO_DOMAIN_MAP,
        )
        assert report["updated"] == 0
        assert report["skipped"] >= 0
        # Index file must be byte-for-byte identical
        assert index_path.read_bytes() == original_bytes


# ---------------------------------------------------------------------------
# (b) Allowlisted record gets domain/status written
# ---------------------------------------------------------------------------

class TestAllowlistedRecordWriteback:
    """Targeted records must receive domain and status classification."""

    def test_single_target_gets_domain_written(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111"}

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert report["updated"] == 1
        records = _read_index(index_path)
        rec_aaa = next(r for r in records if r["content_hash"] == "aaa111")
        assert rec_aaa["domain"] == "pipeline"
        assert rec_aaa["status"] in ("gap", "data_source", "reference", "implemented")
        assert "target_repos" in rec_aaa

    def test_target_repos_populated_from_domain(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111"}

        apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        records = _read_index(index_path)
        rec_aaa = next(r for r in records if r["content_hash"] == "aaa111")
        assert "digitalmodel" in rec_aaa["target_repos"]


# ---------------------------------------------------------------------------
# (c) Non-allowlisted records are untouched
# ---------------------------------------------------------------------------

class TestNonAllowlistedUntouched:
    """Records not in the target list must be byte-for-byte unchanged."""

    def test_non_target_records_unchanged(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        original_lines = index_path.read_text().strip().split("\n")
        original_by_hash = {}
        for line in original_lines:
            rec = json.loads(line)
            original_by_hash[rec["content_hash"]] = line

        target_hashes = {"aaa111"}
        apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        updated_lines = index_path.read_text().strip().split("\n")
        updated_by_hash = {}
        for line in updated_lines:
            rec = json.loads(line)
            updated_by_hash[rec["content_hash"]] = line

        for h in ["bbb222", "ccc333", "ddd444"]:
            assert updated_by_hash[h] == original_by_hash[h], (
                f"Non-target record {h} was mutated"
            )

    def test_record_count_preserved(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111"}

        apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        records = _read_index(index_path)
        assert len(records) == len(SAMPLE_RECORDS)

    def test_already_classified_target_gets_overwritten(self, tmp_path):
        """A target record that already has domain should be re-classified."""
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"ddd444"}

        apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        records = _read_index(index_path)
        rec_ddd = next(r for r in records if r["content_hash"] == "ddd444")
        assert "domain" in rec_ddd
        assert "status" in rec_ddd


# ---------------------------------------------------------------------------
# (d) Multiple selectors handled deterministically
# ---------------------------------------------------------------------------

class TestMultipleSelectors:
    """Multiple targets in the allowlist must all be updated deterministically."""

    def test_multiple_targets_all_updated(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111", "bbb222", "ccc333"}

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert report["updated"] == 3
        records = _read_index(index_path)
        for rec in records:
            if rec["content_hash"] in target_hashes:
                assert "domain" in rec and rec["domain"] is not None
                assert "status" in rec and rec["status"] is not None

    def test_deterministic_across_runs(self, tmp_path):
        """Running twice with the same targets produces identical output."""
        records_copy = [dict(r) for r in SAMPLE_RECORDS]

        (tmp_path / "run1").mkdir(parents=True, exist_ok=True)
        index_path_1 = _make_index(tmp_path / "run1", records_copy)

        (tmp_path / "run2").mkdir(parents=True, exist_ok=True)
        index_path_2 = _make_index(tmp_path / "run2", records_copy)

        target_hashes = {"aaa111", "ccc333"}

        apply_bounded_writeback(
            index_path=index_path_1,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )
        apply_bounded_writeback(
            index_path=index_path_2,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert index_path_1.read_text() == index_path_2.read_text()

    def test_target_not_in_index_counted_as_missing(self, tmp_path):
        """A target hash not found in the index should appear in the report."""
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111", "zzz999"}

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert report["updated"] == 1
        assert report["missing"] == 1


# ---------------------------------------------------------------------------
# (e) Verification report counts are correct
# ---------------------------------------------------------------------------

class TestVerificationReport:
    """The writeback report must accurately reflect what changed."""

    def test_report_structure(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111", "bbb222"}

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert "updated" in report
        assert "skipped" in report
        assert "missing" in report
        assert "total" in report
        assert "updated_hashes" in report

    def test_report_counts_match(self, tmp_path):
        index_path = _make_index(tmp_path, SAMPLE_RECORDS)
        target_hashes = {"aaa111", "ccc333"}

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert report["updated"] == 2
        assert report["skipped"] == 2
        assert report["missing"] == 0
        assert report["total"] == len(SAMPLE_RECORDS)
        assert set(report["updated_hashes"]) == {"aaa111", "ccc333"}

    def test_empty_index_report(self, tmp_path):
        index_path = _make_index(tmp_path, [])
        target_hashes = {"aaa111"}

        report = apply_bounded_writeback(
            index_path=index_path,
            target_hashes=target_hashes,
            repo_domain_map=REPO_DOMAIN_MAP,
        )

        assert report["updated"] == 0
        assert report["total"] == 0
        assert report["missing"] == 1


# ---------------------------------------------------------------------------
# Target list loading
# ---------------------------------------------------------------------------

class TestLoadTargetList:
    """Test loading target hashes from a file."""

    def test_load_one_per_line(self, tmp_path):
        target_file = tmp_path / "targets.txt"
        target_file.write_text("aaa111\nbbb222\nccc333\n")

        result = load_target_list(target_file)
        assert result == {"aaa111", "bbb222", "ccc333"}

    def test_ignores_blank_lines_and_comments(self, tmp_path):
        target_file = tmp_path / "targets.txt"
        target_file.write_text("aaa111\n\n# comment\nbbb222\n  \n")

        result = load_target_list(target_file)
        assert result == {"aaa111", "bbb222"}

    def test_strips_whitespace(self, tmp_path):
        target_file = tmp_path / "targets.txt"
        target_file.write_text("  aaa111  \n  bbb222\n")

        result = load_target_list(target_file)
        assert result == {"aaa111", "bbb222"}
