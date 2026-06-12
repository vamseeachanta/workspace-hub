---
name: crossprovider hermes exit-handoff-documentation-structure-and-locatio
description: Exit handoff documentation structure and location
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [session-close, documentation, git-hygiene]
---

Store session exit handoffs in `docs/session-handoffs/` with required sections: issue link + closed state, landed commit hash + tests passed, validation proof (legal scan, adversarial review verdict), dirty-state exception count/classes (intentionally preserved), worktree disposition, external-action status, and branch/origin sync proof. Serves as restart checkpoint for future sessions and documents why unrelated changes remain uncommitted.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
