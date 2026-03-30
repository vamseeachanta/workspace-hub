---
name: hydrodynamic-pipeline-orcawave-to-orcaflex-direct-integration
description: 'Sub-skill of hydrodynamic-pipeline: OrcaWave to OrcaFlex (Direct Integration)
  (+3).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# OrcaWave to OrcaFlex (Direct Integration) (+3)

## OrcaWave to OrcaFlex (Direct Integration)


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


## AQWA to OrcaFlex (via BEMRosetta or Manual)


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


## Data Format Mapping


| Source (OrcaWave/AQWA) | Target (OrcaFlex) | Notes |
|------------------------|-------------------|-------|
| RAO amplitude + phase | VesselType displacement RAOs | Check heading convention (from/to) |
| Added mass (freq-dep) | VesselType added mass | Infinite-frequency value needed too |
| Radiation damping | VesselType radiation damping | Must be positive definite |
| Mean drift coefficients | VesselType drift coefficients | Newman or full QTF |
| QTFs (diff-frequency) | VesselType QTF data | Slow-drift calculation |
| Hydrostatic stiffness | VesselType stiffness | Cross-check with hand calc |


## Coordinate System Warnings


| Convention | OrcaWave | AQWA | OrcaFlex |
|-----------|----------|------|----------|
| **Origin** | User-defined | User-defined | Vessel reference point |
| **X-axis** | Forward (+ve) | Forward (+ve) | Forward (+ve) |
| **Z-axis** | Up (+ve) | Up (+ve) | Up (+ve) |
| **Wave heading** | 0=from +X | 0=from +X | 0=from +X (verify!) |
| **Phase** | Varies | Varies | Relative to wave crest at origin |

**Critical**: Always verify heading convention. A 180-degree error inverts all RAO phases.
