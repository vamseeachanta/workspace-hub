---
name: mooring-design-design-check-matrix
description: 'Sub-skill of mooring-design: Design Check Matrix (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Design Check Matrix (+2)

## Design Check Matrix


| Check | Intact (DNV) | Damaged (DNV) | Method |
|-------|-------------|---------------|--------|
| Line tension SF | >= 1.67 (dynamic) | >= 1.25 (dynamic) | Max tension / MBL |
| Vessel offset | < 8% water depth | < 12% water depth | Max offset in design storm |
| Anchor capacity | SF >= 1.5 | SF >= 1.2 | Max anchor load / holding capacity |
| Line fatigue | Design life x3 | — | Miner's sum across sea states |
| Collision check | No line-line contact | — | Minimum separation > 2 * line diameter |

## Validation Code


```python
def validate_mooring_design(results, safety_factors):
    """Validate mooring analysis results against design criteria."""
    checks = []
    all_pass = True

    for result in results:
        # Tension safety factor
        sf = result.safety_factor
        sf_req = safety_factors.get(result.load_case, 1.67)

*See sub-skills for full details.*

## Key Standards Reference


| Standard | Application | Key Requirement |
|----------|-------------|-----------------|
| DNV-OS-E301 | Position mooring | Safety factors, fatigue, ALS |
| API RP 2SK | Station keeping | Environmental loads, analysis methods |
| ABS Rules | Mooring systems | Material specs, testing, survey |
| BV NR 493 | Mooring systems | Chain properties, proof testing |
