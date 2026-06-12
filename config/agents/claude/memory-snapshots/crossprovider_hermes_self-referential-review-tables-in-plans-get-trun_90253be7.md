---
name: crossprovider hermes self-referential-review-tables-in-plans-get-trun
description: Self-referential review tables in plans get truncated by fanout script
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review, adversarial-review, tooling-quirk]
---

plan-review-fanout.sh overwrites the target artifact paths before writing provider results. If a plan embeds current-cycle review verdict tables/paths, those get emptied before reviewers can see them, causing false/stale evidence findings. Move verdict summaries to issue comments or separate files instead.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
