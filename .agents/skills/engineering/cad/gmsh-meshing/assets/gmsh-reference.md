# gmsh 4.15.0 Reference

> Condensed reference for gmsh CLI, algorithms, formats, options, and tutorials.
> See SKILL.md for usage patterns and workflows.

## Version Info

- **Version**: 4.15.0
- **Build date**: 2025-10-26
- **Build options**: 64Bit ALGLIB ANN Bamg Blas[petsc] Blossom Cgns DIntegration DomHex Eigen Fltk Gmm Hxt Jpeg Kbipack Lapack[petsc] MathEx Med Mesh Metis Mmg Mpeg Netgen Nii2mesh ONELAB ONELABMetamodel OpenCASCADE OpenCASCADE-CAF OpenGL OpenMP OptHom PETSc Parser Plugins Png Post QuadMeshingTools QuadTri Solver TetGen/BR TinyXML2 Untangle Voro++ WinslowUntangler Zlib tinyobjloader
- **FLTK**: 1.3.11 | **PETSc**: 3.15.0 | **OCC**: 7.8.1 | **MED**: 4.1.0

## CLI Options (Complete)

### Geometry
| Flag | Description |
|------|-------------|
| `-0` | Output model, then exit |
| `-tol <value>` | Set geometrical tolerance |
| `-match` | Match geometries and meshes |

### Mesh
| Flag | Description |
|------|-------------|
| `-1`, `-2`, `-3` | Generate 1D, 2D, or 3D mesh |
| `-format <string>` | Output format (see Formats table) |
| `-bin` | Create binary files when possible |
| `-refine` | Uniform mesh refinement |
| `-barycentric_refine` | Barycentric mesh refinement |
| `-reclassify <angle>` | Reclassify surface mesh |
| `-reparam <angle>` | Reparametrize surface mesh |
| `-hybrid` | Generate hybrid hex-tet mesh |
| `-part <int>` | Partition mesh |
| `-part_weight [types] <int>` | Set partition weight by element type |
| `-part_split` | Save partitions in separate files |
| `-preserve_numbering_msh2` | Preserve MSH2 numbering |
| `-save_all` | Save all elements |
| `-save_parametric` | Save nodes with parametric coordinates |
| `-save_topology` | Save model topology |
| `-algo <string>` | Select mesh algorithm |
| `-smooth <int>` | Number of smoothing steps |
| `-order <int>` | Set mesh order |
| `-optimize[_netgen]` | Optimize tetrahedral quality |
| `-optimize_threshold` | Optimize below quality threshold |
| `-optimize_ho` | Optimize high order meshes |
| `-clscale <value>` | Mesh element size factor |
| `-clmin <value>` | Minimum element size |
| `-clmax <value>` | Maximum element size |
| `-clextend <value>` | Extend sizes from boundaries |
| `-clcurv <value>` | Elements per 2*pi from curvature |
| `-aniso_max <value>` | Max anisotropy (bamg) |
| `-smooth_ratio <value>` | Smoothing ratio (bamg) |
| `-epslc1d <value>` | 1D mesh size field accuracy |
| `-swapangle <value>` | Face swap threshold angle (degrees) |
| `-rand <value>` | Random perturbation factor |
| `-bgm <file>` | Load background mesh |
| `-check` | Perform mesh consistency checks |
| `-ignore_periocity` | Ignore periodic boundaries |

### Post-processing
| Flag | Description |
|------|-------------|
| `-link <int>` | Link mode between views |
| `-combine` | Combine views with identical names |

### Solver
| Flag | Description |
|------|-------------|
| `-listen <string>` | Listen for connection requests |
| `-minterpreter <string>` | Octave interpreter name |
| `-pyinterpreter <string>` | Python interpreter name |
| `-run` | Run ONELAB solver(s) |

### Display
| Flag | Description |
|------|-------------|
| `-n` | Hide all meshes and views on startup |
| `-nodb` | Disable double buffering |
| `-numsubedges` | Subdivisions for high order display |
| `-fontsize <int>` | GUI font size |
| `-theme <string>` | FLTK GUI theme |
| `-display <string>` | Display string |
| `-camera` | Camera mode view |
| `-stereo` | Stereo rendering |
| `-gamepad` | Use gamepad controller |

