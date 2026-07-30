---
name: crossprovider codex test-environment-dependencies-on-fuse-must-inclu
description: Test environment dependencies on FUSE must include all transitive scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, fuse, dependencies, debugging]
---

When a test harness runs in /tmp on a FUSE worktree, missing dependent scripts or fixtures cause import errors that may surface as module-not-found errors. Copy all transitive dependencies (not just the primary test file) to /tmp before running the harness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
