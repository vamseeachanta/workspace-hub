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

This policy is enforced at **Level 3 — Hook** (strongest). Promotion history:

| Level | Status | Artifact |
|-------|--------|----------|
| Level 0 — Prose | ✅ Done (2026-03-31) | This document |
| Level 1 — Micro-skill | ✅ Done | Routing reminders surfaced at review stage entry |
| Level 2 — Script | ✅ Done (2026-04-01) | `scripts/ai/review_routing_gate.py` — analyzes diffs, recommends reviewers |
| Level 3 — Hook | ✅ Done (2026-04-01) | `.claude/hooks/cross-review-gate.sh` — blocks PR creation without review, surfaces routing recommendation |

### How it works

1. **On `gh pr create`**: The PreToolUse hook runs the routing gate against the current diff
2. **Routing gate** analyzes the diff for Gemini trigger conditions (see above)
3. **Block decision**: If no cross-review evidence exists, the hook blocks with a message including recommended reviewers
4. **Pass-through**: If review evidence exists, the hook logs the routing recommendation to stderr for visibility

### Running manually

```bash
# Analyze a diff for routing recommendation:
git diff main...HEAD | scripts/ai/review-routing-gate.sh --stdin

# Audit overall compliance:
scripts/ai/verify-adversarial-reviews.sh --days 30 --verbose

# Check a specific PR:
uv run python scripts/ai/review_routing_gate.py --pr 42
```

See [patterns.md](../../.claude/rules/patterns.md) for the enforcement gradient.
