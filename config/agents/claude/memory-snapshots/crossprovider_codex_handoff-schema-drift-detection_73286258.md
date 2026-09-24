---
name: crossprovider codex handoff-schema-drift-detection
description: Handoff schema drift detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [handoff, schema-evolution, producer-consumer]
---

Producer/consumer handoffs can diverge in key count and enum definitions without detection until explicit review. Session #166 amendment defined 9 keys; consumer #171 required 11 (adding `reviewed_subject_commit` and `review_status`). Verify exact schema alignment at boundaries during code review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
