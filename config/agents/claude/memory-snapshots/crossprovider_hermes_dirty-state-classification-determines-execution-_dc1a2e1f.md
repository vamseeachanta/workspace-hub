---
name: crossprovider hermes dirty-state-classification-determines-execution-
description: Dirty state classification determines execution blocking, not absolute dirt presence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hygiene, dirty-state, classification, blocking]
---

Before deciding whether dirty state blocks execution, classify files as durable (long-term tracked changes worth preserving) vs disposable (generated output, session-scoped artifacts). Disposable dirt does not block; durable dirt may. Executable work can proceed if dirt is isolated (nested repo, worktree) or cleaned; absolute lack of dirt is not always required.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
