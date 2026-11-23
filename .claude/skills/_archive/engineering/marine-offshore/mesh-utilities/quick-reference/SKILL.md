---
name: mesh-utilities-quick-reference
description: 'Sub-skill of mesh-utilities: Quick Reference.'
version: 1.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Quick Reference

## Quick Reference


### Supported Formats


| Format | Extension | Solvers | Description |
|--------|-----------|---------|-------------|
| **GDF** | `.gdf` | WAMIT, OrcaWave | Panel definition with vertices and quads/tris |
| **DAT** | `.dat` | AQWA, NEMOH | Panel mesh for BEM solvers |
| **STL** | `.stl` | Visualization | Surface triangulation (ASCII or binary) |
### Quality Thresholds


| Metric | Good | Acceptable | Warning |
|--------|------|------------|---------|
| Aspect Ratio | < 2.0 | < 3.0 | > 5.0 |
| Panel Count | 500-5000 | 100-15000 | > 20000 |
| Degenerate Panels | 0 | 0-5 | > 5 |
| Duplicate Vertices | 0 | 0-10 | > 50 |
| Normals Consistent | Yes | Yes | No |
