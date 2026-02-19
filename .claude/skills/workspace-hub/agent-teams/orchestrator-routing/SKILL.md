---
name: orchestrator-routing
description: "Main orchestrator as lightweight router — stay responsive to user messages while subagents do heavy work; route tasks to appropriate agents based on workload"
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-02-19
wrk_ref: WRK-212
related_skills:
  - agent-teams
  - ecosystem-health
  - improve
tags:
  - orchestration
  - routing
  - agent-teams
  - responsiveness
  - delegation
platforms: [all]
capabilities: []
requires: []
see_also: []
---

# Orchestrator Routing — Main Session as Lightweight Router

The main Claude session should stay responsive to the user. When a task is
large or parallelisable, delegate to subagents rather than consuming the main
context window. This skill documents the routing pattern.

## Core Pattern

```
User message → Orchestrator (main session)
                    ↓ (route)
            Subagent A  |  Subagent B  |  Subagent C
                    ↓ (results via TaskOutput / SendMessage)
              Orchestrator summarises → User
```

The orchestrator:
1. Classifies the task (size, parallelism, domain)
2. Selects the right agent type(s)
3. Spawns with `run_in_background=True` for long tasks
4. Stays available for next user message
5. Collects results and presents summary

## When to Delegate

Delegate when ANY of these apply:
- Task will take > 5 minutes of sequential tool calls
- Task is clearly partitioned into 2-3 independent streams
- Task requires a read-only research phase that would pollute main context
- User sends a new message while task is still running (re-route remainder)

Keep in main session when:
- Task is < 5 files, < 10 min
- Task requires tight back-and-forth with user
- Task is a single WRK item with no parallelism

## Routing Decision by Task Type

| User request | Route to | Agent type |
|-------------|----------|------------|
| "Search the codebase for X" | Explore agent | `Explore` |
| "Plan WRK-NNN implementation" | Plan agent | `Plan` |
| "Run tests / execute scripts" | Bash agent | `Bash` |
| "Build WRK-205 knowledge graph" | 2-3 agents via team | `general-purpose` + `Bash` |
| "Write a skill / WRK item" | Main session | — |
| "Ecosystem health check" | Background Bash agent | `Bash` |
| "Sync all repos" | Main session (sequential) | — |

## Spawning a Background Agent

```python
result = Task(
    subagent_type="Bash",
    description="Run ecosystem health checks",
    prompt="""
    Run the ecosystem health check suite per the /ecosystem-health skill:
    1. Check git config core.hooksPath == .claude/hooks
    2. Check uv is available
    3. Run .claude/hooks/check-encoding.sh
    4. Check work queue index generates
    Report results as a markdown table.
    """,
    run_in_background=True
)
# result contains output_file path — check later with Read tool
```

After spawning, continue handling user messages. Check progress:
```python
Read(file_path=result["output_file"])
# or
Bash(command=f"tail -20 {result['output_file']}")
```

## Staying Responsive

When a background agent is running and the user sends a new message:
- **Do not wait** for the background agent to finish
- Handle the new message immediately
- Tell the user: "Background agent is working on X. Here's its progress so far: [summary]"

```
User: "While that's running, can you check WRK-205?"
Orchestrator: "Sure — background agent is still scanning 115 files.
               Meanwhile, let me check WRK-205..."
               [reads WRK-205, answers question]
               [later] "Background agent finished: [results]"
```

## Resuming Agents

Agents return an agent ID. Use it to resume rather than spawn fresh:

```python
# First call — spawns fresh
result = Task(subagent_type="general-purpose", description="Research X", prompt="...", run_in_background=True)
agent_id = result["agent_id"]

# Resume later with more context
Task(subagent_type="general-purpose", description="Continue research", prompt="...", resume=agent_id)
```

Resume when: agent needs clarification, new information arrived, task was interrupted.
Spawn fresh when: task is genuinely new, different domain, context is irrelevant.

## Context Window Management

Long tasks consume context. Route to subagents to protect main context:
- **Research tasks**: Always delegate to Explore agent — search results pollute context
- **Bulk file operations**: Delegate to Bash agent — verbose output pollutes context
- **Keep main session for**: User dialogue, synthesis, routing decisions, WRK authoring

When main context is getting long:
- Delegate any remaining bulk work to background agents
- Use /reflect or /insights to compress learnings
- Summarise subagent results rather than including raw output

## WRK Queue Integration

When user asks about pending work:
```
User: "What's pending? Pick the next thing to work on."
Orchestrator:
  1. Read .claude/work-queue/pending/ (fast, keep in main session)
  2. Identify Route A items (user-approved, no cross-review needed)
  3. If item needs research → spawn Explore agent, stay available
  4. If item is small skill authoring → do in main session
  5. If item is large (WRK-205 class) → propose team, await user approval
```

## Related

- `/agent-teams` — full team lifecycle (TeamCreate, TaskCreate, etc.)
- `/ecosystem-health` — example background agent pattern
- CLAUDE.md — `MAX_TEAMMATES=3` constraint
