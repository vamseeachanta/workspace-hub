---
name: crossprovider codex nullability-in-registry-validation-can-bypass-co
description: Nullability in registry validation can bypass completeness checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, validation, architecture]
---

If records carry optional/null fields like `connection: null`, validation loops that skip null records leave those records unvalidated. Registry completeness and validation must be enforced for all rows regardless of nullability; nullability does not exempt validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
