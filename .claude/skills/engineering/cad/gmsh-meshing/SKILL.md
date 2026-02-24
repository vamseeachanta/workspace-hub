---
name: gmsh-meshing
version: "1.0.0"
category: engineering
description: "gmsh Meshing Skill — CLI, .geo scripting, Python API, and solver integration"
tags: [gmsh, mesh, meshing, cad, geometry, bem, fem, marine, hydrodynamic, opencascade]
platforms: [windows, linux, macos]
invocation: gmsh-meshing
depends_on:
  - cad-mesh-generation
  - mesh-utilities
capabilities: []
requires: []
see_also: []
---

# gmsh Meshing Skill

```yaml
name: gmsh-meshing
version: 1.0.0
category: engineering/cad
tags: [gmsh, mesh, cad, bem, marine, opencascade, transfinite, panel-mesh]
created: 2026-02-15
updated: 2026-02-15
author: Claude
description: |
  Comprehensive gmsh meshing skill covering CLI batch operations,
  .geo scripting language, Python API, OpenCASCADE boolean CSG,
  structured/unstructured meshing, field-based refinement, and
  integration with hydrodynamic BEM solvers (AQWA, OrcaWave, Nemoh).
```

## When to Use This Skill

Use this skill when you need to:
- Generate surface panel meshes for BEM hydrodynamic solvers
- Create structured (transfinite) or unstructured meshes
- Script parametric geometries with .geo or Python API
- Perform boolean/CSG operations via OpenCASCADE kernel
- Import and remesh STEP, STL, or IGES geometry
- Control mesh density with size fields (distance, threshold, background)
- Export meshes to AQWA (.DAT), WAMIT (.GDF), Nemoh, or general formats (MSH, STL, VTK, UNV)
- Batch-generate meshes from the command line

**Cross-references:**
- GDF/CDB export code → `skills/data/scientific/cad-mesh-generation/SKILL.md`
- Mesh inspection/conversion → `skills/engineering/marine-offshore/mesh-utilities/SKILL.md`

## Quick Reference

### Executable

| Platform | Path |
|----------|------|
| Windows (local) | `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe` |
| Linux/macOS | `gmsh` (install via package manager or `pip install gmsh`) |
| Python module | `pip install gmsh` (provides `import gmsh`) |

### Supported Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| MSH v2.2 | `.msh` | BEM tools (BEMRosetta, Nemoh) |
| MSH v4.1 | `.msh` | Default, full feature support |
| STL | `.stl` | Visualization, 3D printing |
| VTK | `.vtk` | ParaView visualization |
| UNV | `.unv` | Salome, Code_Aster |
| Nastran BDF | `.bdf` | ANSYS, Nastran FEA |
| Abaqus INP | `.inp` | Abaqus FEA |
| Fluent DAT | `.dat` | Fluent CFD |
| CGNS | `.cgns` | CFD interoperability |
| MED | `.med` | Salome/Code_Aster |
| SU2 | `.su2` | SU2 CFD |
| OFF | `.off` | Geometry processing |

### Mesh Algorithms

| ID | Name | Dimension | Description |
|----|------|-----------|-------------|
| 1 | MeshAdapt | 2D | Adaptive, good for complex geometries |
| 5 | Delaunay | 2D | Default 2D, robust general purpose |
| 6 | Frontal-Delaunay | 2D | Better quality triangles |
| 8 | DelQuad | 2D | Delaunay for quads (recombine) |
| 9 | Packing of Parallelograms | 2D | Structured-like quad meshing |
| 1 | Delaunay | 3D | Default 3D tetrahedral |
| 4 | Frontal | 3D | Better quality tets |
| 7 | MMG3D | 3D | Remeshing with MMG |
| 10 | HXT | 3D | Parallel Delaunay (fast) |

## CLI Reference

### Batch Meshing

```bash
# Generate 2D surface mesh and save
gmsh model.geo -2 -o output.msh

# Generate 3D volume mesh
gmsh model.geo -3 -o output.msh

# Specify output format
gmsh model.geo -2 -format msh22 -o output.msh

# Set mesh size factor (global scaling)
gmsh model.geo -2 -clscale 0.5 -o fine_mesh.msh

# Set min/max element sizes
gmsh model.geo -2 -clmin 0.1 -clmax 2.0 -o output.msh

# Select meshing algorithm
gmsh model.geo -2 -algo del2d -o output.msh

# Binary output
gmsh model.geo -2 -bin -o output.msh

# Mesh refinement
gmsh input.msh -refine -o refined.msh

# Mesh order (quadratic elements)
gmsh model.geo -2 -order 2 -o output.msh

# Optimize mesh quality
gmsh model.geo -3 -optimize -o output.msh

# Save all elements (including internal)
gmsh model.geo -2 -save_all -o output.msh

# Set number of threads
gmsh model.geo -3 -nt 4 -o output.msh

# Run with verbosity
gmsh model.geo -2 -v 3 -o output.msh
```

