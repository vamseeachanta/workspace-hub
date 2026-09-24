---
name: crossprovider codex acceptance-criteria-with-implicit-dependencies-a
description: Acceptance criteria with implicit dependencies are non-implementable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, testing, implicit-dependencies, implementability]
---

Tests that depend on external APIs or imports without naming them explicitly (e.g., 'skip unless #500/#605/#606/#611 public APIs are importable') cannot be implemented objectively. Example: plan #610 deferred the test skipping condition without defining which import paths, functions, or version checks constitute those APIs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
