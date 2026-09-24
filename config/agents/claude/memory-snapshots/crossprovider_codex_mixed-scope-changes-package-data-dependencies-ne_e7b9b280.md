---
name: crossprovider codex mixed-scope-changes-package-data-dependencies-ne
description: Mixed-scope changes (package-data + dependencies) need explicit mixed-diff test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, mixed-changes, regression-prevention]
---

Changes spanning multiple modification types (dependency updates plus package-data edits) can fail silently if test coverage is scoped narrowly. Explicit mixed-diff test cases prevent fail-open gaps where one scope is changed but not tested in combination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
