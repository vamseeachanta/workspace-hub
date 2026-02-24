---
name: hydrodynamic-pipeline
description: Cross-program workflow for hydrodynamic analysis — mesh generation (Gmsh) to diffraction analysis (OrcaWave/AQWA) to dynamic analysis (OrcaFlex). Covers data flow, format conversion, and validation between programs.
version: 1.0.0
updated: 2026-02-23
category: workflow
triggers:
- hydrodynamic pipeline
- diffraction to dynamic
- OrcaWave to OrcaFlex
- AQWA to OrcaFlex
- panel mesh to RAO
- hydrodynamic workflow
- wave-structure interaction pipeline
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires:
- gmsh-meshing
- orcawave-analysis
- orcaflex-modeling
see_also:
- aqwa-analysis
- diffraction-analysis
- orcawave-to-orcaflex
- bemrosetta
---
# Hydrodynamic Analysis Pipeline Workflow Skill

End-to-end cross-program workflow for hydrodynamic analysis of floating structures: panel mesh generation, diffraction/radiation analysis, and coupled dynamic simulation.

## Pipeline Overview

```
FreeCAD / Gmsh                    OrcaWave / AQWA
  (panel mesh)        ────►     (diffraction/radiation)
      │                                  │
  .gdf / .dat mesh                  RAOs, added mass,
                                    damping, QTFs
                                         │
                                         ▼
                                    OrcaFlex
                                (coupled dynamic analysis)
                                         │
                                    .sim results
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                         OrcaFlex Post          ParaView/Blender
                        (statistics)           (visualization)
```

## Stage 1: Geometry to Panel Mesh

### Gmsh Panel Mesh for Hydrodynamics

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

### GDF File Format (OrcaWave)

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

### AQWA Mesh Format (.dat)

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

### Mesh Quality for Hydrodynamics

| Check | Threshold | Why |
|-------|-----------|-----|
| Panel aspect ratio | < 3:1 | Poor aspect ratios cause numerical error |
| Panel size | L/20 to L/10 (L=wavelength) | Must resolve shortest wave of interest |
| Normal direction | Outward (into fluid) | Reversed normals give wrong forces |
| Waterline closure | Gap < panel_size/10 | Leaky waterline causes infinite forces |
| Symmetry | Exact if using ISX/ISY | Asymmetry with symmetry flags gives wrong modes |
| Total panels | 500-5000 typical | Too few: inaccurate. Too many: slow |

## Stage 2: Diffraction/Radiation Analysis

### OrcaWave Execution

```bash
# OrcaWave runs via OrcFxAPI (same as OrcaFlex)
python3 -c "
import OrcFxAPI
model = OrcFxAPI.Model()
model.LoadData('diffraction_model.owd')
model.CalculateStatics()
model.RunSimulation()
model.SaveSimulation('results.owr')
"
```

### AQWA Execution

```bash
# AQWA runs via ANSYS Workbench or command line
# Typical AQWA-LINE execution:
aqwa_line input.dat output.lis

# AQWA-DRIFT for QTFs:
aqwa_drift input.dat output.lis
```

### Key Outputs from Diffraction Analysis

| Output | Format | Used By | Description |
|--------|--------|---------|-------------|
| **RAOs** | .owd / .lis | OrcaFlex VesselType | Response amplitude operators (6 DOF) |
| **Added mass** | Frequency-dependent | OrcaFlex | Mass added by fluid acceleration |
| **Radiation damping** | Frequency-dependent | OrcaFlex | Energy radiated as waves |
| **Mean drift** | Force per wave amplitude² | OrcaFlex | Steady drift forces |
| **QTFs** | Difference/sum frequency | OrcaFlex | Second-order slow-drift forces |
| **Hydrostatic stiffness** | 6x6 matrix | OrcaFlex | Restoring forces |

### Extracting Results for OrcaFlex

```python
import OrcFxAPI

def extract_diffraction_results(owd_path):
    """Extract hydrodynamic data from OrcaWave for OrcaFlex."""
    model = OrcFxAPI.Model()
    model.LoadSimulation(owd_path.replace('.owd', '.owr'))

    # Access vessel results
    vessel = model['Vessel']

    results = {
        "periods": list(vessel.WavePeriods),
        "headings": list(vessel.WaveHeadings),
        "raos": {},
        "added_mass": {},
        "damping": {},
    }

    # Extract RAOs for each DOF
    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
    for i, dof in enumerate(dof_names):
        results["raos"][dof] = {
            "amplitude": [],
            "phase": [],
        }
        for period in results["periods"]:
            for heading in results["headings"]:
                amp = vessel.RAOAmplitude(i, period, heading)
                phase = vessel.RAOPhase(i, period, heading)
                results["raos"][dof]["amplitude"].append(amp)
                results["raos"][dof]["phase"].append(phase)

    return results
```

