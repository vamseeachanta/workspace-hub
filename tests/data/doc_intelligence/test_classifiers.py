"""Tests for heuristic content-type classifiers."""

import pytest

from scripts.data.doc_intelligence.classifiers import classify_section
from scripts.data.doc_intelligence.schema import ExtractedSection, SourceLocation


def _section(text, heading=None):
    """Helper to build an ExtractedSection with minimal boilerplate."""
    return ExtractedSection(
        heading=heading,
        level=1,
        text=text,
        source=SourceLocation(document="test.pdf", section=heading, page=1),
    )


class TestClassifyConstants:
    def test_symbol_equals_value_units(self):
        s = _section("GM = 1.5 m, safety factor SF = 2.0")
        assert classify_section(s) == "constants"

    def test_explicit_constant_keyword(self):
        s = _section("The constant value is k = 0.85")
        assert classify_section(s) == "constants"

    def test_heading_hint(self):
        s = _section("Values used: x = 10", heading="Design Constants")
        assert classify_section(s) == "constants"

    def test_yield_strength_pattern(self):
        s = _section("Fy = 350 MPa, E = 207 GPa")
        assert classify_section(s) == "constants"


class TestClassifyEquations:
    def test_math_expression(self):
        s = _section("R_T = R_f + R_r + R_w where R_f is frictional resistance")
        assert classify_section(s) == "equations"

    def test_equation_keyword(self):
        s = _section("The governing equation is F = m * a")
        assert classify_section(s) == "equations"

    def test_formula_with_operators(self):
        s = _section("sigma = P * D / (2 * t)")
        assert classify_section(s) == "equations"


class TestClassifyRequirements:
    def test_shall_keyword(self):
        s = _section("The system shall withstand 100-year return period.")
        assert classify_section(s) == "requirements"

    def test_must_keyword(self):
        s = _section("All equipment must be certified.")
        assert classify_section(s) == "requirements"

    def test_required_keyword(self):
        s = _section("A safety factor of 2.0 is required for all load cases.")
        assert classify_section(s) == "requirements"

    def test_requirements_heading(self):
        s = _section("Factor of safety: 1.5", heading="Safety Requirements")
        assert classify_section(s) == "requirements"

    def test_shall_takes_priority_over_constants(self):
        """Requirements priority > constants."""
        s = _section("The safety factor shall be SF = 2.0")
        assert classify_section(s) == "requirements"


class TestClassifyProcedures:
    def test_numbered_steps(self):
        s = _section("Step 1: Mobilize vessel. Step 2: Deploy riser.")
        assert classify_section(s) == "procedures"

    def test_procedure_heading(self):
        s = _section("Rig up the equipment and connect.", heading="Installation Procedure")
        assert classify_section(s) == "procedures"

    def test_sequential_action_verbs(self):
        s = _section("1. Remove the cap. 2. Attach the flange. 3. Torque bolts.")
        assert classify_section(s) == "procedures"


class TestClassifyDefinitions:
    def test_means_keyword(self):
        s = _section("Riser means a vertical conduit.")
        assert classify_section(s) == "definitions"

    def test_is_defined_as(self):
        s = _section("Mooring is defined as the system that holds the vessel.")
        assert classify_section(s) == "definitions"

    def test_refers_to(self):
        s = _section("FPSO refers to a floating production storage unit.")
        assert classify_section(s) == "definitions"

    def test_definitions_heading(self):
        s = _section("Terms used in this document.", heading="Definitions")
        assert classify_section(s) == "definitions"


class TestClassifyWorkedExamples:
    def test_example_keyword(self):
        s = _section("Example: Calculate the wall thickness.")
        assert classify_section(s) == "worked_examples"

    def test_given_find_solution(self):
        s = _section("Given: OD = 12 inch. Find: wall thickness. Solution: t = P*D/(2*S)")
        assert classify_section(s) == "worked_examples"

    def test_sample_calculation(self):
        s = _section("Sample calculation for bending stress.")
        assert classify_section(s) == "worked_examples"

    def test_worked_example_heading(self):
        s = _section("Calculate the value.", heading="Worked Example 1")
        assert classify_section(s) == "worked_examples"


class TestClassifyNone:
    def test_general_text_returns_none(self):
        s = _section("This section contains general notes about the project.")
        assert classify_section(s) is None

    def test_empty_text_returns_none(self):
        s = _section("")
        assert classify_section(s) is None

    def test_short_ambiguous_text_returns_none(self):
        s = _section("See above for details.")
        assert classify_section(s) is None
