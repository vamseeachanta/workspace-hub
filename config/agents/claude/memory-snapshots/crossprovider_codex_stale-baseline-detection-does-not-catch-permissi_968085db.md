---
name: crossprovider codex stale-baseline-detection-does-not-catch-permissi
description: Stale-baseline detection does not catch permissive allow-token false negatives
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [baseline-maintenance, allow-token-scope, false-negative-class, orthogonal-checks]
---

A guard can correctly report zero stale baseline entries but still have false negatives if allow-token logic is too permissive. workspace-hub #3060: script correctly reported `0 STALE baseline entries` but line-level allow-token check still bypassed model-ID validation. Stale checks and allow-token scopes must be validated independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
