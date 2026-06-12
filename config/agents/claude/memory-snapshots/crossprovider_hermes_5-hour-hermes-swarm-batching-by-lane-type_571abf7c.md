---
name: crossprovider hermes 5-hour-hermes-swarm-batching-by-lane-type
description: 5-hour Hermes swarm batching by lane type
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [execution, batching, hermes, workflow]
---

Organize 5-hour execution windows by work type: 1 issue per window for execution-ready; 5–10 issues per window for approval-drift repair (evidence-only, no implementation); 3–6 for plan-review synthesis; 3–5 for planning/decomposition; separate audit windows for state hygiene. Prevents context thrashing and aligns to natural batch sizes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
