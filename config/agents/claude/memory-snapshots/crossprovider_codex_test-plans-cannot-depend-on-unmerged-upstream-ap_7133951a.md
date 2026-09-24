---
name: crossprovider codex test-plans-cannot-depend-on-unmerged-upstream-ap
description: Test plans cannot depend on unmerged upstream API contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning-antipattern, upstream-dependencies, test-plan]
---

When a test plan invents binding API/provenance schemas and makes them mandatory test assertions before upstream code has landed and merged, the plan becomes unimplementable (upstream may land with valid but different interface). Require upstream precondition links and reconciliation gates before writing always-on tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