### Format Conversion

```bash
# Convert MSH to STL
gmsh input.msh -o output.stl

# Convert STEP to mesh
gmsh input.step -2 -o output.msh

# Convert to MSH v2.2 (for BEM tools)
gmsh input.msh -format msh22 -o output.msh

# Convert with binary format
gmsh input.msh -bin -convert output.msh
```

### Key CLI Flags

| Flag | Description |
|------|-------------|
| `-0` | Output model only (no mesh), then exit |
| `-1`, `-2`, `-3` | Generate 1D/2D/3D mesh |
| `-format <fmt>` | Output format (msh2, msh22, stl, vtk, etc.) |
| `-o <file>` | Output file path |
| `-bin` | Binary output |
| `-clscale <f>` | Global mesh size factor |
| `-clmin <f>` | Minimum element size |
| `-clmax <f>` | Maximum element size |
| `-clcurv <n>` | Elements per 2*pi for curvature-based sizing |
| `-algo <name>` | Mesh algorithm (del2d, front2d, del3d, etc.) |
| `-order <n>` | Element order (1=linear, 2=quadratic) |
| `-refine` | Uniform refinement |
| `-optimize` | Optimize tetrahedra quality |
| `-smooth <n>` | Smoothing steps |
| `-save_all` | Save all elements |
| `-nt <n>` | Number of threads |
| `-v <n>` | Verbosity level (0-99) |
| `-nopopup` | Suppress GUI dialogs in scripts |
| `-string "..."` | Parse command string at startup |
| `-setnumber name val` | Set numeric parameter |

## GEO Scripting Language

### Geometry Primitives

```geo
// Points: Point(id) = {x, y, z, mesh_size};
Point(1) = {0, 0, 0, 1.0};
Point(2) = {10, 0, 0, 1.0};
Point(3) = {10, 5, 0, 0.5};
Point(4) = {0, 5, 0, 0.5};

// Lines
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

// Curve Loop (ordered, signed)
Curve Loop(1) = {1, 2, 3, 4};

// Plane Surface
Plane Surface(1) = {1};

// Circle Arc: Circle(id) = {start, center, end};
Circle(5) = {1, 5, 2};

// Spline through points
Spline(6) = {1, 2, 3, 4};

// BSpline
BSpline(7) = {1, 2, 3, 4};
```

### Surface and Volume

```geo
// Surface from curve loops (first = outer boundary, rest = holes)
Plane Surface(1) = {1};
Plane Surface(2) = {2, 3};  // Surface 2 with hole defined by loop 3

// Surface Loop (for volumes)
Surface Loop(1) = {1, 2, 3, 4, 5, 6};

// Volume from surface loops
Volume(1) = {1};
```

### Transformations

```geo
// Translate (creates copy if Duplicata used)
Translate {dx, dy, dz} { Surface{1}; }

// Rotate: angle in radians
Rotate {{ax, ay, az}, {px, py, pz}, angle} { Surface{1}; }

// Symmetry
Symmetry {a, b, c, d} { Surface{1}; }  // plane ax+by+cz+d=0

// Extrude surface to create volume
Extrude {0, 0, height} { Surface{1}; }

// Extrude with rotation
Extrude {{0, 0, 1}, {0, 0, 0}, Pi/2} { Surface{1}; }

// Duplicate before transforming
Translate {10, 0, 0} { Duplicata{ Surface{1}; } }
```

### OpenCASCADE Kernel

```geo
// Enable OpenCASCADE kernel (must be first geometry command)
SetFactory("OpenCASCADE");

// Primitives
Box(1) = {x, y, z, dx, dy, dz};
Sphere(2) = {x, y, z, radius};
Cylinder(3) = {x, y, z, dx, dy, dz, radius};
Cone(4) = {x, y, z, dx, dy, dz, r1, r2};
Torus(5) = {x, y, z, r1, r2};
Wedge(6) = {x, y, z, dx, dy, dz, ltx};

// Rectangle and Disk (2D)
Rectangle(1) = {x, y, z, dx, dy};
Disk(2) = {x, y, z, rx, ry};

// Boolean Operations
BooleanUnion{ Volume{1}; Delete; }{ Volume{2}; Delete; }
BooleanIntersection{ Volume{1}; Delete; }{ Volume{2}; Delete; }
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
BooleanFragments{ Volume{1}; Delete; }{ Volume{2}; Delete; }

// Import external geometry
Merge "model.step";
Merge "model.iges";
Merge "model.stl";
```

### Physical Groups

```geo
// Physical groups assign labels for export
Physical Surface("hull") = {1, 2, 3};
Physical Surface("deck") = {4};
Physical Volume("fluid") = {1};

// Numbered groups
Physical Surface(100) = {1, 2, 3};
```

### Mesh Control in .geo

