---
name: crossprovider gemini gemini-session-logs-stored-in-native-chat-store-
description: Gemini session logs stored in native chat store, not named files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gemini-provider-quirk, session-logging, tooling-constraint]
---

Gemini uses `~/.gemini/tmp/workspace-hub/chats/` as native session storage instead of writing named log files to `orchestrator/gemini/`. This breaks parse-session-logs.sh expectations and requires fallback store detection for WRK-ID extraction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
