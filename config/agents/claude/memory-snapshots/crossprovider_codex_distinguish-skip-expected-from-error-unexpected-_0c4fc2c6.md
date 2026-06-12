---
name: crossprovider codex distinguish-skip-expected-from-error-unexpected-
description: Distinguish skip (expected) from error (unexpected) in structured output schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, error-handling]
---

When a repo cannot be audited, explicitly label the reason: `skip_reason=no_pyproject` (expected) vs `audit_failed` (unexpected tool/process failure). This distinction lets downstream consumers distinguish normal filtering from infrastructure problems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