### Other
| Flag | Description |
|------|-------------|
| `-`, `-parse_and_exit` | Parse input files, then exit |
| `-save` | Save output file, then exit |
| `-o <file>` | Output file name |
| `-new` | Create new model before next file |
| `-merge` | Merge next files |
| `-open` | Open next files |
| `-log <filename>` | Log all messages |
| `-a`, `-g`, `-m`, `-s`, `-p` | Start in auto/geometry/mesh/solver/post mode |
| `-pid` | Print process id |
| `-watch <pattern>` | Watch for files to merge |
| `-bg <file>` | Load background file (image/PDF) |
| `-v <int>` | Verbosity level (0-99) |
| `-string "<string>"` | Parse command string at startup |
| `-setnumber <name> <value>` | Set constant/option number |
| `-setstring <name> <value>` | Set constant/option string |
| `-nopopup` | Suppress dialog popups in scripts |
| `-noenv` | Don't modify environment at startup |
| `-nolocale` | Don't modify locale at startup |
| `-option <file>` | Parse option file at startup |
| `-convert <files>` | Convert to latest binary formats |
| `-nt <int>` | Number of threads |
| `-cpu` | Report CPU times |
| `-version` | Show version number |
| `-info` | Show detailed version information |
| `-help` | Show command line usage |
| `-help_options` | Show all options |

## Mesh Algorithms (Detailed)

### 2D Algorithms

| ID | Name | CLI Flag | Description |
|----|------|----------|-------------|
| 1 | MeshAdapt | `meshadapt` | Adaptive mesh, good for complex geometries. Splits/swaps/collapses edges. |
| 2 | Automatic | `auto` | Automatic selection based on geometry |
| 5 | Delaunay | `del2d` | Default 2D. Robust, general purpose Delaunay triangulation. |
| 6 | Frontal-Delaunay | `front2d` | Advancing front with Delaunay. Better quality triangles. **Recommended for BEM.** |
| 7 | BAMG | — | Anisotropic mesh adaptation (2D only) |
| 8 | Frontal-Delaunay for Quads | `delquad` | Generates quads via recombination after Frontal-Delaunay |
| 9 | Packing of Parallelograms | `quadqs` | Quad-dominant structured-like meshing |
| 11 | Quasi-structured Quad | — | Experimental quasi-structured quad meshing |

### 3D Algorithms

| ID | Name | CLI Flag | Description |
|----|------|----------|-------------|
| 1 | Delaunay | `del3d` | Default 3D. Standard Delaunay tetrahedralization. |
| 3 | Initial Mesh Only | `initial3d` | Only create initial mesh, no optimization |
| 4 | Frontal | `front3d` | Advancing front. Better quality but slower. |
| 7 | MMG3D | `mmg3d` | Remeshing with MMG library |
| 10 | HXT | `hxt` | Parallel Delaunay. Fastest for large models. |

## Supported File Formats

### Input Formats

| Format | Extensions | Description |
|--------|-----------|-------------|
| Native | `.geo`, `.geo_unrolled` | gmsh geometry scripts |
| MSH | `.msh` | gmsh mesh format (v1-v4.1) |
| STEP | `.step`, `.stp` | STEP CAD (via OpenCASCADE) |
| IGES | `.iges`, `.igs` | IGES CAD (via OpenCASCADE) |
| BREP | `.brep` | OpenCASCADE BREP |
| STL | `.stl` | Stereolithography |
| OBJ | `.obj` | Wavefront OBJ |
| PLY | `.ply` | Stanford polygon |
| VTK | `.vtk` | Visualization Toolkit |
| UNV | `.unv` | Universal file format |
| MED | `.med` | Salome MED |
| CGNS | `.cgns` | CFD General Notation |
| BDF | `.bdf`, `.nas` | Nastran bulk data |
| INP | `.inp` | Abaqus input |
| P3D | `.p3d` | Plot3D structured |
| POS | `.pos` | gmsh post-processing view |

