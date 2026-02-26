# Open-Source Finite Element Analysis (FEA) Software Survey

**Date:** 2026-02-21
**Scope:** Structural, thermal, and multiphysics analysis on Linux
**Audience:** Engineers evaluating open-source FEA tools for academic and professional assignments

---

## 1. Overview

The open-source finite element analysis landscape has matured substantially over the past decade. What was once dominated exclusively by commercial packages (ANSYS, Abaqus, COMSOL) costing tens of thousands of dollars annually now has viable free alternatives covering structural mechanics, heat transfer, electromagnetics, fluid-structure interaction, and general multiphysics. The ecosystem broadly divides into three tiers:

- **Turnkey solvers with GUIs** (CalculiX + PrePoMax, Salome-Meca/Code\_Aster, Elmer FEM) -- these provide end-to-end workflows from geometry to results.
- **Programmable frameworks** (FEniCSx, MOOSE, deal.II, SfePy, FreeFEM) -- these target users who define problems in code (Python, C++, or domain-specific languages).
- **Ecosystem tools** (FreeCAD, Gmsh, ParaView) -- pre/post-processors and mesh generators that connect to multiple solvers.

Key infrastructure tools underpinning most workflows include **Gmsh** (v4.15.1, February 2026) for mesh generation, **ParaView** for post-processing and visualization, and **FreeCAD** (v1.0 released November 2024, v1.1 in development) as an integrated CAD + FEM environment.

This report evaluates 12 programs across 8 criteria and provides actionable recommendations for engineering assignment use.

---

## 2. Comparison Matrix

| Program | Active Maintenance | Linux Support | Documentation | Learning Curve | File Format Support | Integration | Assignment Suitability | Python Scripting |
|---|---|---|---|---|---|---|---|---|
| **CalculiX** | Good (v2.23, Nov 2025) | Excellent (apt, conda) | Good | Moderate | Excellent (Abaqus INP, Gmsh) | Excellent (FreeCAD, Gmsh, ParaView) | Excellent | Good (pycalculix) |
| **Code\_Aster / Salome-Meca** | Good (v2024.1, 2024) | Good (Singularity container) | Good (French + English) | Steep | Good (MED, STEP, Gmsh) | Good (Salome, ParaView) | Excellent | Good (Python commands) |
| **Elmer FEM** | Good (active dev, v9.0 base) | Good (PPA, build from source) | Good (tutorials, models manual) | Moderate | Good (Gmsh .msh, VTK, ElmerGrid) | Good (Gmsh, ParaView, FreeCAD) | Excellent | Fair (limited API) |
| **MOOSE Framework** | Excellent (continuous, INL) | Good (conda) | Excellent (extensive docs) | Steep | Fair (Exodus, custom) | Fair (ParaView, custom) | Good (advanced) | Good (Python input) |
| **GetDP** | Fair (tied to Gmsh/ONELAB) | Excellent (via Gmsh package) | Fair (academic focus) | Steep | Fair (Gmsh .msh, ONELAB) | Good (Gmsh, ONELAB) | Fair (EM-focused) | Poor (scripted DSL) |
| **PrePoMax** | Excellent (v2.4.5 dev, Feb 2026) | Poor (Windows/.NET, Wine only) | Good (manual, tutorials) | Easy | Excellent (STEP, STL, INP, Gmsh) | Good (CalculiX backend) | Excellent | Poor (GUI-only) |
| **FEniCSx** | Excellent (v0.10, Oct 2025) | Excellent (apt PPA, conda, pip) | Excellent (tutorials, demos) | Moderate-Steep | Fair (Gmsh .msh, XDMF/HDF5) | Good (Gmsh, ParaView, pyvista) | Good (code-based) | Excellent (native Python) |
| **deal.II** | Excellent (v9.7, Jul 2025) | Good (candi installer, apt) | Excellent (1000+ tutorial programs) | Steep | Fair (VTK, custom) | Fair (ParaView) | Good (advanced) | Poor (C++ only) |
| **SU2** | Good (v8.3.0, Sep 2025) | Good (build from source, conda) | Good (tutorials, wiki) | Steep | Fair (SU2 native, CGNS, Gmsh) | Fair (ParaView, Gmsh) | Fair (CFD-focused) | Good (Python wrapping) |
| **FreeFEM** | Good (v4.15, Dec 2024) | Excellent (apt, snap) | Good (extensive examples) | Moderate | Fair (Gmsh, Medit, VTK) | Fair (Gmsh, ParaView) | Good | Fair (own DSL + some Python) |
| **SfePy** | Excellent (v2025.4, Dec 2025) | Excellent (pip, conda) | Good (examples gallery) | Moderate | Good (VTK, Gmsh .msh, HDF5) | Good (Gmsh, ParaView, pyvista) | Good | Excellent (native Python) |
| **OpenRadioss** | Good (active GitHub) | Good (build from source) | Fair (growing docs) | Steep | Good (Radioss, LS-DYNA formats) | Fair (limited ecosystem) | Fair (crash/dynamic focus) | Poor (input deck driven) |

### Rating Legend

- **Excellent**: Best-in-class, ready for immediate productive use
- **Good**: Solid capability with minor limitations
- **Fair**: Usable but requires workarounds or has gaps
- **Poor**: Significant limitations or not applicable

---

## 3. Individual Program Profiles

### CalculiX (v2.23, November 2025)

