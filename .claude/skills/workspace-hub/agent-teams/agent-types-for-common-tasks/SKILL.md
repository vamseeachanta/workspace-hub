---
name: agent-teams-agent-types-for-common-tasks
description: 'Sub-skill of agent-teams: Agent Types for Common Tasks.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Agent Types for Common Tasks

## Agent Types for Common Tasks


| Task | Best subagent_type | Why |
|------|--------------------|-----|
| File reads, searches, analysis | `Explore` | Read-only, fast |
| Writing/editing files, running scripts | `general-purpose` | Full tools |
| Shell commands only | `Bash` | Minimal overhead |
| Research + planning | `Plan` | Structured planning |

Never assign implementation work to `Explore` or `Plan` — they are read-only.
