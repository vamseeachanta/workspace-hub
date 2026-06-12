---
name: crossprovider hermes gmail-account-authentication-refresh-needed-peri
description: Gmail account authentication refresh needed periodically across accounts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail, auth, token-refresh]
---

Secondary Gmail accounts (e.g., achantav@gmail.com, skestatesinc@gmail.com) show `AUTH_FAILED` on token refresh roughly every 6 months or after extended idle. Re-auth is manual; gmail-digest.py will report status. Monitor daily digest output for `AUTH_FAILED` and plan re-authentication during maintenance windows.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
