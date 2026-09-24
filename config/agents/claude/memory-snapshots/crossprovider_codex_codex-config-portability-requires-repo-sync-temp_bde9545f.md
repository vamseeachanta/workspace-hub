---
name: crossprovider codex codex-config-portability-requires-repo-sync-temp
description: Codex config portability requires repo sync template, not native repo config
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, config-portability, codex]
---

Codex reads user config (~/.codex/config.toml) as authoritative; there is no native repo-scoped config. For cross-workstation portability, maintain a repo template (config/agents/codex/config.toml) and extend sync scripts (scripts/_core/sync-agent-configs.sh) to upsert managed keys (model, model_reasoning_effort, etc.) into each user's config on pull/setup. This pattern applies to any agent whose config is user-local.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
