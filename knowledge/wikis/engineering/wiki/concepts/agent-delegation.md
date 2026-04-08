---
title: "Agent Delegation"
tags: [agents, delegation, subagents, context-isolation]
sources:
  - agent-equivalence-architecture-doc
  - ai-agent-guidelines-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Agent Delegation

The practice of spawning focused sub-agents with fresh context to execute specific tasks, rather than accumulating everything in the orchestrator's context window.

## Session Rule

The provider where the session starts is the **orchestrator**. Other providers are **subagents** for that session.

- Orchestrator: can delegate and transition stages
- Subagents: execute delegated stages; cannot alter orchestration state

## Agent Equivalence

All agents (Claude, Codex, Gemini) have equivalent capabilities through shared infrastructure:

| Component | Script |
|-----------|--------|
| Session init | `scripts/agents/session.sh` |
| Work wrapper | `scripts/agents/work.sh` |
| Plan gate | `scripts/agents/plan.sh` |
| Execute gate | `scripts/agents/execute.sh` |
| Review stage | `scripts/agents/review.sh` |

## Delegation Patterns

1. **Subagent via Agent tool** -- Claude Code spawns focused workers
2. **Issue-based routing** -- GitHub issue labels route to specific agents
3. **Worktree isolation** -- git worktrees for parallel feature work
4. **CLI vs MCP** -- CLI tools use ~90K fewer tokens than MCP equivalents

## Anti-Patterns

- Burning orchestrator context on tasks a subagent could handle
- Letting subagents alter orchestration state
- Using MCP tools when CLI equivalents exist (token waste)

## Cross-References

- **Source**: [Agent Equivalence Architecture](../sources/agent-equivalence-architecture-doc.md)
- **Related concept**: [[orchestrator-worker-separation]]
- **Related concept**: [[multi-agent-parity]]
- **Related entity**: [Claude Code](../entities/claude-code.md)
