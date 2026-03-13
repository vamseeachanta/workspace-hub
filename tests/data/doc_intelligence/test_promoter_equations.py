"""Tests for equation promoter — parsing, rendering, and promotion."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.equations import (
    ParsedEquation,
    ParsedParam,
    _parse_params,
    parse_equation,
    promote_equations,
    render_function,
    render_module,
)
from scripts.data.doc_intelligence.promoters.coordinator import PromoteResult

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _load_fixture_records() -> list[dict]:
    """Load equations.jsonl fixture records."""
    records = []
    with open(FIXTURES / "equations.jsonl", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ── Parsing ────────────────────────────────────────────────────────────


class TestParseParams:
    def test_single_param(self):
        params = _parse_params("rho is fluid density [kg/m³]")
        assert len(params) == 1
        assert params[0].name == "rho"
        assert params[0].description == "fluid density"
        assert params[0].unit == "kg/m³"

    def test_multiple_params(self):
        clause = (
            "rho is fluid density [kg/m³], "
            "g is gravitational acceleration [m/s²], "
            "d is depth [m]"
        )
        params = _parse_params(clause)
        assert len(params) == 3
        assert params[2].name == "d"
        assert params[2].unit == "m"

    def test_empty_clause(self):
        assert _parse_params("") == []

    def test_malformed_no_unit(self):
        assert _parse_params("x is some thing") == []


class TestParseEquation:
    def test_hydrostatic_pressure(self):
        records = _load_fixture_records()
        eq = parse_equation(records[0])
        assert eq is not None
        assert eq.function_name == "hydrostatic_pressure"
        assert eq.display_name == "Hydrostatic pressure"
        assert "rho * g * d" in eq.formula
        assert len(eq.params) == 3
        assert eq.params[0].name == "rho"
        assert eq.return_unit == "Pa"
        assert eq.domain == "naval-architecture"

    def test_buoyancy_force(self):
        records = _load_fixture_records()
        eq = parse_equation(records[1])
        assert eq is not None
        assert eq.function_name == "buoyancy_force"
        assert len(eq.params) == 3
        assert eq.params[2].name == "V"
        assert eq.return_unit == "N"

    def test_citation_included(self):
        records = _load_fixture_records()
        eq = parse_equation(records[0])
        assert eq is not None
        assert "DNV-RP-C205.pdf" in eq.citation
        assert "§3.2.1" in eq.citation
        assert "p.15" in eq.citation

    def test_missing_colon_returns_none(self):
        assert parse_equation({"text": "no colon here"}) is None

    def test_missing_where_returns_none(self):
        assert parse_equation({"text": "Name: P = rho * g"}) is None

    def test_missing_returns_clause(self):
        text = "Name: P = rho * g, where rho is density [kg/m³]."
        assert parse_equation({"text": text}) is None

    def test_empty_text_returns_none(self):
        assert parse_equation({"text": ""}) is None
        assert parse_equation({}) is None


# ── Rendering ──────────────────────────────────────────────────────────


class TestRenderFunction:
    def _make_eq(self) -> ParsedEquation:
        return ParsedEquation(
            function_name="hydrostatic_pressure",
            display_name="Hydrostatic pressure",
            formula="P = rho * g * d",
            params=[
                ParsedParam("rho", "fluid density", "kg/m³"),
                ParsedParam("g", "gravitational acceleration", "m/s²"),
                ParsedParam("d", "depth", "m"),
            ],
            return_description="pressure",
            return_unit="Pa",
            citation="DNV-RP-C205.pdf §3.2.1 p.15",
            domain="naval-architecture",
        )

    def test_function_signature(self):
        code = render_function(self._make_eq())
        assert "def hydrostatic_pressure(rho: float, g: float, d: float) -> float:" in code

    def test_docstring_contains_citation(self):
        code = render_function(self._make_eq())
        assert "DNV-RP-C205.pdf §3.2.1 p.15" in code

    def test_docstring_contains_formula(self):
        code = render_function(self._make_eq())
        assert "P = rho * g * d" in code

    def test_parameters_section(self):
        code = render_function(self._make_eq())
        assert "Parameters" in code
        assert "rho : float" in code
        assert "fluid density [kg/m³]." in code

    def test_returns_section(self):
        code = render_function(self._make_eq())
        assert "Returns" in code
        assert "Pressure [Pa]." in code

    def test_body_expression(self):
        code = render_function(self._make_eq())
        assert "return rho * g * d" in code

    def test_valid_python(self):
        code = render_function(self._make_eq())
        compile(code, "<test>", "exec")


class TestRenderModule:
    def _make_eqs(self) -> list[ParsedEquation]:
        return [
            ParsedEquation(
                function_name="hydrostatic_pressure",
                display_name="Hydrostatic pressure",
                formula="P = rho * g * d",
                params=[
                    ParsedParam("rho", "fluid density", "kg/m³"),
                    ParsedParam("g", "gravitational acceleration", "m/s²"),
                    ParsedParam("d", "depth", "m"),
                ],
                return_description="pressure",
                return_unit="Pa",
                citation="DNV-RP-C205.pdf §3.2.1 p.15",
                domain="naval-architecture",
            ),
            ParsedEquation(
                function_name="buoyancy_force",
                display_name="Buoyancy force",
                formula="F_b = rho * g * V",
                params=[
                    ParsedParam("rho", "fluid density", "kg/m³"),
                    ParsedParam("g", "gravitational acceleration", "m/s²"),
                    ParsedParam("V", "displaced volume", "m³"),
                ],
                return_description="force",
                return_unit="N",
                citation="DNV-RP-C205.pdf §3.2.2 p.16",
                domain="naval-architecture",
            ),
        ]

    def test_content_hash_in_header(self):
        module = render_module(self._make_eqs(), "naval-architecture")
        assert "# content-hash:" in module
        # Hash is 64 hex chars
        import re
        m = re.search(r"# content-hash: ([0-9a-f]{64})", module)
        assert m is not None

    def test_domain_label_in_docstring(self):
        module = render_module(self._make_eqs(), "naval-architecture")
        assert "Naval Architecture Equations" in module

    def test_auto_promoted_tag(self):
        module = render_module(self._make_eqs(), "naval-architecture")
        assert "auto-promoted from doc-intelligence" in module

    def test_both_functions_present(self):
        module = render_module(self._make_eqs(), "naval-architecture")
        assert "def hydrostatic_pressure(" in module
        assert "def buoyancy_force(" in module

    def test_valid_python(self):
        module = render_module(self._make_eqs(), "naval-architecture")
        compile(module, "<test>", "exec")


# ── Promotion (integration) ───────────────────────────────────────────


class TestPromoteEquations:
    def test_writes_module_file(self, tmp_dir):
        records = _load_fixture_records()
        result = promote_equations(records, tmp_dir)
        assert isinstance(result, PromoteResult)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0
        # Verify the file exists
        out = (
            tmp_dir / "digitalmodel" / "src" / "digitalmodel"
            / "naval_architecture" / "equations.py"
        )
        assert out.exists()

    def test_output_is_valid_python(self, tmp_dir):
        records = _load_fixture_records()
        promote_equations(records, tmp_dir)
        out = (
            tmp_dir / "digitalmodel" / "src" / "digitalmodel"
            / "naval_architecture" / "equations.py"
        )
        code = out.read_text(encoding="utf-8")
        compile(code, str(out), "exec")

    def test_output_contains_functions(self, tmp_dir):
        records = _load_fixture_records()
        promote_equations(records, tmp_dir)
        out = (
            tmp_dir / "digitalmodel" / "src" / "digitalmodel"
            / "naval_architecture" / "equations.py"
        )
        code = out.read_text(encoding="utf-8")
        assert "def hydrostatic_pressure(" in code
        assert "def buoyancy_force(" in code

    def test_content_hash_present(self, tmp_dir):
        records = _load_fixture_records()
        promote_equations(records, tmp_dir)
        out = (
            tmp_dir / "digitalmodel" / "src" / "digitalmodel"
            / "naval_architecture" / "equations.py"
        )
        code = out.read_text(encoding="utf-8")
        assert "# content-hash:" in code

    def test_source_citations(self, tmp_dir):
        records = _load_fixture_records()
        promote_equations(records, tmp_dir)
        out = (
            tmp_dir / "digitalmodel" / "src" / "digitalmodel"
            / "naval_architecture" / "equations.py"
        )
        code = out.read_text(encoding="utf-8")
        assert "DNV-RP-C205.pdf §3.2.1 p.15" in code
        assert "DNV-RP-C205.pdf §3.2.2 p.16" in code

    def test_empty_records_no_output(self, tmp_dir):
        result = promote_equations([], tmp_dir)
        assert result.files_written == []
        assert result.files_skipped == []
        assert result.errors == []

    def test_idempotency(self, tmp_dir):
        records = _load_fixture_records()
        result1 = promote_equations(records, tmp_dir)
        assert len(result1.files_written) == 1
        # Second run — same content, should skip
        result2 = promote_equations(records, tmp_dir)
        assert len(result2.files_written) == 0
        assert len(result2.files_skipped) == 1

    def test_dry_run_no_files(self, tmp_dir):
        records = _load_fixture_records()
        result = promote_equations(records, tmp_dir, dry_run=True)
        assert len(result.files_written) == 1  # reported as "would write"
        assert len(result.errors) == 0
        # But no file actually created
        out = (
            tmp_dir / "digitalmodel" / "src" / "digitalmodel"
            / "naval_architecture" / "equations.py"
        )
        assert not out.exists()

    def test_unparseable_record_logged_as_error(self, tmp_dir):
        records = [{"text": "no colon or structure here"}]
        result = promote_equations(records, tmp_dir)
        assert len(result.errors) == 1
        assert "Failed to parse" in result.errors[0]
