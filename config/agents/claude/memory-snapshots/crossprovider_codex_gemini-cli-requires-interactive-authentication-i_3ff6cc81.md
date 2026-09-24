---
name: crossprovider codex gemini-cli-requires-interactive-authentication-i
description: Gemini CLI requires interactive authentication in headless mode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [authentication, gemini-cli, non-interactive]
---

Gemini CLI fails with FatalAuthenticationError in non-interactive sessions unless GEMINI_API_KEY or Application Default Credentials are configured. Codex and Claude CLI work headless. Plan provider dispatch accordingly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
