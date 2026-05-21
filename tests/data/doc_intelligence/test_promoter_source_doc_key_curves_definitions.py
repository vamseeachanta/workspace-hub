"""Focused source_doc_key promoter follow-up tests (#2389)."""

from pathlib import Path

import pytest

from tests.data.doc_intelligence.promoter_source_doc_key_helpers import *

class TestCurvesPromoterSourceDocKey:
    """Verify the curves promoter emits and validates source_doc_key."""

    def test_emits_both_headers_on_scaffold(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves([_curve_record(doc_key=SHA256_A)], tmp_dir)

        assert result.errors == [], f"unexpected errors: {result.errors}"
        py_paths = [
            p for p in result.files_written if p.endswith("curves.py")
        ]
        assert py_paths, "expected at least one curves.py output"
        out_text = Path(py_paths[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_emits_both_headers_on_placeholder_csv(self, tmp_dir):
        """Placeholder CSV files are also promoted artifacts; per the contract
        they must carry the same provenance headers."""
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves([_curve_record(doc_key=SHA256_A)], tmp_dir)
        csv_paths = [p for p in result.files_written if p.endswith(".csv")]
        assert csv_paths, "expected at least one placeholder CSV"
        out_text = Path(csv_paths[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves([_curve_record(doc_key=None)], tmp_dir)
        assert result.errors, "expected fail-closed for missing source.doc_key"
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves(
            [_curve_record(doc_key="not-a-hash")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves(
            [_curve_record(doc_key="DNV-RP-C205.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )

        result = promote_curves(
            [_curve_record(doc_key="/mnt/ace/acma-codes/foo.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_without_partial_writes_on_csv_self_loop(self, tmp_dir):
        """If any curve output is invalid, the batch must not leave earlier files.

        The placeholder CSV content hash is deterministic for the empty x/y
        scaffold. Using that hash as source_doc_key should fail closed before
        writing either the Python scaffold or the CSV.
        """
        from scripts.data.doc_intelligence.promoters.curves import (
            promote_curves,
        )
        from scripts.data.doc_intelligence.promoters.text_utils import (
            content_hash,
        )

        placeholder_body_hash = content_hash("x,y\n")
        loop_key = f"sha256:{placeholder_body_hash}"
        result = promote_curves([_curve_record(doc_key=loop_key)], tmp_dir)

        assert result.errors
        assert result.files_written == []
        assert not list(tmp_dir.rglob("curves.py"))
        assert not list(tmp_dir.rglob("*.csv"))


class TestDefinitionsPromoterSourceDocKey:
    """Verify the definitions promoter emits canonical headers and validates."""

    def test_emits_canonical_content_hash_header(self, tmp_dir):
        """Definitions must emit ``# content-hash:`` (dash) per contract,
        replacing the legacy ``# content_hash:`` (underscore) field."""
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected glossary.yaml to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)

    def test_emits_source_doc_key_header(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key=SHA256_A)], tmp_dir,
        )
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key="not-canonical")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.definitions import (
            promote_definitions,
        )

        result = promote_definitions(
            [_definition_record(doc_key="/mnt/ace/x.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []
