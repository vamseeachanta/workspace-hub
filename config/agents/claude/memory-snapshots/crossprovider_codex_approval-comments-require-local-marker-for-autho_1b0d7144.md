---
name: crossprovider codex approval-comments-require-local-marker-for-autho
description: Approval comments require local marker for authority
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-gate, approval-semantics, hard-stop]
---

GitHub comments alone do not grant implementation authority. A local `.planning/plan-approved/<issue>.md` marker is mandatory; the approval comment surfaces the user's intent but is not self-executing. This separation preserves the gate against accidental/unreviewed implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
