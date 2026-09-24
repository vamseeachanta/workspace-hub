---
name: crossprovider codex flake8-scan-scope-is-broader-than-pytest-s-test-
description: Flake8 scan scope is broader than pytest's test scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [flake8, ci-gates, test-scope]
---

Running `flake8 .` scans the entire working tree, while pytest's authoritative test scope may be limited via `[tool.pytest.ini_options] testpaths`. Tooling directories (`.agent-os/`, `scripts/`, `modules/`) can hold flake8 violations unrelated to the package but still block CI if flake8 runs before smoke tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