CalculiX is a mature, lightweight structural FEA solver with Abaqus-compatible input format, making it one of the most practical choices for engineers transitioning from commercial tools. Its solver (CCX) handles linear/nonlinear static, dynamic, thermal, and coupled thermo-mechanical problems. The pre/post-processor (CGX) is functional but dated; most users prefer PrePoMax or FreeCAD's FEM workbench instead. CalculiX is available via `apt` on Debian/Ubuntu (though repository versions lag behind) and via `conda-forge` for the latest builds. **Best for:** Structural assignments where Abaqus-style input is desired, beam bending, plate stress, modal analysis, and heat transfer problems.

**Strengths:** Abaqus INP compatibility, extensive verified element library, lightweight, excellent ecosystem integration.
**Weaknesses:** Text-based input without GUI (mitigated by PrePoMax/FreeCAD), limited parallel scaling, no native multiphysics beyond thermo-mechanical.

### Code\_Aster / Salome-Meca (v2024.1)

Developed by EDF (Electricite de France) for nuclear industry applications, Code\_Aster is arguably the most feature-rich open-source structural solver available. It supports linear/nonlinear mechanics, fatigue, fracture mechanics, thermal analysis, acoustics, and fluid-structure interaction. Salome-Meca bundles Code\_Aster with the Salome platform for pre/post-processing. The steep learning curve and French-origin documentation (increasingly translated) are the main barriers. Installation on Linux uses Singularity containers, which adds complexity but ensures reproducibility. **Best for:** Advanced structural analysis, nuclear/civil engineering, thermo-mechanical coupling where commercial-grade capability is needed at zero cost.

**Strengths:** Massive feature set, EDF validation suite (>5000 test cases), strong thermo-mechanical coupling.
**Weaknesses:** Steep learning curve, Singularity container deployment, documentation still partially French-only, large footprint.

### Elmer FEM (v9.0+, CSC Finland, active development)

