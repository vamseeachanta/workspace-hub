---
name: crossprovider codex dependency-blocking-status-should-be-explicit-in
description: Dependency-blocking status should be explicit in plan metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [workflow, planning, governance]
---

When plan A requires plan B's approval before implementation readiness, mark plan A's status as `status:dependency-blocked` or `status:blocked`, not `status:draft`. Draft signals independence. Observed in llm-wiki #730 — marked draft but explicitly gated on #729 approval, creating ambiguous execution signaling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
