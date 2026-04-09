---
name: cross-review-policy
description: Actionable review routing policy — which agent reviews which agent's work, default three-agent adversarial review
version: 1.0.0
category: coordination
tags: [review, routing, cross-review, governance]
related_skills:
  - workflow-compliance-audit
  - session-corpus-audit
---

# Cross-Review Policy

Actionable enforcement of the AI Review Routing Policy (`docs/standards/AI_REVIEW_ROUTING_POLICY.md`).

## Provider Roles

| Provider | Role | Scope |
|----------|------|-------|
| **Claude Code** | Default orchestrator | Task framing, planning, routing, repo-facing workflow |
| **Codex** | Default coding worker & adversarial reviewer | Bounded implementation, test writing, refactors, diff review |
| **Gemini** | Default adversarial reviewer | Architecture review, large-context research, plan & code review |

## Default: Three-Agent Adversarial Review

All plan-stage and code/artifact-stage work gets reviewed by ALL three agents unless the user explicitly scopes down.

### Plan review
1. Claude frames the plan
2. Codex reviews for implementation feasibility
3. Gemini reviews for architecture and scope

### Code review
1. Implementation agent produces the diff
2. Two other agents review independently
3. Claude synthesizes the combined review result

## Allowed Reductions

A narrower review is allowed ONLY when:

| Condition | Allowed adjustment |
|-----------|--------------------|
| User explicitly requests faster/lighter pass | Reduce to two-agent, document reason |
| Provider unavailable / quota exhausted | Continue with remaining, record missing reviewer |
| Purely clerical change (typo, comment) | Waive one reviewer with explicit note |

## Enforcement

- The pre-push review gate (`scripts/enforcement/require-review-on-push.sh`) checks for review markers
- Cross-review hook: `.claude/hooks/cross-review-gate.sh`
- Compliance tracked by: `scripts/enforcement/compliance-dashboard.sh`

## When to invoke this skill
- Before completing any implementation task
- Before pushing code to main
- When deciding review routing for a new task
