---
name: crossprovider codex cli-smoke-tests-via-version-are-insufficient-for
description: CLI smoke tests via --version are insufficient for tool health verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, health-checks, tooling]
---

A tool can successfully print its version while its runtime entrypoint, interpreter path, plugin loader, config parser, or auth bootstrap are broken. `--version` checks passed before Hermes broke on a shebang pointing to a missing Python. Each tool needs a per-tool, non-destructive functional health check (e.g., actually run a harmless command with dependencies and auth).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
