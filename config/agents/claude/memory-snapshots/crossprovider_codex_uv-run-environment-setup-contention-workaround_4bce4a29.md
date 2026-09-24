---
name: crossprovider codex uv-run-environment-setup-contention-workaround
description: uv run environment setup contention workaround
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv-tooling, test-validation, environment-setup]
---

In shared workspaces, `uv run` may hang during environment setup. Use `uv run --no-sync` to route through uv with existing environment, avoiding the setup path that causes contention; still enforces repo policy while staying responsive.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
