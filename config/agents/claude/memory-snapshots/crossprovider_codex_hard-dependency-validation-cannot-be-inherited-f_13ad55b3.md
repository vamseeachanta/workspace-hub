---
name: crossprovider codex hard-dependency-validation-cannot-be-inherited-f
description: Hard dependency validation cannot be inherited from prior session evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hard-dependencies, gate-validation, transitive-assumptions]
---

Dependent issues' approval state (open + labeled) is not transitive across sessions. Each session must independently validate current state of blocking issues; prior evidence can become stale if dependencies were modified after. Fresh validation is required before deciding implementation is unblocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
