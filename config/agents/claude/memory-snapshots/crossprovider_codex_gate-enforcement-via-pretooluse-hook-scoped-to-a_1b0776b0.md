---
name: crossprovider codex gate-enforcement-via-pretooluse-hook-scoped-to-a
description: Gate enforcement via PreToolUse hook scoped to active-wrk file, not markdown
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-design, hook-architecture, enforcement]
---

WRK-1028 gate-check.py reads .claude/state/active-wrk to determine active WRK_ID, then blocks writes to stage-specific evidence artifacts (e.g., user-review-plan-draft.yaml, lifecycle HTML) unless gate predicates are met. This is custom Python logic, NOT hookify/markdown-based gates — it keeps enforcement clear and testable but requires explicit hook registration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
