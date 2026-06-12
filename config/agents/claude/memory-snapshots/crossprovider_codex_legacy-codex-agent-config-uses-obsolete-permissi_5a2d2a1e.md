---
name: crossprovider codex legacy-codex-agent-config-uses-obsolete-permissi
description: Legacy Codex agent config uses obsolete permission syntax
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex-config, schema-migration, deprecated-syntax]
---

Old `.codex/agents/*/config.toml` files use `[permissions] allow = ["Read(*)", ...]` which fails with `FilesystemPermissionsToml` error on current Codex. Current schema expects flat agent configs with top-level `name`, `description`, `developer_instructions`, `sandbox_mode`. Remove `[role]`, `[permissions]`, `[constraints]`, `[system_prompt]` blocks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
