# Subagent Context Isolation Convention

> Issue: #1427 | Date: 2026-04-01
> Parent: Minimal Harness Architecture (#1514)

---

## Principle

Every WRK execution stage runs in a **fresh 200K context** via subagent dispatch.
The orchestrator coordinates but does not execute. This prevents:

- Context pollution from prior stages bleeding into execution
- Runaway tool-call loops from accumulated state
- Token budget exhaustion on long multi-phase work

## When to Use Subagents

| Stage | Subagent? | Rationale |
|-------|-----------|-----------|
| **Planning** | Yes (gsd-planner) | Plans need focused context on scope, not execution history |
| **Execution** | Yes (gsd-executor) | Each plan gets fresh context with only its PLAN.md + source files |
| **Verification** | Yes (gsd-verifier) | Verifiers must see the result, not the process |
| **Review** | Yes (Codex/Gemini) | Cross-provider review needs unbiased fresh context |
| **Research** | Yes (gsd-phase-researcher) | Research benefits from full context budget for source material |
| **Triage/coordination** | No — orchestrator | Lightweight coordination stays in the main session |
| **Simple fixes** | No — inline | Single-file bug fixes don't justify subagent overhead |

## Context Budget Rule

```
Orchestrator: ~15% of context budget (coordination, routing, status)
Subagent:     100% fresh context per spawn (full 200K for the task)
```

The orchestrator must stay lean. If the orchestrator is consuming >20% of context
on task details, that work should be delegated to a subagent.

## Registered Agent Types

All agents live in `.claude/agents/`. Use exact names:

| Agent | Role |
|-------|------|
| gsd-executor | Execute plan tasks, atomic commits, SUMMARY.md |
| gsd-verifier | Verify phase completion, quality gates |
| gsd-planner | Create detailed plans from phase scope |
| gsd-phase-researcher | Research technical approaches |
| gsd-plan-checker | Review plan quality pre-execution |
| gsd-debugger | Diagnose and fix issues |
| gsd-codebase-mapper | Map project structure and dependencies |
| gsd-integration-checker | Cross-phase integration checks |
| gsd-nyquist-auditor | Verification coverage validation |
| gsd-ui-researcher | UI/UX research |
| gsd-ui-checker | UI implementation review |
| gsd-ui-auditor | UI vs. design audit |

## Dispatch Patterns

### Claude Code
```
Task(subagent_type="gsd-executor", prompt="Execute PLAN.md at <path>")
```

### Codex
```
spawn_agent(agent_type="gsd-executor", message="Execute PLAN.md at <path>")
```

### Fallback (no subagent support)
Sequential inline execution: read and follow the plan directly.
Only use this when the runtime cannot spawn subagents.

## Anti-Patterns

1. **Orchestrator doing execution work.** If the orchestrator is writing code,
   running tests, or making commits — it should have spawned a subagent.

2. **Passing accumulated context to subagents.** Subagents load their own
   context from files (PLAN.md, STATE.md, source code). Do not serialize
   orchestrator state into the subagent prompt.

3. **Chaining subagents.** Subagents should not spawn their own subagents.
   If a task needs sub-delegation, the orchestrator should manage the fan-out.

4. **Skipping subagents for "quick" multi-file changes.** If the change
   touches 3+ files across different modules, use a subagent.

## Verification

To check that this convention is followed:
- Tool-call ceiling (`.claude/hooks/tool-call-ceiling.sh`) detects sessions
  where the orchestrator is doing too much work directly.
- Session-tool-summary signals track per-session tool call counts.
- High-churn sessions (500+ calls) should be investigated for convention violations.
