---
name: crossprovider codex archive-directory-presence-is-the-canonical-wrk-
description: Archive directory presence is the canonical WRK completion signal for cleanup decisions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [state-machine, archive-semantics, cleanup]
---

Use archive presence (find archive/ -name WRK-NNN.md) as the durable signal that a WRK finished, triggering cleanup of teams and ephemeral state. More reliable than stage position or completion flags because archive is immutable once written.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
