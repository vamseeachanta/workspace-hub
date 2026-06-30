---
name: crossprovider codex parallel-exploration-coordination-via-tmp-handof
description: Parallel exploration coordination via /tmp handoff files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-28
  tags: [parallel-work, coordination, durable-handoff]
---

When multiple agents explore large filesystems in parallel, accumulate findings incrementally into a durable `/tmp/` coordination file with schema/findings + next-steps sections. This avoids context-window saturation and prevents parallel lanes from redoing overlapping work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
