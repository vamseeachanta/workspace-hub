---
name: aqwa-output
description: AQWA output formats (RAO CSV, coefficient JSON), LIS parsing conventions,
  result validation, benchmark comparison vs OrcaWave, and validation criteria.
type: reference
version: 1.0.0
updated: 2026-03-16
category: engineering
triggers:
- AQWA output format
- AQWA LIS parsing
- AQWA validation
- AQWA benchmark
- AQWA OrcaWave comparison
- AQWA RAO CSV
capabilities: []
requires: []
see_also:
- aqwa-analysis
tags: []
scripts_exempt: true
---
# AQWA Output Skill

Output formats, LIS parsing conventions, result validation, and benchmark comparison for ANSYS AQWA. See [aqwa](../SKILL.md) for Python API.

## Output Formats

### RAO CSV Format

```csv
frequency_rad_s,direction_deg,surge_amp,surge_phase,sway_amp,sway_phase,heave_amp,heave_phase,roll_amp,roll_phase,pitch_amp,pitch_phase,yaw_amp,yaw_phase
0.100,0.0,0.985,178.2,0.000,0.0,1.023,-2.5,0.000,0.0,0.156,175.8,0.000,0.0
0.100,90.0,0.000,0.0,0.978,175.4,1.015,-3.2,2.345,-8.5,0.000,0.0,0.012,92.1
```

### Coefficient Matrices JSON

```json
{
  "frequencies_rad_s": [0.1, 0.2, 0.3, 0.5, 0.8],
  "added_mass": { "0.1": [[1.2e6, 0, 0, 0, 1.5e7, 0], ...] },
  "damping": { "0.1": [[2.5e5, 0, 0, 0, 3.2e6, 0], ...] }
}
```

## LIS Parsing Conventions

- `ADDED  MASS` header has **double space** — use whitespace normalization for matching
- WAVE FREQUENCY line appears ~23 lines before DAMPING section — search backward 30 lines
- Matrix rows in added mass/damping sections are separated by blank lines
- First RAO section = displacement RAOs; subsequent sections = velocity/acceleration (skip these)

## Post-Processing & Validation

```python
from digitalmodel.aqwa.aqwa_postprocess import AqwaPostProcess
from digitalmodel.aqwa.aqwa_validator import AqwaValidator

postprocess = AqwaPostProcess()
postprocess.load("aqwa_results/vessel.LIS")
postprocess.generate_report(
    output_file="results/aqwa_report.html",
    include=["summary", "rao_plots", "coefficient_tables", "drift_force_plots"]
)

validator = AqwaValidator()
validator.load("aqwa_results/vessel.LIS")
results = validator.validate()
# Check: symmetry_check, low_frequency_check, radiation_check

if not validator.check_positive_definite_damping():
    print("Warning: Damping matrix not positive definite")
if not validator.check_symmetric_added_mass():
    print("Warning: Added mass matrix not symmetric")

kk_result = validator.kramers_kronig_check()
```

## Benchmark Comparison vs OrcaWave

```yaml
aqwa_analysis:
  benchmark_comparison:
    flag: true
    aqwa_results: "aqwa_results/vessel.LIS"
    orcawave_results: "orcawave_results/vessel.sim"
    tolerance: 0.05
    peak_threshold: 0.10
    output:
      comparison_report: "results/aqwa_orcawave_comparison.html"
      peak_analysis: "results/peak_values_comparison.html"
```

### Standalone Comparison Scripts

```bash
# Peak-focused comparison
cd docs/modules/orcawave/L01_aqwa_benchmark
python run_comparison_peaks.py

# Heading-by-heading comparison
python run_proper_comparison.py
```

### Module-Level Integration

```python
from digitalmodel.diffraction.aqwa_converter import AQWAConverter

converter = AQWAConverter(
    analysis_folder="docs/modules/orcawave/L01_aqwa_benchmark",
    vessel_name="SHIP_RAOS"
)
aqwa_results = converter.convert_to_unified_schema(water_depth=30.0)
# Use with DiffractionComparator for full benchmark analysis
```

## Benchmark Validation Criteria

**Engineering Standard Practice:**
- 5% tolerance applies to **peak and significant values only**
- "Significant" = RAO magnitude >= 10% of peak value
- Pass requires 90% of significant points within 5% tolerance
- Low-amplitude responses (<10% of peak) excluded from validation

**Typical Peak Values by DOF:**
- **Heave**: 0.9-1.1 m/m (near natural period)
- **Pitch**: 0.4-0.6 deg/m (near natural period)
- **Roll**: 2-5 deg/m (beam seas, low frequency)
- **Surge**: 0.8-1.0 m/m (following seas)
- **Sway**: 0.8-1.0 m/m (beam seas)
- **Yaw**: Small (<0.1 deg/m for symmetric vessels)

## Related Skills

- [aqwa](../SKILL.md) — Hub skill with Python API
- [aqwa/input](../input/SKILL.md) — Input formats and configurations
- [aqwa/reference](../reference/SKILL.md) — Solver stages and OPTIONS keywords
- [orcawave/analysis](../../orcawave/analysis/SKILL.md) — OrcaWave benchmark validation