```geo
// Characteristic length at points
Characteristic Length {1, 2, 3} = 0.5;

// Transfinite curves (structured)
Transfinite Curve {1, 3} = 20;       // 20 nodes
Transfinite Curve {2, 4} = 10;       // 10 nodes
Transfinite Curve {1} = 20 Using Progression 1.1;  // graded

// Transfinite surface
Transfinite Surface {1} = {1, 2, 3, 4};  // corners
Recombine Surface {1};                     // quads instead of tris

// Transfinite volume
Transfinite Volume {1} = {1, 2, 3, 4, 5, 6, 7, 8};

// Mesh algorithm selection
Mesh.Algorithm = 6;      // Frontal-Delaunay 2D
Mesh.Algorithm3D = 1;    // Delaunay 3D

// Element size controls
Mesh.MeshSizeFactor = 0.5;
Mesh.MeshSizeMin = 0.1;
Mesh.MeshSizeMax = 2.0;
Mesh.MeshSizeFromCurvature = 12;  // elements per 2*pi

// Smoothing
Mesh.Smoothing = 10;

// Element order
Mesh.ElementOrder = 2;

// Optimize
Mesh.Optimize = 1;
```

## Python API Reference

### Initialization and Model Management

```python
import gmsh

# Initialize
gmsh.initialize()
gmsh.option.setNumber("General.Verbosity", 3)

# Create a new model
gmsh.model.add("my_model")

# Finalize (always call at end)
gmsh.finalize()

# Context manager pattern (recommended)
gmsh.initialize()
try:
    gmsh.model.add("my_model")
    # ... build geometry and mesh ...
    gmsh.write("output.msh")
finally:
    gmsh.finalize()
```

### Built-in Kernel (gmsh.model.geo)

```python
# Points
p1 = gmsh.model.geo.addPoint(0, 0, 0, meshSize=1.0)
p2 = gmsh.model.geo.addPoint(10, 0, 0, meshSize=1.0)
p3 = gmsh.model.geo.addPoint(10, 5, 0, meshSize=0.5)

# Lines
l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)

# Circle arc: addCircleArc(start, center, end)
arc = gmsh.model.geo.addCircleArc(p1, p_center, p2)

# Spline
spl = gmsh.model.geo.addSpline([p1, p2, p3, p4])

# Curve loop and surface
cl = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
s = gmsh.model.geo.addPlaneSurface([cl])

# Surface loop and volume
sl = gmsh.model.geo.addSurfaceLoop([s1, s2, s3, s4, s5, s6])
v = gmsh.model.geo.addVolume([sl])

# Extrude
out = gmsh.model.geo.extrude([(2, s)], 0, 0, height)
# Returns list of (dim, tag) pairs: top surface, volume, lateral surfaces

# Transformations
gmsh.model.geo.translate([(2, s)], dx, dy, dz)
gmsh.model.geo.rotate([(2, s)], cx, cy, cz, ax, ay, az, angle)
gmsh.model.geo.copy([(2, s)])
gmsh.model.geo.mirror([(2, s)], a, b, c, d)

# Physical groups
gmsh.model.addPhysicalGroup(2, [s1, s2, s3], tag=100, name="hull")

# MUST synchronize before meshing
gmsh.model.geo.synchronize()
```

### OpenCASCADE Kernel (gmsh.model.occ)

```python
# Box: addBox(x, y, z, dx, dy, dz)
box = gmsh.model.occ.addBox(0, 0, 0, 100, 20, 10)

# Sphere: addSphere(xc, yc, zc, radius)
sphere = gmsh.model.occ.addSphere(0, 0, 0, 5.0)

# Cylinder: addCylinder(x, y, z, dx, dy, dz, r)
cyl = gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, 10, 5.0)

# Cone: addCone(x, y, z, dx, dy, dz, r1, r2)
cone = gmsh.model.occ.addCone(0, 0, 0, 0, 0, 5, 3, 0)

# Torus: addTorus(x, y, z, r1, r2)
torus = gmsh.model.occ.addTorus(0, 0, 0, 10, 2)

# Rectangle: addRectangle(x, y, z, dx, dy)
rect = gmsh.model.occ.addRectangle(0, 0, 0, 10, 5)

# Disk: addDisk(xc, yc, zc, rx, ry)
disk = gmsh.model.occ.addDisk(0, 0, 0, 5, 5)

# Boolean operations
# cut(objectDimTags, toolDimTags, removeObject=True, removeTool=True)
result, result_map = gmsh.model.occ.cut(
    [(3, box)], [(3, sphere)]
)

# fuse (union)
result, result_map = gmsh.model.occ.fuse(
    [(3, box)], [(3, cyl)]
)

# intersect
result, result_map = gmsh.model.occ.intersect(
    [(3, box)], [(3, sphere)]
)

# fragment (all-vs-all intersection, preserves all pieces)
result, result_map = gmsh.model.occ.fragment(
    [(3, box)], [(3, sphere)]
)

# Import STEP/IGES/STL
shapes = gmsh.model.occ.importShapes("model.step")
shapes = gmsh.model.occ.importShapes("model.iges")

# MUST synchronize before meshing
gmsh.model.occ.synchronize()
```

