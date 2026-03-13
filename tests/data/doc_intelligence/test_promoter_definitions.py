"""Tests for definitions promoter — glossary YAML generation."""

import json
from pathlib import Path

import pytest
import yaml

from scripts.data.doc_intelligence.promoters.definitions import (
    parse_definition,
    promote_definitions,
    render_glossary_yaml,
)
from scripts.data.doc_intelligence.promoters.coordinator import PromoteResult

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


# ── parse_definition ───────────────────────────────────────────────────


class TestParseDefinition:
    def test_splits_term_and_definition(self):
        term, defn = parse_definition(
            "Cathodic Protection (CP): A technique used to control corrosion."
        )
        assert term == "Cathodic Protection (CP)"
        assert defn == "A technique used to control corrosion."

    def test_splits_on_first_colon_only(self):
        term, defn = parse_definition("Ratio: 1:2 mix of components")
        assert term == "Ratio"
        assert defn == "1:2 mix of components"

    def test_strips_whitespace(self):
        term, defn = parse_definition("  Term  :  Some definition  ")
        assert term == "Term"
        assert defn == "Some definition"

    def test_no_colon_returns_full_text_as_term(self):
        term, defn = parse_definition("No colon here")
        assert term == "No colon here"
        assert defn == ""

    def test_empty_string(self):
        term, defn = parse_definition("")
        assert term == ""
        assert defn == ""


# ── render_glossary_yaml ───────────────────────────────────────────────


class TestRenderGlossaryYaml:
    def _make_records(self):
        return [
            {
                "text": "Cathodic Protection (CP): A technique to control corrosion.",
                "source": {"document": "DNV-RP-B401.pdf", "section": "1.3", "page": 5},
                "domain": "naval-architecture",
            },
            {
                "text": "Sacrificial Anode: An anode for galvanic protection.",
                "source": {"document": "DNV-RP-B401.pdf", "section": "1.3", "page": 5},
                "domain": "naval-architecture",
            },
        ]

    def test_output_is_valid_yaml(self):
        content = render_glossary_yaml(self._make_records(), "naval-architecture")
        parsed = yaml.safe_load(content)
        assert "terms" in parsed

    def test_terms_count(self):
        content = render_glossary_yaml(self._make_records(), "naval-architecture")
        parsed = yaml.safe_load(content)
        assert len(parsed["terms"]) == 2

    def test_term_fields(self):
        content = render_glossary_yaml(self._make_records(), "naval-architecture")
        parsed = yaml.safe_load(content)
        first = parsed["terms"][0]
        assert first["term"] == "Cathodic Protection (CP)"
        assert "corrosion" in first["definition"]
        assert first["source"] == "DNV-RP-B401.pdf §1.3 p.5"

    def test_content_hash_header_present(self):
        content = render_glossary_yaml(self._make_records(), "naval-architecture")
        assert "# content_hash:" in content

    def test_domain_in_header(self):
        content = render_glossary_yaml(self._make_records(), "naval-architecture")
        assert "# Glossary — naval-architecture" in content

    def test_do_not_edit_warning(self):
        content = render_glossary_yaml(self._make_records(), "naval-architecture")
        assert "Do not edit manually" in content


# ── promote_definitions ────────────────────────────────────────────────


class TestPromoteDefinitions:
    def _load_fixture_records(self):
        records = []
        with open(FIXTURES / "definitions.jsonl", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def test_writes_glossary_file(self, tmp_dir):
        records = self._load_fixture_records()
        result = promote_definitions(records, tmp_dir)
        assert isinstance(result, PromoteResult)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0

    def test_output_path_correct(self, tmp_dir):
        records = self._load_fixture_records()
        promote_definitions(records, tmp_dir)
        expected = tmp_dir / "data" / "standards" / "promoted" / "naval-architecture" / "glossary.yaml"
        assert expected.exists()

    def test_output_is_valid_yaml(self, tmp_dir):
        records = self._load_fixture_records()
        promote_definitions(records, tmp_dir)
        out = tmp_dir / "data" / "standards" / "promoted" / "naval-architecture" / "glossary.yaml"
        parsed = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert len(parsed["terms"]) == 2

    def test_source_citations(self, tmp_dir):
        records = self._load_fixture_records()
        promote_definitions(records, tmp_dir)
        out = tmp_dir / "data" / "standards" / "promoted" / "naval-architecture" / "glossary.yaml"
        parsed = yaml.safe_load(out.read_text(encoding="utf-8"))
        for entry in parsed["terms"]:
            assert "DNV-RP-B401.pdf" in entry["source"]

    def test_empty_records_no_output(self, tmp_dir):
        result = promote_definitions([], tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0
        created = list(tmp_dir.rglob("*.yaml"))
        assert len(created) == 0

    def test_idempotency(self, tmp_dir):
        records = self._load_fixture_records()
        result1 = promote_definitions(records, tmp_dir)
        result2 = promote_definitions(records, tmp_dir)
        assert len(result1.files_written) == 1
        assert len(result2.files_skipped) == 1
        assert len(result2.files_written) == 0

    def test_dry_run_no_files(self, tmp_dir):
        records = self._load_fixture_records()
        result = promote_definitions(records, tmp_dir, dry_run=True)
        assert len(result.files_written) == 1
        created = list(tmp_dir.rglob("*.yaml"))
        assert len(created) == 0

    def test_multiple_domains(self, tmp_dir):
        records = [
            {
                "text": "Term A: Definition A.",
                "source": {"document": "doc1.pdf", "section": "1", "page": 1},
                "domain": "domain-one",
            },
            {
                "text": "Term B: Definition B.",
                "source": {"document": "doc2.pdf", "section": "2", "page": 2},
                "domain": "domain-two",
            },
        ]
        result = promote_definitions(records, tmp_dir)
        assert len(result.files_written) == 2
        assert (tmp_dir / "data" / "standards" / "promoted" / "domain-one" / "glossary.yaml").exists()
        assert (tmp_dir / "data" / "standards" / "promoted" / "domain-two" / "glossary.yaml").exists()

    def test_record_without_colon_still_included(self, tmp_dir):
        records = [
            {
                "text": "Standalone term without colon",
                "source": {"document": "doc.pdf"},
                "domain": "misc",
            },
        ]
        result = promote_definitions(records, tmp_dir)
        out = tmp_dir / "data" / "standards" / "promoted" / "misc" / "glossary.yaml"
        parsed = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert parsed["terms"][0]["term"] == "Standalone term without colon"
        assert parsed["terms"][0]["definition"] == ""
