---
name: yaml-workflow-executor
description: Execute configuration-driven analysis workflows from YAML files. Use
  for running analysis pipelines, data processing tasks, and automation workflows
  defined in YAML configuration.
type: reference
version: 1.1.0
category: development
related_skills:
- data-pipeline-processor
- engineering-report-generator
- parallel-file-processor
capabilities: []
requires: []
tags: []
---

# Yaml Workflow Executor

## Quick Start

```yaml
# config/workflows/analysis.yaml
task: analyze_data

input:
  data_path: data/raw/measurements.csv

output:
  results_path: data/results/analysis.json

parameters:
  filter_column: status
  filter_value: active
```

```python
from workflow_executor import execute_workflow

# Execute workflow
result = execute_workflow("config/workflows/analysis.yaml")
print(f"Status: {result['status']}")
```

```bash
# CLI execution
python -m workflow_executor config/workflows/analysis.yaml --verbose
```

## When to Use

- Running analysis defined in YAML configuration files
- Executing data processing pipelines from config
- Automating repetitive tasks with parameterized configs
- Building reproducible workflows
- Processing multiple scenarios from config variations

## Related Skills

- [data-pipeline-processor](../data-pipeline-processor/SKILL.md) - Data transformation
- [engineering-report-generator](../engineering-report-generator/SKILL.md) - Report generation
- [parallel-file-processor](../parallel-file-processor/SKILL.md) - Batch file processing

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Error Handling, Metrics, Execution Checklist, additional examples
- **1.0.0** (2024-10-15): Initial release with WorkflowConfig, WorkflowRouter, CLI integration

## Sub-Skills

- [Example 1: Run Analysis (+3)](example-1-run-analysis/SKILL.md)
- [Do (+4)](do/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Core Pattern](core-pattern/SKILL.md)
- [Configuration Loader (+3)](configuration-loader/SKILL.md)
- [Basic Structure (+3)](basic-structure/SKILL.md)
- [Command-Line Interface (+1)](command-line-interface/SKILL.md)
