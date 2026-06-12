---
name: crossprovider hermes claude-code-permission-modes-and-billing-are-ind
description: Claude Code permission modes and billing are independent
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-code, auth, permissions, api-design]
---

Permission modes (--permission-mode plan/acceptEdits/auto) work with subscription auth independently—permission mode controls what Claude CAN do (read-only vs read-write), billing mode controls HOW you pay (subscription vs API key). Plan mode is read-only and suitable for cloud audits. Subscription mode does not support --max-budget-usd (API-key-only), but is bound by Claude Max tier rate limits instead.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
