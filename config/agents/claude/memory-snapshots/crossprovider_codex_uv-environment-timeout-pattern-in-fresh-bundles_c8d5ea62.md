---
name: crossprovider codex uv-environment-timeout-pattern-in-fresh-bundles
description: uv environment timeout pattern in fresh bundles
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-tooling, uv, environment-setup]
---

Plain `uv run` deterministically times out in fresh bundles during initial sync; `uv run --no-sync` is fast after sync completes once. Environment repair (reinstall/resync) needed after partial sync interruptions. For repeated TDD runs, use `--no-sync` after first complete sync.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
