---
name: crossprovider codex snapshot-source-kind-phase-pairs-are-coupled-con
description: Snapshot source_kind/phase pairs are coupled constraints
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [snapshot-validation, fail-closed]
---

Invalid source_kind/phase combos can pass validation if URL checks are conditional on a specific phase. Validators must reject invalid combos as early fail-closed gates before checking phase-specific fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
