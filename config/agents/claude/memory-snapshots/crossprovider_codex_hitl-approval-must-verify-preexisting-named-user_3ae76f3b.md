---
name: crossprovider codex hitl-approval-must-verify-preexisting-named-user
description: HITL approval must verify preexisting named-user comment
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [automation, approval, safety, github]
---

When agents create GitHub issues requiring human approval, agent-created approval comments can appear user-authored if running under user account. Guard with explicit checks: approval comment must predate script invocation, be authored by a named human (not the agent's account), reference the issue or batch ID, and contain explicit issue-creation approval text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
