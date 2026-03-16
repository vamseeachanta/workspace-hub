---
name: metocean-visualizer-output-formats
description: 'Sub-skill of metocean-visualizer: Output Formats.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Output Formats

## Output Formats


| Format | Use Case | Method |
|--------|----------|--------|
| Interactive HTML | Web dashboards, reports | `fig.write_html()` |
| PNG/SVG | Static reports, publications | `fig.write_image()` |
| JSON | Data interchange | `fig.to_json()` |
| Dashboard HTML | Multi-panel views | `make_subplots()` |
