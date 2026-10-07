---
name: crossprovider codex collection-behavior-testing-requires-clean-sourc
description: Collection behavior testing requires clean source state, not dirty working tree
metadata:
  type: reference
  source: codex
  bridged: 2026-08-08
  tags: [pytest, testing-methodology, working-tree, measurement]
---

pytest.ini modifications, root conftest.py, and uv.lock changes in the working tree directly affect collection measurements, making it hard to isolate the plan's proposed changes from local edits. Use `pytest -o` flag to override config dynamically rather than relying on worktree-state measurements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
