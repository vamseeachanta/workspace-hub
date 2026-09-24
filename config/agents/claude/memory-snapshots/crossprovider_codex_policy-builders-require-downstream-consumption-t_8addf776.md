---
name: crossprovider codex policy-builders-require-downstream-consumption-t
description: Policy builders require downstream consumption to be effective
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [implementation-completeness, verification, control-flow]
---

A correct policy builder (JSON, validation, test coverage) is not sufficient implementation if the policy is never actually validated/consumed in the code path that enforces it. Verify the policy artifact is read and enforced before traversal/ingest logic, not just written and tested in isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
