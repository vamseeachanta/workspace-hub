---
name: crossprovider hermes claude-superpowers-updates-fail-silently-due-to-
description: Claude Superpowers updates fail silently due to scope mismatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plugin-sync, harness-update, scope-management]
---

Installed at project scope but harness-updater attempts user-scope update, causing 'plugin not found' failures. Superpowers is not handled by sync-agent-configs.sh (only Claude/Codex/Gemini/Hermes are synced). Scope detection needed for reliable multi-scope plugin updates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
