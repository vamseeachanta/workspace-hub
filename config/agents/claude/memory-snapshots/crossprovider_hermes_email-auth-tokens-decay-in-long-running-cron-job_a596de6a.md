---
name: crossprovider hermes email-auth-tokens-decay-in-long-running-cron-job
description: Email auth tokens decay in long-running cron jobs and need re-authentication
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [email-auth, oauth-tokens]
---

Gmail integrations can fail with AUTH_FAILED during token refresh in overnight/cron runs. Do not assume tokens persist across sessions; flag accounts needing re-auth in periodic maintenance reports.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
