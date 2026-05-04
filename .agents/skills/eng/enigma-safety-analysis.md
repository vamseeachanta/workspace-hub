# ENIGMA Safety Analysis Skill

## Invocation

```python
from worldenergydata.safety_analysis.skill import enigma_safety_analysis
result = enigma_safety_analysis("subsea_pipeline", "corrosion")
```

Or via the package namespace:

```python
from worldenergydata.safety_analysis import enigma_safety_analysis, EnigmaResult, SKILL_NAME
```

## Input

- `asset_type`: str — `subsea_pipeline` | `riser` | `wellhead` | `vessel` | `platform` | `mooring`
- `scenario`: str — `fatigue` | `corrosion` | `overpressure` | `structural` | `dropped_object` | `fire_explosion`
- `parameters`: dict (optional) — override defaults; supports `risk_score_override` (float 0.0–1.0)

## Output: EnigmaResult

- `.asset_type` — asset category evaluated
- `.scenario` — failure scenario assessed
- `.risk_score`: float 0.0–1.0 — computed risk magnitude
- `.risk_level`: `low` | `medium` | `high` | `critical`
  - low: < 0.30
  - medium: 0.30–0.59
  - high: 0.60–0.79
  - critical: >= 0.80
- `.fault_propagation`: list[str] — ordered failure event sequence (5 steps)
- `.recommendations`: list[str] — actionable mitigation steps (3 items)
- `.source`: always `"enigma"`

## Risk Matrix Summary

| Scenario        | Base Score | Notes                        |
|-----------------|-----------|------------------------------|
| fatigue         | 0.30      | Cyclic loading driven        |
| corrosion       | 0.40      | Electrochemical degradation  |
| overpressure    | 0.55      | Control system failure path  |
| structural      | 0.50      | Load/metocean event driven   |
| dropped_object  | 0.45      | Lift and rigging hazards     |
| fire_explosion  | 0.75      | Hydrocarbon ignition events  |

Asset modifiers (multiplied against base): riser 1.20, subsea_pipeline 1.10,
mooring 1.05, vessel 1.00, wellhead 0.95, platform 0.90.

## Zero-config guarantee

No setup, network access, or data files required. Works fully offline.
Raises `ValueError` for unsupported asset_type or scenario values.
