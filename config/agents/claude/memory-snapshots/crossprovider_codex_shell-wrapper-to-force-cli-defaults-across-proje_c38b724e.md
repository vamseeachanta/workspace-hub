---
name: crossprovider codex shell-wrapper-to-force-cli-defaults-across-proje
description: Shell wrapper to force CLI defaults across project configs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, cli, config-precedence, shell-wrapper]
---

Codex CLI precedence: project config > global config, but CLI flags override both. To enforce a default across all repos regardless of project-level overrides, use global config plus a shell wrapper injecting the flag (e.g., ~/.local/bin/codex --yolo). This pattern works seamlessly across the repo ecosystem.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