## Stage 3: Diffraction Results to OrcaFlex

### OrcaWave to OrcaFlex (Direct Integration)

```python
import OrcFxAPI

def create_orcaflex_vessel_from_orcawave(owr_path, ofx_model_path):
    """Create OrcaFlex vessel type from OrcaWave results."""
    # OrcaFlex can directly import OrcaWave .owr files
    model = OrcFxAPI.Model()

    # Create vessel type
    vt = model.CreateObject(OrcFxAPI.ObjectType.VesselType)
    vt.Name = "FPSO_VesselType"

    # Import hydrodynamic data from OrcaWave
    vt.WavesReferredToBy = "frequency (rad/s)"
    vt.PrimaryMotion = "Displacement RAOs"

    # Load OrcaWave database
    vt.LoadHydrodynamicData(owr_path)

    # Create vessel instance
    vessel = model.CreateObject(OrcFxAPI.ObjectType.Vessel)
    vessel.Name = "FPSO"
    vessel.VesselType = vt.Name
    vessel.InitialX = 0
    vessel.InitialY = 0
    vessel.InitialZ = 0
    vessel.InitialHeading = 0

    model.SaveData(ofx_model_path)
    return model
```

### AQWA to OrcaFlex (via BEMRosetta or Manual)

```python
def aqwa_to_orcaflex(aqwa_lis_path, orcaflex_model):
    """Import AQWA results into OrcaFlex vessel type.

    Method 1: Use BEMRosetta to convert AQWA format to OrcaFlex-compatible
    Method 2: Parse AQWA .lis file directly and set vessel properties
    """
    # BEMRosetta conversion (preferred)
    import subprocess
    subprocess.run([
        'BEMRosetta', '-i', aqwa_lis_path,
        '-o', 'converted.owd', '-format', 'orcawave'
    ])

    # Then load into OrcaFlex
    vt = orcaflex_model.CreateObject(OrcFxAPI.ObjectType.VesselType)
    vt.LoadHydrodynamicData('converted.owd')
```

### Data Format Mapping

| Source (OrcaWave/AQWA) | Target (OrcaFlex) | Notes |
|------------------------|-------------------|-------|
| RAO amplitude + phase | VesselType displacement RAOs | Check heading convention (from/to) |
| Added mass (freq-dep) | VesselType added mass | Infinite-frequency value needed too |
| Radiation damping | VesselType radiation damping | Must be positive definite |
| Mean drift coefficients | VesselType drift coefficients | Newman or full QTF |
| QTFs (diff-frequency) | VesselType QTF data | Slow-drift calculation |
| Hydrostatic stiffness | VesselType stiffness | Cross-check with hand calc |

### Coordinate System Warnings

| Convention | OrcaWave | AQWA | OrcaFlex |
|-----------|----------|------|----------|
| **Origin** | User-defined | User-defined | Vessel reference point |
| **X-axis** | Forward (+ve) | Forward (+ve) | Forward (+ve) |
| **Z-axis** | Up (+ve) | Up (+ve) | Up (+ve) |
| **Wave heading** | 0=from +X | 0=from +X | 0=from +X (verify!) |
| **Phase** | Varies | Varies | Relative to wave crest at origin |

**Critical**: Always verify heading convention. A 180-degree error inverts all RAO phases.

## Stage 4: OrcaFlex Dynamic Analysis

### OrcaFlex Model Assembly

```yaml
# Typical OrcaFlex model structure after importing hydrodynamics
General:
  WaterDepth: 1500
  StaticsDamping: 50

Environment:
  WaveType: JONSWAP
  WaveHs: 5.0
  WaveTz: 10.0
  RefCurrentSpeed: 1.0

VesselTypes:
  - Name: "FPSO_VesselType"
    # Hydrodynamic data loaded from OrcaWave/AQWA

Vessels:
  - Name: "FPSO"
    VesselType: "FPSO_VesselType"
    InitialX: 0
    InitialY: 0
    InitialHeading: 0

LineTypes:
  - Name: "Chain_R4"
    Category: General
    MassPerUnitLength: 195
    EA: 1.2e9

Lines:
  - Name: "Mooring_1"
    LineType: ["Chain_R4"]
    Length: [2000]
    EndAConnection: Anchored
    EndBConnection: "FPSO"
    EndBConnectionPoint: [-120, 0, 0]
```

