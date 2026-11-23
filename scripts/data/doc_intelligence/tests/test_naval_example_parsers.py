"""Tests for naval_example_parsers — multi-format worked example extraction.

TDD: tests written first, then implementation.
Covers Format A (EN400/DNV), Format B (Tupper/Biran), Format C (Attwood/PNA).
"""

import pytest

from scripts.data.doc_intelligence.naval_example_parsers import (
    EN400Parser,
    TupperBiranParser,
    AttwoodPNAParser,
    parse_examples_multi_format,
)


# ── Fixtures: real section text from manifests ──────────────────────


FORMAT_A_EN400 = (
    "Example 1.1 An object has a mass of 1 slug. Calculate its "
    "corresponding weight.\n"
    "Weight = (mass) × (acceleration)\n"
    "Weight = (1 slug) × (32.17 ft/s2) = (1 lb-s2/ft) × (32.17 ft/s2)\n"
    "Weight = 32.17 lb"
)

FORMAT_A_EN400_WITH_GIVEN = (
    "Example 1.2 A ship floating in salt water has a displaced volume "
    "of 4,000 ft3. Calculate the ship's weight in long tons.\n"
    "Given:\n"
    "  rho = 1.99 lb-s2/ft4\n"
    "  g = 32.17 ft/s2\n"
    "  V = 4000 ft3\n"
    "Solution: Δ = ρgV / 2240 = 114.32 LT"
)

FORMAT_B_TUPPER = (
    "Example 3.1\n\n"
    "Calculate the area between the curve, defined by the ordinates\n"
    "below, and the x-axis. Calculate the first and second moments of\n"
    "area about the x- and y-axes and the position of the centroid of\n"
    "area.\n\n"
    "Solution\n\n"
    "There are 9 ordinates spaced one unit apart. The results can be\n"
    "calculated in tabular fashion as in Table 3.1.\n\n"
    "Hence:\n"
    "Area = 29.8 / 3 = 9.93 m2"
)

FORMAT_B_TUPPER_TRIM = (
    "Example 4.1\n\n"
    "A ship of mass 5000 tonnes, 98m long, floats at draughts of 5.5 m\n"
    "forward and 6.2 m aft. The longitudinal metacentric height is 104m\n"
    "and the centre of flotation is 2.1m aft of amidships. Determine\n"
    "the moment to change trim 1 cm and the new end draughts when a\n"
    "mass of 85 tonnes, which is already on board, is moved 30 m forward.\n\n"
    "Solution\n\n"
    "As the mass is already on board there will be no bodily sinkage.\n"
    "MCT = 5000 × 104 / (100 × 98) = 53.06 tonne m/cm"
)

FORMAT_B_BIRAN = (
    "Example 2.2 - Designing a buoy\n\n"
    "This is a simple application of Archimedes' principle as the base of\n"
    "a design equation. Let us suppose that we want to design a spherical\n"
    "buoy for an instrument having a mass M. The buoy shall be made of\n"
    "3 mm steel plate, of density ps, and shall float so that the centre\n"
    "of the sphere lies in the waterplane.\n\n"
    "Solution\n"
    "R = 0.438 m"
)

FORMAT_C_ATTWOOD = (
    "Example. An armour plate is of the form of a trapezoid with parallel\n"
    "sides 8' 3\" and 8' 9\" long, and their distance apart 12 feet. Find its\n"
    "weight if 6 inches thick, the material of the armour plate weighing\n"
    "490 lbs. per cubic foot.\n\n"
    "First we must find the area, which is given by\n"
    "(8.25 + 8.75) / 2 × 12 = 102 square feet\n"
    "The plate being 6 inches thick = 0.5 foot, the cubical contents\n"
    "will be 102 × 0.5 = 51 cubic feet\n"
    "The weight will therefore be 51 × 490 / 2240 = 11.15 tons"
)

FORMAT_C_ATTWOOD_SECTION = (
    "Example. A coal-bunker has sections 17' 6\" apart, and the areas of\n"
    "the sections are 12, 110, 105, and 12 sq. ft. respectively. Find the\n"
    "volume of the bunker.\n\n"
    "By Simpson's first rule:\n"
    "Volume = (17.5 / 3) × (12 + 3×110 + 3×105 + 12)\n"
    "Volume = 3806.25 cubic feet"
)


# ── Format A (EN400/DNV) tests ──────────────────────────────────────


class TestEN400Parser:
    def setup_method(self):
        self.parser = EN400Parser()

    def test_can_parse_en400_format(self):
        assert self.parser.can_parse(FORMAT_A_EN400)

    def test_can_parse_en400_with_given(self):
        assert self.parser.can_parse(FORMAT_A_EN400_WITH_GIVEN)

    def test_cannot_parse_tupper_format(self):
        assert not self.parser.can_parse(FORMAT_B_TUPPER)

    def test_cannot_parse_attwood_format(self):
        assert not self.parser.can_parse(FORMAT_C_ATTWOOD)

    def test_parse_en400_basic(self):
        source = {"document": "EN400.pdf", "page": 17}
        results = self.parser.parse(FORMAT_A_EN400, source, "naval-architecture")
        assert len(results) == 1
        ex = results[0]
        assert ex["number"] == "1.1"
        assert ex["expected_value"] == pytest.approx(32.17)
        assert ex["parser_format"] == "en400_dnv"
        assert ex["source_book"] == "EN400.pdf"
        assert ex["domain"] == "naval-architecture"

    def test_parse_en400_with_given_section(self):
        source = {"document": "EN400.pdf", "page": 18}
        results = self.parser.parse(
            FORMAT_A_EN400_WITH_GIVEN, source, "naval-architecture"
        )
        assert len(results) == 1
        ex = results[0]
        assert ex["number"] == "1.2"
        assert ex["expected_value"] == pytest.approx(114.32)
        assert ex["output_unit"] == "LT"
        assert len(ex["inputs"]) >= 2

    def test_no_match_returns_empty(self):
        results = self.parser.parse("No examples here.", {}, "general")
        assert results == []


