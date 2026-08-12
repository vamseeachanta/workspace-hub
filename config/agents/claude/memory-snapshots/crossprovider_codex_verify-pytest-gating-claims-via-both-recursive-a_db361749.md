---
name: crossprovider codex verify-pytest-gating-claims-via-both-recursive-a
description: Verify pytest gating claims via both recursive and explicit-path invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-08-11
  tags: [pytest, verification, gating]
---

Plans claiming 'no recursive collection' must be tested under both `pytest .` (recursive) and `pytest <explicit-path>` scenarios; conftest-based collection guards protect only the recursive case. Incomplete testing masks leaky behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
