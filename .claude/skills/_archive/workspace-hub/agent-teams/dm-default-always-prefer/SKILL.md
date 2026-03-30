---
name: agent-teams-dm-default-always-prefer
description: "Sub-skill of agent-teams: DM (default \u2014 always prefer) (+2)."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# DM (default — always prefer) (+2)

## DM (default — always prefer)

```python
SendMessage(type="message", recipient="teammate-name",
    content="Graph YAML looks good. Add edge: skill-creator → improve.",
    summary="Graph edge addition request")
```


## Broadcast (expensive — use only for critical team-wide issues)

```python
SendMessage(type="broadcast",
    content="STOP. Found a merge conflict in SKILLS_GRAPH.yaml. Hold all writes.",
    summary="Critical: stop all writes")
```

Broadcast = N messages (one per teammate). Use for genuine emergencies only.


## Plan approval (when teammate has plan_mode_required)

```python
SendMessage(type="plan_approval_response", request_id="abc-123",
    recipient="teammate", approve=True)
```
