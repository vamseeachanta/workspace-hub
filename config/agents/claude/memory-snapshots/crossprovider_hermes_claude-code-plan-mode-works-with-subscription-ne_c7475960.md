---
name: crossprovider hermes claude-code-plan-mode-works-with-subscription-ne
description: Claude Code plan mode works with subscription, never API key without permission
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-code, authentication, permissions]
---

`--permission-mode plan` (read-only audit mode) works with Claude subscription OAuth, not just API keys. User policy: never use API key mode without explicit permission. Subscription is the default auth method for Claude Code.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
