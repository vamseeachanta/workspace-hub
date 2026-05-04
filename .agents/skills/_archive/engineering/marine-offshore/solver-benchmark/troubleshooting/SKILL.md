---
name: solver-benchmark-troubleshooting
description: 'Sub-skill of solver-benchmark: Troubleshooting.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Troubleshooting

## Troubleshooting


| Issue | Cause | Solution |
|-------|-------|----------|
| Solver not found | Path not configured | Set `SOLVER_PATHS` or env var |
| License error | Missing/expired license | Check license server |
| NO_CONSENSUS | Mismatched inputs | Verify spec is identical for all solvers |
| Mesh error | Incompatible format | Convert mesh using `/mesh` skill |
| Timeout | Complex geometry | Increase timeout or coarsen mesh |
