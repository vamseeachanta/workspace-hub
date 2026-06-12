---
name: crossprovider hermes gmail-secondary-accounts-fail-token-refresh-in-c
description: Gmail secondary accounts fail token refresh in cron digest jobs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail, authentication, automation, operations]
---

Cron-based Gmail digest job (scripts/email/gmail-digest.py) shows consistent AUTH_FAILED with HTTP 400 token refresh errors on secondary accounts (achantav@gmail.com, skestatesinc@gmail.com) while primary account (vamsee.achanta@aceengineer.com) works. Secondary accounts may require periodic manual OAuth re-authentication or fresh token generation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
