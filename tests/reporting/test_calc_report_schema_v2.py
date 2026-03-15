"""TDD tests for calculation report schema v2 — new optional sections.

Tests cover: backwards compatibility, new section validation,
HTML builders for v2 sections, and integration rendering.
Run: uv run --no-project python -m pytest tests/reporting/ -v
"""
import pytest

from conftest import REPO_ROOT


# ── v2 fixture ────────────────────────────────────────────────────────────

@pytest.fixture
def v2_scope():
    """Scope section with realistic engineering content."""
    return {
        "objective": "Assess fatigue life of pipeline girth weld at KP 12.4",
        "inclusions": [
            "Fatigue damage from wave-induced loading",
            "Vortex-induced vibration contribution",
        ],
        "exclusions": [
            "Corrosion fatigue interaction",
            "Installation loads",
        ],
        "limitations": "Valid for water depths 50-200 m only",
        "validity_range": "Design life 25 years, seawater environment",
    }


@pytest.fixture
def v2_design_basis():
    """Design basis section with codes and parameters."""
    return {
        "codes": [
            {"code": "DNV-RP-C203", "edition": "2021", "clause": "Section 2"},
            {"code": "DNV-ST-F101", "edition": "2021", "clause": "Section 5"},
        ],
        "design_life": 25,
        "safety_class": "high",
        "load_combinations": [
            "ULS: 1.3G + 1.5Q",
            "FLS: 1.0G + 1.0E (10^-2 annual probability)",
        ],
        "environment": "North Sea, 120 m water depth",
    }


@pytest.fixture
def v2_materials():
    """Materials section with pipeline steel properties."""
    return [
        {
            "name": "Pipe Steel",
            "grade": "X65",
            "value": 450,
            "unit": "MPa",
            "source": "DNV-ST-F101 Table 5-2",
            "partial_factor": 1.15,
            "certificate": "MTR-2026-001",
        },
        {
            "name": "Weld Metal",
            "grade": "E71T-1",
            "value": 480,
            "unit": "MPa",
            "source": "AWS D1.1",
        },
    ]


@pytest.fixture
def v2_calculations():
    """Calculations section with numbered steps."""
    return [
        {
            "step": 1,
            "description": "Calculate hot-spot stress range",
            "detail": "SCF = 1.2 applied to nominal stress from FEA",
            "code_clause": "DNV-RP-C203 Eq. 2.3.1",
            "intermediate_results": [
                {"name": "SCF", "value": 1.2, "unit": "-"},
                {"name": "Hot-spot stress", "value": 145.6, "unit": "MPa"},
            ],
        },
        {
            "step": 2,
            "description": "Determine S-N curve parameters",
            "code_clause": "DNV-RP-C203 Table 2-1",
        },
        {
            "step": 3,
            "description": "Compute Miner sum",
            "detail": "Sum damage fractions across all sea states",
        },
    ]


@pytest.fixture
def v2_sensitivity():
    """Sensitivity analysis with parameter sweeps."""
    return [
        {"parameter": "Wall Thickness", "range": "19.1 - 25.4 mm", "result": "UC 0.45 - 0.82"},
        {"parameter": "SCF", "range": "1.0 - 1.5", "result": "Damage 0.12 - 0.67"},
        {"parameter": "Design Life", "range": "20 - 30 years", "result": "UC 0.52 - 0.78"},
    ]


@pytest.fixture
def v2_validation():
    """Validation section with test summary."""
    return {
        "method": "Comparison against independent spreadsheet calculation",
        "test_file": "tests/fatigue/test_girth_weld.py",
        "test_count": 14,
        "test_categories": ["stress_range", "sn_curve", "miner_sum", "unity_check"],
        "benchmark_source": "DNV-RP-C203 Example B.1",
    }


@pytest.fixture
def v2_verification():
    """Verification section with checker record."""
    return {
        "checker": "J. Smith, PE",
        "date": "2026-02-15",
        "method": "Independent hand calculation of governing load case",
        "findings": "Results within 2% of independent check. Approved.",
        "status": "approved",
    }


