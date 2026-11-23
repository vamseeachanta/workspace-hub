---
name: orcawave-aqwa-benchmark-common-causes-of-deviation
description: 'Sub-skill of orcawave-aqwa-benchmark: Common Causes of Deviation (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Causes of Deviation (+1)

## Common Causes of Deviation


| Issue | Typical Deviation | Solution |
|-------|-------------------|----------|
| Mesh differences | 5-15% | Use similar panel counts |
| Coordinate systems | Phase shift | Verify origin/orientation |
| Frequency resolution | Variable | Interpolate to common frequencies |
| Irregular frequency removal | 10-20% at specific freqs | Check lid method settings |
| Viscous damping | Roll/pitch deviation | Ensure consistent settings |

## Diagnostic Workflow


```python
from digitalmodel.diffraction.comparison_framework import DiagnosticAnalyzer

# Initialize diagnostic analyzer
diagnostic = DiagnosticAnalyzer()

# Run diagnostics
issues = diagnostic.identify_issues(
    aqwa_results=aqwa_data,
    orcawave_results=orcawave_data,

*See sub-skills for full details.*
