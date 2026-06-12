---
name: crossprovider codex early-return-in-shared-filtering-functions-has-u
description: Early return in shared filtering functions has unintended broad scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [control-flow, filtering-scope, shell-patterns]
---

Placing `[condition] && return` before all section-routing logic suppresses items from downstream sections (WORKING, BLOCKED, ready buckets). Filters intended for ready-to-start buckets inadvertently hide active work. Guard filters must be scoped to target section only, not early in the function.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
