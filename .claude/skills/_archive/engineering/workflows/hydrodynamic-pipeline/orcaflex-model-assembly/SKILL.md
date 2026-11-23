---
name: hydrodynamic-pipeline-orcaflex-model-assembly
description: 'Sub-skill of hydrodynamic-pipeline: OrcaFlex Model Assembly (+1).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# OrcaFlex Model Assembly (+1)

## OrcaFlex Model Assembly


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


## Execution


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