### Mesh Generation (gmsh.model.mesh)

```python
# Generate mesh
gmsh.model.mesh.generate(1)   # 1D
gmsh.model.mesh.generate(2)   # 2D surface
gmsh.model.mesh.generate(3)   # 3D volume

# Recombine triangles to quads
gmsh.model.mesh.recombine()

# Set transfinite constraints
gmsh.model.mesh.setTransfiniteCurve(line_tag, numNodes,
    meshType="Progression", coef=1.0)
gmsh.model.mesh.setTransfiniteSurface(surf_tag,
    arrangement="Left", cornerTags=[p1, p2, p3, p4])
gmsh.model.mesh.setTransfiniteVolume(vol_tag,
    cornerTags=[p1, p2, p3, p4, p5, p6, p7, p8])

# Refinement
gmsh.model.mesh.refine()

# Optimize
gmsh.model.mesh.optimize("Laplace2D")
gmsh.model.mesh.optimize("Netgen")
gmsh.model.mesh.optimize("HighOrder")

# Set mesh order
gmsh.model.mesh.setOrder(2)

# Get mesh data
node_tags, coords, _ = gmsh.model.mesh.getNodes()
elem_types, elem_tags, node_tags = gmsh.model.mesh.getElements()

# Get elements by type on surface
elem_types, elem_tags, node_tags = gmsh.model.mesh.getElements(dim=2, tag=surf_tag)

# Get node coordinates
coords = gmsh.model.mesh.getNode(nodeTag)  # returns (coords, parametricCoords, dim, tag)
```

### Options (gmsh.option)

```python
# Mesh algorithm selection
gmsh.option.setNumber("Mesh.Algorithm", 6)       # Frontal-Delaunay 2D
gmsh.option.setNumber("Mesh.Algorithm3D", 1)      # Delaunay 3D

# Size controls
gmsh.option.setNumber("Mesh.MeshSizeFactor", 0.5)
gmsh.option.setNumber("Mesh.MeshSizeMin", 0.1)
gmsh.option.setNumber("Mesh.MeshSizeMax", 2.0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)

# Smoothing
gmsh.option.setNumber("Mesh.Smoothing", 10)

# Element order
gmsh.option.setNumber("Mesh.ElementOrder", 2)

# Optimization
gmsh.option.setNumber("Mesh.Optimize", 1)
gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)

# Output format
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)   # MSH v2.2
gmsh.option.setNumber("Mesh.Binary", 1)               # Binary output

# Geometry tolerance
gmsh.option.setNumber("Geometry.Tolerance", 1e-6)
gmsh.option.setNumber("Geometry.OCCFixDegenerated", 1)
gmsh.option.setNumber("Geometry.OCCFixSmallEdges", 1)
gmsh.option.setNumber("Geometry.OCCFixSmallFaces", 1)
gmsh.option.setNumber("Geometry.OCCSewFaces", 1)

# Recombination
gmsh.option.setNumber("Mesh.RecombineAll", 1)
gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 1)  # Blossom

# Save options
gmsh.option.setNumber("Mesh.SaveAll", 1)

# Verbosity
gmsh.option.setNumber("General.Verbosity", 5)
```

### Mesh Size Fields (gmsh.model.mesh.field)

```python
# Distance field — distance from curves or points
f_dist = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(f_dist, "CurvesList", [1, 2, 3])
gmsh.model.mesh.field.setNumber(f_dist, "Sampling", 100)

# Threshold field — size based on distance
f_thresh = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(f_thresh, "InField", f_dist)
gmsh.model.mesh.field.setNumber(f_thresh, "SizeMin", 0.1)    # size at DistMin
gmsh.model.mesh.field.setNumber(f_thresh, "SizeMax", 2.0)    # size at DistMax
gmsh.model.mesh.field.setNumber(f_thresh, "DistMin", 0.5)    # start transition
gmsh.model.mesh.field.setNumber(f_thresh, "DistMax", 10.0)   # end transition

# Box field — size inside/outside a box region
f_box = gmsh.model.mesh.field.add("Box")
gmsh.model.mesh.field.setNumber(f_box, "VIn", 0.5)
gmsh.model.mesh.field.setNumber(f_box, "VOut", 2.0)
gmsh.model.mesh.field.setNumber(f_box, "XMin", -5)
gmsh.model.mesh.field.setNumber(f_box, "XMax", 5)
gmsh.model.mesh.field.setNumber(f_box, "YMin", -5)
gmsh.model.mesh.field.setNumber(f_box, "YMax", 5)
gmsh.model.mesh.field.setNumber(f_box, "ZMin", -5)
gmsh.model.mesh.field.setNumber(f_box, "ZMax", 5)

# MathEval field — size from mathematical expression
f_math = gmsh.model.mesh.field.add("MathEval")
gmsh.model.mesh.field.setString(f_math, "F", "0.1 + 0.01*x*x")

# Min field — take minimum of multiple fields
f_min = gmsh.model.mesh.field.add("Min")
gmsh.model.mesh.field.setNumbers(f_min, "FieldsList", [f_thresh, f_box])

# Set as background mesh
gmsh.model.mesh.field.setAsBackgroundMesh(f_min)

# Disable other size constraints when using fields
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
```

