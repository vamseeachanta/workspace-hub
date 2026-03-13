"""Tests for utils — doc_ref generation, source availability check."""

import os
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.utils import (
    check_source_available,
    generate_doc_ref,
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


class TestCheckSourceAvailable:
    def test_existing_file_returns_true(self, tmp_dir):
        f = tmp_dir / "exists.pdf"
        f.write_bytes(b"data")
        assert check_source_available(str(f)) is True

    def test_missing_file_returns_false(self):
        assert check_source_available("/nonexistent/path/file.pdf") is False

    def test_directory_returns_false(self, tmp_dir):
        assert check_source_available(str(tmp_dir)) is False
