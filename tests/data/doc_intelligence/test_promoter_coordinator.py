"""Tests for promoter coordinator and text_utils."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    PromoteStats,
    _read_jsonl,
    promote_all,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    content_hash,
    sanitize_identifier,
    source_citation,
    write_atomic,
)

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


# ── text_utils ──────────────────────────────────────────────────────────


class TestSanitizeIdentifier:
    def test_basic_text(self):
        assert sanitize_identifier("Steel yield strength") == "steel_yield_strength"

    def test_strips_special_chars(self):
        assert sanitize_identifier("Yield (MPa)") == "yield_mpa"

    def test_leading_digit(self):
        result = sanitize_identifier("3.1 Some heading")
        assert result.startswith("_")
        assert not result[0].isdigit()

    def test_collapses_whitespace(self):
        assert sanitize_identifier("a   b  c") == "a_b_c"

    def test_empty_string(self):
        assert sanitize_identifier("") == ""

    def test_screaming_snake_preserved(self):
        result = sanitize_identifier("STEEL_DENSITY")
        assert result == "steel_density"


class TestContentHash:
    def test_deterministic(self):
        h1 = content_hash("hello")
        h2 = content_hash("hello")
        assert h1 == h2

    def test_different_for_different_content(self):
        assert content_hash("a") != content_hash("b")

    def test_returns_hex_string(self):
        h = content_hash("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestWriteAtomic:
    def test_creates_file(self, tmp_dir):
        p = tmp_dir / "out.py"
        written = write_atomic(p, "# content-hash: abc\ncode")
        assert written is True
        assert p.exists()

    def test_skips_unchanged(self, tmp_dir):
        content = "# content-hash: abc123\nx = 42\n"
        p = tmp_dir / "out.py"
        write_atomic(p, content)
        written = write_atomic(p, content)
        assert written is False

    def test_overwrites_changed(self, tmp_dir):
        p = tmp_dir / "out.py"
        write_atomic(p, "# content-hash: old\nv1")
        written = write_atomic(p, "# content-hash: new\nv2")
        assert written is True
        assert "v2" in p.read_text()

    def test_creates_parent_dirs(self, tmp_dir):
        p = tmp_dir / "sub" / "deep" / "out.py"
        write_atomic(p, "# content-hash: x\ndata")
        assert p.exists()

    def test_dry_run_no_write(self, tmp_dir):
        p = tmp_dir / "out.py"
        written = write_atomic(p, "data", dry_run=True)
        assert written is True
        assert not p.exists()

    def test_no_tmp_files_remain(self, tmp_dir):
        p = tmp_dir / "out.py"
        write_atomic(p, "# content-hash: x\ndata")
        tmps = list(tmp_dir.rglob("*.tmp"))
        assert len(tmps) == 0


class TestSourceCitation:
    def test_full_citation(self):
        s = {"document": "DNV-RP-B401.pdf", "section": "3.2", "page": 15}
        assert source_citation(s) == "DNV-RP-B401.pdf §3.2 p.15"

    def test_document_only(self):
        assert source_citation({"document": "foo.pdf"}) == "foo.pdf"

    def test_with_sheet(self):
        s = {"document": "data.xlsx", "sheet": "Summary"}
        assert source_citation(s) == "data.xlsx sheet:Summary"


# ── coordinator ─────────────────────────────────────────────────────────


class TestReadJsonl:
    def test_reads_fixture(self):
        records = _read_jsonl(FIXTURES / "constants.jsonl")
        assert len(records) == 2
        assert records[0]["domain"] == "naval-architecture"

    def test_missing_file_returns_empty(self, tmp_dir):
        assert _read_jsonl(tmp_dir / "nonexistent.jsonl") == []

    def test_empty_file(self, tmp_dir):
        p = tmp_dir / "empty.jsonl"
        p.write_text("")
        assert _read_jsonl(p) == []


class TestPromoteResult:
    def test_defaults_empty(self):
        r = PromoteResult()
        assert r.files_written == []
        assert r.files_skipped == []
        assert r.errors == []


class TestPromoteStats:
    def test_defaults_zero(self):
        s = PromoteStats()
        assert s.total_written == 0
        assert s.total_skipped == 0
        assert s.total_errors == 0


class TestPromoteAll:
    def test_unknown_type_reports_error(self, tmp_dir):
        stats = promote_all(
            index_dir=FIXTURES,
            project_root=tmp_dir,
            types=["nonexistent"],
        )
        assert stats.total_errors >= 1
        assert "nonexistent" in stats.results_by_type

    def test_empty_indexes_no_crash(self, tmp_dir):
        empty_dir = tmp_dir / "indexes"
        empty_dir.mkdir()
        stats = promote_all(
            index_dir=empty_dir,
            project_root=tmp_dir,
        )
        assert isinstance(stats, PromoteStats)

    def test_dry_run_writes_nothing(self, tmp_dir):
        stats = promote_all(
            index_dir=FIXTURES,
            project_root=tmp_dir,
            dry_run=True,
            types=["constants"],
        )
        # Should report files but not actually write them
        result = stats.results_by_type.get("constants")
        assert result is not None
        # Verify no files created under project_root except tmp_dir itself
        created = [f for f in tmp_dir.rglob("*") if f.is_file()]
        assert len(created) == 0
