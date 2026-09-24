---
name: crossprovider codex redistribution-logic-targeting-full-backlog-vs-e
description: Redistribution logic targeting full backlog vs. executable work creates scope creep
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-creep, queue-semantics, acceptance-criteria]
---

Plan loops every card in dead leader queue but live code doesn't distinguish executable (wip_eligible, approved, execution-ready lane) from full backlog. Acceptance should require filtering on execution-ready lane membership, not just open/unclaimed/not-gated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
