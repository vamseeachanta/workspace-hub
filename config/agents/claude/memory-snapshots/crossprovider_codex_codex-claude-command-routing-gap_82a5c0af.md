---
name: crossprovider codex codex-claude-command-routing-gap
description: Codex-Claude command routing gap
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, provider-gap, work-queue]
---

Codex's work adapter exposes only 5 `/work` subcommands (run, list, approve-batch, next, status), while repo docs and Claude support more (e.g., `/work clash`). This creates a provider-specific usability gap tracked in WRK-1327.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