Elmer is the most genuinely multiphysics open-source FEM package, covering heat transfer, fluid dynamics, structural mechanics, electromagnetics, and acoustics in a single unified framework. Developed by CSC (Finland's IT Center for Science), it excels at coupled problems where multiple physics domains interact. ElmerGUI provides a graphical interface, though command-line workflows via SIF (Solver Input Files) are more common for advanced use. PPA packages exist for Ubuntu, and building from source is well-documented. **Best for:** Multiphysics assignments combining heat transfer with structural or electromagnetic analysis, and academic research.

**Strengths:** True multiphysics coupling, wide solver library (50+ solver modules), active community, good documentation.
**Weaknesses:** PPA not always current for latest Ubuntu, GUI less polished than commercial tools, parallelization can be complex to configure.

### MOOSE Framework (Idaho National Laboratory, continuous releases)

MOOSE (Multiphysics Object-Oriented Simulation Environment) is a C++-based finite element framework designed for solving coupled multiphysics problems, particularly in nuclear engineering. Rather than a turnkey solver, MOOSE is a framework for building physics applications -- users create or use "MOOSE apps" like BISON (nuclear fuel), GRIFFIN (reactor physics), or general heat conduction/mechanics modules. Installation is via conda, and documentation is extensive with active workshops. **Best for:** Researchers and advanced users building custom multiphysics solvers, nuclear engineering, and parametric studies requiring tight code control.

**Strengths:** Powerful multiphysics framework, excellent documentation and workshops, very active development, PETSc/libMesh backend.
**Weaknesses:** Framework-level tool (not turnkey), steep learning curve, overkill for simple assignments, requires C++ for custom physics.

### GetDP (tied to Gmsh/ONELAB ecosystem)

GetDP is a general finite element solver particularly strong in electromagnetics, developed alongside Gmsh as part of the ONELAB ecosystem. It uses a domain-specific language that closely mirrors the mathematical formulation of PDEs, which is elegant but demands solid mathematical background. It integrates seamlessly with Gmsh for mesh generation and post-processing through the ONELAB interface. **Best for:** Electromagnetics assignments and users already comfortable with Gmsh who want a tightly integrated solver.

**Strengths:** Tight Gmsh integration, mathematically rigorous formulation, good for EM problems.
**Weaknesses:** Steep learning curve, limited community outside EM, documentation is academic in nature, not suitable for general structural FEA.

### PrePoMax (v2.4.5 dev, February 2026)

PrePoMax is a modern, intuitive GUI pre/post-processor for the CalculiX solver, developed at the University of Maribor. It has dramatically lowered the barrier to entry for CalculiX by providing point-and-click model setup, meshing (via Netgen), boundary condition application, and results visualization. The major caveat for this survey is that PrePoMax is a Windows/.NET application with no native Linux support -- it can run on Linux via Wine but with display glitches. **Best for:** Windows users wanting the easiest path to production FEA with CalculiX; not recommended as a primary Linux tool.

**Strengths:** Excellent GUI, rapid model setup, active development, comprehensive CalculiX feature coverage.
**Weaknesses:** No native Linux support (Wine only), .NET Framework dependency, no Python scripting API, GUI-only workflow.

### FEniCSx (v0.10, October 2025)

FEniCSx is the next-generation Python/C++ computing platform for solving PDEs using the finite element method. Users express problems in variational form using the Unified Form Language (UFL), and FEniCSx automatically generates efficient C code for assembly. This approach is extraordinarily powerful for custom physics but requires understanding of weak formulations. Installation is straightforward via apt PPA, conda, or Docker. **Best for:** Researchers and students who want to implement custom FEM formulations in Python, parametric studies, and problems not covered by standard solvers.

**Strengths:** Native Python, automatic code generation, excellent for custom PDEs, parallel support via MPI, active development.
**Weaknesses:** Requires PDE/variational formulation knowledge, not turnkey for standard engineering problems, steeper curve than GUI-based tools for simple assignments.

### deal.II (v9.7, July 2025)

deal.II is an award-winning C++ finite element library with over 1000 documented tutorial programs. It is arguably the most feature-rich FEM library for adaptive mesh refinement and supports hp-adaptivity, multigrid solvers, and distributed computing. The library won the 2024 SIAM/ACM Prize in Computational Science and Engineering. Installation uses the `candi` script to build from source with all dependencies. **Best for:** Advanced computational researchers needing adaptive FEM, hp-methods, or building custom solvers in C++.

**Strengths:** Adaptive mesh refinement, massive tutorial collection, award-winning, excellent parallel scaling.
**Weaknesses:** C++ only (no Python), steep learning curve, library (not application), overkill for standard assignments.

### SU2 (v8.3.0 "Harrier", September 2025)

SU2 originated at Stanford University as a CFD solver and has expanded into multiphysics simulation including conjugate heat transfer, fluid-structure interaction, and shape optimization with adjoint methods. While primarily CFD-focused, its structural solver capabilities have grown. It excels in aerodynamic and aerothermal applications. **Best for:** Aerodynamics, conjugate heat transfer, shape optimization, and CFD-adjacent structural analysis.

**Strengths:** Excellent CFD capabilities, adjoint-based optimization, active community, LGPL license.
**Weaknesses:** Primary strength is CFD not structural FEA, limited for pure structural assignments, complex setup for non-CFD problems.

### FreeFEM (v4.15, December 2024)

FreeFEM is a PDE solver using its own high-level scripting language (.edp files) that allows rapid prototyping of finite element solutions. It includes built-in meshing (BAMG), interfaces with PETSc for parallel computing, and recently added boundary element method (BEM) support. The scripting language is accessible to those with mathematical background. **Best for:** Academic PDE courses, rapid prototyping of 2D/3D finite element problems, and researchers needing quick-turnaround custom formulations.

**Strengths:** Rapid prototyping, built-in meshing, BEM support, extensive example library, easy apt installation.
**Weaknesses:** Custom scripting language (not Python), less suitable for standard engineering workflows, limited CAD integration.

### SfePy (v2025.4, December 2025)

SfePy (Simple Finite Elements in Python) is a Python framework for solving PDEs by FEM in 1D, 2D, and 3D. Problems are defined via Python scripts or YAML configuration files, making it highly scriptable and suitable for parametric studies. It supports structural mechanics, heat transfer, acoustics, and more. **Best for:** Python-oriented engineers wanting a lightweight, scriptable FEM tool for moderate-complexity problems.

**Strengths:** Pure Python, pip-installable, good Gmsh/VTK integration, active quarterly releases.
**Weaknesses:** Smaller community than FEniCSx, less documentation, performance limited by Python overhead for large models.

### OpenRadioss (open-sourced 2022, active development)

OpenRadioss is the open-source version of Altair's Radioss explicit dynamics solver, released under AGPL. It specializes in crash simulation, impact analysis, and highly dynamic events. It supports advanced material models, contact algorithms, and can read LS-DYNA input format. **Best for:** Crash simulation, impact dynamics, blast analysis -- not for general static structural or thermal assignments.

**Strengths:** Industry-proven explicit dynamics solver, LS-DYNA compatibility, advanced material models.
**Weaknesses:** Explicit dynamics focus (not for static/thermal), limited pre/post-processing ecosystem, AGPL license restrictions.

---

## 4. Top 3 Recommendations

### Rank 1: CalculiX (with FreeCAD FEM Workbench + Gmsh + ParaView)

**Rationale:** CalculiX provides the best balance of capability, ease of use, and ecosystem integration for engineering assignments on Linux. Its Abaqus-compatible input format means skills transfer to industry. FreeCAD's FEM workbench provides a complete GUI workflow: create geometry, mesh with Gmsh or Netgen, apply boundary conditions, solve with CalculiX, and visualize results -- all within one application. For more advanced post-processing, results export to ParaView. The `apt` package provides immediate installation, and `conda-forge` offers the latest version. Beam bending, plate stress, modal analysis, heat transfer, and thermo-mechanical coupling are all well-supported with extensive tutorials and examples available.

**Assignment coverage:** Cantilever beam (static), plate with hole (stress concentration), modal analysis (eigenfrequency), steady-state heat conduction, transient thermal, contact problems.

### Rank 2: Elmer FEM (with Gmsh + ParaView)

**Rationale:** When assignments require multiphysics -- combining heat transfer with structural mechanics, or adding electromagnetics -- Elmer is the strongest choice. Its 50+ solver modules cover more physics domains than any other open-source package. ElmerGUI provides a usable (if basic) graphical interface, and the SIF-based command-line workflow is well-documented with tutorials from CSC. Elmer integrates well with Gmsh for meshing and ParaView for visualization. The Ubuntu PPA provides easy installation, and building from source is straightforward for newer Ubuntu versions. The learning curve is moderate -- steeper than CalculiX+FreeCAD for simple structural problems, but worth it when multiphysics coupling is needed.

**Assignment coverage:** Heat conduction (steady/transient), structural mechanics, electromagnetics, fluid flow, coupled thermo-mechanical, acoustic analysis, Navier-Stokes.

### Rank 3: FEniCSx (with Gmsh + ParaView/pyvista)

**Rationale:** For students and researchers who want deep understanding of FEM and the ability to solve custom PDE problems, FEniCSx is unmatched. Its Python-native workflow enables parametric studies, optimization loops, and automated report generation. The variational formulation approach teaches fundamentals while the automatic code generation delivers high performance. Installation via apt PPA, conda, or Docker is straightforward. While it requires more mathematical sophistication than CalculiX or Elmer, the investment pays off in flexibility: any PDE system expressible in weak form can be solved. Excellent for heat transfer, elasticity, Stokes flow, and coupled problems defined mathematically.

**Assignment coverage:** Any PDE-based problem: elasticity, heat equation, Poisson, Stokes, Navier-Stokes, custom coupled systems. Best for assignments where the variational formulation is part of the learning objective.

---

## 5. Installation Instructions (Ubuntu/Debian Linux)

### 5.1 CalculiX + FreeCAD + Gmsh + ParaView

```bash
# Update package lists
sudo apt update

# Install CalculiX solver and pre/post-processor
sudo apt install calculix-ccx calculix-cgx

# Install FreeCAD (includes FEM workbench with CalculiX and Gmsh integration)
# For the latest stable version, use the PPA:
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo apt update
sudo apt install freecad

# Install Gmsh (standalone, for advanced meshing outside FreeCAD)
sudo apt install gmsh
# Or for the latest version via pip:
pip install gmsh

# Install ParaView for advanced post-processing
sudo apt install paraview

# Optional: Install latest CalculiX via conda-forge (for version 2.23)
# conda install -c conda-forge calculix

# Optional: Install pycalculix for Python automation
# pip install pycalculix

# Verify installations
ccx -v          # CalculiX solver version
cgx -v          # CalculiX pre/post-processor version
gmsh --version  # Gmsh version
paraview --version  # ParaView version
freecad --version   # FreeCAD version
```

**Note:** The `apt` version of CalculiX may lag behind the latest release (v2.23). For the most current version, use `conda-forge` or compile from source:

```bash
# Building CalculiX 2.23 from source (if needed)
sudo apt install build-essential gfortran libspooles-dev libarpack2-dev libyaml-cpp-dev
wget http://www.dhondt.de/ccx_2.23.src.tar.bz2
wget http://www.dhondt.de/cgx_2.23.all.tar.bz2
# Follow compilation instructions at http://www.dhondt.de/
```

### 5.2 Elmer FEM + Gmsh + ParaView

```bash
# Method A: Ubuntu PPA (recommended for Ubuntu 20.04/22.04)
sudo add-apt-repository ppa:elmer-csc-ubuntu/elmer-csc-ppa
sudo apt update
sudo apt install elmerfem-csc

# Method B: Build from source (recommended for Ubuntu 24.04+)
sudo apt install git cmake build-essential gfortran \
    libopenmpi-dev libblas-dev liblapack-dev \
    libmumps-dev libhypre-dev libqt5opengl5-dev \
    libqt5svg5-dev qttools5-dev

git clone https://github.com/ElmerCSC/elmerfem.git
cd elmerfem
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local/elmer \
         -DWITH_MPI=TRUE \
         -DWITH_OpenMP=TRUE \
         -DWITH_ELMERGUI=TRUE
make -j$(nproc)
sudo make install

# Add Elmer to PATH
echo 'export PATH="/usr/local/elmer/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install Gmsh and ParaView (if not already installed)
sudo apt install gmsh paraview

# Verify
ElmerSolver --version
ElmerGUI &  # Launch GUI
```

### 5.3 FEniCSx + Gmsh + ParaView

```bash
# Method A: Ubuntu PPA (easiest)
sudo add-apt-repository ppa:fenics-packages/fenics
sudo apt update
sudo apt install fenicsx

# Method B: Conda (recommended for latest version 0.10)
# Install miniforge first if conda not available:
# wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
# bash Miniforge3-Linux-x86_64.sh
conda create -n fenicsx-env
conda activate fenicsx-env
conda install -c conda-forge fenics-dolfinx mpich pyvista

# Method C: Docker (most reproducible)
docker pull dolfinx/dolfinx:stable
docker run -it --rm -v $(pwd):/home/fenics/shared dolfinx/dolfinx:stable

# Install Gmsh Python API (for mesh generation in scripts)
pip install gmsh

# Install pyvista for inline visualization
pip install pyvista

# Install ParaView for external visualization
sudo apt install paraview

# Verify
python3 -c "import dolfinx; print(dolfinx.__version__)"
python3 -c "import gmsh; print(gmsh.__version__)"
```

---

## 6. Example Assignment Workflows

### 6.1 Cantilever Beam Structural Analysis

**Problem:** A steel cantilever beam (length 100 mm, cross-section 10 x 10 mm) fixed at one end, with a 1 kN point load at the free end. Determine the maximum deflection and von Mises stress distribution.

**Material:** Steel, E = 210 GPa, nu = 0.3

#### Workflow A: FreeCAD + CalculiX (GUI-based, Recommended for Beginners)

**Tool chain:** FreeCAD (geometry + meshing + solving + visualization)

```
Step 1: Create Geometry in FreeCAD
  - Open FreeCAD, create a new document
  - Switch to Part Design workbench
  - Create a sketch on XY plane: 100mm x 10mm rectangle
  - Pad to 10mm depth to create a 3D solid beam

Step 2: Switch to FEM Workbench
  - Select the beam body
  - Click "Analysis" > "New Analysis" (adds CalculiX solver automatically)
  - FreeCAD 1.0+ includes a built-in cantilever beam example:
    File > New > FEM Examples > FEMExample.FcStd

Step 3: Apply Material
  - Click "Model" > "Material for Solid"
  - Select "Steel-Generic" from the material library
  - Confirm E = 210000 MPa, nu = 0.3

Step 4: Apply Boundary Conditions
  - Select the fixed face (left end)
  - Click "Model" > "Fixed Boundary Condition"
  - Select the free end face or vertex
  - Click "Model" > "Force Boundary Condition"
  - Set Fx = 0, Fy = -1000 N (or Fz depending on orientation)

Step 5: Generate Mesh
  - Click "Mesh" > "FEM Mesh from Shape by Gmsh"
  - Set element size to 2mm for good resolution
  - Click "Apply" to generate mesh

Step 6: Solve
  - Click "Solve" > "Solver CalculiX Standard"
  - Click "Run CalculiX"
  - Wait for "CalculiX done without error!" message

Step 7: Post-Process
  - Double-click the results object in the model tree
  - Select "Von Mises Stress" or "Displacement Magnitude"
  - For advanced visualization: Results > Post Pipeline > Export to VTK
  - Open .vtk file in ParaView for publication-quality plots
```

#### Workflow B: Gmsh + CalculiX + ParaView (Command-Line, Recommended for Automation)

**Tool chain:** Gmsh (geometry + mesh) --> CalculiX CCX (solve) --> ParaView (visualize)

```bash
# Step 1: Create geometry and mesh with Gmsh (cantilever_beam.geo)
```

```
// cantilever_beam.geo - Gmsh geometry file
SetFactory("OpenCASCADE");

// Beam dimensions
L = 100;   // length in mm
W = 10;    // width in mm
H = 10;    // height in mm

// Create box
Box(1) = {0, 0, 0, L, W, H};

// Define physical groups for boundary conditions
Physical Surface("fixed_end") = {1};     // x=0 face
Physical Surface("loaded_end") = {2};    // x=L face
Physical Volume("beam") = {1};

// Mesh control
Mesh.CharacteristicLengthMax = 2;
Mesh.ElementOrder = 2;  // Second-order elements
Mesh 3;

// Export in Abaqus format for CalculiX
Save "cantilever_beam.inp";
```

```bash
# Step 2: Generate mesh
gmsh cantilever_beam.geo -3 -format inp -o cantilever_beam.inp

# Step 3: Create CalculiX input file (cantilever_solve.inp)
```

```
** cantilever_solve.inp - CalculiX input deck
*INCLUDE, INPUT=cantilever_beam.inp
**
*MATERIAL, NAME=STEEL
*ELASTIC
210000., 0.3
**
*SOLID SECTION, ELSET=beam, MATERIAL=STEEL
**
*STEP
*STATIC
**
*BOUNDARY
fixed_end, 1, 3, 0.0
**
*CLOAD
** Apply distributed load on loaded_end nodes
loaded_end, 2, -100.0
**
*NODE FILE
U
*EL FILE
S, E
**
*END STEP
```

```bash
# Step 4: Run CalculiX solver
ccx cantilever_solve

# Step 5: Convert results to VTK for ParaView
# Install ccx2paraview: pip install ccx2paraview
ccx2paraview cantilever_solve.frd vtk

# Step 6: Open in ParaView
paraview cantilever_solve.vtk
# Apply "Warp By Vector" filter for deformed shape
# Color by "von Mises Stress" field
```

#### Workflow C: FEniCSx Python Script (Code-Based)

```python
#!/usr/bin/env python3
"""Cantilever beam analysis using FEniCSx."""

import numpy as np
from mpi4py import MPI
from dolfinx import mesh, fem, default_scalar_type
from dolfinx.fem.petsc import LinearProblem
import ufl

# Create beam mesh
L, W, H = 100.0, 10.0, 10.0
domain = mesh.create_box(
    MPI.COMM_WORLD,
    [np.array([0, 0, 0]), np.array([L, W, H])],
    [50, 5, 5],
    cell_type=mesh.CellType.hexahedron,
)

# Material properties (steel)
E = 210000.0       # Young's modulus [MPa]
nu = 0.3            # Poisson's ratio
mu = E / (2.0 * (1.0 + nu))
lmbda = E * nu / ((1.0 + nu) * (1.0 - 2.0 * nu))

# Function space (vector, degree 1)
V = fem.functionspace(domain, ("Lagrange", 1, (domain.geometry.dim,)))

# Boundary conditions: fix left end (x=0)
def left_boundary(x):
    return np.isclose(x[0], 0.0)

fdim = domain.topology.dim - 1
left_facets = mesh.locate_entities_boundary(domain, fdim, left_boundary)
u_zero = np.array([0, 0, 0], dtype=default_scalar_type)
bc = fem.dirichletbc(u_zero, fem.locate_dofs_topological(V, fdim, left_facets), V)

# Variational formulation
def epsilon(u):
    return ufl.sym(ufl.grad(u))

def sigma(u):
    return lmbda * ufl.nabla_div(u) * ufl.Identity(len(u)) + 2 * mu * epsilon(u)

u = ufl.TrialFunction(V)
v = ufl.TestFunction(V)

# Load: body force or traction on right end
f = fem.Constant(domain, default_scalar_type((0, -0.1, 0)))  # Body force
a = ufl.inner(sigma(u), epsilon(v)) * ufl.dx
L_form = ufl.dot(f, v) * ufl.dx

# Solve
problem = LinearProblem(a, L_form, bcs=[bc])
uh = problem.solve()

# Post-process: write to file for ParaView
from dolfinx.io import XDMFFile
with XDMFFile(domain.comm, "cantilever_results.xdmf", "w") as xdmf:
    xdmf.write_mesh(domain)
    xdmf.write_function(uh)

# Print max displacement
print(f"Max displacement: {np.max(np.abs(uh.x.array)):.6f} mm")
```

```bash
# Run the script
python3 cantilever_beam.py

# Open results in ParaView
paraview cantilever_results.xdmf
```

---

### 6.2 Steady-State Heat Conduction

**Problem:** A rectangular steel plate (200 mm x 100 mm x 5 mm) with left edge held at 100 C, right edge at 20 C, top and bottom edges insulated. Determine the temperature distribution and heat flux.

**Material:** Steel, thermal conductivity k = 50 W/(m*K)

#### Workflow A: Elmer FEM with ElmerGUI (GUI-Based)

**Tool chain:** Gmsh (mesh) --> ElmerGUI (setup + solve) --> ParaView (visualize)

```bash
# Step 1: Create mesh with Gmsh
```

```
// heat_plate.geo - Gmsh geometry file
SetFactory("OpenCASCADE");

// Plate dimensions
Lx = 200;  // mm
Ly = 100;  // mm
Lz = 5;    // mm

Box(1) = {0, 0, 0, Lx, Ly, Lz};

// Physical surfaces for boundary conditions
Physical Surface("hot_face") = {1};      // x=0
Physical Surface("cold_face") = {2};     // x=Lx
Physical Surface("insulated") = {3,4,5,6}; // other faces
Physical Volume("plate") = {1};

Mesh.CharacteristicLengthMax = 5;
Mesh 3;
Save "heat_plate.msh";
```

```bash
gmsh heat_plate.geo -3

# Step 2: Launch ElmerGUI
ElmerGUI &
```

```
In ElmerGUI:
  a) File > Open > heat_plate.msh
  b) Model > Setup > Simulation Type = Steady State
  c) Model > Equation > Add > Heat Equation (check Active)
  d) Model > Material > Add
     - Heat Conductivity = 50.0  [W/(m*K)]
  e) Model > Boundary Condition > Add "Hot"
     - Select hot_face boundary
     - Temperature = 373.15  [K] (100 C)
  f) Model > Boundary Condition > Add "Cold"
     - Select cold_face boundary
     - Temperature = 293.15  [K] (20 C)
  g) Model > Boundary Condition > Add "Insulated"
     - Select insulated boundaries
     - (no conditions needed -- natural BC is zero flux)
  h) Sif > Generate
  i) Run > Start Solver
```

```bash
# Step 3: Post-process in ParaView
# Elmer writes results in .vtu format by default
paraview case0001.vtu
# Color by "Temperature" field
# Apply Calculator filter for heat flux: -k * grad(Temperature)
```

#### Workflow B: Elmer FEM Command-Line (SIF File)

**Tool chain:** Gmsh (mesh) --> ElmerGrid (convert) --> ElmerSolver (solve) --> ParaView (visualize)

```bash
# Step 1: Generate mesh (reuse heat_plate.msh from above)
gmsh heat_plate.geo -3

# Step 2: Convert Gmsh mesh to Elmer format
ElmerGrid 14 2 heat_plate.msh
# This creates a directory "heat_plate/" with Elmer mesh files

# Step 3: Create Solver Input File (heat_plate.sif)
```

```
! heat_plate.sif - Elmer Solver Input File

Header
  Mesh DB "." "heat_plate"
End

Simulation
  Coordinate System = Cartesian
  Simulation Type = Steady State
  Steady State Max Iterations = 1
  Output File = "heat_results.result"
  Post File = "heat_results.vtu"
End

Body 1
  Equation = 1
  Material = 1
  Body Force = 1
End

Equation 1
  Active Solvers(1) = 1
End

Solver 1
  Equation = Heat Equation
  Procedure = "HeatSolve" "HeatSolver"
  Variable = Temperature
  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStab
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8
  Linear System Preconditioning = ILU1
End

Material 1
  Heat Conductivity = 50.0
  Density = 7850.0
End

Body Force 1
  Heat Source = 0.0
End

! Hot face (x=0): T = 373.15 K
Boundary Condition 1
  Target Boundaries(1) = 1
  Temperature = 373.15
End

! Cold face (x=Lx): T = 293.15 K
Boundary Condition 2
  Target Boundaries(1) = 2
  Temperature = 293.15
End

! Insulated faces: natural zero-flux BC (no specification needed)
Boundary Condition 3
  Target Boundaries(4) = 3 4 5 6
End
```

```bash
# Step 4: Run solver
ElmerSolver heat_plate.sif

# Step 5: Visualize in ParaView
paraview heat_results.vtu
```

#### Workflow C: FreeCAD + CalculiX (Heat Transfer)

```
Step 1: Create plate geometry in FreeCAD Part Design workbench
  - Sketch 200mm x 100mm rectangle, pad to 5mm

Step 2: Switch to FEM Workbench
  - New Analysis (adds CalculiX solver)
  - Change analysis type: Solve > CalculiX solver > Analysis Type = Thermomechanical

Step 3: Apply material
  - Model > Material for Solid > Steel-Generic
  - Verify thermal conductivity = 50 W/(m*K)

Step 4: Apply boundary conditions
  - Select left face > Model > Temperature Boundary Condition > 373.15 K
  - Select right face > Model > Temperature Boundary Condition > 293.15 K

Step 5: Mesh, solve, and post-process as in section 6.1
```

#### Workflow D: FEniCSx Python Script

```python
#!/usr/bin/env python3
"""Steady-state heat conduction using FEniCSx."""

import numpy as np
from mpi4py import MPI
from dolfinx import mesh, fem, default_scalar_type
from dolfinx.fem.petsc import LinearProblem
import ufl

# Create plate mesh (2D simplification since Lz << Lx, Ly)
domain = mesh.create_rectangle(
    MPI.COMM_WORLD,
    [np.array([0, 0]), np.array([200, 100])],
    [100, 50],
    cell_type=mesh.CellType.triangle,
)

# Function space (scalar, degree 1)
V = fem.functionspace(domain, ("Lagrange", 1))

# Boundary conditions
def left_boundary(x):
    return np.isclose(x[0], 0.0)

def right_boundary(x):
    return np.isclose(x[0], 200.0)

fdim = domain.topology.dim - 1

# Hot face: T = 373.15 K (100 C)
left_facets = mesh.locate_entities_boundary(domain, fdim, left_boundary)
bc_hot = fem.dirichletbc(
    default_scalar_type(373.15),
    fem.locate_dofs_topological(V, fdim, left_facets),
    V,
)

# Cold face: T = 293.15 K (20 C)
right_facets = mesh.locate_entities_boundary(domain, fdim, right_boundary)
bc_cold = fem.dirichletbc(
    default_scalar_type(293.15),
    fem.locate_dofs_topological(V, fdim, right_facets),
    V,
)

# Thermal conductivity
k = fem.Constant(domain, default_scalar_type(50.0))

# Variational form: -k * laplacian(T) = 0
T = ufl.TrialFunction(V)
v = ufl.TestFunction(V)
a = k * ufl.dot(ufl.grad(T), ufl.grad(v)) * ufl.dx
L_form = fem.Constant(domain, default_scalar_type(0.0)) * v * ufl.dx

# Solve
problem = LinearProblem(a, L_form, bcs=[bc_hot, bc_cold])
Th = problem.solve()

# Write results
from dolfinx.io import XDMFFile
with XDMFFile(domain.comm, "heat_results.xdmf", "w") as xdmf:
    xdmf.write_mesh(domain)
    xdmf.write_function(Th)

# Report
T_array = Th.x.array
print(f"Temperature range: {T_array.min():.2f} K to {T_array.max():.2f} K")
print(f"Expected: linear from 373.15 K to 293.15 K")
```

---

## 7. Integration Notes

### 7.1 FreeCAD

| FEA Tool | Integration Level | Notes |
|---|---|---|
| **CalculiX** | Native | FEM workbench directly invokes CCX solver; bundled in FreeCAD packages |
| **Elmer FEM** | Native | FEM workbench supports Elmer as alternative solver (FreeCAD 1.0+) |
| **Code\_Aster** | In development | Initiative underway for FreeCAD 1.1+ to add Code\_Aster solver support |
| **Gmsh** | Native | FEM workbench uses Gmsh as default mesh generator |
| **FEniCSx** | Export only | Export geometry as STEP/BREP, mesh externally, import in Python |
| **MOOSE** | Export only | Export mesh in compatible format, define physics in MOOSE input |

### 7.2 Gmsh

| FEA Tool | Integration Level | Notes |
|---|---|---|
| **CalculiX** | Excellent | Export to Abaqus .inp format directly; `gmsh -format inp` |
| **Elmer FEM** | Excellent | Export .msh, convert with ElmerGrid (`ElmerGrid 14 2 file.msh`) |
| **Code\_Aster** | Good | Export to MED format or .msh v2 |
| **FEniCSx** | Excellent | Python API: `gmsh` module, import via `dolfinx.io.gmshio` |
| **GetDP** | Native | Same ONELAB ecosystem; seamless .msh interchange |
| **SU2** | Good | Export to SU2 native format or CGNS |
| **OpenFOAM** | Good | `gmshToFoam` utility converts .msh v2 to OpenFOAM format |

### 7.3 ParaView

| FEA Tool | Integration Level | Notes |
|---|---|---|
| **CalculiX** | Good | Convert .frd to .vtk/.vtu via `ccx2paraview` or `frd2vtu` |
| **Elmer FEM** | Excellent | Native VTU output; direct ParaView opening |
| **Code\_Aster** | Good | Export to MED format; ParaView has MED reader plugin |
| **FEniCSx** | Excellent | XDMF/HDF5 output; also pyvista for inline visualization |
| **MOOSE** | Excellent | Exodus II output; ParaView has native Exodus reader |
| **SU2** | Good | VTK/Tecplot output supported |
| **OpenFOAM** | Excellent | Native .foam reader in ParaView |

### 7.4 OpenFOAM

| FEA Tool | Integration Level | Notes |
|---|---|---|
| **CalculiX** | Good | Coupled FSI via preCICE adapter; mesh format conversion possible |
| **Elmer FEM** | Fair | Separate solvers; can share meshes via Gmsh intermediate |
| **Code\_Aster** | Fair | Separate ecosystems; MED format as bridge |
| **FEniCSx** | Fair | Both use Gmsh; no direct coupling without custom code |
| **SU2** | Fair | Both CFD-capable; no direct coupling mechanism |

**preCICE** (the coupling library) deserves special mention: it enables fluid-structure interaction by coupling OpenFOAM (fluid) with CalculiX or FEniCSx (structure) through a well-documented adapter system.

### 7.5 Blender

Blender is primarily a 3D modeling and rendering tool, not a CAE platform. Integration with FEA tools is limited to:

- **Geometry export:** Blender can export STL, OBJ, and (with add-ons) STEP files for import into Gmsh or FreeCAD
- **Visualization:** FEA results in VTK format can be imported into Blender via the `bvtkNodes` add-on for photorealistic rendering of simulation results
- **Mesh conversion:** Blender meshes (triangulated surfaces) can be converted to volume meshes via Gmsh for FEA

Blender is not recommended as part of a standard FEA workflow but can be useful for visualization and presentation of results.

### 7.6 BemRosetta

BEMRosetta is specialized for marine hydrodynamics -- it converts and visualizes Boundary Element Method (BEM) coefficients between different hydrodynamic solvers (WAMIT, Nemoh, AQWA, etc.). Its connection to structural FEA is limited to:

- **Mesh conversion:** BEMRosetta can read and convert surface meshes between formats used by various BEM solvers
- **Hydrodynamic loads:** Results from BEMRosetta can provide wave loading data that feeds into structural FEA (e.g., CalculiX or Code\_Aster) for offshore structure analysis
- **OpenFOAM bridge:** BEMRosetta results can inform OpenFOAM CFD simulations for wave-structure interaction

BEMRosetta runs on both Windows and Linux and includes Python glue code for scripting. It is relevant when FEA is applied to marine or offshore engineering structures.

---

## 8. Additional Resources

### Community and Support

| Program | Primary Community | Forum/Chat |
|---|---|---|
| CalculiX | [calculix.discourse.group](https://calculix.discourse.group) | Discourse forum |
| Code\_Aster | [forum.code-aster.org](https://forum.code-aster.org) | Official forum |
| Elmer FEM | [elmerfem.org/forum](https://www.elmerfem.org/forum) | phpBB forum |
| MOOSE | [github.com/idaholab/moose](https://github.com/idaholab/moose) | GitHub Discussions |
| FEniCSx | [fenicsproject.discourse.group](https://fenicsproject.discourse.group) | Discourse forum |
| deal.II | [groups.google.com/g/dealii](https://groups.google.com/g/dealii) | Google Group |
| PrePoMax | [prepomax.discourse.group](https://prepomax.discourse.group) | Discourse forum |
| FreeCAD | [forum.freecad.org](https://forum.freecad.org) | phpBB forum |

### Key Documentation Links

- **CalculiX Manual:** http://www.dhondt.de/ccx_2.23.pdf
- **CalculiX Examples:** https://github.com/calculix/CalculiX-Examples
- **Elmer Models Manual:** https://www.nic.funet.fi/index/elmer/doc/ElmerModelsManual.pdf
- **Elmer Tutorials:** https://www.nic.funet.fi/index/elmer/doc/ElmerTutorials-nonGUI.pdf
- **FEniCSx Documentation:** https://docs.fenicsproject.org/
- **FEniCSx Tutorial:** https://jsdokken.com/dolfinx-tutorial/
- **Gmsh Documentation:** https://gmsh.info/doc/texinfo/gmsh.html
- **FreeCAD FEM Wiki:** https://wiki.freecad.org/FEM_Module
- **Code\_Aster Examples:** https://github.com/Jesusbill/code-aster-examples
- **MOOSE Getting Started:** https://mooseframework.inl.gov/getting_started/

---

## 9. Summary Decision Tree

```
START: What type of FEA assignment?
  |
  +-- Standard structural (beam, plate, modal, contact)
  |     --> CalculiX + FreeCAD FEM + Gmsh + ParaView
  |
  +-- Heat transfer (conduction, convection, radiation)
  |     --> CalculiX (simple) or Elmer FEM (advanced/coupled)
  |
  +-- Multiphysics (thermal + structural + EM)
  |     --> Elmer FEM + Gmsh + ParaView
  |
  +-- Custom PDE / research / parametric study
  |     --> FEniCSx + Gmsh + ParaView
  |
  +-- CFD / aerodynamics / shape optimization
  |     --> SU2 or OpenFOAM (not covered in depth here)
  |
  +-- Crash / impact / explicit dynamics
  |     --> OpenRadioss
  |
  +-- Nuclear engineering / advanced coupling
        --> MOOSE Framework
```

---

*This survey was compiled on 2026-02-21 using publicly available information from official project websites, GitHub repositories, and community forums. Software versions and capabilities are subject to change. Always verify installation instructions against official documentation before proceeding.*
