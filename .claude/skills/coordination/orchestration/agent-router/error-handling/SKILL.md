---
name: agent-router-error-handling
description: 'Sub-skill of agent-router: Error Handling.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


| Error | Cause | Resolution |
|-------|-------|------------|
| `jq is not installed` | Missing dependency | `apt install jq` or `brew install jq` |
| `No CLI providers detected` | No agent CLIs on PATH | Install claude, codex, or gemini CLI |
| `Work item not found` | Invalid WRK-NNN ID | Check `.claude/work-queue/` for valid items |
| Budget guardrail triggered | Daily spend limit hit | Increase budget in usage JSON or wait |
