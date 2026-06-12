---
name: crossprovider codex noconftest-flag-prevents-both-global-and-per-sub
description: `--noconftest` flag prevents both global and per-subdirectory conftest
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest, fixtures, test-infrastructure]
---

When pytest is run with `--noconftest`, it suppresses tests/conftest.py globally AND per-subdirectory conftest.py files are unreachable. Fixtures cannot be injected into tests run with this flag. Workaround: define fixtures inline via unittest.mock or in importable helper modules, not conftest files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
