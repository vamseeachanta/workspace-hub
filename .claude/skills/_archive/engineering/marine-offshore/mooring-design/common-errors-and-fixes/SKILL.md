---
name: mooring-design-common-errors-and-fixes
description: 'Sub-skill of mooring-design: Common Errors and Fixes (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Errors and Fixes (+1)

## Common Errors and Fixes


| Error | Cause | Fix |
|-------|-------|-----|
| Catenary solution diverges | Horizontal tension too low for water depth and line weight | Increase pretension or add more line length |
| Anchor capacity exceeded | Environmental loads larger than holding capacity | Upsize anchor or add anchor line length for catenary reduction |
| Safety factor < required | Line MBL too low for design tensions | Upsize chain/rope diameter or change material grade |
| Vessel offset exceeds limit | Mooring stiffness too low | Add more lines, shorten lines, or increase pretension |
| Line-line interference | Mooring spread angle too narrow | Increase angular spacing between lines (min 30 deg recommended) |
| Snap loading | Slack line becomes taut under dynamic loading | Increase pretension to avoid slack; add damping materials |
| Polyester creep | Long-term elongation under sustained load | Use DNV creep factors; design for post-installation elongation |

## Debugging Mooring Design


```python
def diagnose_mooring_system(system, environment):
    """Check mooring system design for common issues."""
    issues = []

    # Check minimum number of lines
    n_lines = len(system.lines)
    if n_lines < 3:
        issues.append(f"Only {n_lines} lines — minimum 3 for station keeping")


*See sub-skills for full details.*
