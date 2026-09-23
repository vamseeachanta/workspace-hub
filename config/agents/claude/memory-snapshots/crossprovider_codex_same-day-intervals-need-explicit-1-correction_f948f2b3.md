---
name: crossprovider codex same-day-intervals-need-explicit-1-correction
description: Same-day intervals need explicit +1 correction
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [correctness, edge-cases, rig-days]
---

Date arithmetic `(end - start).days` returns 0 for same-day spans; WAR convention is inclusive, so same-day intervals must count as 1 day, not 0. Guard needed for intervals where start == end.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
