---
name: crossprovider codex pytest-collect-ignore-only-blocks-recursive-coll
description: pytest `collect_ignore` only blocks recursive collection, not explicit path targeting
metadata:
  type: reference
  source: codex
  bridged: 2026-08-07
  tags: [pytest, conftest, collection-gating, mechanism]
---

A root `conftest.py` with `collect_ignore` prevents recursive whole-repo traversal but does NOT prevent collection when you explicitly target paths (e.g., `pytest scripts/path/to/file.py`). Directory-level targeting (e.g., `pytest scripts/`) still collects and errors on many top-level scripts. This makes the mechanism leaky for directory targets but effective for single-file precision.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
