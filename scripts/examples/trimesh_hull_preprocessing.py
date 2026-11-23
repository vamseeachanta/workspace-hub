"""
trimesh Hull Mesh Pre-Processing Example
=========================================
Integration example for vamseeachanta/workspace-hub#1493.

Demonstrates the trimesh-based hull geometry pipeline:
  1. Generate a representative hull mesh programmatically (no external file needed)
  2. Check and report mesh quality
  3. Run mesh repair (normals, winding, holes, duplicate vertices)
  4. Compute center of buoyancy and volume
  5. Export a Capytaine-ready STL
  6. Boolean subtraction of a moonpool using the Manifold3D backend

Requirements:
    pip install trimesh numpy manifold3d

Tested against trimesh 4.11.x, manifold3d 3.x.
"""

import sys
import io
import numpy as np

# ---------------------------------------------------------------------------
# 1. Mesh generation helpers — no external STL file required
# ---------------------------------------------------------------------------

def make_box_barge(length=80.0, beam=20.0, draft=5.0):
    """Return a closed box-barge mesh (watertight rectangular hull).

    The mesh represents only the submerged volume: a rectangular cuboid
    whose top face sits at z=0 (waterplane) and bottom at z=-draft.
    """
    import trimesh

    box = trimesh.creation.box(extents=[length, beam, draft])
    # Translate so the top face is at z=0 (waterplane level)
    box.apply_translation([0.0, 0.0, -draft / 2.0])
    return box


def make_moonpool_cutter(mp_length=8.0, mp_beam=6.0, draft=5.0, margin=1.0):
    """Return a rectangular prism slightly taller than the hull draft, used
    as a boolean-subtraction cutter to create a centre moonpool."""
    import trimesh

    cutter = trimesh.creation.box(extents=[mp_length, mp_beam, draft + 2 * margin])
    # Centre in XY, vertically spanning the full hull with margin
    cutter.apply_translation([0.0, 0.0, -(draft / 2.0)])
    return cutter


# ---------------------------------------------------------------------------
# 2. Mesh quality report
# ---------------------------------------------------------------------------

def report_quality(mesh, label="mesh"):
    """Print key quality metrics for a trimesh.Trimesh object."""
    print(f"\n--- Mesh Quality Report: {label} ---")
    print(f"  Vertices      : {len(mesh.vertices):,}")
    print(f"  Faces         : {len(mesh.faces):,}")
    print(f"  is_watertight : {mesh.is_watertight}")
    print(f"  is_winding_consistent : {mesh.is_winding_consistent}")
    if mesh.is_watertight:
        print(f"  Volume        : {mesh.volume:.4f} m³")
        cob = mesh.center_mass
        print(f"  Center of mass (CoB proxy): [{cob[0]:.3f}, {cob[1]:.3f}, {cob[2]:.3f}] m")
    else:
        print("  Volume        : N/A (mesh not watertight)")


# ---------------------------------------------------------------------------
# 3. Mesh repair
# ---------------------------------------------------------------------------

def repair_mesh(mesh):
    """Apply standard trimesh repair operations and return the repaired mesh."""
    import trimesh
    import trimesh.repair as repair

    print("\n--- Running Mesh Repair ---")

    # Merge duplicate / near-duplicate vertices
    mesh.merge_vertices()
    print("  merge_vertices: done")

    # Fix face winding so all normals point outward
    repair.fix_winding(mesh)
    print("  fix_winding: done")

    # Fix normals to be consistent with face winding
    repair.fix_normals(mesh)
    print("  fix_normals: done")

    # Fill any small holes (fan-fill method)
    repair.fill_holes(mesh)
    print("  fill_holes: done")

    print(f"  Post-repair is_watertight: {mesh.is_watertight}")
    return mesh


# ---------------------------------------------------------------------------
# 4. STL export (Capytaine hand-off)
# ---------------------------------------------------------------------------

def export_for_capytaine(mesh, path="hull_capytaine_ready.stl"):
    """Export mesh as binary STL ready for Capytaine BEM."""
    mesh.export(path, file_type="stl")
    print(f"\n--- STL Export ---")
    print(f"  Written: {path}")
    print("  Load in Capytaine: capytaine.mesh.io.load_mesh('{path}')".format(path=path))


# ---------------------------------------------------------------------------
# 5. Boolean moonpool subtraction via Manifold3D
# ---------------------------------------------------------------------------

def demo_moonpool_boolean(barge, cutter):
    """Subtract the moonpool cutter from the barge hull using Manifold3D.

    trimesh.boolean.difference() selects the Manifold3D backend automatically
    when manifold3d is installed, falling back to Blender if not.
    """
    import trimesh.boolean as tb

    print("\n--- Boolean Moonpool Subtraction ---")
    try:
        hull_with_moonpool = tb.difference([barge, cutter], engine="manifold")
        print(f"  Boolean difference succeeded.")
        report_quality(hull_with_moonpool, label="barge_with_moonpool")
        return hull_with_moonpool
    except Exception as exc:
        print(f"  Boolean op failed ({type(exc).__name__}: {exc}).")
        print("  Ensure manifold3d is installed: pip install manifold3d")
        return None


# ---------------------------------------------------------------------------
# 6. Simulate loading from STL bytes (no file on disk required for the demo)
# ---------------------------------------------------------------------------

def round_trip_stl(mesh):
    """Serialize mesh to STL bytes and reload — simulates reading a hull STL."""
    import trimesh

    buf = io.BytesIO()
    mesh.export(buf, file_type="stl")
    buf.seek(0)
    reloaded = trimesh.load(buf, file_type="stl")
    return reloaded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("trimesh Hull Pre-Processing Demo  (issue #1493)")
    print("=" * 60)

    # --- Step 1: Generate barge mesh ---
    print("\n[1] Generating box-barge hull (80 m x 20 m x 5 m draft) ...")
    barge = make_box_barge(length=80.0, beam=20.0, draft=5.0)

    # --- Step 2: Simulate load from STL (round-trip) ---
    print("[2] Round-trip through STL bytes (simulates loading from file) ...")
    barge = round_trip_stl(barge)

    # --- Step 3: Quality report (pre-repair) ---
    report_quality(barge, label="barge (pre-repair)")

    # --- Step 4: Repair ---
    barge = repair_mesh(barge)

    # --- Step 5: Quality report (post-repair) ---
    report_quality(barge, label="barge (post-repair)")

    # --- Step 6: Convex hull ---
    print("\n--- Convex Hull ---")
    hull = barge.convex_hull
    print(f"  Convex hull faces: {len(hull.faces):,}")

    # --- Step 7: Export Capytaine-ready STL ---
    export_for_capytaine(barge, path="hull_capytaine_ready.stl")

    # --- Step 8: Boolean moonpool ---
    cutter = make_moonpool_cutter(mp_length=8.0, mp_beam=6.0, draft=5.0)
    hull_with_moonpool = demo_moonpool_boolean(barge, cutter)

    if hull_with_moonpool is not None:
        export_for_capytaine(hull_with_moonpool, path="hull_moonpool_capytaine_ready.stl")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("Next step: load exported STL with capytaine.mesh.io.load_mesh()")
    print("=" * 60)


if __name__ == "__main__":
    main()
