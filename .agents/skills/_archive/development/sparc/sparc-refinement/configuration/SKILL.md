---
name: sparc-refinement-configuration
description: 'Sub-skill of sparc-refinement: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
# sparc-refinement-config.yaml
tdd_settings:
  cycle: "red-green-refactor"
  coverage_threshold: 80
  test_framework: "jest"

refactoring:
  max_complexity: 10
  max_file_lines: 500
  max_function_lines: 30

performance:
  benchmark_enabled: true
  profiling_enabled: true

quality_metrics:
  code_coverage: 80
  cyclomatic_complexity: 10
  maintainability_index: 20
```
