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
| **Gemini** | Default adversarial reviewer | Architecture review, large-context research, high-stakes synthesis, plan & code review |

## Review Defaults

- **Three-agent adversarial review by default**: Claude, Codex, and Gemini all review plan-stage and code/artifact-stage work unless the user explicitly scopes the review lane down.
- **Claude remains the orchestrator**: Claude frames work, sequences execution, and synthesizes the combined review result.
- **Codex remains the default implementation worker** for bounded coding, tests, and refactors.
- **Gemini is no longer trigger-only** in this repository policy; it participates by default as the third adversarial reviewer because the user's stated preference is all-agent cross-review at both stages.
- Plans get adversarial review by ALL agents by default.
- Code and deliverable artifacts get adversarial review by ALL agents before completion by default.

## Optional Review Reduction Rules

A narrower review set is allowed only when the user explicitly asks for it or when one provider is unavailable.

| Reduction case | Allowed adjustment |
|----------------|--------------------|
| **User requests a faster/lighter pass** | Claude may reduce to two-agent review and document the reason |
| **Provider unavailable / quota exhausted** | Continue with remaining agents, but record the missing reviewer |
| **Purely clerical change** | Claude may waive one reviewer with explicit note in the completion summary |

## Routing Flow

```
1. Claude frames the task (context, scope, plan)
2. Claude decides execution path:
   a. Self-execute (trivial/orchestration work)
   b. Route bounded implementation to Codex (and optionally parallel workers)
3. Before completion, Claude routes review:
   a. Default: Claude + Codex + Gemini all review
   b. If one reviewer is waived, record the reason explicitly
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
2. **Routing gate** analyzes the diff and confirms all three agents (Claude, Codex, Gemini) are included in review
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
