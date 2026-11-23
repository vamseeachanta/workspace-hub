---
name: fe-analyst-plot-types-per-section
description: 'Sub-skill of fe-analyst: Plot Types Per Section.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Plot Types Per Section

## Plot Types Per Section


| Section | Plot Type | Plotly Trace |
|---|---|---|
| Geometry | 3D line profile (x,y,z) | `go.Scatter3d` |
| Geometry | 2D vertical profile (arc length vs. z) | `go.Scatter` |
| Mesh | Segment length distribution | `go.Bar` |
| Mesh | Adjacent ratio heatmap along arc | `go.Scatter` with color |
| Materials | Section property table | `go.Table` |
| BC | 3D model with BC markers | `go.Scatter3d` + annotations |
| Results | Time history (Te, M, z) | `go.Scatter` (time on x) |
| Results | Envelope (max/min vs. arc length) | `go.Scatter` with fill |
| Results | Statistical summary table | `go.Table` |
| Design Checks | Utilization bar chart | `go.Bar` with threshold line |
| Fatigue | Damage vs. arc length | `go.Scatter` |

---