### Execution

```python
import OrcFxAPI

model = OrcFxAPI.Model()
model.LoadData('fpso_moored.yml')

# Run statics
model.CalculateStatics()

# Run dynamics
model.RunSimulation()

# Save results
model.SaveSimulation('fpso_moored.sim')
```

## Validation: Pipeline Checkpoints

### Checkpoint 1: Mesh Quality

```python
def validate_panel_mesh(gdf_path, min_panels=200, max_aspect=3.0):
    """Validate panel mesh before diffraction analysis."""
    checks = {"passed": True, "issues": []}

    # Parse GDF and count panels
    # Check aspect ratios, normal directions, waterline closure
    # (implementation depends on mesh format)

    return checks
```

### Checkpoint 2: Diffraction Results

```python
def validate_diffraction_results(results):
    """Validate diffraction results before passing to OrcaFlex."""
    checks = {"passed": True, "issues": []}

    # RAO sanity checks
    heave_rao_at_long_period = results["raos"]["Heave"]["amplitude"][-1]
    if abs(heave_rao_at_long_period - 1.0) > 0.1:
        checks["issues"].append(
            f"Heave RAO at long period = {heave_rao_at_long_period:.3f} "
            "(expected ~1.0 — vessel should follow wave at low frequency)"
        )

    # Added mass should be positive on diagonal
    # Damping should be positive (energy dissipation)
    # Roll/pitch RAO should have clear resonance peak

    # Check for numerical issues
    for dof, data in results["raos"].items():
        if any(a > 100 for a in data["amplitude"]):
            checks["issues"].append(f"{dof} RAO has spikes > 100 — likely resonance without damping")
            checks["passed"] = False

    return checks
```

### Checkpoint 3: OrcaFlex Results

```python
def validate_orcaflex_moored_results(sim_path):
    """Validate final OrcaFlex simulation results."""
    import OrcFxAPI
    model = OrcFxAPI.Model()
    model.LoadSimulation(sim_path)
    checks = {"passed": True, "issues": []}

    # Check vessel offset
    vessel = model['FPSO']
    max_surge = max(abs(vessel.TimeHistory('X', OrcFxAPI.oeEndA)))
    if max_surge > 50:
        checks["issues"].append(f"Max surge = {max_surge:.1f}m — check mooring stiffness")

    # Check mooring tensions
    for obj in model.objects:
        if obj.typeName == 'Line' and 'Mooring' in obj.name:
            max_tension = max(obj.TimeHistory('Effective tension', OrcFxAPI.oeEndA))
            min_tension = min(obj.TimeHistory('Effective tension', OrcFxAPI.oeEndB))
            if min_tension < 0:
                checks["issues"].append(f"{obj.name}: negative tension (compression) — line may be slack")
                checks["passed"] = False

    return checks
```

## Error Propagation: Where Things Break

| Stage | Common Failure | Propagation Effect | Detection |
|-------|---------------|-------------------|-----------|
| **Mesh** | Panel normals reversed | All forces inverted in diffraction | Heave RAO → -1.0 at long period |
| **Mesh** | Panel size too large | Missing high-frequency response | RAOs truncated above mesh cutoff |
| **Mesh** | Waterline not closed | Infinite hydrostatic forces | Diffraction solver diverges |
| **Diffraction** | Wrong heading convention | RAO phases off by 180 deg | Vessel moves opposite to waves |
| **Diffraction** | No viscous damping | Unrealistic resonance peaks | Roll RAO > 50 at natural period |
| **OrcaFlex import** | Coordinate system mismatch | Forces applied at wrong location | Vessel spins or drifts wrong way |
| **OrcaFlex** | Missing QTF data | No slow-drift motion | Mean offset too small |

## Related Skills

- [orcawave-analysis](../../marine-offshore/orcawave-analysis/SKILL.md) - OrcaWave diffraction
- [orcawave-to-orcaflex](../../marine-offshore/orcawave-to-orcaflex/SKILL.md) - OrcaWave→OrcaFlex conversion
- [aqwa-analysis](../../marine-offshore/aqwa-analysis/SKILL.md) - AQWA diffraction
- [orcaflex-modeling](../../marine-offshore/orcaflex-modeling/SKILL.md) - OrcaFlex dynamic analysis
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) - Panel mesh generation
- [bemrosetta](../../marine-offshore/bemrosetta/SKILL.md) - Format conversion

---

## Version History

- **1.0.0** (2026-02-23): Initial cross-program workflow skill for hydrodynamic pipeline (WRK-372 Phase 4).
