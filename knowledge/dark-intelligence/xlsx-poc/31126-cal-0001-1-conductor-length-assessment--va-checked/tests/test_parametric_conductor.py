"""Parametric tests for conductor length assessment — WRK-1247 POC demo.

Demonstrates the xlsx-to-python parametric test pattern:
- Excel cached values = baseline assertion
- 10 parameter variations cover the input range
- Physical bounds checks for all variations
"""

import math

import pytest


# ── Python implementations of extracted Excel formulas ──────────────────────

def outer_diameter_m(od_inches: float) -> float:
    """Convert outer diameter from inches to meters.

    Excel: G42 = E42 * 25.4 / 1000
    """
    return od_inches * 25.4 / 1000


def wall_thickness_mm(wt_inches: float) -> float:
    """Convert wall thickness from inches to mm.

    Excel: G43 = E43 * 25.4
    """
    return wt_inches * 25.4


def inner_diameter_m(od_m: float, wt_mm: float) -> float:
    """Calculate inner diameter from outer diameter and wall thickness.

    Excel: E44 = G42 - (2 * G43 / 1000)
    """
    return od_m - (2 * wt_mm / 1000)


def mass_per_unit_length(od_m: float, id_m: float, density: float) -> float:
    """Calculate mass per unit length of hollow cylinder.

    Excel: E45 = PI()/4 * (G42^2 - E44^2) * E36
    density = E36 (steel density, kg/m³)
    """
    return math.pi / 4 * (od_m**2 - id_m**2) * density


# ── Baseline test: Excel cached values (ground truth) ──────────────────────

class TestBaselineFromExcel:
    """Baseline tests using exact values from the source spreadsheet."""

    def test_outer_diameter_36inch(self):
        """Excel: E42=36, G42=0.9144"""
        assert outer_diameter_m(36) == pytest.approx(0.9144, rel=1e-6)

    def test_wall_thickness_2inch(self):
        """Excel: E43=2.0, G43=50.8"""
        assert wall_thickness_mm(2.0) == pytest.approx(50.8, rel=1e-6)

    def test_inner_diameter(self):
        """Excel: E44=0.8128"""
        od = outer_diameter_m(36)
        wt = wall_thickness_mm(2.0)
        assert inner_diameter_m(od, wt) == pytest.approx(0.8128, rel=1e-6)

    def test_mass_per_unit_length(self):
        """Excel: E45=1081.9218... (density E36=7850 kg/m³ assumed)."""
        od = outer_diameter_m(36)
        wt = wall_thickness_mm(2.0)
        id_m = inner_diameter_m(od, wt)
        result = mass_per_unit_length(od, id_m, 7850)
        assert result == pytest.approx(1081.9218093689772, rel=1e-6)


# ── Parametric variations ──────────────────────────────────────────────────

# Input ranges from typical conductor/casing engineering values
INPUT_RANGES = {
    "od_inches": {"min": 20, "max": 48, "nominal": 36, "unit": "in"},
    "wt_inches": {"min": 0.5, "max": 3.0, "nominal": 2.0, "unit": "in"},
    "density": {"min": 7800, "max": 7900, "nominal": 7850, "unit": "kg/m³"},
}


def make_case(**overrides):
    """Create test case from nominal values with overrides."""
    case = {k: v["nominal"] for k, v in INPUT_RANGES.items()}
    case.update(overrides)
    return case


VARIATIONS = [
    pytest.param(make_case(), id="1-nominal"),
    pytest.param(
        make_case(**{k: v["min"] for k, v in INPUT_RANGES.items()}),
        id="2-all-min",
    ),
    pytest.param(
        make_case(**{k: v["max"] for k, v in INPUT_RANGES.items()}),
        id="3-all-max",
    ),
    pytest.param(make_case(od_inches=20), id="4-od-low"),
    pytest.param(make_case(od_inches=48), id="5-od-high"),
    pytest.param(make_case(wt_inches=0.5), id="6-wt-low"),
    pytest.param(make_case(wt_inches=3.0), id="7-wt-high"),
    pytest.param(
        make_case(od_inches=20, wt_inches=3.0),
        id="8-stress-min-od-max-wt",
    ),
    pytest.param(make_case(od_inches=48, wt_inches=0.5), id="9-large-thin"),
    pytest.param(make_case(od_inches=30, wt_inches=1.5), id="10-mid-range"),
]


@pytest.mark.parametrize("inputs", VARIATIONS)
def test_conductor_mass_parametric(inputs):
    """Parametric variation — verify conductor mass calculation across input range."""
    od = outer_diameter_m(inputs["od_inches"])
    wt = wall_thickness_mm(inputs["wt_inches"])
    id_m = inner_diameter_m(od, wt)
    result = mass_per_unit_length(od, id_m, inputs["density"])

    # Physical bounds: mass must be positive and finite
    assert result > 0, f"Mass must be positive, got {result}"
    assert math.isfinite(result), f"Mass must be finite, got {result}"

    # Inner diameter must be positive (wall thickness can't exceed radius)
    assert id_m > 0, f"Inner diameter must be positive, got {id_m}"

    # Sanity: conductor mass typically 200-3000 kg/m for these sizes
    assert 50 < result < 5000, f"Mass {result} outside typical range 50-5000 kg/m"


@pytest.mark.parametrize("inputs", VARIATIONS)
def test_unit_conversions_parametric(inputs):
    """Parametric — verify unit conversions are consistent."""
    od = outer_diameter_m(inputs["od_inches"])
    wt = wall_thickness_mm(inputs["wt_inches"])

    # OD in meters must be OD_inches * 0.0254
    assert od == pytest.approx(inputs["od_inches"] * 0.0254, rel=1e-10)

    # WT in mm must be WT_inches * 25.4
    assert wt == pytest.approx(inputs["wt_inches"] * 25.4, rel=1e-10)
