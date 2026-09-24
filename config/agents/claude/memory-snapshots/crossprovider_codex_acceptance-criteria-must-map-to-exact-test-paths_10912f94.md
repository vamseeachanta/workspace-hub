---
name: crossprovider codex acceptance-criteria-must-map-to-exact-test-paths
description: Acceptance criteria must map to exact test paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, tdd, design, acceptance-criteria]
---

When acceptance criteria claim behavior, plan's TDD section must list concrete test names, file paths, and expected inputs/outputs for each criterion. Circular references ('existing tests will cover') fail review. Verify tests exist and are executable before claiming coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
