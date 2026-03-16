---
name: orcawave-mesh-generation-panel-quality-thresholds
description: 'Sub-skill of orcawave-mesh-generation: Panel Quality Thresholds (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Panel Quality Thresholds (+1)

## Panel Quality Thresholds


| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Aspect Ratio | < 2.0 | < 3.0 | < 5.0 | >= 5.0 |
| Skewness | < 0.3 | < 0.5 | < 0.7 | >= 0.7 |
| Panel Count | 2000-4000 | 1000-5000 | 500-8000 | < 500 or > 10000 |
| Quality Score | > 0.9 | > 0.7 | > 0.5 | <= 0.5 |

## Validation Checks


```python
from digitalmodel.diffraction.geometry_quality import GeometryQualityChecker

# Initialize checker
checker = GeometryQualityChecker()

# Run all quality checks
results = checker.validate(
    mesh_file="geometry/hull.gdf",
    checks=[

*See sub-skills for full details.*
