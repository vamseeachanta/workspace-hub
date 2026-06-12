---
name: crossprovider codex uv-run-rebuilds-virtualenv-even-for-isolated-tes
description: uv run rebuilds virtualenv even for isolated tests
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [uv-run, virtualenv-overhead, isolated-validation]
---

`uv run pytest` rebuilds `.venv` and package on every run, taking 60+ seconds and hanging under concurrent git load. Use `uv run --no-project --with pytest pytest <test-path>` to validate pure-Python slices without repo build overhead. Standard `uv run pytest` only works when workspace I/O is quiet.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
