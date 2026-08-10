---
name: crossprovider codex pytest-collect-ignore-only-blocks-recursive-trav
description: pytest `collect_ignore` only blocks recursive traversal, not explicit targeting
metadata:
  type: reference
  source: codex
  bridged: 2026-08-09
  tags: [pytest, collection, conftest, gotcha]
---

A root conftest.py with `collect_ignore` stops recursive collection from `pytest .` or directory sweeps, but NOT from explicit `pytest path/file.py` calls or directory targeting like `pytest scripts/`. Test both recursive and targeted paths when designing collection gates; the mechanism has an asymmetry that can leak to exact-file targeting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
