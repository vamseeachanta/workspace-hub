---
name: crossprovider codex uv-run-timeout-in-isolated-bundles-use-no-sync-f
description: uv run timeout in isolated bundles; use --no-sync for targeted tests
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [environment-optimization, uv-patterns, isolated-bundles]
---

Plain `uv run` in fresh/isolated bundles with large dependency graphs times out before Python starts (15-20s). `uv run --no-sync` executes quickly if environment exists. For bounded TDD: create environment once with plain `uv run`, then use `--no-sync` for repeated test runs to avoid re-syncing costs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
