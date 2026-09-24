---
name: crossprovider codex code-level-vocabulary-does-not-guarantee-artifac
description: Code-level vocabulary does not guarantee artifact-level completeness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, artifact-validation, spec-compliance]
---

A script may define PUBLIC_BUCKETS as a constant, but if those buckets are never actually used in report generation, tests may pass while the generated JSON/HTML remains incomplete. Verify that code-level constructs are actively rendered in artifacts, not just declared.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
