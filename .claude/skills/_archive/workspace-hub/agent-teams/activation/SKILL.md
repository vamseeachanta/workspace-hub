---
name: agent-teams-activation
description: 'Sub-skill of agent-teams: Activation.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Activation

## Activation


Agent teams are **disabled globally by default** and must be explicitly
enabled per workspace:

```json
// .claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "MAX_TEAMMATES": "10"
  }
}
```

This workspace has teams enabled. New workspaces start with teams OFF.
