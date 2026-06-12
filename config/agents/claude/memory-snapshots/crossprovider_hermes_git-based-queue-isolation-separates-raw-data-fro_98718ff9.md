---
name: crossprovider hermes git-based-queue-isolation-separates-raw-data-fro
description: Git-based queue isolation separates raw data from wiki summaries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, queue-model, data-boundaries]
---

Queue pattern: jobs in `queue/pending/`, processed by Windows hosts, results to `queue/completed/` or `queue/failed/`. Raw data stays `/mnt/ace`, persists outside git. Wiki receives summaries + metadata only after separate per-gap approval; no raw data copy into git/wiki.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
