---
name: crossprovider codex codex-statusline-config-uses-toml-file-not-comma
description: Codex statusline config uses toml file, not command-based
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, configuration, cross-provider]
---

`~/.codex/config.toml` with `[status_line]` items array replaces Claude's shell-command approach. Missing fields: WRK queue counts, custom cost calculations, vim mode indicator.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
