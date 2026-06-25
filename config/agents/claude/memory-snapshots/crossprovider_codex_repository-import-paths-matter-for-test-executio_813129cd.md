---
name: crossprovider codex repository-import-paths-matter-for-test-executio
description: Repository import paths matter for test execution in monorepo layouts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [test-execution, import-paths, monorepo-layout]
---

When running tests in a repo where `scripts/` contains shared modules, test invocation must set `PYTHONPATH=.` from the repo root, not assume the Python path is configured globally. A test file that imports `scripts.ingest.module` will fail silently in CI if PYTHONPATH is not set, but pass in a developer session that added the path manually.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
