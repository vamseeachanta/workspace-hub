"""
stub_gmsh.py — Gmsh solver stub for the multi-physics pipeline.

Generates a synthetic Gmsh MSH2 file for a cylinder in a rectangular domain.
The mesh topology is valid but coarse (suitable for testing pipeline logic
rather than accurate physics).

The stub injects analytically correct drag estimates using:
    Cd = 1.0 (bluff cylinder, Re >> 1)
    F_drag = 0.5 * rho * U^2 * D * L * Cd

Usage:
    from stubs.stub_gmsh import run_gmsh_stub
    result = run_gmsh_stub(
        diameter=1.0, length=5.0, velocity=1.0, output_msh="mesh.msh"
    )
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any


# MSH2 format constants
_MSH2_HEADER = """\
$MeshFormat
2.2 0 8
$EndMeshFormat
"""


def run_gmsh_stub(
    diameter: float,
    length: float,
    velocity: float,
    output_msh: str | Path,
    domain_scale: float = 10.0,
    nx: int = 20,
    ny: int = 10,
    nz: int = 5,
) -> dict[str, Any]:
    """Generate a synthetic .msh file for a cylinder-in-flow geometry.

    The geometry is a rectangular box with the cylinder approximated as
    a set of cells removed from the centre.  Cell quality is set to be
    within acceptable limits so Gate 1 passes.

    Args:
        diameter: Cylinder diameter [m].
        length: Cylinder length [m].
        velocity: Free-stream velocity [m/s] (used in metadata only).
        output_msh: Destination .msh file path.
        domain_scale: Domain half-width as a multiple of diameter.
        nx, ny, nz: Grid resolution in each direction.

    Returns:
        Result dict with keys: passed, msh_path, cell_count,
        max_skewness, max_non_orthogonality_deg, drag_force_N.
    """
    output_msh = Path(output_msh)
    output_msh.parent.mkdir(parents=True, exist_ok=True)

    # Geometry dimensions
    lx = domain_scale * diameter
    ly = domain_scale * diameter * 0.5
    lz = length

    dx = lx / nx
    dy = ly / ny
    dz = lz / nz

    # Build structured hex mesh
    points: list[tuple[float, float, float]] = []
    cells: list[tuple[int, ...]] = []

    # Node indices: (ix, iy, iz) → node_id
    node_id = 1  # MSH2 is 1-indexed
    node_map: dict[tuple[int, int, int], int] = {}

    for iz in range(nz + 1):
        for iy in range(ny + 1):
            for ix in range(nx + 1):
                x = ix * dx - lx / 2.0
                y = iy * dy - ly / 2.0
                z = iz * dz
                points.append((x, y, z))
                node_map[(ix, iy, iz)] = node_id
                node_id += 1

    # Build hex cells (skip cells that overlap the cylinder cross-section)
    r_cyl = diameter / 2.0
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                # Cell centre
                cx = (ix + 0.5) * dx - lx / 2.0
                cy = (iy + 0.5) * dy - ly / 2.0
                if math.hypot(cx, cy) < r_cyl * 1.1:
                    continue  # Skip cylinder interior

                n000 = node_map[(ix, iy, iz)]
                n100 = node_map[(ix + 1, iy, iz)]
                n110 = node_map[(ix + 1, iy + 1, iz)]
                n010 = node_map[(ix, iy + 1, iz)]
                n001 = node_map[(ix, iy, iz + 1)]
                n101 = node_map[(ix + 1, iy, iz + 1)]
                n111 = node_map[(ix + 1, iy + 1, iz + 1)]
                n011 = node_map[(ix, iy + 1, iz + 1)]
                cells.append((n000, n100, n110, n010, n001, n101, n111, n011))

    # Physical groups (patches)
    # Inlet: x = -lx/2 (ix=0)
    # Outlet: x = +lx/2 (ix=nx)
    # Cylinder: nodes near r_cyl
    # top/bottom/sides: remaining boundary faces
    inlet_faces: list[tuple[int, ...]] = []
    outlet_faces: list[tuple[int, ...]] = []
    cyl_faces: list[tuple[int, ...]] = []

    for iz in range(nz):
        for iy in range(ny):
            # inlet quad (ix=0)
            f = (
                node_map[(0, iy, iz)],
                node_map[(0, iy + 1, iz)],
                node_map[(0, iy + 1, iz + 1)],
                node_map[(0, iy, iz + 1)],
            )
            inlet_faces.append(f)

            # outlet quad (ix=nx)
            f = (
                node_map[(nx, iy, iz)],
                node_map[(nx, iy + 1, iz)],
                node_map[(nx, iy + 1, iz + 1)],
                node_map[(nx, iy, iz + 1)],
            )
            outlet_faces.append(f)

    # Write MSH2
    with open(output_msh, "w") as fh:
        fh.write(_MSH2_HEADER)

        # Physical names
        fh.write("$PhysicalNames\n4\n")
        fh.write('3 1 "fluid"\n')
        fh.write('2 2 "inlet"\n')
        fh.write('2 3 "outlet"\n')
        fh.write('2 4 "cylinder"\n')
        fh.write("$EndPhysicalNames\n")

        # Nodes
        fh.write("$Nodes\n")
        fh.write(f"{len(points)}\n")
        for i, (x, y, z) in enumerate(points, 1):
            fh.write(f"{i} {x:.6g} {y:.6g} {z:.6g}\n")
        fh.write("$EndNodes\n")

        # Elements
        total_elements = (
            len(cells) + len(inlet_faces) + len(outlet_faces)
        )
        fh.write("$Elements\n")
        fh.write(f"{total_elements}\n")
        elem_id = 1

        # Hex8 cells (type 5)
        for cell in cells:
            nodes_str = " ".join(str(n) for n in cell)
            fh.write(f"{elem_id} 5 2 1 1 {nodes_str}\n")
            elem_id += 1

        # Inlet quads (type 3)
        for face in inlet_faces:
            nodes_str = " ".join(str(n) for n in face)
            fh.write(f"{elem_id} 3 2 2 2 {nodes_str}\n")
            elem_id += 1

        # Outlet quads (type 3)
        for face in outlet_faces:
            nodes_str = " ".join(str(n) for n in face)
            fh.write(f"{elem_id} 3 2 3 3 {nodes_str}\n")
            elem_id += 1

        fh.write("$EndElements\n")

    # Analytical drag estimate
    rho = 1025.0  # seawater density [kg/m³]
    cd = 1.0      # cylinder drag coefficient
    drag_n = 0.5 * rho * velocity ** 2 * diameter * length * cd

    return {
        "passed": True,
        "msh_path": str(output_msh),
        "cell_count": len(cells),
        "max_skewness": 0.4,
        "max_non_orthogonality_deg": 25.0,
        "drag_force_N": round(drag_n, 2),
        "stub": True,
    }
