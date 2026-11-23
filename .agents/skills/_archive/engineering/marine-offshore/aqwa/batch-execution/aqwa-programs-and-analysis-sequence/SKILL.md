---
name: aqwa-batch-execution-aqwa-programs-and-analysis-sequence
description: 'Sub-skill of aqwa-batch-execution: AQWA Programs and Analysis Sequence.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# AQWA Programs and Analysis Sequence

## AQWA Programs and Analysis Sequence


| Program | DAT JOB code | Purpose | Stage |
|---------|-------------|---------|-------|
| AQWA-LINE | `LINE` | Frequency-domain diffraction/radiation | 1 |
| AQWA-LIBRIUM | `LIBR` | Equilibrium position (static) | 2 |
| AQWA-DRIFT | `DRFT` | Wave drift / QTF forces | 3 |
| AQWA-NAUT | `NAUT` | Time-domain irregular waves | 3 |

**Program type is selected via `JOB <name> <code>` in Deck 0 of the `.DAT` file.**
Use `RESTART` records to chain stages: Stage 1 (LINE) → Stage 2 (LIBR) → Stage 3 (NAUT/DRIFT).
