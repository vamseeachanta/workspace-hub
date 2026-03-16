---
name: ecosystem-health-usage
description: 'Sub-skill of ecosystem-health: Usage.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Usage

## Usage


```
/ecosystem-health           — full suite, report only
/ecosystem-health --fix     — fix auto-fixable issues (encoding conversions)
/ecosystem-health --signal  — emit JSON signal for /improve consumption
```

Or spawned by the orchestrator:
```python
Task(
    subagent_type="Bash",
    description="Run ecosystem health checks",
    prompt="Run .claude/hooks/check-encoding.sh and the checks in the ecosystem-health skill. Report results.",
    run_in_background=True
)
```
