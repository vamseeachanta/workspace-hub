# AI Review Routing Policy

> Explicit routing rules for AI-assisted review in workspace-hub repositories.
>
> Issue: #1515 | Parent: #1514 | Date: 2026-03-31
> Architecture decision: [Minimal Harness Operating Model](../modules/ai/MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md)
> Control-plane contract: [CONTROL_PLANE_CONTRACT.md](CONTROL_PLANE_CONTRACT.md)

---

## Provider Roles

| Provider | Role | Scope |
|----------|------|-------|
| **Claude Code** | Default orchestrator | Task framing, planning, routing decisions, repo-facing workflow |
| **Codex** | Default coding worker & adversarial reviewer | Bounded implementation, test writing, refactors, diff review |
| **Gemini** | Narrow third-lane reviewer | Architecture review, large-context research, high-stakes synthesis |

## Review Defaults

- **Two-provider review by default**: Claude produces the plan or artifact; Codex provides adversarial review.
- **Three-provider review only when justified**: Gemini is added as a third reviewer under specific trigger conditions (see below).
- Plans get adversarial review by default for non-trivial work.
- Code and deliverable artifacts get adversarial review before completion when the change is risky, architectural, cross-cutting, or hard to verify locally.

## Gemini Third-Lane Trigger Rules

Add Gemini as a third reviewer when **any** of these conditions apply:

| Trigger | Rationale |
|---------|-----------|
| **Architecture-heavy change** | Cross-module or cross-repo structural change that benefits from an independent architectural perspective |
| **Research-heavy task** | Task requires synthesizing multiple external sources, standards, or large documents where Gemini's context window adds material value |
| **Ambiguous requirements** | Requirements are underspecified or contested — a third independent interpretation reduces risk |
| **High-stakes delivery** | Change affects production systems, security boundaries, data integrity, or compliance — cost of error justifies extra review |
| **Context saturation** | Claude's context is already saturated with task material — Gemini can process overflow without losing fidelity |

**Do not add Gemini** for routine implementation, standard refactors, test additions, or documentation-only changes.

## Routing Flow

```
1. Claude frames the task (context, scope, plan)
2. Claude decides execution path:
   a. Self-execute (trivial/orchestration work)
   b. Route to Codex (bounded implementation, tests, refactors)
3. Before completion, Claude routes review:
   a. Default: Codex reviews (two-provider)
   b. If trigger condition met: Codex + Gemini review (three-provider)
4. Resolve review findings before marking complete
```

## Legacy Surfaces

The following directories are **legacy** and must not drive new architecture decisions:

| Path | Status | Reference |
|------|--------|-----------|
| `.hive-mind/` | Legacy — do not extend | See `LEGACY.md` in directory |
| `.swarm/` | Legacy — do not extend | See `LEGACY.md` in directory |
| `.SLASH_COMMAND_ECOSYSTEM/` | Legacy — do not extend | See `LEGACY.md` in directory |

New workflow logic belongs in `.claude/` (skills, rules, hooks) with thin adapters in `.codex/` and `.gemini/` per the [Control-Plane Contract](CONTROL_PLANE_CONTRACT.md).

## Enforcement

This policy is currently **advisory** (Level 0 — Prose). Promotion path:

- Level 1: Micro-skill that surfaces routing reminders at review stage entry
- Level 2: Script that checks PR metadata for review-provider annotations
- Level 3: Hook that blocks completion without documented review provider

See [patterns.md](../../.claude/rules/patterns.md) for the enforcement gradient.
