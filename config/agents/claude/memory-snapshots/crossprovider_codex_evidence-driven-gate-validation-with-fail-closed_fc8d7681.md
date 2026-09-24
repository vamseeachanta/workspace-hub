---
name: crossprovider codex evidence-driven-gate-validation-with-fail-closed
description: Evidence-driven gate validation with fail-closed semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-driven, fail-closed, audit-trail]
---

Gate state can be enforced via YAML evidence artifacts with required identity fields (timestamp, reviewer, approval decision, commit reference). Missing or mismatched evidence (e.g., approved commit ≠ published commit) must fail closed, not degrade silently. This pattern decouples gate logic from ambient policy text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
