#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
normalize_units.py — Unit normalization for O&G engineering.

Supports SI / Imperial / Field unit systems covering pressure, length,
volume, mass, temperature, density, flow, force, and stress.

Conversion strategy
-------------------
Each category stores conversion factors relative to a canonical SI base
unit (e.g. Pa for pressure, m for length).  Temperature is handled as a
special case using affine (offset + scale) transforms to/from Kelvin.

Usage (CLI)
-----------
  uv run --no-project python normalize_units.py --from-unit psi --to-unit MPa --value 1000
  uv run --no-project python normalize_units.py --list
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Unit registry
# ---------------------------------------------------------------------------
# Structure per non-temperature category:
#   { unit_string: (factor_to_SI_base, SI_base_unit, system) }
# where value_in_SI = value * factor_to_SI_base
#
# Temperature uses a separate registry (affine transforms).

_UNIT_REGISTRY: Dict[str, Tuple[float, str, str]] = {
    # ---- Pressure (base: Pa) -------------------------------------------
    "Pa":    (1.0,          "Pa", "SI"),
    "kPa":   (1e3,          "Pa", "SI"),
    "MPa":   (1e6,          "Pa", "SI"),
    "GPa":   (1e9,          "Pa", "SI"),        # also used for stress
    "bar":   (1e5,          "Pa", "SI"),
    "atm":   (101325.0,     "Pa", "Imperial"),
    "psi":   (6894.757,     "Pa", "Imperial"),
    "ksi":   (6894757.0,    "Pa", "Imperial"),  # 1 ksi = 1000 psi
    # ---- Length (base: m) -----------------------------------------------
    "m":     (1.0,          "m",  "SI"),
    "mm":    (1e-3,         "m",  "SI"),
    "cm":    (1e-2,         "m",  "SI"),
    "km":    (1e3,          "m",  "SI"),
    "ft":    (0.3048,       "m",  "Imperial"),
    "in":    (0.0254,       "m",  "Imperial"),
    "mi":    (1609.344,     "m",  "Imperial"),
    # ---- Volume (base: m³) ----------------------------------------------
    "m3":    (1.0,          "m3", "SI"),
    "L":     (1e-3,         "m3", "SI"),
    "bbl":   (0.158987,     "m3", "Field"),
    "gal":   (3.785411784e-3, "m3", "Imperial"),
    # ---- Mass (base: kg) ------------------------------------------------
    "kg":    (1.0,          "kg", "SI"),
    "g":     (1e-3,         "kg", "SI"),
    "tonne": (1000.0,       "kg", "SI"),        # metric tonne
    "lb":    (0.45359237,   "kg", "Imperial"),
    "ton":   (907.18474,    "kg", "Imperial"),  # short ton (US) = 2000 lb
    # ---- Density (base: kg/m³) ------------------------------------------
    "kg/m3": (1.0,          "kg/m3", "SI"),
    "lb/ft3":(16.01846337,  "kg/m3", "Imperial"),
    # ---- Flow (base: m³/s) ----------------------------------------------
    "m3/s":  (1.0,          "m3/s", "SI"),
    "m3/d":  (1.0 / 86400.0, "m3/s", "SI"),
    "bbl/d": (0.158987 / 86400.0, "m3/s", "Field"),
    # ---- Force (base: N) ------------------------------------------------
    "N":     (1.0,          "N",  "SI"),
    "kN":    (1e3,          "N",  "SI"),
    "MN":    (1e6,          "N",  "SI"),
    "lbf":   (4.4482216153, "N",  "Imperial"),
    # ---- Stress (base: Pa — reuses pressure entries above) -------------
    # GPa, MPa, ksi, Pa, kPa already registered under pressure
}

# Temperature: affine transforms to/from Kelvin (K is SI base)
# to_K(v)   = v * scale + offset
# from_K(v) = (v - offset) / scale
_TEMP_REGISTRY: Dict[str, Tuple[float, float, str]] = {
    #        scale    offset   system
    "K":  (1.0,      0.0,     "SI"),
    "C":  (1.0,      273.15,  "SI"),
    "F":  (5.0/9.0,  459.67 * 5.0/9.0, "Imperial"),
    # F→K: K = (F + 459.67) * 5/9
}

_TEMPERATURE_UNITS = set(_TEMP_REGISTRY.keys())

# Category map for list_supported_units()
_CATEGORY_MAP: Dict[str, List[str]] = {
    "pressure":    ["Pa", "kPa", "MPa", "GPa", "bar", "atm", "psi", "ksi"],
    "length":      ["m", "mm", "cm", "km", "ft", "in", "mi"],
    "volume":      ["m3", "L", "bbl", "gal"],
    "mass":        ["kg", "g", "tonne", "lb", "ton"],
    "temperature": ["K", "C", "F"],
    "density":     ["kg/m3", "lb/ft3"],
    "flow":        ["m3/s", "m3/d", "bbl/d"],
    "force":       ["N", "kN", "MN", "lbf"],
    "stress":      ["Pa", "kPa", "MPa", "GPa", "psi", "ksi"],
}

