---
name: crossprovider codex hard-authorization-gate-requires-both-marker-and
description: Hard authorization gate requires both marker and artifact
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [gates, authorization, workflow]
---

Implementation gate requires `status:plan-approved` label AND `.planning/plan-approved/<issue>.md` file; owner approval comment alone does not satisfy the gate. Agent cannot self-label; user must apply both.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
