"""Focused source_doc_key promoter follow-up tests (#2389)."""

from pathlib import Path

import pytest

from tests.data.doc_intelligence.promoter_source_doc_key_helpers import *

class TestTablesPromoterSourceDocKey:
    """Verify the tables promoter prepends headers to copied CSVs."""

    def test_emits_both_headers_at_csv_head(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key=SHA256_A)
        result = promote_tables([rec], tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected promoted CSV to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        # Original CSV body must still be present after the header block.
        assert "Material,Yield (MPa)" in out_text
        assert "S355,355" in out_text

    def test_csv_headers_precede_data(self, tmp_dir):
        """Headers must appear BEFORE the first non-comment data line, so
        comment-aware parsers (pandas comment='#') skip them naturally."""
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key=SHA256_A)
        result = promote_tables([rec], tmp_dir)
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        non_comment_lines = [
            ln for ln in out_text.splitlines() if not ln.startswith("#")
        ]
        assert non_comment_lines[0].startswith("Material"), (
            "expected first non-comment line to be the original CSV header"
        )

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key=None)
        result = promote_tables([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(project_root=tmp_dir, doc_key="bad")
        result = promote_tables([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_path_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.tables import (
            promote_tables,
        )

        rec = _table_record(
            project_root=tmp_dir, doc_key="/mnt/ace/acma-codes/x.csv",
        )
        result = promote_tables([rec], tmp_dir)
        assert result.errors
        assert result.files_written == []


class TestWorkedExamplesPromoterSourceDocKey:
    """Verify the worked-examples promoter threads source_doc_key."""

    def test_emits_both_headers(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key=SHA256_A)], tmp_dir,
        )
        assert result.errors == [], f"unexpected errors: {result.errors}"
        assert result.files_written, "expected test_*.py to be written"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        _assert_content_hash_header(out_text)
        _assert_source_doc_key_header(out_text, SHA256_A)
        _assert_no_path_leakage_in_doc_key_headers(out_text)

    def test_multiple_distinct_doc_keys_all_emitted(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        recs = [
            _worked_example_record(doc_key=SHA256_A),
            _worked_example_record(
                text=(
                    "Example 5.2: Determine buoyancy on 2m³ object.\n"
                    "Given: rho = 1025 kg/m³, g = 9.81 m/s², V = 2 m³\n"
                    "Solution: F_b = 1025 × 9.81 × 2 = 20,110.5 N"
                ),
                doc_key=SHA256_B,
            ),
        ]
        result = promote_worked_examples(recs, tmp_dir)
        assert result.errors == [], f"unexpected errors: {result.errors}"
        out_text = Path(result.files_written[0]).read_text(encoding="utf-8")
        assert SHA256_A in out_text
        assert SHA256_B in out_text

    def test_fails_closed_when_doc_key_missing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key=None)], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_malformed_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key="bad")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []

    def test_fails_closed_on_filename_doc_key(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples(
            [_worked_example_record(doc_key="DNV-RP-C205.pdf")], tmp_dir,
        )
        assert result.errors
        assert result.files_written == []
