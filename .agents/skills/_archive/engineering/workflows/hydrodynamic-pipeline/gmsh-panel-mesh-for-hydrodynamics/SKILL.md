---
name: hydrodynamic-pipeline-gmsh-panel-mesh-for-hydrodynamics
description: 'Sub-skill of hydrodynamic-pipeline: Gmsh Panel Mesh for Hydrodynamics
  (+3).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Gmsh Panel Mesh for Hydrodynamics (+3)

## Gmsh Panel Mesh for Hydrodynamics


```python
import gmsh

def create_panel_mesh(length, beam, draft, panel_size=2.0, output_gdf='hull.gdf'):
    """Create panel mesh for diffraction analysis using Gmsh.

    For OrcaWave/AQWA, mesh must be:
    - Wetted surface only (below waterline)
    - Quadrilateral panels preferred (OrcaWave)
    - Triangular panels accepted (AQWA)
    - Normal vectors pointing outward (into fluid)
    """
    gmsh.initialize()
    gmsh.model.add("hull_panels")

    # Simple box barge example (replace with actual hull geometry)
    # Only mesh the wetted surface (z <= 0)
    half_l = length / 2
    half_b = beam / 2

    # Bottom
    p1 = gmsh.model.occ.addPoint(-half_l, -half_b, -draft)
    p2 = gmsh.model.occ.addPoint(half_l, -half_b, -draft)
    p3 = gmsh.model.occ.addPoint(half_l, half_b, -draft)
    p4 = gmsh.model.occ.addPoint(-half_l, half_b, -draft)

    # Waterline
    p5 = gmsh.model.occ.addPoint(-half_l, -half_b, 0)
    p6 = gmsh.model.occ.addPoint(half_l, -half_b, 0)
    p7 = gmsh.model.occ.addPoint(half_l, half_b, 0)
    p8 = gmsh.model.occ.addPoint(-half_l, half_b, 0)

    # Create surfaces (bottom + 4 sides below waterline)
    # ... (connect points into lines and surfaces)
    gmsh.model.occ.synchronize()

    # Set mesh size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", panel_size)
    gmsh.option.setNumber("Mesh.Algorithm", 8)  # Frontal-Delaunay for quads
    gmsh.option.setNumber("Mesh.RecombineAll", 1)  # Force quads

    gmsh.model.mesh.generate(2)

    # Export as GDF for OrcaWave
    export_gdf(gmsh.model, output_gdf, length, beam, draft)

    gmsh.finalize()
```


## GDF File Format (OrcaWave)


```
HULL PANEL MESH - Barge 280m x 48m x 18m draft
 9.81      0.0       # gravity, waterline z
 1  1                # ISX, ISY symmetry flags (1=yes)
 500                 # number of panels
 x1  y1  z1          # panel vertex 1 (4 vertices per panel)
 x2  y2  z2          # panel vertex 2
 x3  y3  z3          # panel vertex 3
 x4  y4  z4          # panel vertex 4
 ...                  # repeat for each panel
```


## AQWA Mesh Format (.dat)


```python
def export_aqwa_mesh(vertices, panels, output_dat):
    """Export panel mesh in AQWA format."""
    with open(output_dat, 'w') as f:
        f.write("* AQWA panel mesh\n")
        # Nodes
        for i, (x, y, z) in enumerate(vertices, 1):
            f.write(f"NODE {i:6d} {x:12.4f} {y:12.4f} {z:12.4f}\n")
        # Elements (quad panels)
        for i, panel in enumerate(panels, 1):
            n1, n2, n3, n4 = panel
            f.write(f"ELEM {i:6d} {n1:6d} {n2:6d} {n3:6d} {n4:6d}\n")
```


## Mesh Quality for Hydrodynamics


| Check | Threshold | Why |
|-------|-----------|-----|
| Panel aspect ratio | < 3:1 | Poor aspect ratios cause numerical error |
| Panel size | L/20 to L/10 (L=wavelength) | Must resolve shortest wave of interest |
| Normal direction | Outward (into fluid) | Reversed normals give wrong forces |
| Waterline closure | Gap < panel_size/10 | Leaky waterline causes infinite forces |
| Symmetry | Exact if using ISX/ISY | Asymmetry with symmetry flags gives wrong modes |
| Total panels | 500-5000 typical | Too few: inaccurate. Too many: slow |
