---
name: crossprovider codex virtualenv-editable-install-loads-stale-modules-
description: Virtualenv editable install loads stale modules in direct execution
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [environment, python, editable-install]
---

When a repo has editable install pointing to main checkout, direct Python execution loads main's old code. Pytest respects PYTHONPATH config automatically, but `python -c` and subprocess calls don't. Workaround: prefix with `PYTHONPATH=src` for direct probes; pytest already handles it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