### File I/O

```python
# Write mesh
gmsh.write("output.msh")       # Default format
gmsh.write("output.stl")       # STL
gmsh.write("output.vtk")       # VTK
gmsh.write("output.unv")       # Universal
gmsh.write("output.bdf")       # Nastran

# Write specific format version
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write("output.msh")

# Open/merge files
gmsh.open("model.geo")         # Open (replaces current)
gmsh.merge("model.step")       # Merge into current

# Launch GUI (for interactive inspection)
gmsh.fltk.run()
```

## Mesh Generation Workflows

### Box Barge Surface Mesh (BEM)

Typical marine box barge for hydrodynamic BEM analysis. Only the wetted surface is meshed (no deck).

```python
import gmsh
import numpy as np

def create_box_barge_mesh(
    length: float,
    beam: float,
    draft: float,
    mesh_size: float = 2.0,
    output_file: str = "barge.msh"
):
    """Create box barge wetted surface mesh for BEM analysis.

    Args:
        length: Barge length (m)
        beam: Barge beam/width (m)
        draft: Barge draft (m), positive downward
        mesh_size: Target element size (m)
        output_file: Output mesh file path
    """
    gmsh.initialize()
    gmsh.model.add("box_barge")

    # Half-dimensions (origin at waterplane center)
    hL, hB = length / 2, beam / 2

    # Wetted surface corners (z=0 is waterplane, z=-draft is keel)
    # Bottom face
    p1 = gmsh.model.occ.addPoint(-hL, -hB, -draft, mesh_size)
    p2 = gmsh.model.occ.addPoint( hL, -hB, -draft, mesh_size)
    p3 = gmsh.model.occ.addPoint( hL,  hB, -draft, mesh_size)
    p4 = gmsh.model.occ.addPoint(-hL,  hB, -draft, mesh_size)

    # Waterplane corners
    p5 = gmsh.model.occ.addPoint(-hL, -hB, 0, mesh_size)
    p6 = gmsh.model.occ.addPoint( hL, -hB, 0, mesh_size)
    p7 = gmsh.model.occ.addPoint( hL,  hB, 0, mesh_size)
    p8 = gmsh.model.occ.addPoint(-hL,  hB, 0, mesh_size)

    # Bottom face
    bottom = gmsh.model.occ.addRectangle(-hL, -hB, -draft, length, beam)

    # Side faces (4 sides from keel to waterplane)
    side_bow   = gmsh.model.occ.addRectangle(-hL, -hB, -draft, beam, draft,
                                              tag=-1)
    gmsh.model.occ.rotate([(2, side_bow)], -hL, -hB, -draft, 0, 1, 0, -np.pi/2)

    # Simpler approach: use a box and extract wetted surfaces
    box = gmsh.model.occ.addBox(-hL, -hB, -draft, length, beam, draft)
    gmsh.model.occ.synchronize()

    # Get all surfaces of the box
    surfaces = gmsh.model.getEntities(dim=2)

    # Identify and remove the top surface (at z=0, the waterplane)
    wetted_surfaces = []
    for dim, tag in surfaces:
        com = gmsh.model.occ.getCenterOfMass(dim, tag)
        if abs(com[2] - 0.0) > 1e-6:  # Not the top face
            wetted_surfaces.append(tag)
        # Keep top face for internal lid if needed

    # Physical group for wetted surface
    gmsh.model.addPhysicalGroup(2, wetted_surfaces, name="wetted_surface")

    # Mesh settings
    gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
    gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size * 0.5)
    gmsh.option.setNumber("Mesh.Smoothing", 5)

    # Generate 2D surface mesh
    gmsh.model.mesh.generate(2)

    # Write output
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(output_file)

    gmsh.finalize()
```

### Cylinder Panel Mesh

```python
def create_cylinder_mesh(
    radius: float,
    draft: float,
    mesh_size: float = 1.0,
    output_file: str = "cylinder.msh"
):
    """Create cylinder wetted surface mesh for BEM analysis."""
    gmsh.initialize()
    gmsh.model.add("cylinder")

    # Cylinder from keel to waterplane
    cyl = gmsh.model.occ.addCylinder(0, 0, -draft, 0, 0, draft, radius)
    gmsh.model.occ.synchronize()

    # Get surfaces, exclude top (waterplane)
    surfaces = gmsh.model.getEntities(dim=2)
    wetted = []
    for dim, tag in surfaces:
        com = gmsh.model.occ.getCenterOfMass(dim, tag)
        if com[2] < -1e-6 or abs(com[2] + draft/2) < draft/2:
            wetted.append(tag)

    gmsh.model.addPhysicalGroup(2, wetted, name="wetted_surface")

    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
    gmsh.model.mesh.generate(2)

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(output_file)
    gmsh.finalize()
```

