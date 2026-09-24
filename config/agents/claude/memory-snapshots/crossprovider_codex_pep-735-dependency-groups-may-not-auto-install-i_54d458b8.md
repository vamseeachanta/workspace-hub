---
name: crossprovider codex pep-735-dependency-groups-may-not-auto-install-i
description: PEP 735 dependency groups may not auto-install in CI workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, ci, uv, pytest]
---

Packages declared in `[dependency-groups] benchmark` (PEP 735) in pyproject.toml may not install via `uv sync --all-extras` if CI only handles `[project.optional-dependencies]`. Verify CI install commands explicitly include the dependency group or move critical test dependencies to optional-dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
