---
name: crossprovider codex plan-retrieval-failure-is-an-approval-blocker
description: Plan retrieval failure is an approval blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, approval-gate, retrieval]
---

Plans that cannot be accessed/read in review environments (missing local file, not on remote, or paths marked 'tbd') receive MAJOR verdict automatically. Unresolved file paths or missing GitHub presence = non-negotiable blocker, not fixable in later review rounds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
