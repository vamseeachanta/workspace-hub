---
name: orcawave-analysis-orcawave-api-properties-reference
description: 'Sub-skill of orcawave-analysis: OrcaWave API Properties Reference.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaWave API Properties Reference

## OrcaWave API Properties Reference


These properties return the same data as shown on the validation page in the OrcaWave GUI:

**Frequency/Period Data:**
- `headings` - Wave heading angles (degrees)
- `frequencies` - Wave frequencies (rad/s)
- `angularFrequencies` - Angular frequencies
- `periods` - Wave periods (seconds)
- `periodsOrFrequencies` - Display format

**Hydrostatic and Frequency-Dependent:**
- `hydrostaticResults` - Hydrostatic stiffness matrix
- `addedMass` - Frequency-dependent added mass
- `infiniteFrequencyAddedMass` - Infinite frequency added mass
- `damping` - Radiation damping coefficients

**RAO Data:**
- `loadRAOsHaskind` - Force/moment RAOs (Haskind method) - N/m, N·m/m
- `loadRAOsDiffraction` - Force/moment RAOs (diffraction) - N/m, N·m/m
- `displacementRAOs` - **Motion/displacement RAOs** (m/m, rad/m) - **Use for AQWA comparison**

**QTF Data:**
- `meanDriftHeadingPairs` - Mean drift force heading combinations
- `QTFHeadingPairs` - QTF heading pairs
- `QTFFrequencies`, `QTFAngularFrequencies`, `QTFPeriods`, `QTFPeriodsOrFrequencies`


*See sub-skills for full details.*
