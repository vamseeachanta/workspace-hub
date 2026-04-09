---
name: cross-review-policy
description: Actionable skill that enforces the AI review routing policy. Determines which agent reviews which agent's work, enforces three-agent adversarial review by default, and provides the routing flow for plan and code review stages.
version: 1.0.0
category: coordination
type: skill
trigger: review-stage
auto_execute: false
tools:
  - Bash
  - Read
tags:
  - review
  - governance
  - cross-review
  - routing
  - enforcement
related_skills:
  - enforcement-audit-and-upgrade
  - session-start-routine
issue_ref: "#2057"
---

# Cross-Review Policy

Actionable skill that enforces the AI review routing policy defined in
`docs/standards/AI_REVIEW_ROUTING_POLICY.md`. Determines which agent reviews
which agent's work and enforces three-agent adversarial review by default.

## Provider Roles

| Provider | Role | Scope |
|----------|------|-------|
| Claude Code | Default orchestrator | Task framing, planning, routing decisions, repo-facing workflow |
| Codex | Default coding worker and adversarial reviewer | Bounded implementation, test writing, refactors, diff review |
| Gemini | Default adversarial reviewer | Architecture review, large-context research, plan and code review |

## Default: Three-Agent Adversarial Review

All three providers review by default at both stages:

1. **Plan review stage**: Claude + Codex + Gemini review plans before execution
2. **Code/artifact review stage**: Claude + Codex + Gemini review deliverables before completion

## Routing Flow

```
1. Claude frames the task (context, scope, plan)
2. Claude decides execution path:
   a. Self-execute (trivial/orchestration work)
   b. Route bounded implementation to Codex
3. Before completion, Claude routes review:
   a. Default: all three providers review
   b. If one reviewer is waived, record the reason explicitly
4. Resolve review findings before marking complete
```

## Review Routing Matrix

### Who Reviews Whom

| Author | Reviewer 1 | Reviewer 2 | Reviewer 3 |
|--------|-----------|-----------|-----------|
| Claude | Codex | Gemini | Claude (self-review) |
| Codex | Claude | Gemini | - |
| Gemini | Claude | Codex | - |
| Multi-agent | All three | - | - |

### Review Invocation Commands

**Invoke Codex review:**
```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
# Generate diff for review
DIFF_FILE="/tmp/review-diff-$(date +%s).patch"
git diff main...HEAD > "$DIFF_FILE"
echo "Diff written to $DIFF_FILE for Codex review"
# Codex reviews via codex-cli or the rescue subagent
```

**Invoke Gemini review:**
```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
# Gemini reviews via Hermes router
echo "Route to Gemini via: h-router-gemini -t terminal,file"
```

**Check review gate status:**
```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
# The cross-review gate blocks PR creation without evidence of review
bash scripts/enforcement/require-review-on-push.sh --check 2>&1 || true
```

## Reduction Rules

A narrower review set is allowed only when explicitly requested:

| Condition | Allowed Adjustment |
|-----------|-------------------|
| User requests faster/lighter pass | Claude may reduce to two-agent review, documenting the reason |
| Provider unavailable or quota exhausted | Continue with remaining agents, record the missing reviewer |
| Purely clerical change | Claude may waive one reviewer with explicit note |

## Enforcement Levels

This policy is enforced at Level 3 (Hook) — the strongest tier:

| Level | Status | Artifact |
|-------|--------|----------|
| Level 0 - Prose | Done | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
| Level 1 - Micro-skill | Done | This skill file |
| Level 2 - Script | Done | `scripts/ai/review_routing_gate.py` |
| Level 3 - Hook | Done | `.claude/hooks/cross-review-gate.sh` |

## Verification Commands

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Analyze current diff for routing recommendation
git diff main...HEAD | bash scripts/ai/review-routing-gate.sh --stdin 2>&1 || true

# Audit overall compliance (last 30 days)
bash scripts/ai/verify-adversarial-reviews.sh --days 30 --verbose 2>&1 || true
```

## Completion Checklist

Before marking any task complete, verify:

- [ ] Plan was reviewed by all three agents (or reduction documented)
- [ ] Code was reviewed by all three agents (or reduction documented)
- [ ] Review findings were resolved or explicitly acknowledged
- [ ] Issue comment includes review summary with verdict per agent
- [ ] If any reviewer was waived, the reason is recorded in the commit or PR

## Red Flags

These situations indicate the review policy is being bypassed:

- PR created without cross-review evidence in the description
- Review summary says "LGTM" without specific findings
- Only one agent reviewed (silent omission of others)
- Review conducted by the same agent that authored the code
- `SKIP_REVIEW_GATE=1` used without documented justification
