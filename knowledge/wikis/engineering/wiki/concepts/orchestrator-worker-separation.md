---
title: "Orchestrator-Worker Separation"
tags: [methodology, orchestrator, worker, context-isolation, delegation]
sources:
  - compound-engineering-methodology
  - agent-equivalence-architecture-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Orchestrator-Worker Separation

Single agent handling everything leads to context overload. The agent loses the plan, forgets constraints, and produces inconsistent results. The solution: one orchestrator maintains the plan; workers execute focused tasks with fresh context.

## The Problem

```
Single Agent Session (4+ hours)
  Hour 1: Plans the feature (reads 15 files, creates plan)
  Hour 2: Starts implementing (context window 40% full)
  Hour 3: More implementation (context 70% full, plan truncated)
  Hour 4: Reviews own work (plan forgotten, drift)
```

## The Solution

```
Orchestrator (maintains plan, delegates, verifies)
  +-- Worker 1: Fresh context, focused on Task A
  +-- Worker 2: Fresh context, focused on Task B
  +-- Worker 3: Fresh context, focused on Task C
```

## Benefits

| Problem | Single Agent | Orchestrator-Worker |
|---------|-------------|---------------------|
| Context overload | Accumulates | Each worker starts fresh |
| Plan drift | Forgets the plan | Orchestrator maintains it |
| Parallel work | Sequential | Workers run in parallel |
| Self-review bias | Same agent | Different reviewer |
| Failure recovery | Lost context | Restart worker with same context |

## Implementation Patterns

1. **Subagent delegation** -- Hermes `delegate_task`, Claude Code `Agent` tool
2. **GitHub issue routing** -- issues with agent-specific labels
3. **Worktree isolation** -- Claude Code git worktrees for parallel feature work

## Design Principles

- **Orchestrator context is working memory** -- never wipe it
- **Delegate down**: if a subagent can do it, spawn it
- **Domain modules are the moat**: routing layer is commodity, protect domain logic

## Cross-References

- **Source**: [Compound Engineering Methodology](../sources/compound-engineering-methodology.md)
- **Source**: [Agent Equivalence Architecture](../sources/agent-equivalence-architecture-doc.md)
- **Related concept**: [[compound-engineering]]
- **Related concept**: [[agent-delegation]]
- **Related entity**: [Claude Code](../entities/claude-code.md)
