---
name: aqwa-analysis
description: Integrate with AQWA hydrodynamic software for RAO computation, damping
  analysis, and coefficient extraction. Hub skill — delegates to aqwa-input, aqwa-output,
  aqwa-reference for details.
type: reference
version: 4.0.0
updated: 2026-03-16
category: engineering
triggers:
- AQWA analysis
- RAO extraction
- added mass calculation
- damping coefficient
- wave diffraction
- radiation analysis
- AQWA-LINE
- AQWA-DRIFT
- AQWA-LIBRIUM
- AQWA-NAUT
capabilities: []
requires: []
see_also:
- aqwa-input
- aqwa-output
- aqwa-reference
tags: []
scripts_exempt: true
---
# AQWA Analysis Skill

Hub for ANSYS AQWA hydrodynamic analysis — RAO computation, added mass/damping extraction, coefficient management.

## When to Use

- RAO (Response Amplitude Operator) computation
- Hydrodynamic coefficient extraction (added mass, damping)
- Viscous damping determination
- Diffraction/radiation analysis (AQWA-LINE)
- Time domain motions (AQWA-DRIFT)
- Stability analysis (AQWA-LIBRIUM)
- Cable dynamics (AQWA-NAUT), coupled analysis (AQWA-WAVE)

## Prerequisites

- Python environment with `digitalmodel` package
- AQWA output files (LIS, DAT, or MES format)
- For running AQWA: ANSYS AQWA license

## Industry Standards

- DNV-RP-C205 (Environmental Conditions)
- API RP 2SK (Stationkeeping)
- ISO 19901-7 (Mooring Systems)
- IEC 61400-3 (Wind Turbines)

## Python API

### RAO Extraction

```python
from digitalmodel.aqwa.aqwa_raos import AqwaRAOs

raos = AqwaRAOs()
raos.load("aqwa_results/vessel.LIS")

surge_rao = raos.get_rao(motion="surge", wave_direction=180.0)
rao_df = raos.to_dataframe()

raos.plot_rao(
    motions=["heave", "pitch", "roll"],
    directions=[0, 90, 180],
    output_file="results/rao_comparison.html"
)
raos.export_orcaflex("vessel_raos.yml")
```

### Analysis Router

```python
from digitalmodel.aqwa.aqwa_analysis import AqwaAnalysis

aqwa = AqwaAnalysis()
cfg = {
    "aqwa": {
        "input_file": "aqwa_results/vessel.LIS",
        "extract": ["raos", "added_mass", "damping", "drift_forces"],
        "output_directory": "results/"
    }
}
results = aqwa.run(cfg)
```

### Coefficient Extraction

```python
from digitalmodel.aqwa.aqwa_reader import AqwaReader

reader = AqwaReader()
data = reader.read("aqwa_results/vessel.LIS")

added_mass = data.get_added_mass(0.1)  # 6x6 numpy array at ω=0.1 rad/s
damping = data.get_damping(0.1)
```

### Pre-Processing

```python
from digitalmodel.aqwa.aqwa_preprocess import AqwaPreProcess

preprocess = AqwaPreProcess()
preprocess.generate_input(
    vessel_geometry="geometry/hull.stl",
    water_depth=1000.0,
    wave_frequencies=[0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0],
    wave_directions=[0, 45, 90, 135, 180],
    output_file="aqwa_input/vessel.dat"
)
```

## Key Classes

| Class | Purpose |
|-------|---------|
| `AqwaAnalysis` | Main analysis router |
| `AqwaRAOs` | RAO computation and export |
| `AqwaReader` | File parsing (LIS, DAT, MES) |
| `AqwaPreProcess` | Input file generation |
| `AqwaPostProcess` | Results post-processing |
| `AqwaValidator` | Result validation |

## Related Skills

- [aqwa/input](input/SKILL.md) — Analysis configs, file formats, DAT conventions, mesh quality
- [aqwa/output](output/SKILL.md) — Output formats, validation, benchmarks
- [aqwa/reference](reference/SKILL.md) — Solver stages, OPTIONS keywords, FIDP/FISK cards
- [aqwa/batch-execution](batch-execution/SKILL.md) — Batch run orchestration
- [diffraction-analysis](../diffraction-analysis/SKILL.md) — **Master skill** for all diffraction workflows
- [bemrosetta](../bemrosetta/SKILL.md) — AQWA to OrcaFlex conversion
- [orcawave/analysis](../orcawave/analysis/SKILL.md) — Benchmark validation

## References

- ANSYS AQWA User Manual
- DNV-RP-C205: Environmental Conditions and Environmental Loads
- Newman, J.N.: Marine Hydrodynamics
