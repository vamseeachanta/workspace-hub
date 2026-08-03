---
name: crossprovider codex archived-session-artifacts-need-checksums-and-ca
description: Archived session artifacts need checksums and canonical-copy verification before cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cleanup, archive, verification, fsaudit]
---

Durable session outputs (MISSION_LOG, artifacts, reviews) cannot be safely disposed without manifests/checksums for rehydration proof. Duplicate canonical copies need content review; divergent material indicates intentional variants, not dedup targets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
