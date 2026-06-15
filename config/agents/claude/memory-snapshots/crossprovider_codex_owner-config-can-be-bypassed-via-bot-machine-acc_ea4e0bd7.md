---
name: crossprovider codex owner-config-can-be-bypassed-via-bot-machine-acc
description: Owner config can be bypassed via bot/machine accounts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, approval-gate, automation-risk]
---

PLAN_APPROVAL_OWNERS can include bot/machine logins or machine-user PATs, allowing automation to apply approval labels. Must fail if owner config is missing or includes known bot accounts. Protect owner changes, document permission model, and test machine-user label application paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
