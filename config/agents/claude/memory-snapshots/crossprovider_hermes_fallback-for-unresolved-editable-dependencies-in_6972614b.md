---
name: crossprovider hermes fallback-for-unresolved-editable-dependencies-in
description: Fallback for unresolved editable dependencies in monorepo
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, virtualenv, monorepo]
---

When `uv run pytest` fails on missing editable deps (e.g., assetutilities at beta maturity), fallback works: `PYTHONPATH=src .venv/bin/python -m pytest <path>`. Explicit venv + import-path bypasses uv's dependency resolution graph.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
