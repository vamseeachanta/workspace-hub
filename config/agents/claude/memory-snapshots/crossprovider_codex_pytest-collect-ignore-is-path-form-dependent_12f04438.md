---
name: crossprovider codex pytest-collect-ignore-is-path-form-dependent
description: Pytest `collect_ignore` is path-form dependent
metadata:
  type: reference
  source: codex
  bridged: 2026-08-10
  tags: [pytest, test-collection, quirk]
---

`collect_ignore` in a root conftest.py prevents recursive collection from `pytest scripts/` but does NOT block explicit `pytest scripts/file.py` file targeting. This asymmetry means directory vs. file path arguments trigger different collection behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
