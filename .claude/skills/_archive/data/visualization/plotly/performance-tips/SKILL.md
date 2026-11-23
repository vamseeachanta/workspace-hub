---
name: plotly-performance-tips
description: 'Sub-skill of plotly: Performance Tips.'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Performance Tips

## Performance Tips


1. **Use WebGL for large datasets** - Scattergl, Scattermapbox
2. **Limit animation frames** - Keep under 50 frames
3. **Simplify traces** - Reduce number of data points for complex charts
4. **Disable hover** - For static exports: `hovermode=False`
5. **Optimize layout updates** - Batch updates when possible
