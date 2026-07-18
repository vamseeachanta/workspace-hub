---
name: crossprovider codex handoff-schemas-require-exact-field-parity-verif
description: Handoff schemas require exact field parity verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [handoff, schema, verification, producer-consumer]
---

Cross-document handoffs can silently diverge in field count and enums. The 9-key vs 11-key mismatch between #166 producer and #171 consumer broke on `reviewed_subject_commit` and `review_status` fields; classification enums (PUBLIC|INTERNAL vs authority/confidentiality/residency) also diverged. Count and compare schemas explicitly before claiming compatibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
