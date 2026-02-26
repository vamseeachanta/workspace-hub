"""
validate_cfd_convergence.py — Gate 2 of the Gmsh→OpenFOAM→OrcaFlex pipeline.

Parses an OpenFOAM solver log for final residuals and checks the force balance
against a far-field reference value.

Usage (standalone):
    python validate_cfd_convergence.py --log /path/to/log.simpleFoam
    python validate_cfd_convergence.py \\
        --log /path/to/log.simpleFoam \\
        --forces /path/to/postProcessing/forces/0/force.dat \\
        --expected-fx 850.0

Thresholds:
    final residuals < RESIDUAL_LIMIT (1e-4 by default)
    force balance error < FORCE_BALANCE_LIMIT_PCT (5 % by default)
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
RESIDUAL_LIMIT = 1e-4
FORCE_BALANCE_LIMIT_PCT = 5.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_convergence(
    log_path: str | Path,
    forces_path: str | Path | None = None,
    expected_fx: float | None = None,
) -> dict[str, Any]:
    """Check OpenFOAM solver convergence and (optionally) force balance.

    Args:
        log_path: Path to the simpleFoam / pimpleFoam solver log.
        forces_path: Path to the OpenFOAM forces postProcessing file
            (postProcessing/forces/0/force.dat).  Optional.
        expected_fx: Expected drag force [N] for balance check.  Optional.
            When provided, the check computes the relative error between the
            CFD-integrated force and this reference.

    Returns:
        Result dict with keys: passed, converged, final_residuals,
        force_balance, issues.
    """
    log_path = Path(log_path)
    result: dict[str, Any] = {
        "log_path": str(log_path),
        "passed": True,
        "converged": False,
        "final_residuals": {},
        "force_balance": {},
        "issues": [],
    }

    if not log_path.exists():
        result["passed"] = False
        result["issues"].append(f"Log file not found: {log_path}")
        return result

    log_text = log_path.read_text(errors="replace")

    _parse_residuals(log_text, result)
    _check_solver_divergence(log_text, result)

    if forces_path is not None:
        _check_force_balance(
            Path(forces_path), expected_fx, result
        )

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_residuals(log_text: str, result: dict[str, Any]) -> None:
    """Extract final iteration residuals from solver log."""
    # Pattern: "Solving for Ux, Initial residual = ..., Final residual = N"
    pattern = re.compile(
        r"Solving for (\w+),\s*Initial residual = [\d.e+\-]+,\s*"
        r"Final residual = ([\d.e+\-]+)",
    )
    last_residuals: dict[str, float] = {}
    for name, val in pattern.findall(log_text):
        try:
            last_residuals[name] = float(val)
        except ValueError:
            pass

    result["final_residuals"] = last_residuals

    if not last_residuals:
        result["passed"] = False
        result["issues"].append(
            "No residuals found in log — solver may not have run"
        )
        return

    all_converged = all(
        v < RESIDUAL_LIMIT for v in last_residuals.values()
    )
    result["converged"] = all_converged

    if not all_converged:
        not_conv = {
            k: v for k, v in last_residuals.items()
            if v >= RESIDUAL_LIMIT
        }
        result["passed"] = False
        result["issues"].append(
            f"Residuals not converged (limit={RESIDUAL_LIMIT}): {not_conv}"
        )


def _check_solver_divergence(log_text: str, result: dict[str, Any]) -> None:
    """Detect hard divergence markers in the solver log."""
    divergence_patterns = [
        r"Floating point exception",
        r"solution singularity",
        r"FOAM FATAL ERROR",
        r"maximum number of iterations exceeded",
        r"Divergence detected",
    ]
    for pat in divergence_patterns:
        if re.search(pat, log_text, re.IGNORECASE):
            result["passed"] = False
            result["converged"] = False
            result["issues"].append(
                f"Divergence marker found in log: '{pat}'"
            )


def _check_force_balance(
    forces_path: Path,
    expected_fx: float | None,
    result: dict[str, Any],
) -> None:
    """Parse OpenFOAM force.dat and compare to expected reference.

    OpenFOAM forces format (postProcessing/forces/0/force.dat):
        # Time  (Fpx Fpy Fpz) (Fvx Fvy Fvz) (Fox Foy Foz)
        0.1     (100 2 -1)    (50 1 -0.5)   (0 0 0)
    """
    if not forces_path.exists():
        result["issues"].append(
            f"Forces file not found: {forces_path} — force balance skipped"
        )
        return

    lines = forces_path.read_text(errors="replace").splitlines()
    data_lines = [
        ln for ln in lines if ln.strip() and not ln.startswith("#")
    ]
    if not data_lines:
        result["issues"].append("Forces file is empty — force balance skipped")
        return

    # Parse last time step
    last = data_lines[-1]
    numbers = re.findall(r"[-+]?[\d]*\.?[\d]+(?:[eE][-+]?\d+)?", last)
    if len(numbers) < 7:
        result["issues"].append(
            "Cannot parse forces file — expected >=7 numbers per row"
        )
        return

    # Columns: time, Fpx Fpy Fpz, Fvx Fvy Fvz, ...
    try:
        time_val = float(numbers[0])
        # Total Fx = pressure Fx + viscous Fx
        total_fx = float(numbers[1]) + float(numbers[4])
        total_fy = float(numbers[2]) + float(numbers[5])
        total_fz = float(numbers[3]) + float(numbers[6])
    except (IndexError, ValueError) as exc:
        result["issues"].append(f"Force parse error: {exc}")
        return

    balance: dict[str, Any] = {
        "time": time_val,
        "Fx": total_fx,
        "Fy": total_fy,
        "Fz": total_fz,
    }

    if expected_fx is not None and abs(expected_fx) > 1e-12:
        error_pct = abs(total_fx - expected_fx) / abs(expected_fx) * 100.0
        balance["expected_Fx"] = expected_fx
        balance["balance_error_pct"] = round(error_pct, 2)
        if error_pct > FORCE_BALANCE_LIMIT_PCT:
            result["passed"] = False
            result["issues"].append(
                f"Force balance error {error_pct:.1f}% "
                f"> limit {FORCE_BALANCE_LIMIT_PCT}%"
            )

    result["force_balance"] = balance


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate CFD convergence for the multi-physics pipeline"
    )
    parser.add_argument("--log", required=True, help="Path to solver log")
    parser.add_argument(
        "--forces",
        help="Path to postProcessing/forces/0/force.dat",
    )
    parser.add_argument(
        "--expected-fx",
        type=float,
        help="Expected drag force [N] for balance check",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    result = validate_convergence(
        log_path=args.log,
        forces_path=args.forces,
        expected_fx=args.expected_fx,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[Gate 2 — CFD Convergence] {status}")
        if result["final_residuals"]:
            for var, val in result["final_residuals"].items():
                flag = (
                    "OK" if val < RESIDUAL_LIMIT else f"FAIL (>{RESIDUAL_LIMIT})"
                )
                print(f"  {var:<10}: {val:.2e}  {flag}")
        if result.get("force_balance"):
            fb = result["force_balance"]
            print(
                f"  Fx={fb.get('Fx', 0):.1f} N  "
                f"Fy={fb.get('Fy', 0):.1f} N  "
                f"Fz={fb.get('Fz', 0):.1f} N"
            )
            if "balance_error_pct" in fb:
                print(f"  Force balance error: {fb['balance_error_pct']:.2f}%")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  WARNING: {issue}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
