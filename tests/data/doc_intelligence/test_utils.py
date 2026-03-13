"""Tests for utils — doc_ref generation, source availability check."""

import os
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.utils import (
    check_source_available,
    generate_doc_ref,
    generate_doc_ref_from_url,
)


class TestGenerateDocRef:
    def test_strips_extension(self):
        ref = generate_doc_ref("report.pdf")
        assert not ref.endswith(".pdf")

    def test_lowercases(self):
        ref = generate_doc_ref("MyReport.PDF")
        assert ref == ref.lower()

    def test_replaces_spaces_with_hyphens(self):
        ref = generate_doc_ref("my report name.pdf")
        assert " " not in ref
        assert "my-report-name" in ref

    def test_custom_override(self):
        ref = generate_doc_ref("anything.pdf", doc_ref="custom-ref")
        assert ref == "custom-ref"

    def test_handles_path_input(self):
        ref = generate_doc_ref("/some/path/to/Report.pdf")
        assert ref == "report"

    def test_replaces_underscores(self):
        ref = generate_doc_ref("my_report_v2.docx")
        assert ref == "my-report-v2"


class TestGenerateDocRefFromUrl:
    def test_basic_url_with_title(self):
        url = "https://ocw.mit.edu/courses/marine-hydrodynamics/"
        ref = generate_doc_ref_from_url(url, "MIT OCW Marine Hydrodynamics Lecture 1")
        # Should start with 8-char SHA256 hash prefix
        assert len(ref.split("-", 1)[0]) == 8
        assert "mit-ocw-marine-hydrodynamics-lecture-1" in ref

    def test_hash_is_deterministic(self):
        url = "https://example.com/page"
        r1 = generate_doc_ref_from_url(url, "Test")
        r2 = generate_doc_ref_from_url(url, "Test")
        assert r1 == r2

    def test_different_urls_different_hashes(self):
        r1 = generate_doc_ref_from_url("https://a.com/1", "Same Title")
        r2 = generate_doc_ref_from_url("https://b.com/2", "Same Title")
        assert r1 != r2

    def test_title_truncated_to_60_chars(self):
        long_title = "A" * 100
        ref = generate_doc_ref_from_url("https://example.com", long_title)
        # 8 hash + hyphen + title portion
        title_part = ref[9:]  # after "abcd1234-"
        assert len(title_part) <= 60

    def test_none_title_uses_url_only(self):
        ref = generate_doc_ref_from_url("https://example.com/page.html", None)
        assert len(ref) == 8  # just the hash prefix

    def test_special_chars_removed(self):
        ref = generate_doc_ref_from_url(
            "https://example.com", "Title: With (Special) Chars!"
        )
        assert ":" not in ref
        assert "(" not in ref
        assert "!" not in ref

    def test_multiple_spaces_collapsed(self):
        ref = generate_doc_ref_from_url("https://example.com", "a   b   c")
        assert "--" not in ref


class TestCheckSourceAvailable:
    def test_existing_file_returns_true(self, tmp_dir):
        f = tmp_dir / "exists.pdf"
        f.write_bytes(b"data")
        assert check_source_available(str(f)) is True

    def test_missing_file_returns_false(self):
        assert check_source_available("/nonexistent/path/file.pdf") is False

    def test_directory_returns_false(self, tmp_dir):
        assert check_source_available(str(tmp_dir)) is False
