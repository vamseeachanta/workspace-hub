"""
stub_orcaflex.py — OrcaFlex solver stub for the multi-physics pipeline.

Provides a drop-in replacement for OrcFxAPI when Orcina's commercial library
is not installed (CI, ace-linux-1, open-source environments).

The stub computes simplified structural response using beam theory:
    Static deflection of a fixed-free beam under uniform transverse load:
        delta = (w * L^4) / (8 * E * I)
    where w = force_per_unit_length [N/m], L = length [m].

For mooring tension:
    T = axial_stiffness * (elongation_fraction)

Usage:
    # In the pipeline, check for OrcFxAPI and fall back:
    try:
        import OrcFxAPI
        result = run_orcaflex_real(model_path, loads_csv)
    except ImportError:
        from stubs.stub_orcaflex import run_orcaflex_stub
        result = run_orcaflex_stub(loads_csv, diameter, length, ...)
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any


# Default structural parameters for a 1 m diameter steel cylinder
_DEFAULT_YOUNGS_MODULUS = 200e9   # Pa (steel)
_DEFAULT_WALL_THICKNESS = 0.05   # m (50 mm wall)
_DEFAULT_MOORING_EA = 1.2e9      # N (typical chain EA)
_DEFAULT_MOORING_LENGTH = 200.0  # m


def run_orcaflex_stub(
    loads_csv: str | Path,
    diameter: float,
    length: float,
    youngs_modulus: float = _DEFAULT_YOUNGS_MODULUS,
    wall_thickness: float = _DEFAULT_WALL_THICKNESS,
    mooring_ea: float = _DEFAULT_MOORING_EA,
    mooring_length: float = _DEFAULT_MOORING_LENGTH,
) -> dict[str, Any]:
    """Compute simplified structural response to applied fluid loads.

    Reads ``loads_csv`` (OrcaFlex load time-history CSV) and computes:
    - Maximum mid-span deflection of the cylinder as a fixed-free cantilever
    - Peak axial tension in a simplified mooring line

    Args:
        loads_csv: Path to the loads CSV from convert_openfoam_to_orcaflex.py.
        diameter: Cylinder outer diameter [m].
        length: Cylinder length [m].
        youngs_modulus: Young's modulus of the cylinder material [Pa].
        wall_thickness: Cylinder wall thickness [m].
        mooring_ea: Mooring line axial stiffness [N].
        mooring_length: Mooring line length [m].

    Returns:
        Result dict with keys: passed, max_deflection_m, max_tension_N,
        max_fx_N, time_range, issues.
    """
    loads_csv = Path(loads_csv)
    result: dict[str, Any] = {
        "loads_csv": str(loads_csv),
        "passed": False,
        "max_deflection_m": 0.0,
        "max_tension_N": 0.0,
        "max_fx_N": 0.0,
        "time_range": [0.0, 0.0],
        "issues": [],
        "stub": True,
    }

    if not loads_csv.exists():
        result["issues"].append(f"Loads CSV not found: {loads_csv}")
        return result

    rows = _read_loads_csv(loads_csv, result)
    if not rows:
        return result

    times = [r[0] for r in rows]
    fx_values = [r[1] for r in rows]
    fy_values = [r[2] for r in rows]

    max_fx = max(abs(f) for f in fx_values)
    max_fy = max(abs(f) for f in fy_values)
    max_transverse = max(max_fx, max_fy)
    result["max_fx_N"] = max_fx

    # Second moment of area for hollow cylinder
    r_outer = diameter / 2.0
    r_inner = r_outer - wall_thickness
    moment_of_inertia = (math.pi / 64.0) * (
        diameter ** 4 - (2 * r_inner) ** 4
    )

    # Load per unit length (uniform, cantilever)
    w = max_transverse / length

    # Fixed-free cantilever max deflection: delta = w*L^4 / (8*E*I)
    if youngs_modulus > 0 and moment_of_inertia > 0:
        deflection = (w * length ** 4) / (8.0 * youngs_modulus * moment_of_inertia)
    else:
        deflection = 0.0
        result["issues"].append("Invalid structural parameters — deflection is 0")

    result["max_deflection_m"] = round(deflection, 6)

    # Mooring tension: T = EA * (delta / mooring_length)
    # The horizontal force must be balanced by the mooring; tension ≈ max_fx
    if mooring_length > 0:
        elongation = deflection / mooring_length
        tension = mooring_ea * elongation + max_fx
    else:
        tension = max_fx

    result["max_tension_N"] = round(tension, 2)
    result["time_range"] = [times[0], times[-1]]
    result["passed"] = True

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_loads_csv(
    loads_csv: Path,
    result: dict[str, Any],
) -> list[tuple[float, ...]]:
    """Read the OrcaFlex load CSV into a list of numeric tuples."""
    rows: list[tuple[float, ...]] = []
    with open(loads_csv, newline="") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split(",")
            try:
                vals = tuple(float(p.strip()) for p in parts)
                if len(vals) >= 4:
                    rows.append(vals)
            except ValueError:
                continue  # header row

    if not rows:
        result["issues"].append("No numeric data rows in loads CSV")

    return rows