### Output Formats

| CLI `-format` | Extension | Description |
|---------------|-----------|-------------|
| `msh`, `msh41` | `.msh` | MSH v4.1 (default) |
| `msh4`, `msh40` | `.msh` | MSH v4.0 |
| `msh2`, `msh22` | `.msh` | MSH v2.2 (**use for BEM tools**) |
| `msh1` | `.msh` | MSH v1.0 |
| `unv` | `.unv` | Universal |
| `vtk` | `.vtk` | VTK |
| `stl` | `.stl` | STL |
| `mesh` | `.mesh` | Medit |
| `bdf` | `.bdf` | Nastran |
| `cgns` | `.cgns` | CGNS |
| `med` | `.med` | MED |
| `inp` | `.inp` | Abaqus |
| `su2` | `.su2` | SU2 |
| `dat` | `.dat` | Fluent (NOT AQWA) |
| `key` | `.key` | LS-DYNA |
| `off` | `.off` | Object File Format |
| `rad` | `.rad` | Radioss |
| `obj` | `.obj` | Wavefront OBJ |
| `wrl` | `.wrl` | VRML |
| `mail` | `.mail` | Code_Aster mail |
| `ir3` | `.ir3` | IR3 |
| `celum` | `.celum` | CELUM |
| `p3d` | `.p3d` | Plot3D |
| `neu` | `.neu` | Gambit neutral |
| `m` | `.m` | Matlab |
| `ply2` | `.ply2` | PLY2 |
| `x3d` | `.x3d` | X3D |
| `diff` | `.diff` | DIFF |

**Note**: The `-format dat` produces Fluent DAT, not AQWA DAT. For AQWA, export MSH and convert with custom script (see SKILL.md § Solver Integration).

## Key gmsh.option Settings

### Most-Used Options

| Option | Default | Description |
|--------|---------|-------------|
| `General.Verbosity` | 5 | Message verbosity (0=silent, 99=debug) |
| `General.NumThreads` | 1 | Number of threads |
| `Geometry.Tolerance` | 1e-8 | Geometric tolerance |
| `Geometry.OCCFixDegenerated` | 0 | Fix degenerated edges in OCC |
| `Geometry.OCCFixSmallEdges` | 0 | Fix small edges in OCC |
| `Geometry.OCCFixSmallFaces` | 0 | Fix small faces in OCC |
| `Geometry.OCCSewFaces` | 0 | Sew faces in OCC |
| `Mesh.Algorithm` | 6 | 2D mesh algorithm (see table) |
| `Mesh.Algorithm3D` | 1 | 3D mesh algorithm (see table) |
| `Mesh.MeshSizeFactor` | 1.0 | Global mesh size scaling factor |
| `Mesh.MeshSizeMin` | 0 | Minimum element size |
| `Mesh.MeshSizeMax` | 1e22 | Maximum element size |
| `Mesh.MeshSizeFromCurvature` | 0 | Elements per 2*pi from curvature |
| `Mesh.MeshSizeFromPoints` | 1 | Use size from geometry points |
| `Mesh.MeshSizeExtendFromBoundary` | 1 | Extend sizes from boundary |
| `Mesh.ElementOrder` | 1 | Element order (1=linear, 2=quadratic) |
| `Mesh.Smoothing` | 1 | Number of smoothing steps |
| `Mesh.Optimize` | 1 | Optimize mesh |
| `Mesh.OptimizeNetgen` | 0 | Optimize with Netgen |
| `Mesh.RecombineAll` | 0 | Recombine all surfaces to quads |
| `Mesh.RecombinationAlgorithm` | 1 | 0=simple, 1=blossom, 2=simple full-quad, 3=blossom full-quad |
| `Mesh.MshFileVersion` | 4.1 | MSH file format version |
| `Mesh.Binary` | 0 | Binary file output |
| `Mesh.SaveAll` | 0 | Save all elements |

### Field Types

