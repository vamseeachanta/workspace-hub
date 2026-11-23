"""Tests for query.py — query federated content indexes."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.query import (
    format_full,
    format_stage2_brief,
    query_indexes,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def index_dir(tmp_dir):
    """Build a small set of JSONL indexes for query testing."""
    # Section-type indexes (constants, equations, etc.)
    constants = [
        {
            "text": "GM = 1.5 m (metacentric height)",
            "source": {"document": "stability.pdf", "page": 3},
            "domain": "naval-architecture",
            "manifest": "stability.pdf",
        },
        {
            "text": "rho_sw = 1025 kg/m3 (seawater density)",
            "source": {"document": "hydro.pdf", "page": 1},
            "domain": "hydrodynamics",
            "manifest": "hydro.pdf",
        },
    ]
    equations = [
        {
            "text": "R_T = 0.5 * rho * V^2 * S * C_T",
            "source": {"document": "resistance.pdf", "page": 10},
            "domain": "naval-architecture",
            "manifest": "resistance.pdf",
        },
    ]
    requirements = [
        {
            "text": "The vessel shall maintain positive stability in all loading conditions",
            "source": {"document": "rules.pdf", "section": "3.1"},
            "domain": "naval-architecture",
            "manifest": "rules.pdf",
        },
    ]
    procedures = [
        {
            "text": "Step 1: Calculate displacement. Step 2: Verify trim.",
            "source": {"document": "ops.pdf", "page": 5},
            "domain": "operations",
            "manifest": "ops.pdf",
        },
    ]
    definitions = [
        {
            "text": "Freeboard means the distance from the waterline to the deck edge",
            "source": {"document": "glossary.pdf", "page": 1},
            "domain": "naval-architecture",
            "manifest": "glossary.pdf",
        },
    ]
    worked_examples = [
        {
            "text": "Example: Given OD = 12 inch, calculate section modulus",
            "source": {"document": "calcs.pdf", "page": 7},
            "domain": "structural",
            "manifest": "calcs.pdf",
        },
    ]

    # Tables index (different schema)
    tables = [
        {
            "title": "Resistance coefficients",
            "columns": ["Speed", "Ct", "Cf"],
            "row_count": 10,
            "csv_path": "tables/resistance-table-0.csv",
            "source": {"document": "resistance.pdf", "page": 12},
            "domain": "naval-architecture",
            "manifest": "resistance.pdf",
        },
        {
            "title": "Material properties",
            "columns": ["Grade", "Yield", "UTS"],
            "row_count": 5,
            "csv_path": "tables/materials-table-0.csv",
            "source": {"document": "materials.pdf", "page": 2},
            "domain": "structural",
            "manifest": "materials.pdf",
        },
    ]

    # Curves index (different schema)
    curves = [
        {
            "caption": "Speed-power curve",
            "figure_id": "Fig-3.1",
            "source": {"document": "resistance.pdf", "page": 15},
            "domain": "naval-architecture",
            "manifest": "resistance.pdf",
        },
    ]

    def _write(name, records):
        path = tmp_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    _write("constants.jsonl", constants)
    _write("equations.jsonl", equations)
    _write("requirements.jsonl", requirements)
    _write("procedures.jsonl", procedures)
    _write("definitions.jsonl", definitions)
    _write("worked_examples.jsonl", worked_examples)
    _write("tables/index.jsonl", tables)
    _write("curves/index.jsonl", curves)

    return tmp_dir


@pytest.fixture
def empty_index_dir(tmp_dir):
    """Index directory with all-empty JSONL files."""
    for name in [
        "constants.jsonl", "equations.jsonl", "requirements.jsonl",
        "procedures.jsonl", "definitions.jsonl", "worked_examples.jsonl",
    ]:
        (tmp_dir / name).write_text("")
    (tmp_dir / "tables").mkdir()
    (tmp_dir / "tables" / "index.jsonl").write_text("")
    (tmp_dir / "curves").mkdir()
    (tmp_dir / "curves" / "index.jsonl").write_text("")
    return tmp_dir


# --- query_indexes: content type filtering ---


class TestQueryByType:
    def test_query_constants(self, index_dir):
        results = query_indexes(index_dir, content_type="constants")
        assert len(results) == 2
        assert all(r["_content_type"] == "constants" for r in results)

    def test_query_equations(self, index_dir):
        results = query_indexes(index_dir, content_type="equations")
        assert len(results) == 1
        assert "R_T" in results[0]["text"]

    def test_query_tables(self, index_dir):
        results = query_indexes(index_dir, content_type="tables")
        assert len(results) == 2
        assert "title" in results[0]

    def test_query_curves(self, index_dir):
        results = query_indexes(index_dir, content_type="curves")
        assert len(results) == 1
        assert results[0]["figure_id"] == "Fig-3.1"

    def test_query_all_types(self, index_dir):
        results = query_indexes(index_dir)
        # 2 constants + 1 eq + 1 req + 1 proc + 1 def + 1 worked + 2 tables + 1 curve = 10
        assert len(results) == 10


# --- query_indexes: domain filtering ---


class TestQueryByDomain:
    def test_domain_filter(self, index_dir):
        results = query_indexes(index_dir, domain="naval-architecture")
        domains = {r["domain"] for r in results}
        assert domains == {"naval-architecture"}
        # 1 constant + 1 eq + 1 req + 1 def + 1 table + 1 curve = 6
        assert len(results) == 6

    def test_domain_no_match(self, index_dir):
        results = query_indexes(index_dir, domain="nonexistent")
        assert results == []


# --- query_indexes: keyword filtering ---


class TestQueryByKeyword:
    def test_keyword_case_insensitive(self, index_dir):
        results = query_indexes(index_dir, keyword="SEAWATER")
        assert len(results) == 1
        assert "seawater" in results[0]["text"].lower()

    def test_keyword_in_title(self, index_dir):
        """Keyword should match table title field too."""
        results = query_indexes(index_dir, keyword="resistance")
        assert len(results) >= 1
        assert any(r.get("title") == "Resistance coefficients" for r in results)

    def test_keyword_no_match(self, index_dir):
        results = query_indexes(index_dir, keyword="zzz_no_match_zzz")
        assert results == []


# --- query_indexes: combined filters ---


class TestCombinedFilters:
    def test_type_and_domain(self, index_dir):
        results = query_indexes(
            index_dir, content_type="constants", domain="naval-architecture"
        )
        assert len(results) == 1
        assert "GM" in results[0]["text"]

    def test_type_and_keyword(self, index_dir):
        results = query_indexes(
            index_dir, content_type="tables", keyword="resistance"
        )
        assert len(results) == 1
        assert results[0]["title"] == "Resistance coefficients"

    def test_all_three_filters(self, index_dir):
        results = query_indexes(
            index_dir,
            content_type="constants",
            domain="naval-architecture",
            keyword="metacentric",
        )
        assert len(results) == 1


# --- query_indexes: limit ---


class TestLimit:
    def test_limit_restricts_results(self, index_dir):
        results = query_indexes(index_dir, limit=3)
        assert len(results) == 3

    def test_limit_default_large_enough(self, index_dir):
        results = query_indexes(index_dir, limit=20)
        assert len(results) == 10  # all records


# --- query_indexes: empty/missing indexes ---


class TestEmptyIndexes:
    def test_empty_index_files(self, empty_index_dir):
        results = query_indexes(empty_index_dir)
        assert results == []

    def test_missing_index_dir(self, tmp_dir):
        results = query_indexes(tmp_dir / "nonexistent")
        assert results == []


# --- query_indexes: malformed JSONL ---


class TestMalformedJsonl:
    def test_skips_bad_lines(self, tmp_dir):
        """Malformed JSON lines are skipped, valid lines still returned."""
        (tmp_dir / "constants.jsonl").write_text(
            '{"text":"valid","source":{},"domain":"d","manifest":"m"}\n'
            "NOT JSON\n"
            '{"text":"also valid","source":{},"domain":"d","manifest":"m"}\n'
        )
        results = query_indexes(tmp_dir, content_type="constants")
        assert len(results) == 2


# --- format_stage2_brief ---


class TestFormatStage2Brief:
    def test_brief_output_non_empty(self, index_dir):
        results = query_indexes(index_dir, domain="naval-architecture")
        brief = format_stage2_brief(results, "naval-architecture")
        assert isinstance(brief, str)
        assert len(brief) > 0

    def test_brief_contains_counts(self, index_dir):
        results = query_indexes(index_dir, domain="naval-architecture")
        brief = format_stage2_brief(results, "naval-architecture")
        # Should mention content types found
        assert "constants" in brief.lower() or "table" in brief.lower()

    def test_brief_empty_results(self):
        brief = format_stage2_brief([], "test-domain")
        assert "no" in brief.lower() or brief == ""


# --- format_full ---


class TestFormatFull:
    def test_full_output_contains_source(self, index_dir):
        results = query_indexes(index_dir, content_type="constants")
        full = format_full(results)
        assert "stability.pdf" in full

    def test_full_output_empty(self):
        full = format_full([])
        assert isinstance(full, str)
