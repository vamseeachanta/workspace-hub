---
name: crossprovider codex minimal-test-fixtures-reduce-fixture-maintenance
description: Minimal test fixtures reduce fixture maintenance burden
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, test-isolation, minimal-setup]
---

When testing complex logic that touches file paths, create fixture directories with only the required path structure (e.g., `.claude/work-queue/logs/`) without populating full log content for most tests. Populate content only for tests that exercise the reading logic. This keeps fixture setup lightweight and discoverable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
