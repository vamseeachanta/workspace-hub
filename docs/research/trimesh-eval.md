# trimesh Evaluation — Hull Geometry Mesh Processing

**Issue:** vamseeachanta/workspace-hub#1493
**Date:** 2026-03-29
**Verdict:** ADOPT — trimesh is the right tool for hull mesh pre-processing and repair before Capytaine BEM runs.

---

## Summary

trimesh (https://github.com/mikedh/trimesh) is a mature, pure-Python library (numpy-only hard dependency, v4.11.x as of 2026) for loading, repairing, analyzing, and exporting triangular meshes. It covers every format needed for the hull geometry pipeline and provides the mesh quality tooling required to prepare watertight, consistently-wound surfaces. Integration with Capytaine is achievable indirectly via STL export or through the meshio bridge that Capytaine natively supports.

---

## Format Support

| Format | Import | Export | Notes |
|--------|--------|--------|-------|
| STL (binary + ASCII) | Yes | Yes | Capytaine also reads STL directly |
| OBJ (Wavefront) | Yes | Yes | |
| PLY (binary + ASCII) | Yes | Yes | |
| GLTF / GLB 2.0 | Yes | Yes | |
| OFF (ASCII) | Yes | Yes | |
| 3MF | Yes | Yes | |
| COLLADA (.dae) | No | Yes | Export only |
| DXF / SVG (2D paths) | Yes | Yes | Cross-section extraction |
| XAML / 3DXML | Yes | No | Import only |

All five target formats (STL, OBJ, PLY, GLTF, OFF) are supported for both import and export.

---

## Mesh Quality Capabilities

| Capability | Available | Notes |
|---|---|---|
| Watertight check | Yes | `mesh.is_watertight` property |
| Normal consistency check | Yes | `mesh.is_winding_consistent` |
| Fix normals / winding | Yes | `repair.fix_normals()`, `repair.fix_winding()` |
| Fix inversion (outward normals) | Yes | `repair.fix_inversion()` |
| Hole filling | Yes | `repair.fill_holes()` — fan-fill method |
| Identify broken faces | Yes | `repair.broken_faces()` |
| Stitch boundary edges | Yes | `repair.stitch()` |
| Merge duplicate vertices | Yes | `mesh.merge_vertices()` |
| Degenerate face removal | Yes | `validate=True` on load |
| Connected component analysis | Yes | Topological decomposition |
| Volume / mass properties | Yes | Requires watertight mesh |
| Convex hull | Yes | |

---

## Boolean Operations (CSG)

trimesh supports **union, intersection, and difference** on meshes. These require an external backend:

- **Manifold3D** (`pip install manifold3d`) — recommended, fast, pure-Python wheel
- **Blender** — fallback if Manifold3D not available

For hull meshes (10k–100k triangles), Manifold3D is sufficient and does not require Blender.

---

## Capytaine Integration Assessment

| Factor | Assessment |
|---|---|
| Direct trimesh → Capytaine API | No direct binding |
| Via STL export | **Yes** — Capytaine reads `.stl`; trimesh exports binary/ASCII STL |
| Via meshio bridge | **Yes** — Capytaine's `load_from_meshio()` accepts meshio objects; trimesh can write formats meshio reads |
| Watertight requirement | Not strictly required by Capytaine — "a mesh is merely a set of independent faces" |
| Recommended workflow | trimesh (load + repair + validate) → `mesh.export('hull.stl')` → `capytaine.load_mesh('hull.stl')` |

The integration path is **STL as the hand-off format**. This is robust, zero-dependency (no meshio needed), and already documented in both libraries.

---

## Performance

- **Architecture:** numpy-backed with lazy evaluation and automatic cache invalidation via TrackedArray hashing (MD5/CRC/xxhash). Expensive properties (volume, adjacency) are computed once and cached until the mesh changes.
- **10k–100k triangle range:** Well within trimesh's operational envelope. Community usage confirms this range is routine (CAD, FEA pre-processing). No explicit throughput benchmarks in docs, but numpy vectorization makes operations on 100k faces typically sub-second.
- **Ray queries:** Optional `embreex` backend accelerates ray-mesh intersection for larger meshes.
- **Memory:** Only numpy arrays are held; no copies unless explicitly requested.

---

## Visualization

| Method | Available |
|---|---|
| Interactive OpenGL window (pyglet) | Yes — `mesh.show()` |
| Jupyter / Marimo inline (three.js) | Yes |
| Scene graph with transform tree | Yes |
| Export to image | Via pyglet screenshot |

Built-in viewer is functional for inspection but not publication-quality rendering.

---

## Recommendation

**ADOPT**

trimesh fills a clear gap in the hull geometry pipeline:

1. **Mesh import** from CAD/IGES outputs (STL, OBJ, PLY) into Python
2. **Repair** before BEM: fix normals, fill small holes, remove degenerate faces
3. **Validation** — confirm watertight status before handing off to Capytaine
4. **Hand-off** — export clean STL directly loadable by Capytaine

Install path: `pip install trimesh` (minimal) + `pip install manifold3d` for boolean ops.

No competing library offers this combination at this maturity level without heavier dependencies (e.g., VTK, Open3D).

---

**One-liner verdict:** trimesh is the mesh repair and format-conversion workhorse for the hull geometry pipeline — adopt it as the standard pre-processing step before Capytaine BEM runs.
