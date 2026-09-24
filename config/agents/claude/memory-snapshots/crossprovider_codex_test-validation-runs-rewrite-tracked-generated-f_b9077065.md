---
name: crossprovider codex test-validation-runs-rewrite-tracked-generated-f
description: Test validation runs rewrite tracked generated files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, git-cleanup, pytest]
---

Full pytest runs, smoke harnesses, and data validation scripts can rewrite tracked fixture files, schema files, and generated metadata as side effects. Restore generated artifacts before committing issue-scoped changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
