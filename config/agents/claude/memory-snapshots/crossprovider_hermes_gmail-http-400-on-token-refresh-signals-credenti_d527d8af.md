---
name: crossprovider hermes gmail-http-400-on-token-refresh-signals-credenti
description: Gmail HTTP 400 on token refresh signals credential expiry
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail, auth-signals, monitoring]
---

Cron digest script detects auth failures as "Token refresh failed: HTTP Error 400: Bad Request" (not 401 or network errors); signals expired OAuth tokens. Scheduled task can flag the issue but cannot auto-recover; requires manual re-authentication.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
