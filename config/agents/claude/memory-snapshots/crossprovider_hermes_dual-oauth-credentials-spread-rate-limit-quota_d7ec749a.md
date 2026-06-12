---
name: crossprovider hermes dual-oauth-credentials-spread-rate-limit-quota
description: Dual-OAuth credentials spread rate-limit quota
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-config, credential-management, load-balancing]
---

Single credential insufficient; dual OAuth creds with `round_robin` load balancing spreads quota across providers. Hermes pattern: primary gpt-4.1 via cred-1, fallback gpt-4.1 via cred-2, tertiary copilot/claude-sonnet-4.6.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
