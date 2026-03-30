---
name: repo-structure-agent-infrastructure-rules
description: 'Sub-skill of repo-structure: Agent Infrastructure Rules.'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Agent Infrastructure Rules

## Agent Infrastructure Rules


Only ONE location for agent configuration per repo:

```
.claude/
  agents/       ← agent YAML definitions
  commands/     ← slash commands
  skills/       ← repo-local skills (if any)
  hooks/
  docs/
  settings.json
```

**Never create** `agents/` at repo root. **Never create** `.agent-os/`. These are
superseded patterns.

---
