---
name: gmsh-meshing-initialization-and-model-management
description: 'Sub-skill of gmsh-meshing: Initialization and Model Management (+6).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Initialization and Model Management (+6)

## Initialization and Model Management


```python
import gmsh

# Initialize
gmsh.initialize()
gmsh.option.setNumber("General.Verbosity", 3)

# Create a new model
gmsh.model.add("my_model")


*See sub-skills for full details.*

## Built-in Kernel (gmsh.model.geo)


```python
# Points
p1 = gmsh.model.geo.addPoint(0, 0, 0, meshSize=1.0)
p2 = gmsh.model.geo.addPoint(10, 0, 0, meshSize=1.0)
p3 = gmsh.model.geo.addPoint(10, 5, 0, meshSize=0.5)

# Lines
l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)


*See sub-skills for full details.*

## OpenCASCADE Kernel (gmsh.model.occ)


```python
# Box: addBox(x, y, z, dx, dy, dz)
box = gmsh.model.occ.addBox(0, 0, 0, 100, 20, 10)

# Sphere: addSphere(xc, yc, zc, radius)
sphere = gmsh.model.occ.addSphere(0, 0, 0, 5.0)

# Cylinder: addCylinder(x, y, z, dx, dy, dz, r)
cyl = gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, 10, 5.0)


*See sub-skills for full details.*

## Mesh Generation (gmsh.model.mesh)


```python
# Generate mesh
gmsh.model.mesh.generate(1)   # 1D
gmsh.model.mesh.generate(2)   # 2D surface
gmsh.model.mesh.generate(3)   # 3D volume

# Recombine triangles to quads
gmsh.model.mesh.recombine()

# Set transfinite constraints

*See sub-skills for full details.*

## Options (gmsh.option)


```python
# Mesh algorithm selection
gmsh.option.setNumber("Mesh.Algorithm", 6)       # Frontal-Delaunay 2D
gmsh.option.setNumber("Mesh.Algorithm3D", 1)      # Delaunay 3D

# Size controls
gmsh.option.setNumber("Mesh.MeshSizeFactor", 0.5)
gmsh.option.setNumber("Mesh.MeshSizeMin", 0.1)
gmsh.option.setNumber("Mesh.MeshSizeMax", 2.0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)

*See sub-skills for full details.*

## Mesh Size Fields (gmsh.model.mesh.field)


```python
# Distance field — distance from curves or points
f_dist = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(f_dist, "CurvesList", [1, 2, 3])
gmsh.model.mesh.field.setNumber(f_dist, "Sampling", 100)

# Threshold field — size based on distance
f_thresh = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(f_thresh, "InField", f_dist)
gmsh.model.mesh.field.setNumber(f_thresh, "SizeMin", 0.1)    # size at DistMin

*See sub-skills for full details.*

## File I/O


```python
# Write mesh
gmsh.write("output.msh")       # Default format
gmsh.write("output.stl")       # STL
gmsh.write("output.vtk")       # VTK
gmsh.write("output.unv")       # Universal
gmsh.write("output.bdf")       # Nastran

# Write specific format version
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

*See sub-skills for full details.*