@pytest.fixture
def v2_conclusions():
    """Conclusions section with adequacy statement."""
    return {
        "adequacy": "The girth weld fatigue life exceeds the 25-year design requirement "
                     "with a unity check of 0.65.",
        "governing_check": "Fatigue damage at weld toe, sea state H_s = 4.5 m",
        "recommendations": [
            "Monitor weld inspection intervals per ITP-2026-003",
            "Re-assess if operating conditions change beyond validity range",
        ],
        "compliance_statement": "Calculation complies with DNV-RP-C203 (2021) and "
                                "DNV-ST-F101 (2021) for safety class HIGH.",
    }


@pytest.fixture
def v2_data(minimal_valid, v2_scope, v2_design_basis, v2_materials,
            v2_calculations, v2_sensitivity, v2_validation,
            v2_verification, v2_conclusions):
    """Full v2 data: minimal_valid extended with all new sections."""
    data = dict(minimal_valid)
    data["schema_version"] = 2
    data["scope"] = v2_scope
    data["design_basis"] = v2_design_basis
    data["materials"] = v2_materials
    data["calculations"] = v2_calculations
    data["sensitivity"] = v2_sensitivity
    data["validation"] = v2_validation
    data["verification"] = v2_verification
    data["conclusions"] = v2_conclusions
    return data


# ── Phase 1: Schema v2 Validation ────────────────────────────────────────

