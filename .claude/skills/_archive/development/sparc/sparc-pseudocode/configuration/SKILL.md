---
name: sparc-pseudocode-configuration
description: 'Sub-skill of sparc-pseudocode: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
# sparc-pseudocode-config.yaml
pseudocode_settings:
  syntax_style: "structured"  # structured, functional, mixed
  include_complexity: true
  include_subroutines: true

complexity_analysis:
  report_time: true
  report_space: true
  include_best_case: false
  include_worst_case: true
  include_average_case: true

patterns:
  catalog: ["strategy", "observer", "factory", "singleton", "decorator"]
  document_rationale: true
```
