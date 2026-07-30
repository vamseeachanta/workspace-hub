---
name: crossprovider codex baseline-fixture-stall-use-noconftest-pytest-dis
description: Baseline fixture stall — use --noconftest + PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 for issue-scoped tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [testing, pytest, fixture-isolation, tdd]
---

When a repository's shared test baseline fixture is slow or stalled (e.g. Faker stalling >6 min), isolate issue-specific tests using `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` env var and `--noconftest` flag instead of waiting or fixing the unrelated fixture. Captures genuine RED/GREEN for the focused contract without depending on the baseline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
