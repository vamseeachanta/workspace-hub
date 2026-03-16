---
name: orcaflex-line-wizard-post-wizard-checks
description: 'Sub-skill of orcaflex-line-wizard: Post-Wizard Checks.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Post-Wizard Checks

## Post-Wizard Checks


| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Tension achieved | Compare actual vs target | Error < 1% of target |
| Line length positive | All section lengths > 0 | No negative lengths |
| Catenary shape valid | Visual check or arc length > span | Line doesn't go through seabed |
| Static convergence | `model.CalculateStatics()` | Converges after wizard adjustment |
| Anchor holding | Tension at anchor < holding capacity | With safety factor (SF > 1.5) |

```python
def validate_wizard_results(model, configs):

*See sub-skills for full details.*
