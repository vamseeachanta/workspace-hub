---
name: crossprovider codex red-only-scope-forbids-implementation-synthesis-
description: RED-only scope forbids implementation synthesis; import-time failures are intentional
metadata:
  type: reference
  source: codex
  bridged: 2026-08-05
  tags: [tdd, red-wave, scope-discipline]
---

RED-wave tasks that forbid source changes are binding. Import-time collection failures (missing modules) are intentional RED state, not a blocker to fix. Do not synthesize implementation to make tests collect; wait for the GREEN-wave authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
