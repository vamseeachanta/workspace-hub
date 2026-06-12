---
name: crossprovider codex mypy-requires-per-repo-execution-context-cd-into
description: Mypy requires per-repo execution context (cd into repo first)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [python-runtime, mypy, uv-run]
---

`uv run mypy <path>` from workspace root loses repo-local dependencies and import paths, causing false failures or missing-import errors. Must `cd` into the target repo, then invoke mypy from that root. This is especially critical for repos with local path sources in pyproject.toml (e.g. OGManufacturing, assethold).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
