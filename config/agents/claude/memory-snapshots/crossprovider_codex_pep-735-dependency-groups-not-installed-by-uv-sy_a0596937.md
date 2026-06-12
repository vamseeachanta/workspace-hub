---
name: crossprovider codex pep-735-dependency-groups-not-installed-by-uv-sy
description: PEP 735 dependency-groups not installed by uv sync --all-extras
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [uv, dependencies, python, pep-735]
---

`uv sync --all-extras` installs `[project.optional-dependencies]` but NOT PEP 735 `[dependency-groups]`; must use `--all-groups` or `--group <name>` explicitly. worldenergydata declares `pytest-benchmark` in both places; CI runs hit missing-fixture because --all-extras skipped the benchmark dependency-group.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
