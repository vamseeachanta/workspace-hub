---
name: clean-code-naming-rules-enforcement
description: 'Sub-skill of clean-code: Naming Rules (Enforcement).'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Naming Rules (Enforcement)

## Naming Rules (Enforcement)


| Item | Rule | Wrong | Correct |
|------|------|-------|---------|
| Python files | `snake_case.py` | `PipeCapacity.py` | `pipe_capacity.py` |
| Python dirs | `snake_case/` | `orcaflex-dashboard/` | `orcaflex_dashboard/` |
| Classes | `PascalCase` | `pipe_capacity` | `PipeCapacity` |
| Functions | `snake_case` | `calcWallThick` | `calc_wall_thickness` |
| Constants | `SCREAMING_SNAKE` | `safetyFactor` | `SAFETY_FACTOR` |
| Private helpers | `_snake_case` | `__helper` | `_helper` |
| Test files | `test_<module>.py` | `PipeCapacityTest.py` | `test_pipe_capacity.py` |

**Quick check for PascalCase file names** (violation):
```bash
find src/ -name "*.py" | grep -E '/[A-Z][a-zA-Z]+\.py$'
```

---
