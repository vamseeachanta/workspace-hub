---
name: planning-code-goal-configuration
description: 'Sub-skill of planning-code-goal: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
sparc_goap_config:
  phases:
    specification:
      timeout_minutes: 30

    architecture:
      timeout_minutes: 45

    refinement:
      timeout_minutes: 120

    completion:
      timeout_minutes: 60

  metrics:
    test_coverage_target: 80
    performance_target: "A"
    max_tech_debt_hours: 40

  risk_assessment:
    technical_weight: 0.3
    timeline_weight: 0.3
    quality_weight: 0.2
    security_weight: 0.2
```
