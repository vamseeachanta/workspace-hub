"""
convert_openfoam_to_orcaflex.py — Format converter: OpenFOAM surface forces →
OrcaFlex load time-history CSV.

Reads OpenFOAM ``postProcessing/forces/0/force.dat`` (or the equivalent
``forces.dat`` from the ``forces`` function object) and writes a CSV file
compatible with the OrcaFlex ``LoadAppliedToEnvironment`` API, which accepts
a six-component force/moment time series.

Usage (standalone):
    python convert_openfoam_to_orcaflex.py \\
        --forces postProcessing/forces/0/force.dat \\
        --output loads.csv \\
        [--scale-factor 1.0] [--time-step 0.1]

Output CSV columns (SI units):
    Time [s], Fx [N], Fy [N], Fz [N], Mx [N.m], My [N.m], Mz [N.m]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert(
    forces_path: str | Path,
    output_csv: str | Path,
    scale_factor: float = 1.0,
    time_step: float | None = None,
) -> dict[str, Any]:
    """Convert OpenFOAM forces output to OrcaFlex load time-history CSV.

    The function handles two common OpenFOAM forces output formats:
    - ``force.dat``: bracketed tuples, one row per time step
    - ``forces.dat``: similar format with slightly different header

    Args:
        forces_path: Path to the OpenFOAM force output file.
        output_csv: Destination CSV file path.
        scale_factor: Multiply all force/moment components by this factor.
            Use to convert units (e.g. model scale → full scale).
        time_step: If provided, re-sample the time series to this step size.

    Returns:
        Result dict with keys: passed, row_count, time_range, issues.
    """
    forces_path = Path(forces_path)
    output_csv = Path(output_csv)

    result: dict[str, Any] = {
        "forces_path": str(forces_path),
        "output_csv": str(output_csv),
        "passed": False,
        "row_count": 0,
        "time_range": [0.0, 0.0],
        "issues": [],
    }

    if not forces_path.exists():
        result["issues"].append(f"Forces file not found: {forces_path}")
        return result

    rows = _parse_forces_file(forces_path, result)
    if not rows:
        return result

    if scale_factor != 1.0:
        rows = [
            (t,) + tuple(v * scale_factor for v in fmoms)
            for t, *fmoms in rows
        ]

    if time_step is not None:
        rows = _resample(rows, time_step)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(rows, output_csv, result)

    if result["row_count"] > 0:
        result["passed"] = True
        result["time_range"] = [rows[0][0], rows[-1][0]]

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_forces_file(
    forces_path: Path,
    result: dict[str, Any],
) -> list[tuple]:
    """Parse OpenFOAM force.dat into list of (t, Fx, Fy, Fz, Mx, My, Mz)."""
    lines = forces_path.read_text(errors="replace").splitlines()
    rows: list[tuple] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Extract all floating-point numbers from the line
        nums = re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?", stripped)
        if len(nums) < 7:
            continue

        try:
            vals = [float(x) for x in nums]
        except ValueError:
            continue

        # Layout: time  (Fpx Fpy Fpz) (Fvx Fvy Fvz) (Mopx Mopy Mopz) ...
        # Total force = pressure + viscous
        t = vals[0]
        fx = vals[1] + vals[4]  # Fpx + Fvx
        fy = vals[2] + vals[5]
        fz = vals[3] + vals[6]
        # Moments (indices 7-9 = pressure moments, 10-12 = viscous moments)
        mx = vals[7] + vals[10] if len(vals) > 12 else 0.0
        my = vals[8] + vals[11] if len(vals) > 12 else 0.0
        mz = vals[9] + vals[12] if len(vals) > 12 else 0.0

        rows.append((t, fx, fy, fz, mx, my, mz))

    if not rows:
        result["issues"].append("No valid data rows found in forces file")

    return rows


def _resample(
    rows: list[tuple],
    target_dt: float,
) -> list[tuple]:
    """Linearly interpolate rows to a uniform time step."""
    if len(rows) < 2:
        return rows

    t_start = rows[0][0]
    t_end = rows[-1][0]
    n_steps = max(2, int(round((t_end - t_start) / target_dt)) + 1)
    new_times = [t_start + i * target_dt for i in range(n_steps)]

    resampled: list[tuple] = []
    j = 0
    for t_new in new_times:
        if t_new > t_end:
            t_new = t_end
        # Advance j so rows[j] <= t_new < rows[j+1]
        while j < len(rows) - 2 and rows[j + 1][0] <= t_new:
            j += 1

        t0, t1 = rows[j][0], rows[j + 1][0]
        alpha = (t_new - t0) / (t1 - t0) if (t1 - t0) > 1e-12 else 0.0
        interp = tuple(
            rows[j][k] + alpha * (rows[j + 1][k] - rows[j][k])
            for k in range(len(rows[0]))
        )
        resampled.append((t_new,) + interp[1:])

    return resampled


def _write_csv(
    rows: list[tuple],
    output_csv: Path,
    result: dict[str, Any],
) -> None:
    """Write rows to CSV with OrcaFlex-compatible header."""
    with open(output_csv, "w", newline="") as fh:
        fh.write(
            "# OpenFOAM surface force export → OrcaFlex load time-history\n"
            "# Generated by convert_openfoam_to_orcaflex.py\n"
            "# Units: time [s], force [N], moment [N.m]\n"
        )
        writer = csv.writer(fh)
        writer.writerow(["Time", "Fx", "Fy", "Fz", "Mx", "My", "Mz"])
        for row in rows:
            writer.writerow([f"{v:.6g}" for v in row])

    result["row_count"] = len(rows)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert OpenFOAM forces to OrcaFlex load CSV"
    )
    parser.add_argument(
        "--forces",
        required=True,
        help="Path to OpenFOAM postProcessing/forces/0/force.dat",
    )
    parser.add_argument(
        "--output", required=True, help="Destination OrcaFlex loads CSV"
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=1.0,
        help="Multiply all force/moment values by this factor (default: 1.0)",
    )
    parser.add_argument(
        "--time-step",
        type=float,
        default=None,
        help="Re-sample to uniform time step [s]",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    result = convert(
        forces_path=args.forces,
        output_csv=args.output,
        scale_factor=args.scale_factor,
        time_step=args.time_step,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[Converter 2 — OF Forces→OrcaFlex CSV] {status}")
        print(f"  Rows written  : {result['row_count']}")
        if result["row_count"] > 0:
            t0, t1 = result["time_range"]
            print(f"  Time range    : {t0:.2f} → {t1:.2f} s")
        print(f"  Output CSV    : {result['output_csv']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  WARNING: {issue}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
