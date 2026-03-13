"""Tests for the requirements promoter module."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.text_utils import content_hash

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _make_record(text, document="test.pdf", section="1.0", page=1,
                 domain="naval-architecture", manifest="test.pdf"):
    """Helper to build a requirements record."""
    return {
        "text": text,
        "source": {"document": document, "section": section, "page": page},
        "domain": domain,
        "manifest": manifest,
    }


def _read_fixture_records():
    """Load the test fixture JSONL."""
    records = []
    fixture = FIXTURES / "requirements.jsonl"
    with open(fixture, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# -- numbering ---------------------------------------------------------


class TestRequirementNumbering:
    """Verify sequential REQ_NNN numbering."""

    def test_single_requirement_numbered_001(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [_make_record("Steel shall comply with EN 10025.")]
        result = promote_requirements(records, tmp_dir)
        assert len(result.files_written) == 1
        content = Path(result.files_written[0]).read_text()
        assert "REQ_001" in content

    def test_two_requirements_numbered_sequentially(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [
            _make_record("First requirement text."),
            _make_record("Second requirement text."),
        ]
        result = promote_requirements(records, tmp_dir)
        content = Path(result.files_written[0]).read_text()
        assert "REQ_001" in content
        assert "REQ_002" in content


# -- rendering ---------------------------------------------------------


class TestRenderRequirementsModule:
    """Verify rendered Python module format."""

    def test_content_hash_in_header(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [_make_record("A requirement.")]
        result = promote_requirements(records, tmp_dir)
        content = Path(result.files_written[0]).read_text()
        assert "# content-hash: " in content
        # Extract hash and verify length
        for line in content.splitlines():
            if "# content-hash:" in line:
                hash_val = line.split("# content-hash: ")[1].strip()
                assert len(hash_val) == 64
                break

    def test_module_docstring_mentions_domain(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [_make_record("A requirement.", domain="naval-architecture")]
        result = promote_requirements(records, tmp_dir)
        content = Path(result.files_written[0]).read_text()
        assert "naval-architecture" in content
        assert "auto-promoted from doc-intelligence" in content

    def test_string_constant_valid_python(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = _read_fixture_records()
        result = promote_requirements(records, tmp_dir)
        content = Path(result.files_written[0]).read_text()
        # Must compile without syntax errors
        compile(content, "requirements.py", "exec")

    def test_source_citation_in_docstring(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [_make_record(
            "Cathodic protection design life shall be 25 years.",
            document="DNV-RP-B401.pdf", section="4.1.2", page=10,
        )]
        result = promote_requirements(records, tmp_dir)
        content = Path(result.files_written[0]).read_text()
        assert "DNV-RP-B401.pdf" in content
        assert "§4.1.2" in content
        assert "p.10" in content

    def test_long_string_uses_parenthesized_continuation(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        long_text = (
            "The minimum design life for cathodic protection systems "
            "shall be 25 years unless otherwise specified by the "
            "operator and approved by the relevant authority."
        )
        records = [_make_record(long_text)]
        result = promote_requirements(records, tmp_dir)
        content = Path(result.files_written[0]).read_text()
        # Should use parenthesized continuation
        assert "(\n" in content or '= (\n' in content


# -- grouping by domain ------------------------------------------------


class TestDomainGrouping:
    """Verify one output file per domain."""

    def test_two_domains_produce_two_files(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [
            _make_record("Req A.", domain="naval-architecture"),
            _make_record("Req B.", domain="structural"),
        ]
        result = promote_requirements(records, tmp_dir)
        assert len(result.files_written) == 2
        paths = [Path(p) for p in result.files_written]
        domains_found = {p.parent.name for p in paths}
        assert "naval-architecture" in domains_found
        assert "structural" in domains_found

    def test_numbering_restarts_per_domain(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = [
            _make_record("Req A.", domain="domain-a"),
            _make_record("Req B.", domain="domain-b"),
        ]
        result = promote_requirements(records, tmp_dir)
        for path_str in result.files_written:
            content = Path(path_str).read_text()
            assert "REQ_001" in content


# -- promote_requirements integration ----------------------------------


class TestPromoteRequirements:
    """Integration tests for the full promote_requirements function."""

    def test_writes_output_file(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = _read_fixture_records()
        result = promote_requirements(records, tmp_dir)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0
        out_path = Path(result.files_written[0])
        assert out_path.exists()
        content = out_path.read_text()
        assert "REQ_001" in content
        assert "REQ_002" in content

    def test_idempotency_skips_on_second_call(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = _read_fixture_records()
        promote_requirements(records, tmp_dir)
        result2 = promote_requirements(records, tmp_dir)
        assert len(result2.files_skipped) == 1
        assert len(result2.files_written) == 0

    def test_dry_run_writes_nothing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = _read_fixture_records()
        result = promote_requirements(records, tmp_dir, dry_run=True)
        assert len(result.files_written) == 1
        out_path = Path(result.files_written[0])
        assert not out_path.exists()

    def test_empty_records_no_output(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        result = promote_requirements([], tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0

    def test_output_path_under_promoted_directory(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.requirements import (
            promote_requirements,
        )
        records = _read_fixture_records()
        result = promote_requirements(records, tmp_dir)
        out_path = Path(result.files_written[0])
        assert "data/standards/promoted" in str(out_path)
        assert out_path.name == "requirements.py"

    def test_registration(self):
        from scripts.data.doc_intelligence.promoters.coordinator import (
            _PROMOTER_REGISTRY,
        )
        # Force import to trigger registration
        import scripts.data.doc_intelligence.promoters.requirements  # noqa: F401
        assert "requirements" in _PROMOTER_REGISTRY
