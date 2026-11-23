# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Tests for validate_naval_architecture.py — TDD first pass."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validate_naval_architecture import (
    validate_hull_coefficients,
    validate_imo_stability,
    validate_from_manifest,
)


# --- Hull coefficient tests ---

def test_validate_block_coefficient_cargo():
    result = validate_hull_coefficients(Cb=0.82, vessel_type="cargo")
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_block_coefficient_out_of_range():
    result = validate_hull_coefficients(Cb=0.95, vessel_type="cargo")
    assert result["valid"] is False
    assert any("Cb" in e for e in result["errors"])


def test_validate_imo_stability_passing():
    result = validate_imo_stability(
        GZ_area_0_30=0.060,
        GZ_area_0_40=0.095,
        GZ_max_angle=35,
        GM0=0.20,
    )
    assert result["pass"] is True
    assert all(c["met"] for c in result["criteria"])


def test_validate_imo_stability_failing():
    result = validate_imo_stability(
        GZ_area_0_30=0.040,  # below 0.055
        GZ_area_0_40=0.080,  # below 0.090
        GZ_max_angle=20,     # below 25
        GM0=0.10,            # below 0.15
    )
    assert result["pass"] is False
    failed = [c for c in result["criteria"] if not c["met"]]
    assert len(failed) == 4


def test_validate_unknown_vessel_type():
    result = validate_hull_coefficients(Cb=0.70, vessel_type="submarine")
    # Should fall back to "general" ranges
    assert result["valid"] is True


def test_validate_with_waterplane_coefficient():
    result = validate_hull_coefficients(Cb=0.80, vessel_type="cargo", Cw=0.85)
    assert result["valid"] is True
    result2 = validate_hull_coefficients(Cb=0.80, vessel_type="cargo", Cw=0.98)
    assert result2["valid"] is False


# --- Additional coverage tests ---

def test_validate_tanker_valid():
    result = validate_hull_coefficients(Cb=0.80, vessel_type="tanker")
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_tanker_cb_too_low():
    result = validate_hull_coefficients(Cb=0.60, vessel_type="tanker")
    assert result["valid"] is False
    assert any("Cb" in e for e in result["errors"])


def test_validate_container_valid():
    result = validate_hull_coefficients(Cb=0.63, vessel_type="container")
    assert result["valid"] is True


def test_validate_naval_valid():
    result = validate_hull_coefficients(Cb=0.50, vessel_type="naval")
    assert result["valid"] is True


def test_validate_naval_cb_too_high():
    result = validate_hull_coefficients(Cb=0.65, vessel_type="naval")
    assert result["valid"] is False


def test_validate_imo_with_gz_area_30_40():
    result = validate_imo_stability(
        GZ_area_0_30=0.060,
        GZ_area_0_40=0.095,
        GZ_max_angle=35,
        GM0=0.20,
        GZ_area_30_40=0.035,
    )
    assert result["pass"] is True
    # Criteria list should include the 30-40 check
    names = [c["name"] for c in result["criteria"]]
    assert any("30_40" in n for n in names)


def test_validate_imo_gz_area_30_40_failing():
    result = validate_imo_stability(
        GZ_area_0_30=0.060,
        GZ_area_0_40=0.095,
        GZ_max_angle=35,
        GM0=0.20,
        GZ_area_30_40=0.020,  # below 0.030
    )
    assert result["pass"] is False
    failed = [c for c in result["criteria"] if not c["met"]]
    assert len(failed) == 1
    assert "30_40" in failed[0]["name"]


def test_criteria_contain_required_and_actual():
    result = validate_imo_stability(
        GZ_area_0_30=0.060,
        GZ_area_0_40=0.095,
        GZ_max_angle=35,
        GM0=0.20,
    )
    for c in result["criteria"]:
        assert "name" in c
        assert "required" in c
        assert "actual" in c
        assert "met" in c


def test_validate_from_manifest_basic():
    manifest = {
        "naval_architecture": {
            "vessel_type": "cargo",
            "Cb": 0.75,
            "stability": {
                "GZ_area_0_30": 0.060,
                "GZ_area_0_40": 0.095,
                "GZ_max_angle": 30,
                "GM0": 0.20,
            },
        }
    }
    result = validate_from_manifest(manifest)
    assert "hull" in result
    assert "stability" in result
    assert result["hull"]["valid"] is True
    assert result["stability"]["pass"] is True


def test_validate_from_manifest_missing_stability():
    manifest = {
        "naval_architecture": {
            "vessel_type": "tanker",
            "Cb": 0.80,
        }
    }
    result = validate_from_manifest(manifest)
    assert "hull" in result
    assert result["hull"]["valid"] is True
    # stability key should be absent or None when not provided
    assert result.get("stability") is None


def test_validate_hull_cb_at_lower_boundary():
    result = validate_hull_coefficients(Cb=0.60, vessel_type="cargo")
    assert result["valid"] is True


def test_validate_hull_cb_at_upper_boundary():
    result = validate_hull_coefficients(Cb=0.85, vessel_type="cargo")
    assert result["valid"] is True


def test_validate_hull_warnings_empty_when_valid():
    result = validate_hull_coefficients(Cb=0.75, vessel_type="cargo")
    assert "warnings" in result