# SI base unit per category (used by get_si_equivalent)
_CATEGORY_SI_BASE: Dict[str, str] = {
    "pressure":    "Pa",
    "length":      "m",
    "volume":      "m3",
    "mass":        "kg",
    "temperature": "K",
    "density":     "kg/m3",
    "flow":        "m3/s",
    "force":       "N",
    "stress":      "Pa",
}


def _unit_category(unit: str) -> str:
    """Return the category name for *unit*, raising ValueError if unknown."""
    if unit in _TEMPERATURE_UNITS:
        return "temperature"
    for cat, units in _CATEGORY_MAP.items():
        if cat == "temperature":
            continue
        if unit in units:
            return cat
    raise ValueError(f"Unknown unit: {unit!r}")


def _to_kelvin(value: float, unit: str) -> float:
    scale, offset, _ = _TEMP_REGISTRY[unit]
    return value * scale + offset


def _from_kelvin(value_k: float, unit: str) -> float:
    scale, offset, _ = _TEMP_REGISTRY[unit]
    return (value_k - offset) / scale


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize(from_unit: str, to_unit: str, value: float) -> float:
    """Convert *value* from *from_unit* to *to_unit*.

    Raises
    ------
    ValueError
        If either unit is unknown, or if the units belong to different
        physical categories (e.g. pressure vs length).
    """
    # Validate units exist
    if from_unit not in _UNIT_REGISTRY and from_unit not in _TEMPERATURE_UNITS:
        raise ValueError(f"Unknown unit: {from_unit!r}")
    if to_unit not in _UNIT_REGISTRY and to_unit not in _TEMPERATURE_UNITS:
        raise ValueError(f"Unknown unit: {to_unit!r}")

    # Identity shortcut
    if from_unit == to_unit:
        return float(value)

    from_cat = _unit_category(from_unit)
    to_cat = _unit_category(to_unit)
    if from_cat != to_cat:
        raise ValueError(
            f"Cannot convert between categories {from_cat!r} and {to_cat!r}"
        )

    # Temperature (affine)
    if from_cat == "temperature":
        return _from_kelvin(_to_kelvin(value, from_unit), to_unit)

    # All other categories (linear scaling through SI base)
    from_factor, _, _ = _UNIT_REGISTRY[from_unit]
    to_factor, _, _ = _UNIT_REGISTRY[to_unit]
    return value * from_factor / to_factor


def detect_system(unit: str) -> str:
    """Return the unit system: ``"SI"``, ``"Imperial"``, or ``"Field"``.

    Raises
    ------
    ValueError
        If *unit* is not in the registry.
    """
    if unit in _TEMPERATURE_UNITS:
        _, _, system = _TEMP_REGISTRY[unit]
        return system
    if unit in _UNIT_REGISTRY:
        _, _, system = _UNIT_REGISTRY[unit]
        return system
    raise ValueError(f"Unknown unit: {unit!r}")


def get_si_equivalent(value: float, unit: str) -> Tuple[float, str]:
    """Convert *value* in *unit* to its SI base unit.

    Returns
    -------
    (si_value, si_unit)
    """
    cat = _unit_category(unit)
    si_base = _CATEGORY_SI_BASE[cat]

    if cat == "temperature":
        return _to_kelvin(value, unit), "K"

    factor, _, _ = _UNIT_REGISTRY[unit]
    si_factor, _, _ = _UNIT_REGISTRY[si_base]
    return value * factor / si_factor, si_base


def list_supported_units() -> Dict[str, List[str]]:
    """Return ``{category: [unit, ...]}`` for all supported units."""
    return {cat: list(units) for cat, units in _CATEGORY_MAP.items()}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert values between engineering unit systems."
    )
    p.add_argument("--from-unit", help="Source unit (e.g. psi)")
    p.add_argument("--to-unit", help="Target unit (e.g. MPa)")
    p.add_argument("--value", type=float, help="Numeric value to convert")
    p.add_argument(
        "--list", action="store_true", help="List all supported units by category"
    )
    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.list:
        units = list_supported_units()
        for cat, unit_list in units.items():
            print(f"{cat}: {', '.join(unit_list)}")
        return

    if not (args.from_unit and args.to_unit and args.value is not None):
        parser.error("--from-unit, --to-unit, and --value are all required")

    try:
        result = normalize(args.from_unit, args.to_unit, args.value)
        print(f"{args.value} {args.from_unit} = {result} {args.to_unit}")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
