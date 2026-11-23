"""
meshio Multi-Format Mesh I/O Evaluation
========================================
Integration example for vamseeachanta/workspace-hub#1449.

Demonstrates meshio capabilities relevant to engineering workflows:
  1. Programmatic mesh generation (no external files needed)
  2. Multi-format write: VTK, Gmsh, Abaqus/Nastran, STL
  3. Round-trip conversion with integrity validation (node/element counts)
  4. Format chain: STL -> VTK -> Gmsh (typical ACE pipeline path)
  5. Supported format matrix for offshore/structural/marine workflows

Requirements:
    pip install meshio numpy

Tested against meshio 5.3.5, NumPy 2.x.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

import meshio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def mesh_summary(mesh: meshio.Mesh, label: str = "mesh") -> dict:
    """Return a summary dict of node/element counts."""
    total_cells = sum(len(cb.data) for cb in mesh.cells)
    cell_types = {cb.type: len(cb.data) for cb in mesh.cells}
    return {
        "label": label,
        "nodes": len(mesh.points),
        "total_cells": total_cells,
        "cell_types": cell_types,
        "point_data_keys": list(mesh.point_data.keys()),
        "cell_data_keys": list(mesh.cell_data.keys()),
    }


def print_mesh_summary(summary: dict) -> None:
    """Print a mesh summary dict."""
    print(f"  Label       : {summary['label']}")
    print(f"  Nodes       : {summary['nodes']}")
    print(f"  Total cells : {summary['total_cells']}")
    for ctype, count in summary["cell_types"].items():
        print(f"    {ctype:12s}: {count}")
    if summary["point_data_keys"]:
        print(f"  Point data  : {summary['point_data_keys']}")
    if summary["cell_data_keys"]:
        print(f"  Cell data   : {summary['cell_data_keys']}")


# ---------------------------------------------------------------------------
# 1. Generate a sample tetrahedral mesh (simple cube)
# ---------------------------------------------------------------------------

def generate_cube_tet_mesh() -> meshio.Mesh:
    """Generate a cube [0,1]^3 meshed with tetrahedra.

    Uses a structured decomposition: 8 corners -> 6 tets per cube.
    This avoids any external meshing dependency.
    """
    # 3x3x3 grid of points
    n = 4  # points per edge
    x = np.linspace(0.0, 1.0, n)
    y = np.linspace(0.0, 1.0, n)
    z = np.linspace(0.0, 1.0, n)
    xx, yy, zz = np.meshgrid(x, y, z, indexing="ij")
    points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    # Build tetrahedra by splitting each hex cell into 6 tets
    tets = []
    for i in range(n - 1):
        for j in range(n - 1):
            for k in range(n - 1):
                # 8 corners of the hex cell
                v = [
                    i * n * n + j * n + k,
                    (i + 1) * n * n + j * n + k,
                    i * n * n + (j + 1) * n + k,
                    (i + 1) * n * n + (j + 1) * n + k,
                    i * n * n + j * n + (k + 1),
                    (i + 1) * n * n + j * n + (k + 1),
                    i * n * n + (j + 1) * n + (k + 1),
                    (i + 1) * n * n + (j + 1) * n + (k + 1),
                ]
                # Standard 6-tet decomposition of a hex
                tets.append([v[0], v[1], v[3], v[7]])
                tets.append([v[0], v[1], v[5], v[7]])
                tets.append([v[0], v[2], v[3], v[7]])
                tets.append([v[0], v[2], v[6], v[7]])
                tets.append([v[0], v[4], v[5], v[7]])
                tets.append([v[0], v[4], v[6], v[7]])

    cells = [meshio.CellBlock("tetra", np.array(tets, dtype=np.int64))]

    # Add sample point data (a scalar field)
    point_data = {
        "temperature": np.linalg.norm(points - 0.5, axis=1),
    }

    return meshio.Mesh(points=points, cells=cells, point_data=point_data)


def generate_triangle_surface() -> meshio.Mesh:
    """Generate a simple triangulated surface (flat plate) for STL testing."""
    # 5x5 grid -> triangulated
    n = 5
    x = np.linspace(0.0, 2.0, n)
    y = np.linspace(0.0, 1.0, n)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    zz = np.zeros_like(xx)
    points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    triangles = []
    for i in range(n - 1):
        for j in range(n - 1):
            v0 = i * n + j
            v1 = (i + 1) * n + j
            v2 = i * n + (j + 1)
            v3 = (i + 1) * n + (j + 1)
            triangles.append([v0, v1, v2])
            triangles.append([v1, v3, v2])

    cells = [meshio.CellBlock("triangle", np.array(triangles, dtype=np.int64))]
    return meshio.Mesh(points=points, cells=cells)


# ---------------------------------------------------------------------------
# 2. Format conversion tests
# ---------------------------------------------------------------------------

FORMAT_TESTS = [
    # (extension, meshio format name, description, supports_volume)
    (".vtu", "vtu", "VTK Unstructured Grid (XML)", True),
    (".vtk", "vtk", "VTK Legacy", True),
    (".msh", "gmsh", "Gmsh v4", True),
    (".inp", "abaqus", "Abaqus/CalculiX INP", True),
    (".stl", "stl", "STL (surface only)", False),
    (".obj", "obj", "Wavefront OBJ (surface only)", False),
    (".xdmf", "xdmf", "XDMF (HDF5-backed)", True),
]


def test_write_read_roundtrip(
    mesh: meshio.Mesh,
    tmpdir: Path,
    ext: str,
    fmt: str,
    label: str,
    supports_volume: bool,
) -> dict:
    """Write a mesh to a format, read it back, compare node/cell counts.

    Returns a result dict with pass/fail and details.
    """
    result = {
        "format": label,
        "extension": ext,
        "passed": False,
        "write_ok": False,
        "read_ok": False,
        "nodes_match": False,
        "cells_match": False,
        "notes": "",
    }

    filepath = tmpdir / f"test_mesh{ext}"

    # For surface-only formats, use the triangle surface mesh
    if not supports_volume:
        source = generate_triangle_surface()
        source_summary = mesh_summary(source, f"source ({label})")
    else:
        source = mesh
        source_summary = mesh_summary(source, f"source ({label})")

    # Write
    try:
        meshio.write(str(filepath), source)
        result["write_ok"] = True
    except Exception as exc:
        result["notes"] = f"Write failed: {exc}"
        return result

    # Read back
    try:
        reloaded = meshio.read(str(filepath))
        result["read_ok"] = True
    except Exception as exc:
        result["notes"] = f"Read failed: {exc}"
        return result

    # Compare
    reloaded_summary = mesh_summary(reloaded, f"reloaded ({label})")
    result["nodes_match"] = source_summary["nodes"] == reloaded_summary["nodes"]
    result["cells_match"] = source_summary["total_cells"] == reloaded_summary["total_cells"]

    if result["nodes_match"] and result["cells_match"]:
        result["passed"] = True
    else:
        result["notes"] = (
            f"Mismatch: nodes {source_summary['nodes']}->{reloaded_summary['nodes']}, "
            f"cells {source_summary['total_cells']}->{reloaded_summary['total_cells']}"
        )

    return result


# ---------------------------------------------------------------------------
# 3. Format chain test: STL -> VTK -> Gmsh
# ---------------------------------------------------------------------------

def test_format_chain(tmpdir: Path) -> dict:
    """Test a multi-hop conversion: STL -> VTK -> Gmsh.

    This simulates a typical ACE workflow where geometry arrives as STL
    (from CAD/3D scanning), gets converted to VTK for PyVista visualization,
    then to Gmsh for solver input.
    """
    result = {
        "chain": "STL -> VTK -> Gmsh",
        "passed": False,
        "steps": [],
    }

    surface = generate_triangle_surface()
    original = mesh_summary(surface, "original")

    # Step 1: Write STL
    stl_path = tmpdir / "chain_input.stl"
    try:
        meshio.write(str(stl_path), surface)
        result["steps"].append("STL write: OK")
    except Exception as exc:
        result["steps"].append(f"STL write: FAIL ({exc})")
        return result

    # Step 2: Read STL, write VTK
    vtk_path = tmpdir / "chain_intermediate.vtu"
    try:
        mesh_from_stl = meshio.read(str(stl_path))
        meshio.write(str(vtk_path), mesh_from_stl)
        result["steps"].append("STL->VTK: OK")
    except Exception as exc:
        result["steps"].append(f"STL->VTK: FAIL ({exc})")
        return result

    # Step 3: Read VTK, write Gmsh
    gmsh_path = tmpdir / "chain_output.msh"
    try:
        mesh_from_vtk = meshio.read(str(vtk_path))
        meshio.write(str(gmsh_path), mesh_from_vtk)
        result["steps"].append("VTK->Gmsh: OK")
    except Exception as exc:
        result["steps"].append(f"VTK->Gmsh: FAIL ({exc})")
        return result

    # Step 4: Read Gmsh back, validate
    try:
        final_mesh = meshio.read(str(gmsh_path))
        final = mesh_summary(final_mesh, "final")
        nodes_ok = original["nodes"] == final["nodes"]
        cells_ok = original["total_cells"] == final["total_cells"]
        result["steps"].append(
            f"Integrity: nodes {'OK' if nodes_ok else 'MISMATCH'} "
            f"({original['nodes']}->{final['nodes']}), "
            f"cells {'OK' if cells_ok else 'MISMATCH'} "
            f"({original['total_cells']}->{final['total_cells']})"
        )
        result["passed"] = nodes_ok and cells_ok
    except Exception as exc:
        result["steps"].append(f"Final read: FAIL ({exc})")

    return result


# ---------------------------------------------------------------------------
# 4. ACE format matrix
# ---------------------------------------------------------------------------

ACE_FORMAT_MATRIX = """
Supported Format Matrix — ACE Engineering Workflows
=====================================================