### STEP/STL Import and Remesh

```python
def remesh_step_file(
    step_file: str,
    mesh_size: float = 1.0,
    output_file: str = "remeshed.msh"
):
    """Import STEP geometry and generate new mesh."""
    gmsh.initialize()
    gmsh.model.add("imported")

    # Import STEP
    gmsh.model.occ.importShapes(step_file)
    gmsh.model.occ.synchronize()

    # Fix geometry issues
    gmsh.option.setNumber("Geometry.OCCFixDegenerated", 1)
    gmsh.option.setNumber("Geometry.OCCFixSmallEdges", 1)
    gmsh.option.setNumber("Geometry.OCCSewFaces", 1)

    # Mesh settings
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
    gmsh.option.setNumber("Mesh.Smoothing", 5)

    gmsh.model.mesh.generate(2)

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(output_file)
    gmsh.finalize()


def remesh_stl_file(
    stl_file: str,
    mesh_size: float = 1.0,
    angle: float = 40.0,
    output_file: str = "remeshed.msh"
):
    """Import STL and remesh (classify + reparametrize)."""
    gmsh.initialize()
    gmsh.model.add("stl_remesh")

    gmsh.merge(stl_file)

    # Classify mesh to create geometry
    gmsh.model.mesh.classifySurfaces(
        angle * np.pi / 180,  # angle threshold
        True,   # boundary edges
        False,  # curved edges
        180 * np.pi / 180  # curveAngle
    )
    gmsh.model.mesh.createGeometry()
    gmsh.model.geo.synchronize()

    # Generate new mesh on classified geometry
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
    gmsh.model.mesh.generate(2)

    gmsh.write(output_file)
    gmsh.finalize()
```

### Transfinite Structured Mesh

```python
def create_structured_plate(
    lx: float, ly: float,
    nx: int, ny: int,
    output_file: str = "plate.msh"
):
    """Create a structured quad mesh on a rectangular plate."""
    gmsh.initialize()
    gmsh.model.add("plate")

    # Create rectangle
    p1 = gmsh.model.geo.addPoint(0, 0, 0)
    p2 = gmsh.model.geo.addPoint(lx, 0, 0)
    p3 = gmsh.model.geo.addPoint(lx, ly, 0)
    p4 = gmsh.model.geo.addPoint(0, ly, 0)

    l1 = gmsh.model.geo.addLine(p1, p2)
    l2 = gmsh.model.geo.addLine(p2, p3)
    l3 = gmsh.model.geo.addLine(p3, p4)
    l4 = gmsh.model.geo.addLine(p4, p1)

    cl = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
    s = gmsh.model.geo.addPlaneSurface([cl])

    # Transfinite constraints
    gmsh.model.geo.mesh.setTransfiniteCurve(l1, nx + 1)
    gmsh.model.geo.mesh.setTransfiniteCurve(l3, nx + 1)
    gmsh.model.geo.mesh.setTransfiniteCurve(l2, ny + 1)
    gmsh.model.geo.mesh.setTransfiniteCurve(l4, ny + 1)
    gmsh.model.geo.mesh.setTransfiniteSurface(s, "Left", [p1, p2, p3, p4])
    gmsh.model.geo.mesh.setRecombine(2, s)  # Quads

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)

    gmsh.write(output_file)
    gmsh.finalize()
```

### Field-Based Refinement

```python
def create_refined_mesh(output_file: str = "refined.msh"):
    """Mesh with distance-based refinement near a feature."""
    gmsh.initialize()
    gmsh.model.add("refined")

    # Create geometry (example: plate with hole)
    gmsh.model.occ.addRectangle(0, 0, 0, 20, 10)
    gmsh.model.occ.addDisk(10, 5, 0, 2, 2)
    gmsh.model.occ.cut([(2, 1)], [(2, 2)])
    gmsh.model.occ.synchronize()

    # Distance field from hole boundary
    curves = gmsh.model.getEntities(dim=1)
    f_dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_dist, "CurvesList",
        [c[1] for c in curves if True])  # Filter as needed
    gmsh.model.mesh.field.setNumber(f_dist, "Sampling", 200)

    # Threshold: fine near hole, coarse far away
    f_thresh = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_thresh, "InField", f_dist)
    gmsh.model.mesh.field.setNumber(f_thresh, "SizeMin", 0.2)
    gmsh.model.mesh.field.setNumber(f_thresh, "SizeMax", 2.0)
    gmsh.model.mesh.field.setNumber(f_thresh, "DistMin", 0.5)
    gmsh.model.mesh.field.setNumber(f_thresh, "DistMax", 5.0)

    # Use as background field
    gmsh.model.mesh.field.setAsBackgroundMesh(f_thresh)

    # Disable other size sources
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)

    gmsh.model.mesh.generate(2)
    gmsh.write(output_file)
    gmsh.finalize()
```

