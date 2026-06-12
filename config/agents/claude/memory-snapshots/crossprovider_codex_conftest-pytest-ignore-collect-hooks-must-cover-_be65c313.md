---
name: crossprovider codex conftest-pytest-ignore-collect-hooks-must-cover-
description: conftest pytest_ignore_collect hooks must cover all error paths
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest, conftest, collection, imports]
---

If a conftest extends `pytest_ignore_collect` to skip collection errors, omitted paths will be collected and executed, causing runtime failures. Audit failed paths against the skip list; if not present, add them or fix the underlying import/path issue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
