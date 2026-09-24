---
name: crossprovider gemini snapshot-freshness-check-via-o-1-metadata-lookup
description: Snapshot freshness check via O(1) metadata lookup
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [email, performance]
---

Email state snapshots include `.meta.yaml` with `last_log_byte_offset` + `last_log_sha` for O(1) staleness detection without replaying logs. Enables fast hot-path reads against append-only JSONL logs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
