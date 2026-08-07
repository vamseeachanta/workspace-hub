---
name: crossprovider codex pytest-collect-ignore-at-root-conftest-doesn-t-b
description: pytest `collect_ignore` at root conftest doesn't block explicit path arguments
metadata:
  type: reference
  source: codex
  bridged: 2026-08-06
  tags: [pytest, collection-control, conftest, gotcha]
---

When `collect_ignore` is set at the root conftest level, it blocks recursive whole-repo collection but doesn't prevent collection when directories or files are targeted explicitly (e.g., `pytest scripts/`). This creates a false isolation boundary that is vulnerable to deliberate path targeting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