class TestSchemaV2Validation:
    """Validation must handle v1 backwards compat and v2 new sections."""

    def test_v1_data_still_validates(self, minimal_valid):
        """v1 data without new sections must pass validation."""
        from generate_calc_report import load_and_validate
        result = load_and_validate(minimal_valid)
        assert result["metadata"]["title"] == "Test Calc"

    def test_schema_version_defaults_to_1(self, minimal_valid):
        """When schema_version is absent, treat as v1."""
        from generate_calc_report import load_and_validate
        result = load_and_validate(minimal_valid)
        assert result.get("schema_version", 1) == 1

    def test_v2_with_scope_validates(self, minimal_valid, v2_scope):
        from generate_calc_report import load_and_validate
        minimal_valid["scope"] = v2_scope
        result = load_and_validate(minimal_valid)
        assert result["scope"]["objective"] == v2_scope["objective"]

    def test_v2_with_design_basis_validates(self, minimal_valid, v2_design_basis):
        from generate_calc_report import load_and_validate
        minimal_valid["design_basis"] = v2_design_basis
        result = load_and_validate(minimal_valid)
        assert result["design_basis"]["design_life"] == 25

    def test_v2_with_materials_validates(self, minimal_valid, v2_materials):
        from generate_calc_report import load_and_validate
        minimal_valid["materials"] = v2_materials
        result = load_and_validate(minimal_valid)
        assert len(result["materials"]) == 2

    def test_v2_with_calculations_validates(self, minimal_valid, v2_calculations):
        from generate_calc_report import load_and_validate
        minimal_valid["calculations"] = v2_calculations
        result = load_and_validate(minimal_valid)
        assert len(result["calculations"]) == 3

    def test_v2_with_sensitivity_validates(self, minimal_valid, v2_sensitivity):
        from generate_calc_report import load_and_validate
        minimal_valid["sensitivity"] = v2_sensitivity
        result = load_and_validate(minimal_valid)
        assert len(result["sensitivity"]) == 3

    def test_v2_with_validation_validates(self, minimal_valid, v2_validation):
        from generate_calc_report import load_and_validate
        minimal_valid["validation"] = v2_validation
        result = load_and_validate(minimal_valid)
        assert result["validation"]["method"] is not None

    def test_v2_with_verification_validates(self, minimal_valid, v2_verification):
        from generate_calc_report import load_and_validate
        minimal_valid["verification"] = v2_verification
        result = load_and_validate(minimal_valid)
        assert result["verification"]["checker"] == "J. Smith, PE"

    def test_v2_with_conclusions_validates(self, minimal_valid, v2_conclusions):
        from generate_calc_report import load_and_validate
        minimal_valid["conclusions"] = v2_conclusions
        result = load_and_validate(minimal_valid)
        assert "unity check" in result["conclusions"]["adequacy"]

    def test_scope_missing_objective_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["scope"] = {"inclusions": ["a"], "exclusions": ["b"]}
        with pytest.raises(ValueError, match="objective"):
            load_and_validate(minimal_valid)

    def test_scope_missing_inclusions_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["scope"] = {"objective": "Test", "exclusions": ["b"]}
        with pytest.raises(ValueError, match="inclusions"):
            load_and_validate(minimal_valid)

    def test_design_basis_missing_codes_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["design_basis"] = {"design_life": 25}
        with pytest.raises(ValueError, match="codes"):
            load_and_validate(minimal_valid)

    def test_design_basis_missing_design_life_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["design_basis"] = {"codes": [{"code": "X", "edition": "1"}]}
        with pytest.raises(ValueError, match="design_life"):
            load_and_validate(minimal_valid)

    def test_materials_missing_name_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["materials"] = [{"grade": "X65", "value": 450, "unit": "MPa"}]
        with pytest.raises(ValueError, match="name"):
            load_and_validate(minimal_valid)

    def test_calculations_missing_step_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["calculations"] = [{"description": "Do something"}]
        with pytest.raises(ValueError, match="step"):
            load_and_validate(minimal_valid)

    def test_sensitivity_missing_parameter_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["sensitivity"] = [{"range": "1-2", "result": "ok"}]
        with pytest.raises(ValueError, match="parameter"):
            load_and_validate(minimal_valid)

    def test_validation_without_method_accepts(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["validation"] = {"test_file": "test.py"}
        result = load_and_validate(minimal_valid)
        assert "validation" in result

    def test_verification_missing_checker_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["verification"] = {"date": "2026-01-01", "method": "hand calc"}
        with pytest.raises(ValueError, match="checker"):
            load_and_validate(minimal_valid)

    def test_verification_missing_date_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["verification"] = {"checker": "J. Doe", "method": "hand calc"}
        with pytest.raises(ValueError, match="date"):
            load_and_validate(minimal_valid)

    def test_conclusions_missing_adequacy_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["conclusions"] = {"governing_check": "fatigue"}
        with pytest.raises(ValueError, match="adequacy"):
            load_and_validate(minimal_valid)

    def test_conclusions_missing_governing_check_raises(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["conclusions"] = {"adequacy": "OK"}
        with pytest.raises(ValueError, match="governing_check"):
            load_and_validate(minimal_valid)


# ── Phase 2: HTML Builders ───────────────────────────────────────────────

class TestSchemaV2HTMLBuilders:
    """New builder functions must produce valid HTML cards."""

    def test_build_scope_card_has_objective(self, v2_scope):
        from calc_report_html import build_scope_card
        html = build_scope_card(v2_scope)
        assert "card" in html
        assert "Scope" in html
        assert "KP 12.4" in html

    def test_build_scope_card_has_inclusions(self, v2_scope):
        from calc_report_html import build_scope_card
        html = build_scope_card(v2_scope)
        assert "wave-induced" in html
        assert "<li>" in html

    def test_build_scope_card_has_exclusions(self, v2_scope):
        from calc_report_html import build_scope_card
        html = build_scope_card(v2_scope)
        assert "Corrosion fatigue" in html

    def test_build_scope_card_optional_limitations(self, v2_scope):
        from calc_report_html import build_scope_card
        html = build_scope_card(v2_scope)
        assert "50-200 m" in html

    def test_build_scope_card_without_optionals(self):
        from calc_report_html import build_scope_card
        scope = {
            "objective": "Simple check",
            "inclusions": ["Item A"],
            "exclusions": ["Item B"],
        }
        html = build_scope_card(scope)
        assert "Simple check" in html
        assert "Limitations" not in html

    def test_build_design_basis_card_has_codes(self, v2_design_basis):
        from calc_report_html import build_design_basis_card
        html = build_design_basis_card(v2_design_basis)
        assert "card" in html
        assert "Design Basis" in html
        assert "DNV-RP-C203" in html
        assert "<table" in html

    def test_build_design_basis_card_has_design_life(self, v2_design_basis):
        from calc_report_html import build_design_basis_card
        html = build_design_basis_card(v2_design_basis)
        assert "25" in html

    def test_build_design_basis_card_optional_safety_class(self, v2_design_basis):
        from calc_report_html import build_design_basis_card
        html = build_design_basis_card(v2_design_basis)
        assert "high" in html.lower()

    def test_build_materials_card_produces_table(self, v2_materials):
        from calc_report_html import build_materials_card
        html = build_materials_card(v2_materials)
        assert "card" in html
        assert "Materials" in html
        assert "<table" in html
        assert "X65" in html
        assert "450" in html

    def test_build_materials_card_has_columns(self, v2_materials):
        from calc_report_html import build_materials_card
        html = build_materials_card(v2_materials)
        assert "Name" in html
        assert "Grade" in html
        assert "Value" in html
        assert "Unit" in html

    def test_build_calculations_card_numbered_steps(self, v2_calculations):
        from calc_report_html import build_calculations_card
        html = build_calculations_card(v2_calculations)
        assert "card" in html
        assert "Calculations" in html
        assert "Step 1" in html
        assert "Step 2" in html
        assert "Step 3" in html

    def test_build_calculations_card_has_description(self, v2_calculations):
        from calc_report_html import build_calculations_card
        html = build_calculations_card(v2_calculations)
        assert "hot-spot stress" in html

    def test_build_calculations_card_optional_detail(self, v2_calculations):
        from calc_report_html import build_calculations_card
        html = build_calculations_card(v2_calculations)
        assert "SCF = 1.2" in html

    def test_build_calculations_card_optional_code_clause(self, v2_calculations):
        from calc_report_html import build_calculations_card
        html = build_calculations_card(v2_calculations)
        assert "DNV-RP-C203 Eq. 2.3.1" in html

    def test_build_sensitivity_card_produces_table(self, v2_sensitivity):
        from calc_report_html import build_sensitivity_card
        html = build_sensitivity_card(v2_sensitivity)
        assert "card" in html
        assert "Sensitivity" in html
        assert "<table" in html
        assert "Wall Thickness" in html

    def test_build_sensitivity_card_has_columns(self, v2_sensitivity):
        from calc_report_html import build_sensitivity_card
        html = build_sensitivity_card(v2_sensitivity)
        assert "Parameter" in html
        assert "Range" in html
        assert "Result" in html

    def test_build_validation_card_has_method(self, v2_validation):
        from calc_report_html import build_validation_card
        html = build_validation_card(v2_validation)
        assert "card" in html
        assert "Validation" in html
        assert "independent spreadsheet" in html

    def test_build_validation_card_has_test_count(self, v2_validation):
        from calc_report_html import build_validation_card
        html = build_validation_card(v2_validation)
        assert "14" in html

    def test_build_validation_card_has_categories(self, v2_validation):
        from calc_report_html import build_validation_card
        html = build_validation_card(v2_validation)
        assert "stress_range" in html
        assert "miner_sum" in html

    def test_build_validation_card_without_optionals(self):
        from calc_report_html import build_validation_card
        val = {"method": "Peer review"}
        html = build_validation_card(val)
        assert "Peer review" in html
        assert "card" in html

    def test_build_verification_card_has_checker(self, v2_verification):
        from calc_report_html import build_verification_card
        html = build_verification_card(v2_verification)
        assert "card" in html
        assert "Verification" in html
        assert "J. Smith, PE" in html

    def test_build_verification_card_has_date(self, v2_verification):
        from calc_report_html import build_verification_card
        html = build_verification_card(v2_verification)
        assert "2026-02-15" in html

    def test_build_verification_card_has_method(self, v2_verification):
        from calc_report_html import build_verification_card
        html = build_verification_card(v2_verification)
        assert "hand calculation" in html

    def test_build_verification_card_optional_findings(self, v2_verification):
        from calc_report_html import build_verification_card
        html = build_verification_card(v2_verification)
        assert "within 2%" in html

    def test_build_verification_card_optional_status(self, v2_verification):
        from calc_report_html import build_verification_card
        html = build_verification_card(v2_verification)
        assert "approved" in html.lower()

    def test_build_conclusions_card_has_adequacy(self, v2_conclusions):
        from calc_report_html import build_conclusions_card
        html = build_conclusions_card(v2_conclusions)
        assert "card" in html
        assert "Conclusions" in html
        assert "unity check of 0.65" in html

    def test_build_conclusions_card_has_governing_check(self, v2_conclusions):
        from calc_report_html import build_conclusions_card
        html = build_conclusions_card(v2_conclusions)
        assert "H_s = 4.5 m" in html

    def test_build_conclusions_card_optional_recommendations(self, v2_conclusions):
        from calc_report_html import build_conclusions_card
        html = build_conclusions_card(v2_conclusions)
        assert "Monitor weld" in html
        assert "<li>" in html

    def test_build_conclusions_card_optional_compliance(self, v2_conclusions):
        from calc_report_html import build_conclusions_card
        html = build_conclusions_card(v2_conclusions)
        assert "DNV-RP-C203 (2021)" in html

    def test_build_conclusions_card_without_optionals(self):
        from calc_report_html import build_conclusions_card
        conc = {
            "adequacy": "Design is adequate.",
            "governing_check": "Bending stress at midspan",
        }
        html = build_conclusions_card(conc)
        assert "Design is adequate" in html
        assert "Recommendations" not in html


# ── Phase 3: Integration ─────────────────────────────────────────────────

class TestSchemaV2Integration:
    """Full v2 data must render correctly to HTML and Markdown."""

    def test_v2_html_contains_all_new_sections(self, v2_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(v2_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "Scope" in html
        assert "Design Basis" in html
        assert "Materials" in html
        assert "Calculations" in html
        assert "Sensitivity" in html
        assert "Validation" in html
        assert "Verification" in html
        assert "Conclusions" in html

    def test_v2_html_section_order(self, v2_data):
        """New sections appear in correct order in HTML output."""
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(v2_data)
        md = render_markdown(data)
        html = render_html(data, md)
        ordered_markers = [
            "Scope", "Design Basis", "Inputs", "Materials",
            "Methodology", "Calculations", "Outputs", "Sensitivity",
            "Validation", "Verification", "Conclusions",
        ]
        positions = [html.index(m) for m in ordered_markers]
        assert positions == sorted(positions), (
            f"Sections out of order: {list(zip(ordered_markers, positions))}"
        )

    def test_v2_markdown_contains_all_new_sections(self, v2_data):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(v2_data)
        md = render_markdown(data)
        assert "## Scope" in md
        assert "## Design Basis" in md
        assert "## Materials" in md
        assert "## Calculations" in md
        assert "## Sensitivity" in md
        assert "## Validation" in md
        assert "## Verification" in md
        assert "## Conclusions" in md

    def test_v2_markdown_section_order(self, v2_data):
        """New sections appear in correct order in Markdown output."""
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(v2_data)
        md = render_markdown(data)
        ordered = [
            "## Scope", "## Design Basis", "## Inputs", "## Materials",
            "## Methodology", "## Calculations", "## Outputs",
            "## Sensitivity", "## Validation", "## Verification",
            "## Conclusions",
        ]
        positions = [md.index(s) for s in ordered]
        assert positions == sorted(positions), "Markdown sections out of order"

    def test_v2_html_still_has_v1_sections(self, v2_data):
        """v2 data must still render all v1 sections."""
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(v2_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "Inputs" in html
        assert "Methodology" in html
        assert "Outputs" in html
        assert "Assumptions" in html
        assert "References" in html

    def test_v2_html_escapes_user_content(self, v2_data):
        """HTML special chars in v2 sections must be escaped."""
        from generate_calc_report import load_and_validate, render_markdown, render_html
        v2_data["scope"]["objective"] = 'Check <b>bold</b> & "quotes"'
        data = load_and_validate(v2_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "&lt;b&gt;" in html
        assert "&amp;" in html
