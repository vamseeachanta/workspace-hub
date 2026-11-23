---
name: solver-benchmark-mandatory-checks-before-committing-reports
description: 'Sub-skill of solver-benchmark: Mandatory Checks Before Committing Reports
  (+2).'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Mandatory Checks Before Committing Reports (+2)

## Mandatory Checks Before Committing Reports


```
[ ] Master summary verdict matches individual report content
[ ] "Headings: N" shows the correct count (not 0 for cases with wave headings defined)
[ ] DOF plots contain actual data (not flat lines from empty heading arrays)
[ ] All physics sections present: hydrostatics, load RAOs, roll damping, mesh quality
[ ] Navigation links between combined report and per-body reports work
```

## Known Bug: `diff.headings` Returns Empty After `Calculate()`


**Affected cases**: `full_qtf` analysis type, certain bi-symmetric configurations, fixed-DOF bodies.

**Symptom**: Report header shows `Headings: 0 (°)` even though wave headings are
defined in spec.yml. DOF plots appear empty because heading data is missing.

**Root cause**: `OrcFxAPI.Diffraction.headings` may return an empty array after
`Calculate()` is called in memory. The property is only reliably populated after
`LoadResults()` from a saved `.owr` file.

**Workaround**: Pass the saved `.owr` path to the report generator via:

*See sub-skills for full details.*

## Regenerating Stale Reports


```bash
# Regenerate a single case (re-runs OrcaWave — takes ~30-120s)
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 2.2

# Regenerate master summary only (fast — reads cached JSON, no OrcaWave run)
uv run python scripts/benchmark/validate_owd_vs_spec.py --summary-only

# Regenerate all cases (slow — runs OrcaWave for each)
uv run python scripts/benchmark/validate_owd_vs_spec.py --all
```
