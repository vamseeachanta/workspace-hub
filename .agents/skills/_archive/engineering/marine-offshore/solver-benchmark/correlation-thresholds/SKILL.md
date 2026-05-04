---
name: solver-benchmark-correlation-thresholds
description: 'Sub-skill of solver-benchmark: Correlation Thresholds (+1).'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Correlation Thresholds (+1)

## Correlation Thresholds


| Range | Interpretation | Action |
|-------|---------------|--------|
| > 0.99 | Excellent agreement | Solvers validated |
| 0.95 – 0.99 | Good agreement | Minor differences (phase convention, numerics) |
| 0.80 – 0.95 | Fair agreement | Investigate input differences |
| < 0.80 | Poor agreement | Likely input mismatch or unit error |
| Negative | Anti-correlated | Data extraction bug (wrong frequency order, wrong units) |

## Common Causes of Poor Correlation


1. **Negative correlations**: Frequency arrays in different order (ascending vs descending)
2. **Near-zero correlations**: Hz vs rad/s mismatch (factor of 2*pi offset)
3. **NaN correlations**: Zero standard deviation (all-zero DOF, e.g. yaw for head seas)
4. **Good amplitude, bad phase**: Different time convention (e^{+iwt} vs e^{-iwt})
