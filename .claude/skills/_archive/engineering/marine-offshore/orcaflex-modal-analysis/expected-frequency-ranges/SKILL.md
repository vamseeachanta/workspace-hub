---
name: orcaflex-modal-analysis-expected-frequency-ranges
description: 'Sub-skill of orcaflex-modal-analysis: Expected Frequency Ranges (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Expected Frequency Ranges (+1)

## Expected Frequency Ranges


| Structure Type | Typical Period Range | Notes |
|---------------|---------------------|-------|
| SCR (Steel Catenary Riser) | 2-30s | In-line and cross-flow modes |
| Mooring line | 5-60s | Depends on length and pretension |
| FPSO (hull) | 5-15s (heave/pitch) | Compare with RAO peaks |
| TTR (Top Tensioned Riser) | 1-20s | Higher tension = higher frequency |
| Jumper | 1-10s | Short span, higher frequencies |

## Validation Checks


| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Fundamental mode period | Compare with analytical catenary formula | Within 20% of T = 2L/n * sqrt(m/T) |
| Mode shape continuity | Plot mode shapes | No discontinuities or jumps |
| VIV susceptibility | Check 4 < Vr < 8 for any mode | Flag modes with lock-in risk |
| DOF energy sum | Sum DOF percentages per mode | Should sum to ~100% |
| Symmetric model | Check paired modes | Degenerate pairs should have similar periods |

```python
def validate_modal_results(modes, expected_period_range=(1.0, 60.0)):

*See sub-skills for full details.*