## Solver Integration

### Export to AQWA (.DAT Format)

AQWA requires panel meshes in its proprietary .DAT format. gmsh cannot export directly to AQWA format, so a post-processing conversion is needed.

```python
def msh_to_aqwa_panels(msh_file: str, dat_file: str):
    """Convert gmsh MSH to AQWA panel data.

    AQWA expects quad panels (QPPL DIFF cards) with nodes
    defined in counter-clockwise order when viewed from outside.

    See: skills/data/scientific/cad-mesh-generation/SKILL.md
    for complete AQWA .DAT generation.
    """
    gmsh.initialize()
    gmsh.open(msh_file)

    # Get triangle elements
    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    nodes = coords.reshape(-1, 3)
    node_map = {int(t): i for i, t in enumerate(node_tags)}

    elem_types, elem_tags, elem_nodes = gmsh.model.mesh.getElements(dim=2)

    with open(dat_file, 'w') as f:
        # Write node coordinates
        for i, tag in enumerate(node_tags):
            x, y, z = nodes[i]
            f.write(f"NODE {int(tag):6d}  {x:12.4f}{y:12.4f}{z:12.4f}\n")

        # Write elements as QPPL DIFF
        for etype, etags, enodes in zip(elem_types, elem_tags, elem_nodes):
            if etype == 2:  # Triangle (3 nodes)
                n_per_elem = 3
                for j in range(len(etags)):
                    n = enodes[j*n_per_elem:(j+1)*n_per_elem]
                    # AQWA uses repeated 4th node for triangles
                    f.write(f"QPPL DIFF {int(n[0]):6d}{int(n[1]):6d}"
                            f"{int(n[2]):6d}{int(n[2]):6d}\n")
            elif etype == 3:  # Quad (4 nodes)
                n_per_elem = 4
                for j in range(len(etags)):
                    n = enodes[j*n_per_elem:(j+1)*n_per_elem]
                    f.write(f"QPPL DIFF {int(n[0]):6d}{int(n[1]):6d}"
                            f"{int(n[2]):6d}{int(n[3]):6d}\n")

    gmsh.finalize()
```

### Export to WAMIT (GDF Format)

```python
def msh_to_gdf(msh_file: str, gdf_file: str, ulen: float = 1.0,
               gravity: float = 9.81):
    """Convert gmsh MSH to WAMIT/OrcaWave GDF format.

    See: skills/data/scientific/cad-mesh-generation/SKILL.md
    for complete GDF export implementation.
    """
    # GDF format reference:
    # Line 1: header
    # Line 2: ulen, gravity
    # Line 3: isx, isy (symmetry flags)
    # Line 4: npanel
    # Lines 5+: x1 y1 z1  x2 y2 z2  x3 y3 z3  x4 y4 z4 (one panel per line)
    pass  # See cross-referenced skill for full implementation
```

### Export to Nemoh/BEMRosetta

```python
def export_for_nemoh(msh_file: str, nemoh_dir: str):
    """Export gmsh mesh for Nemoh solver.

    Nemoh expects mesh in its own format. Use BEMRosetta for conversion:
      BEMRosetta_cl.exe -mesh -i input.msh -o output.dat -f nemoh

    Alternative: export MSH v2.2 and use BEMRosetta CLI.
    """
    gmsh.initialize()
    gmsh.open(msh_file)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(f"{nemoh_dir}/mesh.msh")
    gmsh.finalize()
    # Then convert with BEMRosetta:
    # D:/software/BEMRosetta/BEMRosetta_cl.exe -mesh -i mesh.msh -o mesh.dat -f nemoh
```

### MSH v2.2 for BEM Tools

Many BEM tools require MSH v2.2 format (ASCII). Always set:

```python
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.option.setNumber("Mesh.Binary", 0)  # ASCII
gmsh.write("output.msh")
```

### Quality Targets for Hydrodynamic Analysis

| Metric | Target | Critical |
|--------|--------|----------|
| Panel count | 500-3000 | Min 200 per body |
| Aspect ratio | < 3:1 | < 5:1 |
| Adjacent panel ratio | < 2:1 | < 3:1 |
| Min panel angle | > 30° | > 15° |
| Panel size | ~L/20 to L/40 | Depends on frequency |
| Normals | Outward pointing | Consistent orientation |

**Rule of thumb**: Element size <= lambda/7 where lambda is the shortest wavelength of interest.

## Mesh Quality Assessment

### Quality Metrics

