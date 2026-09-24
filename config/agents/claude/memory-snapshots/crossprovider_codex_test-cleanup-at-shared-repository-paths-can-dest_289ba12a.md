---
name: crossprovider codex test-cleanup-at-shared-repository-paths-can-dest
description: Test cleanup at shared repository paths can destroy fixture content
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-safety, fixture-management]
---

Test teardown that unconditionally deletes files at repository fixture paths can destroy fixtures from other tests or prior runs. Use isolated temporary directories for test artifacts and avoid unconditional unlink of repository-tracked or shared paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
