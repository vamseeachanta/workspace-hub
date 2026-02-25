---
name: agent-teams
description: "Agent team protocols for workspace-hub — when to use teams, decision matrix, team lifecycle, communication patterns, and MAX_TEAMMATES=3 constraint"
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-02-19
wrk_ref: WRK-212
related_skills:
  - orchestrator-routing
  - ecosystem-health
  - improve
  - repo-sync
tags:
  - agent-teams
  - orchestration
  - protocols
  - coordination
  - parallel-agents
platforms: [all]
capabilities: []
requires: []
see_also: []
---

# Agent Teams Protocol

Workspace-hub uses Claude Code's TeamCreate/Task/SendMessage primitives for
parallel work. This skill documents when to use teams, how to run them, and
how to keep the main orchestrator responsive while subagents work.

## Core Constraint

```
MAX_TEAMMATES = 3  (set in .claude/settings.json — git-tracked)
```

Default to **fewer agents**, not more. Spawn only as many as strictly needed.
Coordination overhead grows quadratically; benefits only appear when tasks are
truly parallel and long-running.

## Decision Matrix: Team vs Sequential

| Task profile | Use team? | Rationale |
|-------------|-----------|-----------|
| < 5 files, single domain | **No** | Sequential is faster than team overhead |
| Writing WRK items / skills | **No** | Small, sequential, ~minutes each |
| 3+ independent workstreams > 20 min each | **Yes** | Parallelism pays off |
| Bulk file transforms (50+ files) | **Yes** | Bash agent per batch |
| Research + implementation (separate concerns) | **Yes** | Explore agent + Bash agent |
| Cross-repo changes (each repo independent) | **Yes** | One agent per repo |
| WRK-205 knowledge graph (115 files) | **Yes** | 3 parallel streams |

**Rule of thumb**: If you would finish faster doing it yourself than explaining
it to a teammate, do it yourself.

## Team Lifecycle

### 1. Create team
```python
TeamCreate(team_name="my-work", description="Implementing WRK-205")
```

### 2. Create tasks
```python
TaskCreate(subject="Build SKILLS_GRAPH.yaml", description="...", activeForm="Building graph YAML")
TaskCreate(subject="Script diverged canonical_ref", description="...", activeForm="Scripting canonical refs")
```

### 3. Spawn teammates
```python
Task(
    subagent_type="general-purpose",
    name="graph-builder",
    team_name="my-work",
    prompt="You are graph-builder. Check TaskList for your work..."
)
Task(
    subagent_type="Bash",
    name="script-runner",
    team_name="my-work",
    prompt="You are script-runner. Check TaskList for your work..."
)
```

### 4. Assign tasks
```python
TaskUpdate(taskId="1", owner="graph-builder", status="in_progress")
TaskUpdate(taskId="2", owner="script-runner", status="in_progress")
```

### 5. Stay responsive
While teammates work, the main orchestrator stays available for user messages.
Use `run_in_background=True` for long tasks. Check progress with `TaskList`.

### 6. Shutdown
```python
SendMessage(type="shutdown_request", recipient="graph-builder", content="Work complete")
SendMessage(type="shutdown_request", recipient="script-runner", content="Work complete")
# After both confirm shutdown:
TeamDelete()
```

## Communication Patterns

### DM (default — always prefer)
```python
SendMessage(type="message", recipient="teammate-name",
    content="Graph YAML looks good. Add edge: skill-creator → improve.",
    summary="Graph edge addition request")
```

### Broadcast (expensive — use only for critical team-wide issues)
```python
SendMessage(type="broadcast",
    content="STOP. Found a merge conflict in SKILLS_GRAPH.yaml. Hold all writes.",
    summary="Critical: stop all writes")
```

Broadcast = N messages (one per teammate). Use for genuine emergencies only.

### Plan approval (when teammate has plan_mode_required)
```python
SendMessage(type="plan_approval_response", request_id="abc-123",
    recipient="teammate", approve=True)
```

## Agent Types for Common Tasks

| Task | Best subagent_type | Why |
|------|--------------------|-----|
| File reads, searches, analysis | `Explore` | Read-only, fast |
| Writing/editing files, running scripts | `general-purpose` | Full tools |
| Shell commands only | `Bash` | Minimal overhead |
| Research + planning | `Plan` | Structured planning |

Never assign implementation work to `Explore` or `Plan` — they are read-only.

## Work Queue Integration

Teammates must follow the same WRK gate rules as the main orchestrator:
- Every task maps to a WRK item
- `plan_approved: true` before implementation
- Route B/C: `plan_reviewed: true` required

When a teammate completes a WRK deliverable:
1. `TaskUpdate(taskId=..., status="completed")`
2. `SendMessage` to orchestrator: "WRK-NNN deliverable done. Committed as <hash>."

## Hook Inheritance & Learning Capture

Subagents spawned via the Task tool are separate `claude` processes that
inherit the same `.claude/settings.json`. Stop hooks fire automatically in
each subagent — but the heavy hooks are suppressed via `CLAUDE_SUBAGENT=1`
so the main orchestrator stays light and responsive.

### Subagent startup convention

Set this as the **first Bash call** in every non-trivial subagent session:

```bash
export CLAUDE_SUBAGENT=1
```

### Hook behaviour by context

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

### Result

Main orchestrator stays lean and interactive. User can inject messages and
redirect subagents mid-flight. Learnings accumulate in the background without
adding any overhead to the orchestrator between Task completions.

## Idle State

Teammates go idle after every turn — this is normal. An idle notification
does NOT mean the teammate is done or unavailable. Send them a message to
wake them up. Do not interpret idle as failure.

## Related

- `/orchestrator-routing` — main session as lightweight router pattern
- `/ecosystem-health` — example of background parallel agent
- `CLAUDE.md` — `MAX_TEAMMATES=3` is set here, git-tracked
