---
name: crossprovider codex future-work-gate-passes-with-self-references-onl
description: Future work gate passes with self-references only
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gate-design, validation-gap, future-work]
---

Gate `check_future_work_gate()` returns true when `future-work-recommendations.md` contains only the current WRK ID (self-reference) with no actual follow-up WRKs or rationale. Spec intends to validate that future work is distinct from current item. Needs explicit check that recommended WRK IDs differ from the item being closed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
