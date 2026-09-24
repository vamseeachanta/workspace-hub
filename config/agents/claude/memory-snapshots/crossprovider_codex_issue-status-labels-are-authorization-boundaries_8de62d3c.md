---
name: crossprovider codex issue-status-labels-are-authorization-boundaries
description: Issue status labels are authorization boundaries, not tracking metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-lifecycle, authorization, gates]
---

Status labels like `status:plan-approved` gate authorization to proceed, not just track state. Work conducted before explicit status approval violates the contract and must be blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
