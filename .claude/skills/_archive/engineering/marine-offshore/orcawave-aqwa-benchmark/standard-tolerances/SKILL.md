---
name: orcawave-aqwa-benchmark-standard-tolerances
description: 'Sub-skill of orcawave-aqwa-benchmark: Standard Tolerances (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Standard Tolerances (+1)

## Standard Tolerances


| Metric | Tolerance | Scope |
|--------|-----------|-------|
| Peak RAO Deviation | 5% | Significant values (>=10% of peak) |
| Phase Deviation | 5 degrees | At significant RAO values |
| Added Mass | 5% | Diagonal terms |
| Damping | 10% | Frequency-dependent |
| Mean Drift | 10% | All headings |

## Significance Threshold


Only values >= 10% of peak magnitude are considered for validation. This focuses comparison on physically meaningful responses rather than numerical noise in low-response regions.
