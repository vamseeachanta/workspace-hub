---
name: development-workflow-orchestrator-integration-flow
description: 'Sub-skill of development-workflow-orchestrator: Integration Flow.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Integration Flow

## Integration Flow


```
MAIN FUNCTION run_pipeline(config_file):
  1. config = LOAD_YAML_CONFIG(config_file)
  2. data = DataLoader.load_csv(config.input.path, config)
  3. stats = StatisticsCalculator.calculate_statistics(data, config)
  4. plot = VisualizationGenerator.generate_interactive_plot(data, stats, config)
  5. report = ReportBuilder.generate_html(data, stats, plot, config)

  IF config.output.export_json:
    EXPORT_JSON(stats, output_path)

  RETURN report_path
```
