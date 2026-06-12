---
name: crossprovider hermes live-agent-sessions-cache-runtime-state-per-turn
description: Live agent sessions cache runtime state per-turn; config edits don't propagate to running sessions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, agent-state, config-safety]
---

Hermes and similar agents restore their primary runtime on each turn even after config changes. Editing ~/.hermes/config.yaml while a session is running (e.g., switching from Gemini to Codex) has no effect because the agent restores the cached state before each turn. Must kill/restart the session to pick up config changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