Format          | Ext          | meshio | Read | Write | ACE Use Case
----------------|--------------|--------|------|-------|-----------------------------------
Abaqus          | .inp         |  yes   |  R   |  W    | CalculiX FEA input decks
ANSYS msh       | .msh         |  yes   |  R   |  W    | Legacy ANSYS interop
CGNS            | .cgns        |  yes   |  R   |  W    | CFD standard (OpenFOAM bridge)
Exodus          | .e/.exo      |  yes   |  R   |  W    | Sandia FEA ecosystem
FLAC3D          | .f3grid      |  yes   |  R   |  W    | Geotechnical modeling
Gmsh            | .msh (v2/v4) |  yes   |  R   |  W    | Primary meshing tool
H5M (MOAB)      | .h5m         |  yes   |  R   |  W    | Neutronics / advanced FEA
MED/Salome      | .med         |  yes   |  R   |  W    | Code_Aster / Elmer bridge
Nastran         | .bdf/.nas    |  yes   |  R   |  W    | Structural FEA exchange
OBJ             | .obj         |  yes   |  R   |  W    | Blender visualization
STL             | .stl         |  yes   |  R   |  W    | BEM panels, 3D printing, CFD surf
VTK Legacy      | .vtk         |  yes   |  R   |  W    | ParaView / pyvista visualization
VTU (XML VTK)   | .vtu         |  yes   |  R   |  W    | ParaView / pyvista (preferred)
XDMF            | .xdmf        |  yes   |  R   |  W    | FEniCSx, time-series results

