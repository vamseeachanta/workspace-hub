---
name: crossprovider codex global-pytest-addopts-e-g-cov-fail-under-contami
description: Global pytest addopts (e.g., --cov-fail-under) contaminate supposedly isolated unit tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, tdd, config-pollution]
---

When pyproject.toml contains repo-wide `addopts` like `--cov-fail-under=80`, even targeted unit test commands inherit those gates and can fail for unrelated whole-repo coverage. TDD commands must either explicitly override `addopts` with `-o addopts=''` or use non-pytest forms, or acceptance criteria become unprovable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
