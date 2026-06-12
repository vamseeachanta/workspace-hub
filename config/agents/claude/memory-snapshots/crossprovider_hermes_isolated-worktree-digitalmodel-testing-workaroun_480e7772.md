---
name: crossprovider hermes isolated-worktree-digitalmodel-testing-workaroun
description: Isolated worktree digitalmodel testing workaround for editable dependency resolution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, digitalmodel, worktree, uv-limitations]
---

When `uv run python -m pytest` fails in an isolated digitalmodel worktree due to editable dependency path resolution, use the shared main repo venv: `PYTHONPATH=src /mnt/local-analysis/workspace-hub/digitalmodel/.venv/bin/python -m pytest <target> -q`. This bypasses isolated worktree uv context issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
