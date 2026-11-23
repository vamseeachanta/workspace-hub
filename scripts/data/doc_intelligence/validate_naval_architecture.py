# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Validate extracted naval architecture data against IMO stability criteria
and hull coefficient ranges.

Usage:
    uv run --no-project python validate_naval_architecture.py \
        --input manifest.yaml --output report.yaml
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Hull coefficient range definitions per vessel type
# ---------------------------------------------------------------------------

_HULL_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "cargo": {
        "Cb": (0.60, 0.85),
        "Cw": (0.70, 0.92),
    },
    "tanker": {
        "Cb": (0.75, 0.85),
        "Cw": (0.80, 0.92),
    },
    "container": {
        "Cb": (0.55, 0.70),
        "Cw": (0.65, 0.80),
    },
    "naval": {
        "Cb": (0.45, 0.55),
        "Cw": (0.65, 0.75),
    },
    "general": {
        "Cb": (0.40, 0.90),
        "Cw": (0.60, 0.95),
    },
}

# IMO Intact Stability Code 2008 — minimum thresholds
_IMO_THRESHOLDS = {
    "GZ_area_0_30": 0.055,   # m·rad
    "GZ_area_0_40": 0.090,   # m·rad
    "GZ_area_30_40": 0.030,  # m·rad
    "GZ_max_angle": 25.0,    # degrees
    "GM0": 0.15,             # m
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_hull_coefficients(
    Cb: float,
    vessel_type: str,
    Cw: float | None = None,
    Cm: float | None = None,
    Cp: float | None = None,
) -> dict[str, Any]:
    """Validate hull coefficients against known ranges for the vessel type.

    Falls back to "general" ranges for unrecognised vessel types.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
        }
    """
    ranges = _HULL_RANGES.get(vessel_type.lower(), _HULL_RANGES["general"])
    errors: list[str] = []
    warnings: list[str] = []

    # Block coefficient (always validated)
    cb_lo, cb_hi = ranges["Cb"]
    if not (cb_lo <= Cb <= cb_hi):
        errors.append(
            f"Cb={Cb:.4f} out of range [{cb_lo}, {cb_hi}] for vessel_type='{vessel_type}'"
        )

    # Waterplane coefficient (optional)
    if Cw is not None and "Cw" in ranges:
        cw_lo, cw_hi = ranges["Cw"]
        if not (cw_lo <= Cw <= cw_hi):
            errors.append(
                f"Cw={Cw:.4f} out of range [{cw_lo}, {cw_hi}] for vessel_type='{vessel_type}'"
            )

    # Midship and prismatic coefficients — no hard range defined; warn if unusual
    if Cm is not None:
        if not (0.80 <= Cm <= 1.00):
            warnings.append(f"Cm={Cm:.4f} outside typical range [0.80, 1.00]")

    if Cp is not None:
        if not (0.55 <= Cp <= 0.90):
            warnings.append(f"Cp={Cp:.4f} outside typical range [0.55, 0.90]")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_imo_stability(
    GZ_area_0_30: float,
    GZ_area_0_40: float,
    GZ_max_angle: float,
    GM0: float,
    GZ_area_30_40: float | None = None,
) -> dict[str, Any]:
    """Check IMO Intact Stability Code 2008 criteria.

    Returns:
        {
            "pass": bool,
            "criteria": [
                {
                    "name": str,
                    "required": float,
                    "actual": float,
                    "met": bool,
                },
                ...
            ],
        }
    """
    criteria: list[dict[str, Any]] = []

    def _check(name: str, actual: float, required: float) -> None:
        criteria.append(
            {
                "name": name,
                "required": required,
                "actual": actual,
                "met": actual >= required,
            }
        )

    _check("GZ_area_0_30", GZ_area_0_30, _IMO_THRESHOLDS["GZ_area_0_30"])
    _check("GZ_area_0_40", GZ_area_0_40, _IMO_THRESHOLDS["GZ_area_0_40"])
    _check("GZ_max_angle", GZ_max_angle, _IMO_THRESHOLDS["GZ_max_angle"])
    _check("GM0", GM0, _IMO_THRESHOLDS["GM0"])

    if GZ_area_30_40 is not None:
        _check("GZ_area_30_40", GZ_area_30_40, _IMO_THRESHOLDS["GZ_area_30_40"])

    return {
        "pass": all(c["met"] for c in criteria),
        "criteria": criteria,
    }


def validate_from_manifest(manifest_dict: dict[str, Any]) -> dict[str, Any]:
    """Extract naval architecture parameters from a manifest and run both validators.

    Expects manifest structure:
        naval_architecture:
          vessel_type: cargo
          Cb: 0.75
          Cw: 0.85          # optional
          Cm: 0.99          # optional
          Cp: 0.78          # optional
          stability:        # optional block
            GZ_area_0_30: 0.060
            GZ_area_0_40: 0.095
            GZ_max_angle: 30
            GM0: 0.20
            GZ_area_30_40: 0.035   # optional

    Returns:
        {
            "hull": <validate_hull_coefficients result>,
            "stability": <validate_imo_stability result> | None,
        }
    """
    na = manifest_dict.get("naval_architecture", {})
    vessel_type = na.get("vessel_type", "general")
    Cb = float(na["Cb"])

    hull_result = validate_hull_coefficients(
        Cb=Cb,
        vessel_type=vessel_type,
        Cw=na.get("Cw"),
        Cm=na.get("Cm"),
        Cp=na.get("Cp"),
    )

    stability_block = na.get("stability")
    if stability_block:
        stability_result = validate_imo_stability(
            GZ_area_0_30=float(stability_block["GZ_area_0_30"]),
            GZ_area_0_40=float(stability_block["GZ_area_0_40"]),
            GZ_max_angle=float(stability_block["GZ_max_angle"]),
            GM0=float(stability_block["GM0"]),
            GZ_area_30_40=(
                float(stability_block["GZ_area_30_40"])
                if "GZ_area_30_40" in stability_block
                else None
            ),
        )
    else:
        stability_result = None

    return {
        "hull": hull_result,
        "stability": stability_result,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate naval architecture data against IMO criteria."
    )
    parser.add_argument("--input", required=True, help="Manifest YAML file path")
    parser.add_argument("--output", required=True, help="Output YAML report path")
    args = parser.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)

    report = validate_from_manifest(manifest)

    with open(args.output, "w", encoding="utf-8") as fh:
        yaml.dump(report, fh, default_flow_style=False, sort_keys=False)

    hull_ok = report["hull"]["valid"]
    stab_ok = report["stability"]["pass"] if report["stability"] else None
    print(f"Hull validation: {'PASS' if hull_ok else 'FAIL'}")
    if stab_ok is not None:
        print(f"IMO stability:   {'PASS' if stab_ok else 'FAIL'}")
    print(f"Report written to {args.output}")
    return 0 if (hull_ok and (stab_ok is None or stab_ok)) else 1


if __name__ == "__main__":
    sys.exit(main())
