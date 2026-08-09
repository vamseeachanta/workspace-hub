---
name: crossprovider codex root-conftest-py-with-collect-ignore-is-asymmetr
description: Root conftest.py with collect_ignore is asymmetric: blocks recursion, not explicit paths
metadata:
  type: reference
  source: codex
  bridged: 2026-08-08
  tags: [pytest, collection, conftest, gating]
---

A root-level conftest.py with collect_ignore prevents pytest from recursively descending into excluded directories (e.g., `pytest scripts/` no longer collects nested tests), but explicit file targeting (e.g., `pytest scripts/test_calm_data_loader.py`) still works and bypasses the ignore. Exact-file targeting is hostile to this mechanism.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
