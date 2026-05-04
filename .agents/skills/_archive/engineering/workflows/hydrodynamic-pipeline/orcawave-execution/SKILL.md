---
name: hydrodynamic-pipeline-orcawave-execution
description: 'Sub-skill of hydrodynamic-pipeline: OrcaWave Execution (+3).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# OrcaWave Execution (+3)

## OrcaWave Execution


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


## AQWA Execution


```bash
# AQWA runs via ANSYS Workbench or command line
# Typical AQWA-LINE execution:
aqwa_line input.dat output.lis

# AQWA-DRIFT for QTFs:
aqwa_drift input.dat output.lis
```


## Key Outputs from Diffraction Analysis


| Output | Format | Used By | Description |
|--------|--------|---------|-------------|
| **RAOs** | .owd / .lis | OrcaFlex VesselType | Response amplitude operators (6 DOF) |
| **Added mass** | Frequency-dependent | OrcaFlex | Mass added by fluid acceleration |
| **Radiation damping** | Frequency-dependent | OrcaFlex | Energy radiated as waves |
| **Mean drift** | Force per wave amplitude² | OrcaFlex | Steady drift forces |
| **QTFs** | Difference/sum frequency | OrcaFlex | Second-order slow-drift forces |
| **Hydrostatic stiffness** | 6x6 matrix | OrcaFlex | Restoring forces |


## Extracting Results for OrcaFlex


```python
import OrcFxAPI

def extract_diffraction_results(owd_path):
    """Extract hydrodynamic data from OrcaWave for OrcaFlex.

    OrcaWave results are accessed via VesselType diffraction data,
    not the Vessel instance directly.
    """
    model = OrcFxAPI.Model()
    model.LoadSimulation(owd_path.replace('.owd', '.owr'))

    # Access vessel type (diffraction data lives on VesselType, not Vessel)
    vessel_type = model['Vessel Type1']

    results = {
        "raos": {},
        "added_mass": {},
        "damping": {},
    }

    # Extract RAOs via VesselType hydrodynamic database
    # RAO data is loaded via VesselType.LoadHydrodynamicData() or
    # accessed after OrcaWave populates the vessel type
    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
    for i, dof in enumerate(dof_names):
        results["raos"][dof] = {
            "amplitude": [],
            "phase": [],
        }
        # Note: exact accessor depends on OrcaWave version; see
        # orcawave-to-orcaflex skill for the canonical extraction pattern

    return results
```
