---
name: crossprovider gemini pep-735-dependency-groups-require-all-groups-fla
description: PEP 735 dependency-groups require --all-groups flag in uv
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [uv, python-deps, ci-config, dependency-resolution]
---

uv sync --all-extras installs optional-dependencies but NOT PEP 735 dependency-groups (declared in [dependency-groups]). Must pass --all-groups or --group <name> explicitly. This gap caused pytest-benchmark and other dependency-group entries to not be installed during CI, causing fixture-not-found errors at runtime.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