# ── Format B (Tupper/Biran) tests ───────────────────────────────────


class TestTupperBiranParser:
    def setup_method(self):
        self.parser = TupperBiranParser()

    def test_can_parse_tupper_format(self):
        assert self.parser.can_parse(FORMAT_B_TUPPER)

    def test_can_parse_biran_format(self):
        assert self.parser.can_parse(FORMAT_B_BIRAN)

    def test_cannot_parse_en400_format(self):
        assert not self.parser.can_parse(FORMAT_A_EN400_WITH_GIVEN)

    def test_parse_tupper_example(self):
        source = {"document": "Tupper-1996.pdf", "page": 35}
        results = self.parser.parse(FORMAT_B_TUPPER, source, "naval-architecture")
        assert len(results) == 1
        ex = results[0]
        assert ex["number"] == "3.1"
        assert ex["expected_value"] == pytest.approx(9.93)
        assert ex["output_unit"] == "m2"
        assert ex["parser_format"] == "tupper_biran"

    def test_parse_tupper_trim_example(self):
        source = {"document": "Tupper-1996.pdf", "page": 54}
        results = self.parser.parse(
            FORMAT_B_TUPPER_TRIM, source, "naval-architecture"
        )
        assert len(results) == 1
        ex = results[0]
        assert ex["number"] == "4.1"
        assert ex["expected_value"] == pytest.approx(53.06)

    def test_parse_biran_titled_example(self):
        source = {"document": "Biran.pdf", "page": 40}
        results = self.parser.parse(FORMAT_B_BIRAN, source, "naval-architecture")
        assert len(results) == 1
        ex = results[0]
        assert ex["number"] == "2.2"
        assert "buoy" in ex["title"].lower() or "designing" in ex["title"].lower()
        assert ex["expected_value"] == pytest.approx(0.438)

    def test_no_match_returns_empty(self):
        results = self.parser.parse("Just some prose.", {}, "general")
        assert results == []


# ── Format C (Attwood/PNA inline) tests ─────────────────────────────


class TestAttwoodPNAParser:
    def setup_method(self):
        self.parser = AttwoodPNAParser()

    def test_can_parse_attwood_format(self):
        assert self.parser.can_parse(FORMAT_C_ATTWOOD)

    def test_cannot_parse_en400_format(self):
        assert not self.parser.can_parse(FORMAT_A_EN400)

    def test_cannot_parse_tupper_format(self):
        assert not self.parser.can_parse(FORMAT_B_TUPPER)

    def test_parse_attwood_trapezoid(self):
        source = {"document": "Attwood-1899.pdf", "page": 3}
        results = self.parser.parse(FORMAT_C_ATTWOOD, source, "naval-architecture")
        assert len(results) == 1
        ex = results[0]
        assert ex["expected_value"] == pytest.approx(11.15)
        assert ex["output_unit"] == "tons"
        assert ex["parser_format"] == "attwood_pna"

    def test_parse_attwood_volume(self):
        source = {"document": "Attwood-1899.pdf", "page": 50}
        results = self.parser.parse(
            FORMAT_C_ATTWOOD_SECTION, source, "naval-architecture"
        )
        assert len(results) == 1
        ex = results[0]
        assert ex["expected_value"] == pytest.approx(3806.25)

    def test_no_match_returns_empty(self):
        results = self.parser.parse("Nothing here.", {}, "general")
        assert results == []


# ── Multi-format dispatcher tests ───────────────────────────────────


class TestMultiFormatDispatcher:
    def test_dispatches_en400(self):
        results = parse_examples_multi_format(
            FORMAT_A_EN400_WITH_GIVEN,
            {"document": "EN400.pdf", "page": 18},
            "naval-architecture",
        )
        assert len(results) == 1
        assert results[0]["parser_format"] == "en400_dnv"

    def test_dispatches_tupper(self):
        results = parse_examples_multi_format(
            FORMAT_B_TUPPER,
            {"document": "Tupper.pdf", "page": 35},
            "naval-architecture",
        )
        assert len(results) == 1
        assert results[0]["parser_format"] == "tupper_biran"

    def test_dispatches_attwood(self):
        results = parse_examples_multi_format(
            FORMAT_C_ATTWOOD,
            {"document": "Attwood.pdf", "page": 3},
            "naval-architecture",
        )
        assert len(results) == 1
        assert results[0]["parser_format"] == "attwood_pna"

    def test_no_match_returns_empty(self):
        results = parse_examples_multi_format(
            "This text has no examples.", {}, "general"
        )
        assert results == []

    def test_output_schema_has_required_fields(self):
        results = parse_examples_multi_format(
            FORMAT_A_EN400_WITH_GIVEN,
            {"document": "EN400.pdf", "page": 18},
            "naval-architecture",
        )
        ex = results[0]
        required = {
            "number", "title", "source_book", "page",
            "parser_format", "inputs", "expected_value",
            "output_unit", "use_as_test", "domain",
        }
        assert required.issubset(set(ex.keys()))

    def test_use_as_test_flag_set(self):
        results = parse_examples_multi_format(
            FORMAT_A_EN400_WITH_GIVEN,
            {"document": "EN400.pdf", "page": 18},
            "naval-architecture",
        )
        assert results[0]["use_as_test"] is True
