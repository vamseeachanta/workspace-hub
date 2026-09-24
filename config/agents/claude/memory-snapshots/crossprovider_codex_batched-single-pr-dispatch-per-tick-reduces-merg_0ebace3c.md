---
name: crossprovider codex batched-single-pr-dispatch-per-tick-reduces-merg
description: Batched single-PR dispatch per tick reduces merge churn vs per-publisher
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-dispatch, pr-churn, batching-pattern]
---

Switching from up to 13 per-publisher PRs per 6h tick to 1 shared-branch PR eliminates constant re-sync churn behind main on union-merged append files. Reuse existing branch/dispatch functions; additive opt-in flag keeps per-publisher path intact. Cuts coordination overhead significantly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
