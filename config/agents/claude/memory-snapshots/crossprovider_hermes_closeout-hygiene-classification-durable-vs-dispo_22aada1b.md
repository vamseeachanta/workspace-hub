---
name: crossprovider hermes closeout-hygiene-classification-durable-vs-dispo
description: Closeout hygiene classification: durable vs disposable artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [closeout-pattern, git-hygiene, workspace-cleanup]
---

Classify dirty state into three buckets: durable evidence (skill patches, plans, tracked reports), recurring telemetry (provider/work-queue JSON/MD already git-tracked), disposable churn (session signals, temp review logs, diagnostic output). Validate formats, stage narrowly, commit durable, restore/remove disposable, then capture clean proof.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
