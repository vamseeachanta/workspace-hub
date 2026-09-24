---
name: crossprovider codex pep-735-dependency-groups-vs-uv-all-extras
description: PEP 735 dependency-groups vs uv --all-extras
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv-tooling, python-packaging, ci-config]
---

The uv tool's `--all-extras` flag installs `[project.optional-dependencies]` but NOT `[dependency-groups]` (PEP 735 declarations). Pytest-benchmark and other PEP 735-declared dependencies require `uv sync --all-groups` or `uv sync --group <name>` to install, causing silent fixture-not-found failures when overlooked in CI workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
