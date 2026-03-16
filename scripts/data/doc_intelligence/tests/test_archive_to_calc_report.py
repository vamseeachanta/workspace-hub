"""TDD tests for archive-to-calc-report converter (WRK-1247)."""

import pytest
import yaml

from scripts.data.doc_intelligence.archive_to_calc_report import (
    convert_archive_to_calc_report,
    excel_formula_to_latex,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

MINIMAL_ARCHIVE = {
    "source_type": "excel",
    "source_description": "Engineering calculation spreadsheet (wellhead domain)",
    "extracted_date": "2026-03-16",
    "legal_scan_passed": False,
    "category": "wellhead",
    "subcategory": "surface-wellhead-sitp-calculations",
    "equations": [
        {
            "name": "D17",
            "excel_formula": "=D16*0.3048",
            "latex": "",
            "description": "Cell D17 in Sheet1",
        },
        {
            "name": "C46",
            "excel_formula": "=(-(D18*D19*D17+D15)*2)/D18",
            "latex": "",
            "description": "Cell C46 in Sheet1",
        },
    ],
    "inputs": [
        {"name": "D16", "symbol": "D16", "unit": "ft", "test_value": 100.0},
        {"name": "D18", "symbol": "D18", "unit": "psi", "test_value": 5000.0},
    ],
    "outputs": [
        {
            "name": "C46",
            "symbol": "C46",
            "unit": "",
            "test_expected": 42.5,
            "tolerance": 1e-6,
        },
    ],
    "worked_examples": [],
    "assumptions": ["Assumes ideal gas"],
    "references": ["API RP 90"],
    "notes": "Auto-extracted by WRK-1247 POC.",
}

EMPTY_ARCHIVE = {
    "source_type": "excel",
    "source_description": "Spreadsheet with no formulas",
    "extracted_date": "2026-03-16",
    "legal_scan_passed": False,
    "category": "cad",
    "subcategory": "flow-rate-calculation",
    "equations": [],
    "inputs": [],
    "outputs": [],
    "worked_examples": [],
    "assumptions": [],
    "references": [],
    "notes": "No formulas found.",
}

ARCHIVE_NO_INPUTS = {
    "source_type": "excel",
    "source_description": "Spreadsheet with equations but no inputs extracted",
    "extracted_date": "2026-03-16",
    "legal_scan_passed": False,
    "category": "energy-economics",
    "subcategory": "sitp-calculations",
    "equations": [
        {
            "name": "D17",
            "excel_formula": "=D16*0.3048",
            "latex": "",
            "description": "Cell D17 in Sheet1",
        },
    ],
    "inputs": [],
    "outputs": [
        {
            "name": "C47",
            "symbol": "C47",
            "unit": "",
            "test_expected": "#NUM!",
            "tolerance": 1e-6,
        },
    ],
    "worked_examples": [],
    "assumptions": [],
    "references": [],
    "notes": "Auto-extracted.",
}


# ── Required sections ─────────────────────────────────────────────────────

class TestRequiredSections:
    """Calc-report schema mandates: metadata, inputs, methodology, outputs,
    assumptions, references."""

    def test_all_required_sections_present(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        for section in ["metadata", "inputs", "methodology", "outputs",
                        "assumptions", "references"]:
            assert section in result, f"Missing required section: {section}"

    def test_metadata_has_required_fields(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        meta = result["metadata"]
        for field in ["title", "doc_id", "revision", "date", "author", "status"]:
            assert field in meta, f"Missing metadata field: {field}"

    def test_metadata_status_is_draft(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        assert result["metadata"]["status"] == "draft"

    def test_metadata_title_from_subcategory(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        assert "surface-wellhead-sitp-calculations" in result["metadata"]["title"].lower().replace(" ", "-")

    def test_metadata_doc_id_generated(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        assert result["metadata"]["doc_id"].startswith("XLSX-")


# ── Inputs mapping ────────────────────────────────────────────────────────

class TestInputsMapping:
    """Archive inputs (name, symbol, unit, test_value) → calc-report inputs
    (name, symbol, value, unit)."""

    def test_inputs_mapped_correctly(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        inputs = result["inputs"]
        assert len(inputs) == 2
        assert inputs[0]["name"] == "D16"
        assert inputs[0]["symbol"] == "D16"
        assert inputs[0]["value"] == 100.0
        assert inputs[0]["unit"] == "ft"

    def test_empty_inputs_get_placeholder(self):
        """When archive has no inputs, provide a placeholder so schema validates."""
        result = convert_archive_to_calc_report(ARCHIVE_NO_INPUTS)
        inputs = result["inputs"]
        assert len(inputs) >= 1
        assert inputs[0]["name"] == "No inputs extracted"

    def test_test_value_mapped_to_value(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        for inp in result["inputs"]:
            assert "value" in inp
            assert "test_value" not in inp


# ── Methodology mapping ───────────────────────────────────────────────────

class TestMethodologyMapping:
    """Archive equations → methodology.equations with id, name, latex, description."""

    def test_methodology_has_standard(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        assert "standard" in result["methodology"]

    def test_methodology_has_equations(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        eqs = result["methodology"]["equations"]
        assert len(eqs) == 2

    def test_equations_have_required_fields(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        for eq in result["methodology"]["equations"]:
            for field in ["id", "name", "latex", "description"]:
                assert field in eq, f"Equation missing: {field}"

    def test_equations_get_sequential_ids(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        ids = [eq["id"] for eq in result["methodology"]["equations"]]
        assert ids == ["eq1", "eq2"]

    def test_latex_generated_from_excel_formula(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        eq1 = result["methodology"]["equations"][0]
        assert eq1["latex"], "LaTeX should not be empty"

    def test_empty_equations_get_placeholder(self):
        result = convert_archive_to_calc_report(EMPTY_ARCHIVE)
        eqs = result["methodology"]["equations"]
        assert len(eqs) >= 1


# ── Outputs mapping ───────────────────────────────────────────────────────

class TestOutputsMapping:
    """Archive outputs (test_expected) → calc-report outputs (value)."""

    def test_outputs_mapped(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        outputs = result["outputs"]
        assert len(outputs) == 1
        assert outputs[0]["value"] == 42.5

    def test_outputs_have_required_fields(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        for out in result["outputs"]:
            for field in ["name", "symbol", "value", "unit"]:
                assert field in out

    def test_error_outputs_excluded(self):
        """Outputs with Excel error values (#NUM!, #REF!) should be excluded."""
        result = convert_archive_to_calc_report(ARCHIVE_NO_INPUTS)
        outputs = result["outputs"]
        for out in outputs:
            val = out["value"]
            if isinstance(val, str):
                assert not val.startswith("#")

    def test_empty_outputs_get_placeholder(self):
        result = convert_archive_to_calc_report(EMPTY_ARCHIVE)
        outputs = result["outputs"]
        assert len(outputs) >= 1


# ── Assumptions & References ──────────────────────────────────────────────

class TestAssumptionsReferences:

    def test_assumptions_passed_through(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        assert result["assumptions"] == ["Assumes ideal gas"]

    def test_references_passed_through(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        assert result["references"] == ["API RP 90"]

    def test_empty_assumptions_get_placeholder(self):
        result = convert_archive_to_calc_report(EMPTY_ARCHIVE)
        assert len(result["assumptions"]) >= 1

    def test_empty_references_get_placeholder(self):
        result = convert_archive_to_calc_report(EMPTY_ARCHIVE)
        assert len(result["references"]) >= 1


# ── Excel formula to LaTeX ────────────────────────────────────────────────

class TestExcelFormulaToLatex:
    """Basic Excel formula → LaTeX conversion."""

    def test_simple_multiply(self):
        result = excel_formula_to_latex("=A1*B1")
        assert "\\times" in result or "\\cdot" in result or "*" not in result

    def test_division(self):
        result = excel_formula_to_latex("=A1/B1")
        assert "\\frac" in result or "/" in result

    def test_sqrt(self):
        result = excel_formula_to_latex("=SQRT(C46)")
        assert "\\sqrt" in result

    def test_power(self):
        result = excel_formula_to_latex("=A1^2")
        assert "^" in result

    def test_constant_multiply(self):
        result = excel_formula_to_latex("=D16*0.3048")
        assert "0.3048" in result

    def test_empty_formula(self):
        result = excel_formula_to_latex("")
        assert result == ""

    def test_no_equals_prefix(self):
        result = excel_formula_to_latex("A1+B1")
        assert result  # should still work without leading =


# ── YAML serialization roundtrip ──────────────────────────────────────────

class TestYamlRoundtrip:

    def test_output_is_valid_yaml(self):
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        dumped = yaml.dump(result, default_flow_style=False)
        reloaded = yaml.safe_load(dumped)
        assert reloaded["metadata"]["title"] == result["metadata"]["title"]

    def test_output_validates_against_schema(self):
        """Verify required sections and fields pass the calc-report validation."""
        result = convert_archive_to_calc_report(MINIMAL_ARCHIVE)
        # Inline validation matching generate-calc-report.py load_and_validate
        for s in ["metadata", "inputs", "methodology", "outputs",
                   "assumptions", "references"]:
            assert s in result, f"Missing: {s}"
        for f in ["title", "doc_id", "revision", "date", "author", "status"]:
            assert f in result["metadata"], f"Missing metadata.{f}"
        assert "standard" in result["methodology"]
        assert "equations" in result["methodology"]
        for eq in result["methodology"]["equations"]:
            assert "name" in eq and "latex" in eq