```python
def check_mesh_quality(msh_file: str):
    """Check mesh quality metrics."""
    gmsh.initialize()
    gmsh.open(msh_file)

    # Get quality statistics
    # Gamma: inscribed/circumscribed radius ratio (1.0 = perfect)
    # Eta: quality measure based on edge lengths
    # Rho: another quality measure

    elem_types, elem_tags, _ = gmsh.model.mesh.getElements(dim=2)
    for etype, etags in zip(elem_types, elem_tags):
        # Get quality for each element
        qualities = gmsh.model.mesh.getElementQualities(
            etags.tolist(), qualityName="minSICN"  # or "gamma", "eta"
        )
        print(f"Element type {etype}: "
              f"min={min(qualities):.3f}, "
              f"max={max(qualities):.3f}, "
              f"mean={sum(qualities)/len(qualities):.3f}")

    gmsh.finalize()
```

### BEM-Specific Quality Checks

- **Adjacent panel ratio**: Ratio between neighboring panel areas should be < 2:1. Gradual variation is acceptable even with large global min/max ratio.
- **Normals consistency**: All panel normals must point outward (into the fluid domain).
- **Watertightness**: No gaps between panels (shared nodes on edges).
- **Panel planarity**: For quad panels, all 4 nodes should be nearly coplanar.

See `skills/engineering/marine-offshore/mesh-utilities/SKILL.md` for mesh inspection tools.

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Empty mesh output | Missing `synchronize()` | Call `gmsh.model.geo.synchronize()` or `gmsh.model.occ.synchronize()` before meshing |
| Wrong element types | Default is triangles | Use `setRecombine()` for quads, or `RecombineAll` option |
| Poor quality at corners | Sharp angles | Add local refinement or increase `Mesh.Smoothing` |
| STEP import fails | Topology issues | Enable `Geometry.OCCFixDegenerated`, `OCCFixSmallEdges`, `OCCSewFaces` |
| MSH format not recognized | Wrong version | Set `Mesh.MshFileVersion` to 2.2 for BEM tools |
| Physical groups empty | Not assigned | Must define physical groups before `write()` |
| Transfinite fails | Incompatible topology | Surface must be 3 or 4-sided, curves must have matching node counts |
| Size fields ignored | Other size sources active | Disable `MeshSizeExtendFromBoundary`, `MeshSizeFromPoints`, `MeshSizeFromCurvature` |
| Crash on large models | Memory | Use `-nt` for parallel meshing, increase verbosity to find bottleneck |
| `gmsh` CLI: `/usr/bin/env: 'python': No such file or directory` | pip-installed gmsh wrapper uses `#!/usr/bin/env python` shebang | Fix shebang: `sed -i 's\|python$\|python3\|' ~/.local/bin/gmsh`; or use `/usr/bin/gmsh` (system binary) |
| pip gmsh shadows system gmsh | `~/.local/bin/gmsh` (pip wrapper) takes precedence over `/usr/bin/gmsh` (native) | Check `type -a gmsh`; pip version is Python-only (no GUI), system version has FLTK GUI |

### Debugging Tips

```python
# Enable verbose output
gmsh.option.setNumber("General.Verbosity", 99)

# Check model entities
print(gmsh.model.getEntities())  # All entities
print(gmsh.model.getEntities(dim=2))  # Surfaces only

# Check bounding box
xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)

# Visualize interactively
gmsh.fltk.run()  # Opens GUI

# Check mesh statistics
gmsh.model.mesh.generate(2)
node_tags, _, _ = gmsh.model.mesh.getNodes()
print(f"Number of nodes: {len(node_tags)}")
elem_types, elem_tags, _ = gmsh.model.mesh.getElements(dim=2)
total_elems = sum(len(t) for t in elem_tags)
print(f"Number of elements: {total_elems}")
```

## Resources

### Online Documentation

- **Official docs**: https://gmsh.info/doc/texinfo/gmsh.html
- **Python API reference**: https://gmsh.info/doc/texinfo/gmsh.html#Gmsh-API
- **Tutorials**: https://gmsh.info/#Tutorials
- **Source repository**: https://gitlab.onelab.info/gmsh/gmsh

### Local Installation

- **Executable**: `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe`
- **Tutorials (.geo)**: `D:\software\gmsh\gmsh-4.15.0-Windows64\tutorials\t1.geo` through `t21.geo`
- **Python tutorials**: `D:\software\gmsh\gmsh-4.15.0-Windows64\tutorials\python\`
- **API examples**: `D:\software\gmsh\gmsh-4.15.0-Windows64\examples\api\`
- **Boolean examples**: `D:\software\gmsh\gmsh-4.15.0-Windows64\examples\boolean\`

### Tutorial Index

See `assets/gmsh-reference.md` for complete tutorial descriptions and CLI options reference.

### Related Skills

- `skills/data/scientific/cad-mesh-generation/SKILL.md` — FreeCAD + gmsh workflows, GDF/CDB export
- `skills/engineering/marine-offshore/mesh-utilities/SKILL.md` — mesh inspection, conversion, quality checks
- `skills/engineering/cad/cad-engineering/SKILL.md` — general CAD engineering
- `skills/engineering/cad/freecad-automation/SKILL.md` — FreeCAD automation
