---
name: crossprovider hermes uv-run-no-sync-required-to-prevent-smoke-test-ha
description: uv run --no-sync required to prevent smoke test hangs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [uv, smoke-test, git-dependencies]
---

uv run (without --no-sync) hangs on git dependencies during resolution phase, causing 30s smoke test timeouts with passed=0/failed=0. Inject --no-sync into uv run commands in smoke test runner to skip dependency sync (venv already installed).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
