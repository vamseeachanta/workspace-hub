---
name: blender-interface-mesh-quality-checks
description: 'Sub-skill of blender-interface: Mesh Quality Checks (+2).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Mesh Quality Checks (+2)

## Mesh Quality Checks


```python
def validate_imported_mesh(obj):
    """Validate mesh quality after import."""
    import bmesh
    checks = {"passed": True, "issues": []}

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Check for non-manifold edges
    non_manifold = [e for e in bm.edges if not e.is_manifold]
    if non_manifold:
        checks["issues"].append(f"{len(non_manifold)} non-manifold edges")

    # Check for loose vertices
    loose = [v for v in bm.verts if not v.link_edges]
    if loose:
        checks["issues"].append(f"{len(loose)} loose vertices")

    # Check for degenerate faces (zero area)
    degen = [f for f in bm.faces if f.calc_area() < 1e-8]
    if degen:
        checks["issues"].append(f"{len(degen)} degenerate faces")

    # Check normals consistency
    bm.normal_update()

    bm.free()

    checks["vertex_count"] = len(mesh.vertices)
    checks["face_count"] = len(mesh.polygons)
    checks["passed"] = len(checks["issues"]) == 0
    return checks
```


## Render Validation


```python
import os

def validate_render_output(output_path, expected_frames=1):
    """Validate render output exists and is reasonable."""
    checks = {"passed": True, "issues": []}

    if not os.path.exists(output_path):
        checks["issues"].append(f"Output not found: {output_path}")
        checks["passed"] = False
        return checks

    size_bytes = os.path.getsize(output_path)
    if size_bytes < 1000:
        checks["issues"].append(f"Output suspiciously small: {size_bytes} bytes (likely blank)")
        checks["passed"] = False

    # Check image dimensions (requires PIL)
    try:
        from PIL import Image
        img = Image.open(output_path)
        checks["resolution"] = img.size
        checks["mode"] = img.mode

        # Check if image is all-black (failed render)
        extrema = img.convert("L").getextrema()
        if extrema == (0, 0):
            checks["issues"].append("Render is all-black — check lighting and materials")
            checks["passed"] = False
    except ImportError:
        checks["issues"].append("PIL not available — skipping image content check")

    return checks
```


## Scale and Units Check


```python
def validate_engineering_scale(obj, expected_max_dim_m=500):
    """Check that imported geometry is at engineering scale (meters)."""
    dims = obj.dimensions
    max_dim = max(dims)

    if max_dim < 0.001:
        return {"issue": f"Max dimension {max_dim:.6f}m — likely in mm, scale by 1000"}
    if max_dim > expected_max_dim_m * 10:
        return {"issue": f"Max dimension {max_dim:.1f}m — likely wrong units"}
    return {"ok": True, "dimensions_m": tuple(dims)}
```
