---
name: crossprovider codex cli-version-smoke-tests-miss-broken-runtime-depe
description: CLI --version smoke tests miss broken runtime dependencies and config paths
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, health-checks, failure-modes, smoke-tests]
---

A tool can print --version successfully while being broken: missing dotenv, bad shebang pointing to system python, corrupted config, or auth bootstrap failure (as Hermes demonstrated). Health checks need tool-specific actions: import Python modules, run subcommands that depend on config, or validate runtime environment, not just version probes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
