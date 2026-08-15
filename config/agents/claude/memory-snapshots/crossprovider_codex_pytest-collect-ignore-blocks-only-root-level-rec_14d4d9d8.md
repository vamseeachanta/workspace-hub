---
name: crossprovider codex pytest-collect-ignore-blocks-only-root-level-rec
description: pytest `collect_ignore` blocks only root-level recursive traversal, not explicit path targeting
metadata:
  type: reference
  source: codex
  bridged: 2026-08-14
  tags: [pytest, collection-mechanics, test-gating]
---

When `collect_ignore` is defined in a root `conftest.py`, running bare `pytest` blocks descent from the repo root, but explicit path arguments like `pytest scripts/test_file.py` or `pytest scripts/` still collect tests in those paths. This scoping distinction is non-obvious and can catch catch-all `collect_ignore` approaches that aim to silence whole-repo traversal but leave targeted collection unprotected.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
