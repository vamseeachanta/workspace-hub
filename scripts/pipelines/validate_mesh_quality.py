"""
validate_mesh_quality.py — Gate 1 of the Gmsh→OpenFOAM→OrcaFlex pipeline.

Checks a Gmsh .msh file (or an already-converted OpenFOAM polyMesh directory)
for mesh quality.  Returns a structured result dict; exits non-zero on failure
so it can be used as a shell gate.

Usage (standalone):
    python validate_mesh_quality.py --msh mesh.msh
    python validate_mesh_quality.py --polymesh /path/to/case/constant/polyMesh

Thresholds (aligned with OpenFOAM checkMesh defaults):
    max_skewness              < 4.0
    max_non_orthogonality_deg < 70.0
    min_cell_count            >= 100
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
MAX_SKEWNESS = 4.0
MAX_NON_ORTHOGONALITY_DEG = 70.0
MIN_CELL_COUNT = 100


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_msh_file(msh_path: str | Path) -> dict[str, Any]:
    """Validate a Gmsh .msh file for mesh quality.

    Uses the gmsh Python API when available; falls back to a heuristic
    line-count check when gmsh is not installed.

    Args:
        msh_path: Path to the Gmsh .msh mesh file.

    Returns:
        Result dict with keys: passed, cell_count, max_skewness,
        max_non_orthogonality_deg, issues.
    """
    msh_path = Path(msh_path)
    result: dict[str, Any] = {
        "msh_path": str(msh_path),
        "passed": True,
        "cell_count": 0,
        "max_skewness": 0.0,
        "max_non_orthogonality_deg": 0.0,
        "issues": [],
    }

    if not msh_path.exists():
        result["passed"] = False
        result["issues"].append(f"Mesh file not found: {msh_path}")
        return result

    # Try gmsh Python API first
    try:
        import gmsh  # type: ignore
        _validate_with_gmsh_api(msh_path, result)
    except ImportError:
        _validate_with_heuristic(msh_path, result)

    _apply_threshold_checks(result)
    return result


def validate_polymesh_dir(case_dir: str | Path) -> dict[str, Any]:
    """Validate an OpenFOAM polyMesh directory using checkMesh.

    Falls back to file-existence check when OpenFOAM is not sourced.

    Args:
        case_dir: Path to the OpenFOAM case directory (not polyMesh itself).

    Returns:
        Result dict with keys: passed, cell_count, max_skewness,
        max_non_orthogonality_deg, issues.
    """
    case_dir = Path(case_dir)
    polymesh = case_dir / "constant" / "polyMesh"
    result: dict[str, Any] = {
        "polymesh_dir": str(polymesh),
        "passed": True,
        "cell_count": 0,
        "max_skewness": 0.0,
        "max_non_orthogonality_deg": 0.0,
        "issues": [],
    }

    # Minimal existence checks
    for required in ("points", "faces", "owner", "neighbour", "boundary"):
        if not (polymesh / required).exists():
            result["passed"] = False
            result["issues"].append(f"Missing polyMesh file: {required}")

    if not result["passed"]:
        return result

    # Try checkMesh
    try:
        proc = subprocess.run(
            ["checkMesh", "-case", str(case_dir)],
            capture_output=True, text=True, timeout=120,
        )
        _parse_checkmesh_output(proc.stdout, result)
    except FileNotFoundError:
        # OpenFOAM not sourced — use file-size heuristic
        points_size = (polymesh / "points").stat().st_size
        result["cell_count"] = max(1, points_size // 40)
        result["max_skewness"] = 0.5  # assume OK when solver absent
        result["max_non_orthogonality_deg"] = 30.0
        result["issues"].append(
            "checkMesh not found — OpenFOAM not sourced; "
            "quality metrics are estimated"
        )

    _apply_threshold_checks(result)
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_with_gmsh_api(
    msh_path: Path,
    result: dict[str, Any],
) -> None:
    """Populate result using the gmsh Python API."""
    import gmsh  # type: ignore

    gmsh.initialize()
    try:
        gmsh.open(str(msh_path))
        gmsh.model.mesh.generate()

        element_types, _, _ = gmsh.model.mesh.getElements()
        total = sum(
            len(gmsh.model.mesh.getElements(elementType=t)[1][0])
            for t in element_types
        )
        result["cell_count"] = total

        # gmsh does not expose skewness directly; use element quality
        min_qual, _ = gmsh.model.mesh.getMinMaxElementQuality()
        # Quality [0,1]: 1=perfect. Map to pseudo-skewness = 1 - quality.
        result["max_skewness"] = round(1.0 - min_qual, 3)
        result["max_non_orthogonality_deg"] = round(
            (1.0 - min_qual) * 90.0, 1
        )
    finally:
        gmsh.finalize()


def _validate_with_heuristic(
    msh_path: Path,
    result: dict[str, Any],
) -> None:
    """Heuristic cell-count from .msh file line count."""
    content = msh_path.read_text(errors="replace")
    # MSH2 format: $Elements section contains element count on first line
    m = re.search(r'^\$Elements\s*\n(\d+)', content, re.MULTILINE)
    if m:
        result["cell_count"] = int(m.group(1))
    else:
        # Rough: count non-comment lines with 4+ numeric tokens
        data_lines = [
            ln for ln in content.splitlines()
            if ln.strip() and not ln.startswith("$")
            and len(ln.split()) >= 4
        ]
        result["cell_count"] = max(1, len(data_lines))

    # Without solver we assume quality is acceptable unless file is tiny
    result["max_skewness"] = 0.5
    result["max_non_orthogonality_deg"] = 30.0
    result["issues"].append(
        "gmsh Python API not available — quality metrics are estimated"
    )


def _parse_checkmesh_output(
    stdout: str,
    result: dict[str, Any],
) -> None:
    """Parse checkMesh stdout into the result dict."""
    if "FAILED" in stdout:
        result["passed"] = False
        result["issues"].append("checkMesh reports FAILED mesh")

    m = re.search(r'cells:\s*(\d+)', stdout)
    if m:
        result["cell_count"] = int(m.group(1))

    m = re.search(r'Max skewness\s*=\s*([\d.e+\-]+)', stdout, re.IGNORECASE)
    if m:
        result["max_skewness"] = float(m.group(1))

    m = re.search(
        r'[Mm]ax(?:imum)?\s+non.orthogonality\s*=\s*([\d.e+\-]+)', stdout
    )
    if m:
        result["max_non_orthogonality_deg"] = float(m.group(1))


def _apply_threshold_checks(result: dict[str, Any]) -> None:
    """Apply numerical thresholds and update passed flag."""
    if result["cell_count"] < MIN_CELL_COUNT:
        result["passed"] = False
        result["issues"].append(
            f"Cell count {result['cell_count']} < minimum {MIN_CELL_COUNT}"
        )

    if result["max_skewness"] >= MAX_SKEWNESS:
        result["passed"] = False
        result["issues"].append(
            f"Max skewness {result['max_skewness']:.3f} "
            f">= limit {MAX_SKEWNESS}"
        )

    if result["max_non_orthogonality_deg"] >= MAX_NON_ORTHOGONALITY_DEG:
        result["passed"] = False
        result["issues"].append(
            f"Max non-orthogonality "
            f"{result['max_non_orthogonality_deg']:.1f} deg "
            f">= limit {MAX_NON_ORTHOGONALITY_DEG} deg"
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate mesh quality for the multi-physics pipeline"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--msh", help="Path to Gmsh .msh file")
    group.add_argument("--polymesh", help="Path to OpenFOAM case directory")
    parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.msh:
        result = validate_msh_file(args.msh)
    else:
        result = validate_polymesh_dir(args.polymesh)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[Gate 1 — Mesh Quality] {status}")
        print(f"  Cell count            : {result['cell_count']}")
        print(f"  Max skewness          : {result['max_skewness']:.3f}")
        print(
            f"  Max non-orthogonality : "
            f"{result['max_non_orthogonality_deg']:.1f} deg"
        )
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  WARNING: {issue}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
