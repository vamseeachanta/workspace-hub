---
name: agent-teams-work-queue-integration
description: 'Sub-skill of agent-teams: Work Queue Integration.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Work Queue Integration

## Work Queue Integration


Teammates must follow the same WRK gate rules as the main orchestrator:
- Every task maps to a WRK item
- `plan_approved: true` before implementation
- Route B/C: `plan_reviewed: true` required

When a teammate completes a WRK deliverable:
1. `TaskUpdate(taskId=..., status="completed")`
2. `SendMessage` to orchestrator: "WRK-NNN deliverable done. Committed as <hash>."
