---
name: planning-goal-configuration
description: 'Sub-skill of planning-goal: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
goap_config:
  planning:
    algorithm: a_star
    max_depth: 50
    timeout_ms: 5000

  execution:
    mode: adaptive  # focused | closed | open
    parallel_actions: true
    replan_on_failure: true

  monitoring:
    ooda_loop: true
    observe_interval_ms: 1000

  cost_weights:
    time: 1.0
    risk: 2.0
    resource: 1.5
```
