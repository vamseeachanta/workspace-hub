---
name: crossprovider hermes claude-code-authentication-rule-subscription-onl
description: Claude Code authentication rule: subscription-only, never API key without explicit permission
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-code, auth, policy]
---

User requires subscription mode (Claude Max $200/mo), never API key mode without explicit permission. User will handle `claude auth login` himself using browser tools. Permission modes (plan/acceptEdits/auto) and auth methods (subscription/API) are independent concepts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
