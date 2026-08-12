---
name: crossprovider codex pytest-collect-ignore-blocks-recursive-collectio
description: pytest `collect_ignore` blocks recursive collection but not explicit path targeting
metadata:
  type: reference
  source: codex
  bridged: 2026-08-11
  tags: [pytest, collection-gating, conftest]
---

A root `conftest.py` with `collect_ignore` prevents whole-repo recursive traversal, but explicit invocations like `pytest scripts/` or `pytest scripts/test_file.py` still collect from the ignored paths. Distinguish between recursive sweeps (blocked) and deliberate directory/file targeting (bypasses the ignore) when designing pytest gating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