Key integration paths for ACE pipelines:
  - CFD:        Gmsh .msh -> meshio -> OpenFOAM (via convert_gmsh_to_openfoam.py)
  - FEA:        Gmsh .msh -> meshio -> Abaqus .inp -> CalculiX
  - Thermal:    Gmsh .msh -> meshio -> MED -> Code_Aster / Elmer
  - Viz:        Any format -> meshio -> VTU -> pyvista / ParaView
  - BEM:        STL -> meshio -> VTK (quality checks) -> BemRosetta
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("  meshio Multi-Format Mesh I/O Evaluation  (issue #1449)")
    print("=" * 60)

    # --- Section 1: Environment ---
    print_section("1. Environment")
    print(f"  meshio version : {meshio.__version__}")
    print(f"  NumPy version  : {np.__version__}")
    print(f"  Python version : {sys.version.split()[0]}")

    # --- Section 2: Generate test mesh ---
    print_section("2. Generate Test Mesh (cube with tetrahedra)")
    cube = generate_cube_tet_mesh()
    cube_info = mesh_summary(cube, "cube_tet_mesh")
    print_mesh_summary(cube_info)

    # --- Section 3: Round-trip format tests ---
    print_section("3. Round-Trip Format Tests")

    with tempfile.TemporaryDirectory(prefix="meshio_eval_") as tmpdir:
        tmppath = Path(tmpdir)
        all_passed = True
        results = []

        for ext, fmt, label, supports_vol in FORMAT_TESTS:
            # Skip XDMF if h5py not available
            if ext == ".xdmf":
                try:
                    import h5py  # noqa: F401
                except ImportError:
                    print(f"\n  [{label}] SKIP — h5py not installed")
                    continue

            result = test_write_read_roundtrip(
                cube, tmppath, ext, fmt, label, supports_vol
            )
            results.append(result)
            status = "PASS" if result["passed"] else "FAIL"
            print(f"\n  [{result['format']}] {status}")
            print(f"    Write: {'OK' if result['write_ok'] else 'FAIL'}")
            print(f"    Read:  {'OK' if result['read_ok'] else 'FAIL'}")
            print(f"    Nodes match: {result['nodes_match']}")
            print(f"    Cells match: {result['cells_match']}")
            if result["notes"]:
                print(f"    Note: {result['notes']}")
            if not result["passed"]:
                all_passed = False

        # --- Section 4: Format chain ---
        print_section("4. Format Chain Test: STL -> VTK -> Gmsh")
        chain_result = test_format_chain(tmppath)
        for step in chain_result["steps"]:
            print(f"    {step}")
        chain_status = "PASS" if chain_result["passed"] else "FAIL"
        print(f"\n  Chain result: {chain_status}")
        if not chain_result["passed"]:
            all_passed = False

    # --- Section 5: Format matrix ---
    print_section("5. ACE Format Matrix")
    print(ACE_FORMAT_MATRIX)

    # --- Summary ---
    print_section("Summary")
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"  Round-trip tests : {passed}/{total} passed")
    print(f"  Format chain     : {chain_status}")
    print(f"  Overall          : {'ALL PASS' if all_passed else 'SOME FAILURES'}")
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
