---
name: crossprovider hermes digitalmodel-tests-require-direct-venv-not-uv-ru
description: Digitalmodel tests require direct venv, not uv run
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, environment, digitalmodel]
---

Use `PYTHONPATH=src /path/.venv/bin/python -m pytest` directly; `uv run` creates editable-path + assetutilities divergence breaking demo tests. Repo venv must be pre-installed; fallback to CI validation if local venv unavailable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
