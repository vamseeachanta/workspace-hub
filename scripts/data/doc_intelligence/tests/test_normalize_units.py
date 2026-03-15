"""
Tests for normalize_units.py — unit normalization for O&G engineering.
TDD: these tests were written before the implementation.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from normalize_units import (
    normalize,
    detect_system,
    get_si_equivalent,
    list_supported_units,
)


# ---------------------------------------------------------------------------
# normalize — pressure
# ---------------------------------------------------------------------------

def test_normalize_pressure_psi_to_mpa():
    assert normalize("psi", "MPa", 1000.0) == pytest.approx(6.8948, rel=1e-3)


def test_normalize_pressure_mpa_to_psi():
    assert normalize("MPa", "psi", 6.8948) == pytest.approx(1000.0, rel=1e-3)


def test_normalize_pressure_bar_to_kpa():
    assert normalize("bar", "kPa", 1.0) == pytest.approx(100.0, rel=1e-4)


def test_normalize_pressure_atm_to_bar():
    assert normalize("atm", "bar", 1.0) == pytest.approx(1.01325, rel=1e-4)


def test_normalize_pressure_ksi_to_mpa():
    assert normalize("ksi", "MPa", 1.0) == pytest.approx(6.8948, rel=1e-3)


def test_normalize_pressure_psi_to_kpa():
    assert normalize("psi", "kPa", 1.0) == pytest.approx(6.8948, rel=1e-3)


# ---------------------------------------------------------------------------
# normalize — length
# ---------------------------------------------------------------------------

def test_normalize_length_ft_to_m():
    assert normalize("ft", "m", 100.0) == pytest.approx(30.48, rel=1e-4)


def test_normalize_length_m_to_ft():
    assert normalize("m", "ft", 30.48) == pytest.approx(100.0, rel=1e-4)


def test_normalize_length_in_to_mm():
    assert normalize("in", "mm", 1.0) == pytest.approx(25.4, rel=1e-5)


def test_normalize_length_km_to_mi():
    assert normalize("km", "mi", 1.0) == pytest.approx(0.621371, rel=1e-4)


def test_normalize_length_cm_to_m():
    assert normalize("cm", "m", 100.0) == pytest.approx(1.0, rel=1e-6)


# ---------------------------------------------------------------------------
# normalize — volume
# ---------------------------------------------------------------------------

def test_normalize_volume_bbl_to_m3():
    assert normalize("bbl", "m3", 1.0) == pytest.approx(0.158987, rel=1e-4)


def test_normalize_volume_m3_to_bbl():
    assert normalize("m3", "bbl", 1.0) == pytest.approx(6.28981, rel=1e-4)


def test_normalize_volume_gal_to_L():
    assert normalize("gal", "L", 1.0) == pytest.approx(3.78541, rel=1e-4)


def test_normalize_volume_L_to_m3():
    assert normalize("L", "m3", 1000.0) == pytest.approx(1.0, rel=1e-6)


# ---------------------------------------------------------------------------
# normalize — mass
# ---------------------------------------------------------------------------

def test_normalize_mass_lb_to_kg():
    assert normalize("lb", "kg", 1.0) == pytest.approx(0.453592, rel=1e-4)


def test_normalize_mass_ton_to_kg():
    # short ton (US) = 2000 lb
    assert normalize("ton", "kg", 1.0) == pytest.approx(907.185, rel=1e-3)


def test_normalize_mass_tonne_to_kg():
    # metric tonne
    assert normalize("tonne", "kg", 1.0) == pytest.approx(1000.0, rel=1e-6)


def test_normalize_mass_kg_to_lb():
    assert normalize("kg", "lb", 1.0) == pytest.approx(2.20462, rel=1e-4)


# ---------------------------------------------------------------------------
# normalize — temperature (offset conversions)
# ---------------------------------------------------------------------------

def test_temperature_f_to_c():
    assert normalize("F", "C", 212.0) == pytest.approx(100.0, rel=1e-4)


def test_temperature_c_to_f():
    assert normalize("C", "F", 0.0) == pytest.approx(32.0, rel=1e-4)


def test_temperature_c_to_k():
    assert normalize("C", "K", 0.0) == pytest.approx(273.15, rel=1e-4)


def test_temperature_k_to_c():
    assert normalize("K", "C", 273.15) == pytest.approx(0.0, abs=1e-6)


def test_temperature_f_to_k():
    assert normalize("F", "K", 32.0) == pytest.approx(273.15, rel=1e-4)


def test_temperature_k_to_f():
    assert normalize("K", "F", 273.15) == pytest.approx(32.0, abs=1e-4)


# ---------------------------------------------------------------------------
# normalize — density
# ---------------------------------------------------------------------------

def test_normalize_density_lbft3_to_kgm3():
    assert normalize("lb/ft3", "kg/m3", 1.0) == pytest.approx(16.0185, rel=1e-3)


def test_normalize_density_kgm3_to_lbft3():
    assert normalize("kg/m3", "lb/ft3", 16.0185) == pytest.approx(1.0, rel=1e-3)


# ---------------------------------------------------------------------------
# normalize — flow rate
# ---------------------------------------------------------------------------

def test_normalize_flow_bbld_to_m3d():
    assert normalize("bbl/d", "m3/d", 1.0) == pytest.approx(0.158987, rel=1e-4)


def test_normalize_flow_m3d_to_m3s():
    assert normalize("m3/d", "m3/s", 86400.0) == pytest.approx(1.0, rel=1e-4)


def test_normalize_flow_m3s_to_bbld():
    assert normalize("m3/s", "bbl/d", 1.0) == pytest.approx(543440.0, rel=1e-3)


# ---------------------------------------------------------------------------
# normalize — force
# ---------------------------------------------------------------------------

def test_normalize_force_lbf_to_n():
    assert normalize("lbf", "N", 1.0) == pytest.approx(4.44822, rel=1e-4)


def test_normalize_force_kn_to_n():
    assert normalize("kN", "N", 1.0) == pytest.approx(1000.0, rel=1e-6)


def test_normalize_force_n_to_lbf():
    assert normalize("N", "lbf", 4.44822) == pytest.approx(1.0, rel=1e-3)


# ---------------------------------------------------------------------------
# normalize — stress
# ---------------------------------------------------------------------------

def test_normalize_stress_ksi_to_mpa():
    assert normalize("ksi", "MPa", 1.0) == pytest.approx(6.8948, rel=1e-3)


def test_normalize_stress_mpa_to_gpa():
    assert normalize("MPa", "GPa", 1000.0) == pytest.approx(1.0, rel=1e-6)


def test_normalize_stress_gpa_to_ksi():
    assert normalize("GPa", "ksi", 1.0) == pytest.approx(145.038, rel=1e-3)


# ---------------------------------------------------------------------------
# normalize — same unit (identity)
# ---------------------------------------------------------------------------

def test_normalize_same_unit_m():
    assert normalize("m", "m", 42.0) == 42.0


def test_normalize_same_unit_psi():
    assert normalize("psi", "psi", 500.0) == 500.0


def test_normalize_same_unit_temperature_c():
    assert normalize("C", "C", 25.0) == 25.0


# ---------------------------------------------------------------------------
# normalize — error handling
# ---------------------------------------------------------------------------

def test_normalize_unknown_from_unit_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        normalize("furlongs", "m", 1.0)


def test_normalize_unknown_to_unit_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        normalize("m", "furlongs", 1.0)


def test_normalize_incompatible_categories_raises():
    with pytest.raises(ValueError):
        normalize("psi", "m", 1.0)


# ---------------------------------------------------------------------------
# detect_system
# ---------------------------------------------------------------------------

def test_detect_system_si_mpa():
    assert detect_system("MPa") == "SI"


def test_detect_system_si_m():
    assert detect_system("m") == "SI"


def test_detect_system_si_kg():
    assert detect_system("kg") == "SI"


def test_detect_system_imperial_psi():
    assert detect_system("psi") == "Imperial"


def test_detect_system_imperial_ft():
    assert detect_system("ft") == "Imperial"


def test_detect_system_imperial_lb():
    assert detect_system("lb") == "Imperial"


def test_detect_system_field_bbld():
    assert detect_system("bbl/d") == "Field"


def test_detect_system_field_bbl():
    assert detect_system("bbl") == "Field"


def test_detect_system_unknown_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        detect_system("furlongs")


# ---------------------------------------------------------------------------
# get_si_equivalent
# ---------------------------------------------------------------------------

def test_get_si_equivalent_pressure_psi():
    val, unit = get_si_equivalent(1000.0, "psi")
    assert unit == "Pa"
    assert val == pytest.approx(6894757.0, rel=1e-3)


def test_get_si_equivalent_length_ft():
    val, unit = get_si_equivalent(1.0, "ft")
    assert unit == "m"
    assert val == pytest.approx(0.3048, rel=1e-5)


def test_get_si_equivalent_mass_lb():
    val, unit = get_si_equivalent(1.0, "lb")
    assert unit == "kg"
    assert val == pytest.approx(0.453592, rel=1e-4)


def test_get_si_equivalent_temperature_f():
    val, unit = get_si_equivalent(32.0, "F")
    assert unit == "K"
    assert val == pytest.approx(273.15, rel=1e-4)


def test_get_si_equivalent_already_si():
    val, unit = get_si_equivalent(100.0, "m")
    assert unit == "m"
    assert val == pytest.approx(100.0)


def test_get_si_equivalent_unknown_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        get_si_equivalent(1.0, "furlongs")


# ---------------------------------------------------------------------------
# list_supported_units
# ---------------------------------------------------------------------------

def test_list_supported_units_returns_dict():
    result = list_supported_units()
    assert isinstance(result, dict)


def test_list_supported_units_has_categories():
    result = list_supported_units()
    for cat in ("pressure", "length", "volume", "mass", "temperature",
                "density", "flow", "force", "stress"):
        assert cat in result, f"Missing category: {cat}"


def test_list_supported_units_minimum_count():
    result = list_supported_units()
    total = sum(len(v) for v in result.values())
    assert total >= 30


def test_list_supported_units_pressure_has_psi():
    result = list_supported_units()
    assert "psi" in result["pressure"]
