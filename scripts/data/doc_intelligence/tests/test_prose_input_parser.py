"""Tests for prose input extraction — parsing numerical values from text.

The existing parse_given_inputs() only handles "symbol = value" in Given:
sections. This tests a new parse_prose_inputs() that extracts numbers
from prose like "a mass of 1 slug" or "450 ft in length".
"""

import pytest

from scripts.data.doc_intelligence.worked_example_parser import (
    parse_prose_inputs,
)


class TestProseInputExtraction:
    """Extract numerical inputs from textbook prose."""

    def test_mass_of_n_slug(self):
        text = "An object has a mass of 1 slug. Calculate its weight."
        inputs = parse_prose_inputs(text)
        assert len(inputs) >= 1
        values = {i["value"] for i in inputs}
        assert 1.0 in values

    def test_ship_displaced_volume(self):
        text = (
            "A ship floating in salt water has a displaced volume "
            "of 4,000 ft3. Calculate the ship's weight."
        )
        inputs = parse_prose_inputs(text)
        values = {i["value"] for i in inputs}
        assert 4000.0 in values

    def test_ship_with_multiple_values(self):
        text = (
            "A ship of mass 5000 tonnes, 98m long, floats at draughts "
            "of 5.5 m forward and 6.2 m aft."
        )
        inputs = parse_prose_inputs(text)
        values = {i["value"] for i in inputs}
        assert 5000.0 in values
        assert 98.0 in values
        assert 5.5 in values
        assert 6.2 in values

    def test_feet_and_inches(self):
        text = (
            "An armour plate with parallel sides 8 and 9 feet long, "
            "and distance apart 12 feet. Weight 490 lbs per cubic foot."
        )
        inputs = parse_prose_inputs(text)
        values = {i["value"] for i in inputs}
        assert 12.0 in values
        assert 490.0 in values

    def test_scientific_notation(self):
        text = "Kinematic viscosity nu = 1.2791e-5 ft2/s at 15 knots."
        inputs = parse_prose_inputs(text)
        values = {i["value"] for i in inputs}
        assert any(abs(v - 1.2791e-5) < 1e-10 for v in values)

    def test_preserves_given_section_inputs(self):
        text = (
            "Given:\n"
            "  rho = 1.99 lb-s2/ft4\n"
            "  g = 32.17 ft/s2\n"
            "  V = 4000 ft3\n"
            "Solution: result = 114.32 LT"
        )
        inputs = parse_prose_inputs(text)
        values = {i["value"] for i in inputs}
        assert 1.99 in values
        assert 32.17 in values
        assert 4000.0 in values

    def test_no_numbers_returns_empty(self):
        text = "Calculate the ship's displacement."
        inputs = parse_prose_inputs(text)
        assert inputs == []

    def test_excludes_solution_values(self):
        """Values after 'Solution' should not be captured as inputs."""
        text = (
            "A ship has a mass of 5000 tonnes.\n"
            "Solution: displacement = 10000 LT"
        )
        inputs = parse_prose_inputs(text)
        values = {i["value"] for i in inputs}
        assert 5000.0 in values
        # 10000 is the answer, not an input
        assert 10000.0 not in values
