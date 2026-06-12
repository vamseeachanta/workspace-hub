---
name: crossprovider codex codex-statusline-configuration-syncing-pattern
description: Codex statusline configuration syncing pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex-config, statusline, cross-agent-sync]
---

Codex supports built-in status fields in `~/.codex/config.toml` (model, git_branch, context_window) but lacks Claude's custom command execution. Workspace template can pre-define `[status_line]` config, but active file needs explicit sync from template—not automatic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
