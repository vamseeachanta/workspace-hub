---
name: crossprovider codex isolated-home-cli-fixtures-for-validation-script
description: Isolated HOME/CLI fixtures for validation scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, fixtures, validation]
---

Using controlled `HOME` and `CODEX_HOME` environment with fake CLIs (that don't require network or external tools) lets validation tests run hermetically and catch fallback chains. Session 4 showed this caught an overlooked case where a pinned binary in npm's global bin but not on `PATH` would fail silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
