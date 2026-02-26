"""
stub_openfoam.py — OpenFOAM solver stub for the multi-physics pipeline.

Writes synthetic solver log and postProcessing/forces output files so that
Gate 2 (CFD convergence) can be validated without a running OpenFOAM install.

The drag force is computed analytically:
    F_drag = 0.5 * rho * U^2 * D * L * Cd   (Cd=1.0 for a bluff cylinder)

Usage:
    from stubs.stub_openfoam import run_openfoam_stub
    result = run_openfoam_stub(
        case_dir="of_case",
        diameter=1.0,
        length=5.0,
        velocity=1.0,
        rho=1025.0,
    )
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any


# Residuals at final iteration (all below 1e-4 to pass Gate 2)
_FINAL_RESIDUALS = {
    "Ux": 3.2e-5,
    "Uy": 1.8e-5,
    "Uz": 9.1e-6,
    "p": 7.4e-5,
    "k": 4.6e-5,
    "omega": 5.9e-5,
}

# Number of synthetic time steps written to force.dat
_N_TIME_STEPS = 50


def run_openfoam_stub(
    case_dir: str | Path,
    diameter: float,
    length: float,
    velocity: float,
    rho: float = 1025.0,
    n_iterations: int = 500,
) -> dict[str, Any]:
    """Produce synthetic OpenFOAM solver output in ``case_dir``.

    Creates:
    - ``log.simpleFoam`` with converging residuals
    - ``postProcessing/forces/0/force.dat`` with steady drag force

    Args:
        case_dir: OpenFOAM case directory (will be created if absent).
        diameter: Cylinder diameter [m].
        length: Cylinder length [m].
        velocity: Free-stream velocity [m/s].
        rho: Fluid density [kg/m³].
        n_iterations: Number of synthetic solver iterations in the log.

    Returns:
        Result dict with keys: passed, log_path, forces_path, drag_force_N.
    """
    case_dir = Path(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)

    # Analytical drag
    cd = 1.0
    drag_n = 0.5 * rho * velocity ** 2 * diameter * length * cd
    lift_n = 0.0  # steady state — no lift

    log_path = case_dir / "log.simpleFoam"
    _write_solver_log(log_path, n_iterations)

    forces_dir = case_dir / "postProcessing" / "forces" / "0"
    forces_dir.mkdir(parents=True, exist_ok=True)
    forces_path = forces_dir / "force.dat"
    _write_forces_dat(forces_path, drag_n, lift_n, n_time_steps=_N_TIME_STEPS)

    return {
        "passed": True,
        "log_path": str(log_path),
        "forces_path": str(forces_path),
        "drag_force_N": round(drag_n, 2),
        "stub": True,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _write_solver_log(log_path: Path, n_iterations: int) -> None:
    """Write a synthetic simpleFoam log with converging residuals."""
    lines = [
        "/*---------------------------------------------------------------------------*\\",
        "  OpenFOAM simpleFoam solver (STUB — no actual solve performed)",
        "\\*---------------------------------------------------------------------------*/",
        "",
        "Starting time loop",
        "",
    ]

    for it in range(1, n_iterations + 1):
        # Residuals decay exponentially from 1e-1 to below 1e-5
        decay = math.exp(-it / (n_iterations / 10.0))
        for field, final_val in _FINAL_RESIDUALS.items():
            init = min(0.1, final_val * 1e3 * decay + final_val)
            final = final_val + final_val * 0.1 * decay
            lines.append(
                f"Solving for {field}, "
                f"Initial residual = {init:.4e}, "
                f"Final residual = {final:.4e}, "
                f"No Iterations 1"
            )

        lines.append(f"Time = {it * 0.1:.1f}")
        lines.append(f"ExecutionTime = {it * 0.5:.1f} s")
        lines.append("")

    lines.append("End")
    log_path.write_text("\n".join(lines))


def _write_forces_dat(
    forces_path: Path,
    drag_n: float,
    lift_n: float,
    n_time_steps: int,
) -> None:
    """Write a synthetic postProcessing/forces/0/force.dat file.

    Format (OpenFOAM forces function object):
        # Time (Fpx Fpy Fpz) (Fvx Fvy Fvz) (Mopx Mopy Mopz) ...
    Pressure Fx = 85% of drag; viscous Fx = 15%.
    """
    lines = [
        "# Time         (Fpx           Fpy    Fpz)    "
        "(Fvx           Fvy    Fvz)    "
        "(Mopx  Mopy  Mopz)  (Movx  Movy  Movz)",
    ]

    fp_frac = 0.85
    fv_frac = 0.15

    for i in range(n_time_steps):
        t = i * 0.1
        # Add small random-like oscillation around steady drag
        noise = drag_n * 0.01 * math.sin(i * 0.37) * math.exp(-i / 30.0)
        fpx = drag_n * fp_frac + noise
        fpy = lift_n * fp_frac
        fpz = 0.0
        fvx = drag_n * fv_frac
        fvy = 0.0
        fvz = 0.0
        mopx = 0.0
        mopy = 0.0
        mopz = drag_n * fp_frac * 0.01  # small pitching moment
        movx = 0.0
        movy = 0.0
        movz = 0.0
        lines.append(
            f"{t:.3f}         "
            f"({fpx:.4f} {fpy:.4f} {fpz:.4f})  "
            f"({fvx:.4f} {fvy:.4f} {fvz:.4f})  "
            f"({mopx:.4f} {mopy:.4f} {mopz:.4f})  "
            f"({movx:.4f} {movy:.4f} {movz:.4f})"
        )

    forces_path.write_text("\n".join(lines) + "\n")
