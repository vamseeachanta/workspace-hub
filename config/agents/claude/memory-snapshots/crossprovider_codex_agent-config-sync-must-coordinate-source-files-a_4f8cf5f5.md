---
name: crossprovider codex agent-config-sync-must-coordinate-source-files-a
description: Agent config sync must coordinate source files and script logic
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [config-management, multi-agent, sync-script]
---

Multi-agent repos (Codex + Hermes) with separate config sources require sync scripts to be updated alongside source files. Solo updates to config.toml or config.yaml.template are reverted on next sync if the script hasn't been patched. Test fixtures must also be updated to prevent regression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
