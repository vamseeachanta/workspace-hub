---
name: crossprovider hermes gmail-batch-digest-cron-fails-auth-silently-on-t
description: Gmail batch digest cron fails auth silently on two accounts, needs manual re-auth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail-api, oauth, batch-automation, email-scripts, auth-failures]
---

When running `scripts/email/gmail-digest.py`, accounts achantav@gmail.com and skestatesinc@gmail.com fail with 'HTTP Error 400: Bad Request' during token refresh. Script completes with AUTH_FAILED status for those accounts in digest output; no automatic recovery. Requires manual user re-authentication to restore digest scanning on those accounts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
