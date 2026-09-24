---
name: crossprovider gemini optional-dependencies-via-uv-extras-over-inline-
description: Optional dependencies via uv extras over inline --with flags
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [dependencies, uv, python, dependency-management]
---

Move CLI tool dependencies from `uv run --no-project --with X --with Y` to `pyproject.toml` `[project.optional-dependencies]` groups, then invoke with `uv run --project <root> --extra groupname`. This centralizes dependency declarations, allows local installation via `pip install -e ".[groupname]"`, and makes the project context explicit to uv.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
