---
name: crossprovider gemini append-only-publish-log-for-authoritative-state
description: Append-only publish log for authoritative state
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [state-management, immutability]
---

Timestamp-based or `HEAD`-based staleness detection fails under concurrent writes and manual edits. Use immutable commit references and append-only `user-review-publish.yaml` event log; the last `plan_draft` event is authoritative.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
