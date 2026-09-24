---
name: crossprovider codex parallel-pr-scope-must-be-explicitly-conditional
description: Parallel PR scope must be explicitly conditional or self-contained
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, planning]
---

When a plan cites work in a parallel PR, either explicitly mark scope as conditional on that PR merging ('after PR #NNN'), or replicate the relevant scope into the current plan. Parallel PRs may not merge as expected; plans that silently assume their content block on upstream failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
