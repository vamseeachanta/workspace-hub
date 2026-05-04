---
name: orcaflex-post-processing-complete-post-processing-configuration
description: 'Sub-skill of orcaflex-post-processing: Complete Post-Processing Configuration
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Complete Post-Processing Configuration (+1)

## Complete Post-Processing Configuration


```yaml
basename: mooring_analysis

orcaflex:
  postprocess:
    # Summary statistics for all key variables
    summary:
      flag: true
      variables:
        - object: "Line1"

*See sub-skills for full details.*

## Minimal Quick Summary


```yaml
orcaflex:
  postprocess:
    summary:
      flag: true
      output_format: csv
      output_path: "results/quick_summary.csv"
```
