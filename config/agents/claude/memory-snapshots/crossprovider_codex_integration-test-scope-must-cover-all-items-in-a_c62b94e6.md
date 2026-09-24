---
name: crossprovider codex integration-test-scope-must-cover-all-items-in-a
description: Integration test scope must cover all items in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, tdd, scope]
---

If AC requires N repos/features/modes, integration tests should touch all N. Single-target testing (e.g., only the smallest repo) misses heterogeneous failure modes and leaves larger targets unvalidated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
