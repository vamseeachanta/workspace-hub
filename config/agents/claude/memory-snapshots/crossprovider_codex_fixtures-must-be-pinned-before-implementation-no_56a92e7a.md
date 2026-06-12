---
name: crossprovider codex fixtures-must-be-pinned-before-implementation-no
description: Fixtures must be pinned before implementation; no 'adjust if needed'
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, tdd, plan, scope]
---

Plans that defer fixture layout or test expectations to implementation time (`'verify/adjust if needed'`) hide critical design decisions until too late. Pin fixtures exactly before Phase 1 TDD; use 'Fixture is pinned; no adjustment' language to prevent scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
