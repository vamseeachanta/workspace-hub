---
name: crossprovider codex workspace-hooks-interfere-with-synthetic-git-rep
description: Workspace hooks interfere with synthetic Git repositories in tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, git-isolation, test-fixtures, enforcement-hooks]
---

Git repositories created during test execution inherit ambient workspace enforcement hooks, causing slow results and incorrect test behavior. Disable hooks only within test-instantiated repositories to isolate behavior and avoid unrelated policy checks polluting test results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
