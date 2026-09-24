---
name: crossprovider codex acceptance-criteria-defined-in-plans-but-omitted
description: Acceptance criteria defined in plans but omitted from implementation detection go unvalidated
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, plan-drift, testing, validation]
---

When a plan promises specific outputs or sub-categories (e.g., `exempt_type` sub-category in commit drift counting), but implementation provides only a subset, tests can still pass if they don't explicitly validate the missing criteria. Audit acceptance criteria against both code and test fixtures before sign-off.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
