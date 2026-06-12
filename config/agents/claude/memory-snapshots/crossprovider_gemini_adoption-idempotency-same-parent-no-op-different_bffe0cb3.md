---
name: crossprovider gemini adoption-idempotency-same-parent-no-op-different
description: Adoption idempotency: same-parent no-op, different-parent hard-fail
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [idempotency, safety, work-queue]
---

When new-feature.sh adopts an existing WRK via wrk_ref: if parent: already matches current feature, skip silently (idempotent rerun). If parent: is different, exit 1 (integrity error—WRK belongs to another feature). If parent: absent, insert normally.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
