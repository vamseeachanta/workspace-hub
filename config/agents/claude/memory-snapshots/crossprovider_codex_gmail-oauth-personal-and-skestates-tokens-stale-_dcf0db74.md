---
name: crossprovider codex gmail-oauth-personal-and-skestates-tokens-stale-
description: Gmail OAuth: personal and skestates tokens stale, only ace account live
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [environment, gmail, authentication]
---

Workspace Gmail tokens for `personal` and `skestates` accounts fail token refresh with HTTP 400. Only `vamsee.achanta@aceengineer.com` (ace account) is live for Gmail API calls. Any CLI/MCP Gmail work must target ace or re-authorize the others.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
