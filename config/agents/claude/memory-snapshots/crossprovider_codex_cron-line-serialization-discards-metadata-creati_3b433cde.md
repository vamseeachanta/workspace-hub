---
name: crossprovider codex cron-line-serialization-discards-metadata-creati
description: Cron line serialization discards metadata, creating correctness risk
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, data-loss, correctness]
---

cron_apply.py and cron-audit.py serialize cron lines as bare fingerprint dicts, discarding sibling metadata like catalog_task_id. Rollback guards in cron_apply.py:188-199 rely on separate classification logic, creating a correctness hazard when reconciling managed vs external lines. Deduplication and preservation guards must preserve and thread metadata consistently through the pipeline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
