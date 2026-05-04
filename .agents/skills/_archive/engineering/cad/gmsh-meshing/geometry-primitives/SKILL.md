---
name: gmsh-meshing-geometry-primitives
description: 'Sub-skill of gmsh-meshing: Geometry Primitives (+5).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Geometry Primitives (+5)

## Geometry Primitives


```geo
// Points: Point(id) = {x, y, z, mesh_size};
Point(1) = {0, 0, 0, 1.0};
Point(2) = {10, 0, 0, 1.0};
Point(3) = {10, 5, 0, 0.5};
Point(4) = {0, 5, 0, 0.5};

// Lines
Line(1) = {1, 2};
Line(2) = {2, 3};

*See sub-skills for full details.*

## Surface and Volume


```geo
// Surface from curve loops (first = outer boundary, rest = holes)
Plane Surface(1) = {1};
Plane Surface(2) = {2, 3};  // Surface 2 with hole defined by loop 3

// Surface Loop (for volumes)
Surface Loop(1) = {1, 2, 3, 4, 5, 6};

// Volume from surface loops
Volume(1) = {1};
```

## Transformations


```geo
// Translate (creates copy if Duplicata used)
Translate {dx, dy, dz} { Surface{1}; }

// Rotate: angle in radians
Rotate {{ax, ay, az}, {px, py, pz}, angle} { Surface{1}; }

// Symmetry
Symmetry {a, b, c, d} { Surface{1}; }  // plane ax+by+cz+d=0


*See sub-skills for full details.*

## OpenCASCADE Kernel


```geo
// Enable OpenCASCADE kernel (must be first geometry command)
SetFactory("OpenCASCADE");

// Primitives
Box(1) = {x, y, z, dx, dy, dz};
Sphere(2) = {x, y, z, radius};
Cylinder(3) = {x, y, z, dx, dy, dz, radius};
Cone(4) = {x, y, z, dx, dy, dz, r1, r2};
Torus(5) = {x, y, z, r1, r2};

*See sub-skills for full details.*

## Physical Groups


```geo
// Physical groups assign labels for export
Physical Surface("hull") = {1, 2, 3};
Physical Surface("deck") = {4};
Physical Volume("fluid") = {1};

// Numbered groups
Physical Surface(100) = {1, 2, 3};
```

## Mesh Control in .geo


```geo
// Characteristic length at points
Characteristic Length {1, 2, 3} = 0.5;

// Transfinite curves (structured)
Transfinite Curve {1, 3} = 20;       // 20 nodes
Transfinite Curve {2, 4} = 10;       // 10 nodes
Transfinite Curve {1} = 20 Using Progression 1.1;  // graded

// Transfinite surface

*See sub-skills for full details.*
