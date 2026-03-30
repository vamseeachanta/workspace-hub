---
name: orcaflex-vessel-setup-basic-vessel-configuration
description: 'Sub-skill of orcaflex-vessel-setup: Basic Vessel Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Vessel Configuration (+1)

## Basic Vessel Configuration


```yaml
# configs/vessel_config.yml

vessel:
  name: "FPSO"
  vessel_type: "FPSO_Type"

  # Position and orientation
  initial_position:
    x: 0.0      # m
    y: 0.0      # m
    z: 0.0      # m (relative to sea surface)

  orientation: 0.0    # deg (heading)
  draught: 15.5       # m

  # Calculation settings
  calculation:
    include_applied_loads: "6 DOF"
    primary_motion: "6 DOF calculated (no wave load RAOs)"
    superimposed_motion: "None"

    # Wave load options
    wave_load: "Calculated from RAOs (first order)"
    drift_load: "Calculated from QTFs"

    # Environmental loads
    current_load: "Calculated"
    wind_load: "Calculated"

    # Damping
    damping_calculation: "From hydrodynamic database"

vessel_type:
  name: "FPSO_Type"
  length: 300.0        # m

  # RAO data source
  hydrodynamic_data:
    source: "aqwa"     # or "orcaflex", "csv"
    file: "data/fpso_aqwa.lis"

  # RAO import settings
  rao_import:
    displacement_raos: true
    load_raos: true
    stiffness_added_mass_damping: true
    qtfs: true
    qtf_type: "Full"   # or "Newman"
```


## AQWA Import Configuration


```yaml
# configs/aqwa_vessel_import.yml

aqwa_import:
  # Source file
  source_file: "data/vessel_aqwa.lis"

  # Body mapping (for multi-body systems)
  body_mapping:
    - aqwa_body: 1
      orcaflex_vessel: "FPSO"
    - aqwa_body: 2
      orcaflex_vessel: "Shuttle_Tanker"

  # Data to import
  import_data:
    displacement_raos: true
    load_raos: true
    added_mass: true
    damping: true
    stiffness: true
    qtfs:
      enabled: true
      type: "Full"     # Full or Newman approximation

  # RAO conventions
  conventions:
    frequency_units: "rad/s"
    phase_convention: "OrcaFlex"   # Check AQWA vs OrcaFlex sign
```
