---
name: crossprovider hermes gmail-account-token-refresh-failures-indicate-st
description: Gmail account token refresh failures indicate stale credentials
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail, credentials, auth, maintenance]
---

Multiple Gmail accounts showing `Token refresh failed: HTTP Error 400: Bad Request` and `AUTH_FAILED` status (e.g., achantav@gmail.com, skestatesinc@gmail.com) suggests credentials or refresh tokens have expired or been revoked. Gmail digest scanner tolerates failures gracefully but these accounts need re-authentication.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
