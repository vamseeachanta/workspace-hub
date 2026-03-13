"""Tests for the procedures promoter module."""

import json
from pathlib import Path

import pytest
import yaml

from scripts.data.doc_intelligence.promoters.coordinator import PromoteResult
from scripts.data.doc_intelligence.promoters.text_utils import content_hash

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _make_record(
    text,
    document="test.pdf",
    section="1.0",
    page=1,
    domain="naval-architecture",
    manifest="test.pdf",
):
    """Helper to build a procedure record."""
    return {
        "text": text,
        "source": {"document": document, "section": section, "page": page},
        "domain": domain,
        "manifest": manifest,
    }


def _read_fixture_records() -> list[dict]:
    """Load the test fixture JSONL."""
    records = []
    fixture = FIXTURES / "procedures.jsonl"
    with open(fixture, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# -- parsing -----------------------------------------------------------------


class TestParseProcedure:
    """Verify extraction of title and steps from text."""

    def test_basic_extraction(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        rec = _make_record(
            "Procedure: Cathodic Protection Survey\n"
            "1. Verify reference electrode calibration\n"
            "2. Measure potential at each test point"
        )
        result = _parse_procedure(rec)
        assert result is not None
        assert result["title"] == "Cathodic Protection Survey"
        assert result["procedure_id"] == "cathodic_protection_survey"
        assert len(result["steps"]) == 2
        assert result["steps"][0] == "Verify reference electrode calibration"
        assert result["steps"][1] == "Measure potential at each test point"

    def test_five_steps_extracted(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        records = _read_fixture_records()
        result = _parse_procedure(records[0])
        assert result is not None
        assert len(result["steps"]) == 5
        assert "Flag" in result["steps"][4]

    def test_no_procedure_prefix_returns_none(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        rec = _make_record("Some random text without procedure prefix.")
        result = _parse_procedure(rec)
        assert result is None

    def test_procedure_without_steps_returns_none(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        rec = _make_record("Procedure: Empty Procedure\nNo numbered steps here.")
        result = _parse_procedure(rec)
        assert result is None

    def test_source_preserved(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        rec = _make_record(
            "Procedure: Weld Inspection\n1. Check weld profile",
            document="AWS-D1.1.pdf",
            section="6.5",
            page=120,
        )
        result = _parse_procedure(rec)
        assert result["source"]["document"] == "AWS-D1.1.pdf"
        assert result["source"]["section"] == "6.5"
        assert result["source"]["page"] == 120

    def test_domain_preserved(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        rec = _make_record(
            "Procedure: Drilling Mud Check\n1. Sample mud weight",
            domain="drilling",
        )
        result = _parse_procedure(rec)
        assert result["domain"] == "drilling"


# -- YAML rendering ----------------------------------------------------------


class TestRenderYaml:
    """Verify rendered YAML skill file format."""

    def _get_parsed(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _parse_procedure,
        )

        records = _read_fixture_records()
        return _parse_procedure(records[0])

    def test_yaml_is_valid(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        # Split on --- delimiters to get frontmatter and body
        parts = output.split("---")
        # parts[0] is empty (before first ---), parts[1] is frontmatter,
        # parts[2] is body
        assert len(parts) >= 3
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter is not None
        body = yaml.safe_load(parts[2])
        assert body is not None

    def test_content_hash_in_frontmatter(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        parts = output.split("---")
        frontmatter = yaml.safe_load(parts[1])
        assert "content_hash" in frontmatter
        assert len(frontmatter["content_hash"]) == 64

    def test_source_citation_in_frontmatter(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        parts = output.split("---")
        frontmatter = yaml.safe_load(parts[1])
        assert "DNV-RP-B401.pdf" in frontmatter["source"]
        assert "8.2" in frontmatter["source"]

    def test_name_is_kebab_case(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        parts = output.split("---")
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["name"] == "cathodic-protection-survey"

    def test_type_is_procedure(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        parts = output.split("---")
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["type"] == "procedure"

    def test_steps_in_body(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        parts = output.split("---")
        body = yaml.safe_load(parts[2])
        assert "steps" in body
        assert len(body["steps"]) == 5
        assert body["steps"][0] == "Verify reference electrode calibration"

    def test_domain_in_frontmatter(self):
        from scripts.data.doc_intelligence.promoters.procedures import (
            _render_yaml,
        )

        parsed = self._get_parsed()
        output = _render_yaml(parsed)
        parts = output.split("---")
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["domain"] == "naval-architecture"


# -- promote_procedures integration ------------------------------------------


class TestPromoteProcedures:
    """Integration tests for the full promote_procedures function."""

    def test_writes_output_file(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        records = _read_fixture_records()
        result = promote_procedures(records, tmp_dir)
        assert isinstance(result, PromoteResult)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0
        out_path = Path(result.files_written[0])
        assert out_path.exists()
        content = out_path.read_text()
        assert "cathodic-protection-survey" in content

    def test_output_path_correct(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        records = _read_fixture_records()
        result = promote_procedures(records, tmp_dir)
        out_path = Path(result.files_written[0])
        expected = (
            tmp_dir
            / ".claude"
            / "skills"
            / "engineering"
            / "naval-architecture"
            / "cathodic_protection_survey.yaml"
        )
        assert out_path == expected

    def test_empty_records_no_output(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        result = promote_procedures([], tmp_dir)
        assert isinstance(result, PromoteResult)
        assert result.files_written == []
        assert result.files_skipped == []
        assert result.errors == []

    def test_idempotency_skips_on_second_call(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        records = _read_fixture_records()
        result1 = promote_procedures(records, tmp_dir)
        assert len(result1.files_written) == 1
        assert len(result1.files_skipped) == 0

        result2 = promote_procedures(records, tmp_dir)
        assert len(result2.files_written) == 0
        assert len(result2.files_skipped) == 1

    def test_dry_run_writes_nothing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        records = _read_fixture_records()
        result = promote_procedures(records, tmp_dir, dry_run=True)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0
        # File should not actually exist
        out_path = Path(result.files_written[0])
        assert not out_path.exists()

    def test_unparseable_records_skipped(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        records = [_make_record("No procedure definition here.")]
        result = promote_procedures(records, tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0

    def test_output_is_valid_yaml(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.procedures import (
            promote_procedures,
        )

        records = _read_fixture_records()
        result = promote_procedures(records, tmp_dir)
        out_path = Path(result.files_written[0])
        content = out_path.read_text()
        # Should parse without errors
        parts = content.split("---")
        frontmatter = yaml.safe_load(parts[1])
        body = yaml.safe_load(parts[2])
        assert frontmatter["type"] == "procedure"
        assert len(body["steps"]) == 5


class TestPromoteProceduresRegistration:
    """Promoter registers itself with the coordinator."""

    def test_registered_as_procedures(self):
        from scripts.data.doc_intelligence.promoters.coordinator import (
            _PROMOTER_REGISTRY,
        )

        import scripts.data.doc_intelligence.promoters.procedures  # noqa: F401

        assert "procedures" in _PROMOTER_REGISTRY
