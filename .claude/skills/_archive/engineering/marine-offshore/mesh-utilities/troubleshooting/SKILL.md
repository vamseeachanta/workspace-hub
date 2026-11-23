---
name: mesh-utilities-troubleshooting
description: 'Sub-skill of mesh-utilities: Troubleshooting.'
version: 1.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Troubleshooting

## Troubleshooting


| Issue | Cause | Solution |
|-------|-------|----------|
| High aspect ratio | Long thin panels | Remesh with more uniform element size |
| Degenerate panels | Collapsed vertices | Clean mesh, remove zero-area panels |
| Inconsistent normals | Mixed orientation | Flip normals to all point outward |
| Not watertight | Gaps/holes in mesh | Check model, close holes |
| Too many panels | Over-refined mesh | Coarsen or regenerate with larger element size |
| Wrong format | Solver incompatibility | Convert to solver-required format |
