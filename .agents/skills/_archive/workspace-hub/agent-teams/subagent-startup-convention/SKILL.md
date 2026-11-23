---
name: agent-teams-subagent-startup-convention
description: 'Sub-skill of agent-teams: Subagent startup convention (+2).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Subagent startup convention (+2)

## Subagent startup convention


Set this as the **first Bash call** in every non-trivial subagent session:

```bash
export CLAUDE_SUBAGENT=1
```


## Hook behaviour by context


| Hook | Main session | Subagent | Reason |
|------|-------------|----------|--------|
| `session-review.sh` | Runs | Runs | Writes signals to `pending-reviews/` |
| `post-task-review.sh` | Runs | Runs | Captures findings to `pending-reviews/` |
| `consume-signals.sh` | Runs | Runs | Processes signals into session-briefing |
| `improve.sh` | Runs | **Skipped** | Narrow context produces low-quality output |
| `query-quota.sh` | Runs | **Skipped** | Quota tracking is main-session only |

The shared `.claude/state/pending-reviews/` directory is the passive message
bus. Subagents write signals via the lighter hooks; the main session's Stop
drains them all via `consume-signals.sh` → `improve.sh` at session end.


## Result


Main orchestrator stays lean and interactive. User can inject messages and
redirect subagents mid-flight. Learnings accumulate in the background without
adding any overhead to the orchestrator between Task completions.
