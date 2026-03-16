---
name: hydrodynamics-1-coefficient-database-management
description: 'Sub-skill of hydrodynamics: 1. Coefficient Database Management (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Coefficient Database Management (+4)

## 1. Coefficient Database Management


Store and retrieve hydrodynamic coefficients.

```yaml
hydrodynamics:
  coefficient_database:
    flag: true
    vessel_name: "FPSO"
    source_file: "data/hydro_coefficients.json"
    coefficients:
      - added_mass
      - damping
      - wave_excitation
    output:
      database_file: "results/coefficient_db.json"
```

## 2. Wave Spectra Modeling


Generate and analyze wave spectra.

```yaml
hydrodynamics:
  wave_spectra:
    flag: true
    spectrum_type: "jonswap"  # jonswap, bretschneider, pm, custom
    parameters:
      hs: 3.5  # Significant wave height (m)
      tp: 10.0  # Peak period (s)

*See sub-skills for full details.*

## 3. OCIMF Environmental Loading


Calculate wind and current loads per OCIMF guidelines.

```yaml
hydrodynamics:
  ocimf_loading:
    flag: true
    vessel:
      length: 300.0
      beam: 50.0
      draft: 20.0

*See sub-skills for full details.*

## 4. RAO Interpolation


Interpolate RAOs across frequencies and directions.

```yaml
hydrodynamics:
  rao_interpolation:
    flag: true
    input_raos: "data/vessel_raos.csv"
    target_frequencies: [0.05, 0.1, 0.15, 0.2, 0.25]
    target_directions: [0, 30, 60, 90, 120, 150, 180]
    method: "cubic"  # linear, cubic, spline
    output:
      interpolated_file: "results/interpolated_raos.csv"
```

## 5. Displacement RAO Quality Checks


Validate displacement RAO data for physical correctness and consistency.

```yaml
hydrodynamics:
  rao_quality_check:
    flag: true
    input_file: "data/vessel_raos.yml"  # OrcaFlex format
    vessel_type: auto  # auto, ship, fpso, semi_submersible, spar, barge
    tolerances:
      amplitude: 0.05  # 5% tolerance

*See sub-skills for full details.*
