---
name: crossprovider codex codex-cli-flags-outrank-config-files-for-repo-pr
description: Codex CLI flags outrank config files for repo-proof defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [tooling, configuration, precedence]
---

CLI flags > project `.codex/config.toml` > user `~/.codex/config.toml`. A global user config alone cannot guarantee behavior across repositories with local overrides; a shell wrapper injecting the CLI flag (e.g., `--yolo`) achieves highest precedence everywhere.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
