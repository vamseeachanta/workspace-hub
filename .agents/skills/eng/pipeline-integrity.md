# Pipeline Integrity Skill

## Invocation

```python
from digitalmodel.asset_integrity.pipeline_skill import (
    pipeline_integrity, PipelineInput, SKILL_NAME
)

inp = PipelineInput(
    outer_diameter_mm=323.9,
    wall_thickness_mm=14.3,
    design_pressure_mpa=10.0,
    material_grade="X65",
    corrosion_depth_mm=3.0,
    corrosion_length_mm=150.0,
)
result = pipeline_integrity(inp)
```

## Input: PipelineInput

| Field | Type | Default | Description |
|---|---|---|---|
| `outer_diameter_mm` | float | required | Pipe outer diameter (mm) |
| `wall_thickness_mm` | float | required | Nominal wall thickness (mm) |
| `design_pressure_mpa` | float | required | Maximum design/operating pressure (MPa) |
| `material_grade` | str | `"X65"` | API 5L grade: X52, X60, X65, X70, X80, X100 |
| `corrosion_depth_mm` | float | `0.0` | Maximum corrosion pit depth (mm) |
| `corrosion_length_mm` | float | `0.0` | Axial corrosion extent (mm) |

All dimensional inputs must be positive (or zero for corrosion fields). Invalid
`material_grade` raises `ValueError`.

## Output: PipelineIntegrityResult

| Field | Type | Description |
|---|---|---|
| `wall_thickness_ok` | bool | True if hoop utilisation <= 1.0 |
| `utilisation_ratio` | float | Hoop stress / allowable (design factor 0.72 * SMYS) |
| `ffs_verdict` | str | `"accept"` / `"repair"` / `"replace"` / `"not_applicable"` |
| `ffs_safe_pressure_mpa` | float | Barlow MAWP for measured thickness (MPa) |
| `summary` | dict | Full parameter set for audit/logging |
| `source` | str | Always `"skill:pipeline_integrity"` |

## Assessment Logic

**Step 1 — Wall thickness check (ASME B31.4/B31.8 style)**

```
hoop_stress = P * OD / (2 * t)
allowable   = SMYS * 0.72
utilisation = hoop_stress / allowable
wall_thickness_ok = utilisation <= 1.0
```

**Step 2 — FFS corrosion assessment (API 579-1 Level 1)**

Only runs when `corrosion_depth_mm > 0`. Uses `rsf_calculations.check_ffs_level1`
with the remaining measured thickness `t_measured = t_nominal - corrosion_depth`.

| Verdict | Condition |
|---|---|
| `not_applicable` | No corrosion present |
| `accept` | RSF >= 0.90 and measured WT >= required WT |
| `repair` | RSF < 0.90, metal loss < 80% of wall |
| `replace` | Corrosion >= 80% wall loss, or measured WT <= 0 |

## Material Grade SMYS Table (MPa)

| Grade | SMYS (MPa) |
|---|---|
| X52 | 359 |
| X60 | 414 |
| X65 | 448 |
| X70 | 483 |
| X80 | 552 |
| X100 | 690 |

## Zero-config guarantee

No setup, network access, data files, or config objects required.
Fully offline and deterministic. All units are SI (mm, MPa) at the public API.

## Module location

`digitalmodel/src/digitalmodel/asset_integrity/pipeline_skill.py`

Tests: `digitalmodel/tests/asset_integrity/test_pipeline_skill.py` (39 tests)
