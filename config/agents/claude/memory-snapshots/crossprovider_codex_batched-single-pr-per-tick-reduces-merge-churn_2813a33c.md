---
name: crossprovider codex batched-single-pr-per-tick-reduces-merge-churn
description: Batched single-PR per tick reduces merge churn
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron-ingest, git-flow, merge-strategy]
---

Replace per-publisher PRs with one batched PR per cron tick when working with union-merged shared files. Reduces merge events from up to 13 per tick to 1, eliminating constant re-sync against main.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
