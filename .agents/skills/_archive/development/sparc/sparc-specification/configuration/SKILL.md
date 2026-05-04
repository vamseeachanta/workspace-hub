---
name: sparc-specification-configuration
description: 'Sub-skill of sparc-specification: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
# sparc-specification-config.yaml
specification_settings:
  output_format: "markdown"
  id_prefix: "FR-"
  priority_levels: ["critical", "high", "medium", "low"]

templates:
  requirements_doc: ".agent-os/specs/{spec-name}/spec.md"
  use_cases: ".agent-os/specs/{spec-name}/sub-specs/use-cases.md"

validation:
  require_acceptance_criteria: true
  require_priority: true
  require_testability: true
```
