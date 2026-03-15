"""Tests for enhanced worked example parsing — inputs, units, real assertions."""

import pytest

from scripts.data.doc_intelligence.worked_example_parser import (
    parse_given_inputs,
    parse_solution_units,
    parse_enhanced_example,
    render_real_test_file,
)


class TestParseGivenInputs:
    """Extract input parameters from 'Given:' section."""

    def test_simple_key_value(self):
        text = "Given: rho = 1025 kg/m3"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 1
        assert inputs[0]["symbol"] == "rho"
        assert inputs[0]["value"] == 1025.0
        assert inputs[0]["unit"] == "kg/m3"

    def test_multiple_inputs_comma_separated(self):
        text = "Given: L = 10 m, W = 5 m, H = 3 m"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 3
        assert inputs[0]["symbol"] == "L"
        assert inputs[0]["value"] == 10.0
        assert inputs[1]["symbol"] == "W"
        assert inputs[2]["symbol"] == "H"

    def test_multiple_inputs_newline_separated(self):
        text = "Given:\nrho = 1025 kg/m3\ng = 9.81 m/s2\nd = 100 m"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 3
        assert inputs[0]["symbol"] == "rho"
        assert inputs[1]["symbol"] == "g"
        assert inputs[1]["value"] == 9.81
        assert inputs[2]["symbol"] == "d"

    def test_no_given_section_returns_empty(self):
        text = "This text has no Given section."
        inputs = parse_given_inputs(text)
        assert inputs == []

    def test_unitless_values(self):
        text = "Given: Cd = 0.65, n = 3"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 2
        assert inputs[0]["symbol"] == "Cd"
        assert inputs[0]["value"] == 0.65
        assert inputs[0]["unit"] == ""
        assert inputs[1]["value"] == 3.0

    def test_subscript_symbols(self):
        text = "Given: F_b = 500 N"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 1
        assert inputs[0]["symbol"] == "F_b"
        assert inputs[0]["value"] == 500.0
        assert inputs[0]["unit"] == "N"

    def test_scientific_notation(self):
        text = "Given: E = 2.1e11 Pa"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 1
        assert inputs[0]["value"] == 2.1e11

    def test_comma_in_number(self):
        text = "Given: P = 1,005,525 Pa"
        inputs = parse_given_inputs(text)
        assert len(inputs) == 1
        assert inputs[0]["value"] == 1005525.0


class TestParseSolutionUnits:
    """Extract units from the Solution line."""

    def test_basic_unit_extraction(self):
        text = "Solution: P = 1025 * 9.81 * 100 = 1,005,525 Pa"
        unit = parse_solution_units(text)
        assert unit == "Pa"

    def test_compound_unit(self):
        text = "Solution: v = 12.5 m/s"
        unit = parse_solution_units(text)
        assert unit == "m/s"

    def test_no_solution_returns_empty(self):
        text = "The answer is 42."
        unit = parse_solution_units(text)
        assert unit == ""

    def test_unit_with_exponent(self):
        text = "Solution: A = 50 m2"
        unit = parse_solution_units(text)
        assert unit == "m2"

    def test_percentage(self):
        text = "Solution: efficiency = 85.5 %"
        unit = parse_solution_units(text)
        assert unit == "%"


class TestParseEnhancedExample:
    """Full enhanced parsing with inputs + output."""

    def test_full_parse(self):
        text = (
            "Example 3.1: Calculate hydrostatic pressure at 100m depth.\n"
            "Given: rho = 1025 kg/m3, g = 9.81 m/s2, d = 100 m\n"
            "Solution: P = rho * g * d = 1025 * 9.81 * 100 = 1,005,525 Pa"
        )
        result = parse_enhanced_example(text, domain="naval-architecture")
        assert result is not None
        assert result["number"] == "3.1"
        assert result["title"] == "Calculate hydrostatic pressure at 100m depth"
        assert result["expected_value"] == 1005525.0
        assert result["output_unit"] == "Pa"
        assert len(result["inputs"]) == 3
        assert result["inputs"][0]["symbol"] == "rho"

    def test_no_example_pattern_returns_none(self):
        result = parse_enhanced_example("No example here", domain="general")
        assert result is None

    def test_missing_solution_returns_none(self):
        text = "Example 1.1: Some calc.\nGiven: x = 10\nNo solution line."
        result = parse_enhanced_example(text, domain="general")
        assert result is None

    def test_missing_given_still_parses(self):
        text = (
            "Example 2.1: Direct result.\n"
            "Solution: F = 500 N"
        )
        result = parse_enhanced_example(text, domain="structural")
        assert result is not None
        assert result["inputs"] == []
        assert result["expected_value"] == 500.0


class TestRenderRealTestFile:
    """Test generation of real pytest assertions."""

    def test_generates_pytest_approx(self):
        examples = [
            {
                "number": "3.1",
                "title": "Calculate hydrostatic pressure",
                "expected_value": 1005525.0,
                "output_unit": "Pa",
                "inputs": [
                    {"symbol": "rho", "value": 1025.0, "unit": "kg/m3"},
                    {"symbol": "g", "value": 9.81, "unit": "m/s2"},
                    {"symbol": "d", "value": 100.0, "unit": "m"},
                ],
                "source": {"document": "DNV-RP-C205.pdf", "page": 15},
                "domain": "naval-architecture",
            }
        ]
        output = render_real_test_file("DNV-RP-C205.pdf", examples)
        assert "pytest.approx" in output
        assert "1005525" in output
        assert "rho = 1025" in output
        assert "rel=1e-3" in output

    def test_generates_valid_python(self):
        examples = [
            {
                "number": "1.1",
                "title": "Area calc",
                "expected_value": 50.0,
                "output_unit": "m2",
                "inputs": [
                    {"symbol": "L", "value": 10.0, "unit": "m"},
                    {"symbol": "W", "value": 5.0, "unit": "m"},
                ],
                "source": {"document": "test.pdf", "page": 1},
                "domain": "structural",
            }
        ]
        output = render_real_test_file("test.pdf", examples)
        compile(output, "<test>", "exec")

    def test_multiple_examples(self):
        examples = [
            {
                "number": "3.1",
                "title": "Pressure",
                "expected_value": 1005525.0,
                "output_unit": "Pa",
                "inputs": [{"symbol": "rho", "value": 1025.0, "unit": ""}],
                "source": {"document": "t.pdf", "page": 1},
                "domain": "naval-architecture",
            },
            {
                "number": "5.2",
                "title": "Force",
                "expected_value": 500.0,
                "output_unit": "N",
                "inputs": [],
                "source": {"document": "t.pdf", "page": 2},
                "domain": "naval-architecture",
            },
        ]
        output = render_real_test_file("t.pdf", examples)
        assert "test_example_3_1" in output
        assert "test_example_5_2" in output

    def test_empty_examples_returns_empty(self):
        output = render_real_test_file("t.pdf", [])
        assert output == ""

    def test_no_inputs_still_generates_test(self):
        examples = [
            {
                "number": "1.1",
                "title": "Simple",
                "expected_value": 42.0,
                "output_unit": "",
                "inputs": [],
                "source": {"document": "t.pdf", "page": 1},
                "domain": "general",
            }
        ]
        output = render_real_test_file("t.pdf", examples)
        assert "expected = 42" in output
        assert "pytest.approx" in output
