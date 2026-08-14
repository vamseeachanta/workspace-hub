---
name: crossprovider codex pytest-collect-ignore-blocks-recursive-traversal
description: pytest collect_ignore blocks recursive traversal but allows explicit path arguments
metadata:
  type: reference
  source: codex
  bridged: 2026-08-13
  tags: [pytest, collection-gating, conftest]
---

A root `conftest.py` with `collect_ignore` prevents recursive collection (e.g., `pytest` from repo root), but explicit file/directory arguments bypass it (e.g., `pytest scripts/test_file.py` still collects). This asymmetry means `collect_ignore` protects against accidental sprawl but requires additional gating if deliberate single-file runs must also be blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
