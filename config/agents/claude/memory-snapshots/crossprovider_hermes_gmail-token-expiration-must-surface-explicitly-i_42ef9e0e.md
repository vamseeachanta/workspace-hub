---
name: crossprovider hermes gmail-token-expiration-must-surface-explicitly-i
description: Gmail token expiration must surface explicitly in digest output, not silent skip
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [email-ops, auth-monitoring, operational-visibility]
---

Auth failures (AUTH_FAILED) in Gmail digest scanner indicate token expiration. Surface these explicitly in digest output so user can re-authenticate before next run. Silent skips mask the problem and degrade coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
