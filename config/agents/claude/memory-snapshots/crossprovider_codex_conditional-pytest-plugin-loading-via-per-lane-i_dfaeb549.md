---
name: crossprovider codex conditional-pytest-plugin-loading-via-per-lane-i
description: Conditional pytest plugin loading via per-lane invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, ci-lanes, performance]
---

Plugin disabling (pytest-benchmark, pytest-randomly) should be specified at invocation time, not in global pytest.ini addopts. Global config disables plugins for all lanes including full/nightly, reducing coverage. Fast lane disables via invocation; full lane keeps plugins enabled via separate invocation strategy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
