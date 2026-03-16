---
name: development-workflow-orchestrator-module-visualizationgenerator
description: 'Sub-skill of development-workflow-orchestrator: Module: VisualizationGenerator.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Module: VisualizationGenerator

## Module: VisualizationGenerator


```
FUNCTION generate_interactive_plot(data, statistics, config):
  # MANDATORY: Use Plotly for interactive visualization
  # NO static matplotlib exports allowed

  plot = CREATE_PLOTLY_FIGURE()

  ADD_SCATTER(plot, data.x, data.y)
  ADD_HOVER_TOOLTIPS(plot, data)
  ADD_STATISTICS_ANNOTATIONS(plot, statistics)

  CONFIGURE_LAYOUT(plot, responsive=true)

  RETURN plot
```
