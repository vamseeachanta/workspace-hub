---
name: crossprovider hermes gmail-account-oauth-refresh-fails-with-http-400
description: Gmail account OAuth refresh fails with HTTP 400
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail, oauth, auth-failure]
---

Gmail digest cron reported AUTH_FAILED on personal and SKEstates accounts; token refresh returned HTTP 400 Bad Request (not rate limit or abuse). May indicate revoked/expired credentials; both accounts require manual re-authentication.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
