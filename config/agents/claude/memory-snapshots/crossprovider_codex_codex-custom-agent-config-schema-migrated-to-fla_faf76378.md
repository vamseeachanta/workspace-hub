---
name: crossprovider codex codex-custom-agent-config-schema-migrated-to-fla
description: Codex custom agent config schema migrated to flat format with sandbox_mode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-config, schema-migration, agent-configuration]
---

Codex agent role files using legacy `[role]`, `[permissions]`, `[constraints]`, `[system_prompt]` blocks with string-based permissions like `"Read(*)"` are obsolete. Current schema expects flat config files with top-level `name`, `description`, `developer_instructions`, and optional `sandbox_mode = "workspace-write"|"read-only"`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
