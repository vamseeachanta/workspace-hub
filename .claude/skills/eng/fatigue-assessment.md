# Fatigue Assessment Skill

Zero-config agent-callable wrapper around the Digital Model fatigue analysis
engine. Accepts a stress-range histogram (ranges + cycle counts) and returns
Palmgren-Miner cumulative damage, fatigue life, utilisation ratio, and per-bin
damage contributions — no API keys, environment variables, or data files required.

## Invocation

```python
from digitalmodel.structural.fatigue.skill import (
    fatigue_assessment, FatigueAssessmentInput, SKILL_NAME
)

inp = FatigueAssessmentInput(
    stress_ranges=[150.0, 100.0, 70.0, 50.0],
    cycle_counts=[500.0, 5000.0, 50000.0, 200000.0],
    sn_curve_name="F",
    design_code="DNV",
)
result = fatigue_assessment(inp)
print(result.utilisation_ratio)   # Miner's D
print(result.life_years)          # 1 / D
print(result.governing_load_case) # e.g. "150.0 MPa"
```

Or importing directly from the package:

```python
from digitalmodel.structural.fatigue import skill as fatigue_skill
result = fatigue_skill.fatigue_assessment(fatigue_skill.FatigueAssessmentInput(
    stress_ranges=[100.0], cycle_counts=[10000.0]
))
```

## Input: `FatigueAssessmentInput`

| Field | Type | Default | Description |
|---|---|---|---|
| `stress_ranges` | `list[float]` | required | Stress range histogram bin values in MPa |
| `cycle_counts` | `list[float]` | required | Applied cycle count for each bin (same length as `stress_ranges`) |
| `sn_curve_name` | `str` | `"D"` | S-N curve class identifier (see table below) |
| `design_code` | `str` | `"DNV"` | Standard: `"DNV"`, `"API"`, or `"BS"` |
| `output_formats` | `list[str]` | `["summary"]` | Requested output sections (reserved for future use) |

### S-N Curve Classes by Standard

| Standard | Valid Classes | Notes |
|---|---|---|
| `DNV` | B1, B2, C, C1, C2, D, E, F, F1, F3, G, W1, W2, W3 | DNV-RP-C203 (in air, T=16-25 mm) |
| `API` | X, X\_prime, Y, S-N1, S-N2 | API RP 2A-WSD |
| `BS` | B, C, D, E, F, F2, G, W | BS 7608 |

DNV class hierarchy (strongest to weakest): B1 > B2 > C > C1 > C2 > D > E > F > F1 > F3 > G > W1 > W2 > W3.
For offshore structural connections in air, D is the most common default. Use F or weaker classes for
fillet welds and complex geometry. Use E for butt welds. G and W1 apply to low-quality welds.

## Output: `FatigueAssessmentResult`

| Field | Type | Description |
|---|---|---|
| `utilisation_ratio` | `float` | Miner's cumulative damage D = Σ(nᵢ/Nᵢ). Failure at D ≥ 1.0 |
| `life_years` | `float` | 1 / D (block-normalised). `math.inf` when D = 0 |
| `governing_load_case` | `str` | Stress range [MPa] contributing the most damage (e.g. `"150.0 MPa"`) |
| `sn_curve_used` | `str` | S-N curve label applied (e.g. `"DNV-F"`) |
| `damage_per_block` | `list[float]` | Damage increment per histogram bin, same length as input |
| `summary` | `dict` | Aggregated statistics (see keys below) |
| `source` | `str` | Always `"skill:fatigue_assessment"` |

### `summary` dict keys

| Key | Type | Description |
|---|---|---|
| `total_damage` | `float` | Miner's sum (same as `utilisation_ratio`) |
| `life_years` | `float` | 1 / D |
| `utilisation_ratio` | `float` | Miner's sum |
| `sn_curve` | `str` | Curve label (e.g. `"DNV-D"`) |
| `total_cycles` | `float` | Sum of all applied cycle counts |
| `max_stress_range_mpa` | `float` | Largest stress range in the histogram |
| `governing_load_case` | `str` | Bin label with highest damage contribution |

## Error Conditions

`ValueError` is raised (never silently swallowed) when:

- `stress_ranges` is empty
- `stress_ranges` and `cycle_counts` have different lengths
- `design_code` is not `"DNV"`, `"API"`, or `"BS"` (case-insensitive)
- `sn_curve_name` is not valid for the selected `design_code`

## Zero-config Guarantee

No setup, network access, or data files required. Works fully offline.
All S-N curve parameters are embedded in the module.

## Module Location

- Skill implementation: `digitalmodel/src/digitalmodel/structural/fatigue/skill.py`
- Skill name constant: `SKILL_NAME = "fatigue_assessment"`
- Tests: `digitalmodel/tests/structural/fatigue/test_fatigue_skill.py`

## Background

The skill uses **Palmgren-Miner linear damage accumulation** (D = Σ nᵢ/Nᵢ)
with **power-law S-N curves** (N = A · S^(-m)) from the selected standard.
Stress ranges at or below the curve's constant-amplitude fatigue limit (CAFL)
are assigned infinite life and contribute zero damage.

For offshore structural applications the typical workflow is:

1. Extract stress-range histogram from a time-domain analysis (rainflow counting).
2. Call this skill with the histogram + appropriate S-N curve.
3. Compare `utilisation_ratio` against the code limit (usually ≤ 1.0 / DFF
   where DFF is the design fatigue factor, e.g. 3.0 for inspectable zones).
