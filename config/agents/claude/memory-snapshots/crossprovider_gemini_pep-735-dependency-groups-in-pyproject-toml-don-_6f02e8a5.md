---
name: crossprovider gemini pep-735-dependency-groups-in-pyproject-toml-don-
description: PEP 735 dependency-groups in pyproject.toml don't auto-install in CI
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-cd, python-packaging, dependencies]
---

Declaring a package in `[dependency-groups]` (PEP 735) or `[project.optional-dependencies]` does not guarantee it installs in CI unless the CI command explicitly includes the dependency group (e.g., `uv sync --all-extras`). Verify plugin presence in CI logs, not just pyproject.toml declaration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