| Field | Description |
|-------|-------------|
| `Distance` | Distance from points, curves, or surfaces |
| `Threshold` | Size based on distance field (linear interpolation) |
| `Box` | Different size inside/outside a box |
| `Ball` | Different size inside/outside a ball |
| `Cylinder` | Different size inside/outside a cylinder |
| `Frustum` | Different size inside/outside a frustum |
| `MathEval` | Size from mathematical expression |
| `Param` | Size from parametric coordinates |
| `PostView` | Size from post-processing view |
| `Attractor` | Deprecated, use Distance |
| `Min` | Minimum of multiple fields |
| `Max` | Maximum of multiple fields |
| `Mean` | Mean of multiple fields |
| `Restrict` | Restrict field to specific surfaces/volumes |
| `Constant` | Constant size value |
| `Structured` | Structured background mesh |
| `ExternalProcess` | Size from external process |

## Tutorial Index

### Core Tutorials (t1-t21)

| Tutorial | Title | Key Concepts |
|----------|-------|-------------|
| t1 | Geometry basics, elementary entities | Points, lines, curve loops, surfaces, physical groups |
| t2 | Transformations, extruded meshes | Translate, rotate, extrude, holes in surfaces |
| t3 | Extruded meshes, ONELAB parameters | Extrusion, parameters, variables |
| t4 | Built-in functions, macros, loops | Functions, For loops, string manipulation |
| t5 | Mesh sizes, macros, loops | Characteristic lengths, Include, Printf |
| t6 | Transfinite meshes, constraints | Transfinite curves/surfaces/volumes, structured mesh |
| t7 | Background mesh | Size fields from .pos file, background mesh |
| t8 | Post-processing, image export | Views, plugins, annotations |
| t9 | Post-processing plugins | Isosurface, cutting plane, annotations |
| t10 | Mesh size fields | Distance, Threshold, Min fields |
| t11 | Unstructured quadrilateral meshes | Quad meshing, recombination |
| t12 | Cross-patch meshing | Compound surfaces, cross-patch meshing |
| t13 | Remeshing STL geometry | STL import, classification, remeshing |
| t14 | Homology and cohomology | Homology computations |
| t15 | Embedded points, lines, surfaces | Embedding entities in higher-dim entities |
| t16 | Constructive Solid Geometry (CSG) | OpenCASCADE boolean operations |
| t17 | Anisotropic background mesh | Anisotropic size field, .pos background |
| t18 | Periodic meshes | Periodic boundary conditions, mesh copying |
| t19 | Thrusections, pipes, fillets | OCC thrusections, pipe, fillet, chamfer |
| t20 | STEP import, geometry healing | STEP import, OCC healing options |
| t21 | Mesh partitioning | Metis/CHACO partitioning, ghost cells |

### Extended Tutorials (x1-x7, Python/C++/Julia only)

| Tutorial | Title | Key Concepts |
|----------|-------|-------------|
| x1 | Geometry and mesh data | Accessing mesh data via API |
| x2 | Mesh import, discrete entities | Importing external meshes |
| x3 | Post-processing data import | Importing post-processing data |
| x4 | Mesh generation, parametric coords | Parametric coordinates, reparametrization |
| x5 | Additional mesh data | Element qualities, Jacobians |
| x6 | Additional geometry data | Curvature, normals, bounding boxes |
| x7 | Background mesh from field | Field-based background mesh |

## Online Resources

| Resource | URL |
|----------|-----|
| Official website | https://gmsh.info |
| Full documentation | https://gmsh.info/doc/texinfo/gmsh.html |
| Python API reference | https://gmsh.info/doc/texinfo/gmsh.html#Gmsh-API |
| Tutorial pages | https://gmsh.info/#Tutorials |
| GitLab repository | https://gitlab.onelab.info/gmsh/gmsh |
| PyPI package | https://pypi.org/project/gmsh/ |
| Mailing list archives | https://gmsh.info/mailman/listinfo/gmsh |
| Changelog | https://gmsh.info/changelog |
| Wiki | https://gitlab.onelab.info/gmsh/gmsh/-/wikis/home |
