---
name: crossprovider codex hitl-approval-enforcement-via-gh-api-verificatio
description: HITL approval enforcement via gh API verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hitl-approvals, enforcement, github-api]
---

Automated operations like GitHub issue creation require enforcement beyond documentation. Approval comments must be preexisting (before script invocation), user-authored (not agent), reference the issue/batch ID, and contain explicit approval text, verified through gh api before proceeding. Agent-created or ambiguous approvals are invalid.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
