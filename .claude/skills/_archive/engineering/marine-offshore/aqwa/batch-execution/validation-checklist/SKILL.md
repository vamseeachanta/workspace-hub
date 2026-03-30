---
name: aqwa-batch-execution-validation-checklist
description: 'Sub-skill of aqwa-batch-execution: Validation Checklist.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Validation Checklist

## Validation Checklist


After any AQWA-LINE run:

- [ ] `.MES` file has no `ERROR` / `FATAL` / `ABORT` strings
- [ ] `.RES` and `.PLT` files exist (required for Stage 2/3)
- [ ] Panel count in `.LIS` matches expected model size
- [ ] No `NON-DIFFRACTING` warnings in `.LIS` (would mean missing `DIFF` keyword)
- [ ] Surge/sway/yaw RAO → 1.0 at low frequency (long-wave limit)
- [ ] Heave RAO → 1.0 at low frequency
- [ ] Added mass matrix is positive semi-definite at all frequencies
- [ ] Roll RAO peak aligns with expected natural period
