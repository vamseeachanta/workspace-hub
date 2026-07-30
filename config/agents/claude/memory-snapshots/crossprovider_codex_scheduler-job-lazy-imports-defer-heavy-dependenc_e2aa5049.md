---
name: crossprovider codex scheduler-job-lazy-imports-defer-heavy-dependenc
description: Scheduler job lazy imports defer heavy dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [scheduler-jobs, lazy-imports, python-patterns]
---

When adding scheduler jobs with heavy external package dependencies, defer imports inside `run()` or a lazy initializer (e.g., `HseRefreshJob._acquirer()`), not at module level. This allows the CLI's lazy job registry to load without importing transitive dependencies. Register jobs as string class paths in `_JOB_SPECS`, not concrete imports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
