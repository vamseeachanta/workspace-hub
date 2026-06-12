---
name: crossprovider hermes self-approval-gate-is-a-user-preference-gate-bui
description: Self-approval gate is a user-preference gate-building pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [user-preference, approval-workflow, governance]
---

Across multiple sessions, user explicitly rejects auto-approval: 'DO NOT self-label status:plan-approved', 'never offer to self-label', 'post ready-for-approval comment, label status:plan-review, stop unless preauthorized'. This is a deliberate approval-workflow gate, not a generic best-practice; preserve this user preference across sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
