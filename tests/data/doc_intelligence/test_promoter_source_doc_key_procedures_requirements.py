"""Focused source_doc_key promoter follow-up tests (#2389)."""

from pathlib import Path

import pytest

from tests.data.doc_intelligence.promoter_source_doc_key_helpers import *

class TestProceduresPromoterSourceDocKey:
    """Verify the procedures promoter emits canonical comment headers."""

    def test_emits_both_headers_in_yaml(self, tmp_dir):
        """YAML output must carry ``# content-hash:`` and ``# source_doc_key:``
        comment-form headers per contract section 8.3."""
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected procedure YAML to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key="bad")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures(
            [_procedure_record(doc_key="proc.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []


class TestRequirementsPromoterSourceDocKey:
    """Verify the requirements promoter threads source_doc_key."""

    def test_emits_both_headers(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        result = promote_requirements(
            [_requirement_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected requirements.py to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_multiple_distinct_doc_keys_all_emitted(self, tmp_dir):
        """Grouped requirements module aggregates per-record sources; every
        distinct source_doc_key must appear."""
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        recs = [
            _requirement_record(
                text="The minimum design life shall be 25 years.",
                doc_key=SHA256_A,
            ),
            _requirement_record(
                text=(
                    "All structural steel shall comply with EN 10025 Grade "
                    "S355 or equivalent."
                ),
                doc_key=SHA256_B,
                document="EN-10025.pdf",
            ),
        ]
        result = promote_requirements(recs, tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        assert SHA256_A in out_text
        assert SHA256_B in out_text

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        result = promote_requirements(
            [_requirement_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )

        result = promote_requirements(
            [_requirement_record(doc_key="garbage")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []
