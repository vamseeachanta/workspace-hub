---
name: crossprovider codex enforcement-scope-must-match-cited-problem-domai
description: Enforcement scope must match cited problem domains
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-gates, scope-coverage, acceptance-criteria]
---

Enforcement rules that scan only narrow scopes (e.g., scripts/ config/) hide regressions when the issue cites broader surfaces (e.g., .claude/skills/ agent-library/). Scope definitions must explicitly cover all surfaces mentioned in acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
