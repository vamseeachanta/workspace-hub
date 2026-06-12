---
name: crossprovider codex codex-plan-review-verdicts-render-as-json
description: Codex plan review verdicts render as JSON
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex, tooling, review-output]
---

Codex outputs plan review verdicts as `{"verdict":"MAJOR", "summary":"...", "issues_found":[...]}` JSON structures, not markdown. Relevant for cross-provider review aggregation (Claude renders markdown) and Codex-specific parsing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
