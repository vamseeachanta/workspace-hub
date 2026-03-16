---
name: ecosystem-health-when-to-run
description: 'Sub-skill of ecosystem-health: When to Run.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# When to Run

## When to Run


| Trigger | Who spawns it |
|---------|---------------|
| End of `/repo-sync` (Phase 5) | repo-sync skill |
| Session exit | `ecosystem-health-check.sh` stop hook |
| Manual | User runs `/ecosystem-health` |
| After bulk file operations | Orchestrator spawns as parallel agent |
