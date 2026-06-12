---
name: crossprovider hermes rag-benchmark-gate-weakness-aggregate-only-thres
description: RAG benchmark gate weakness: aggregate-only thresholds mask per-domain red
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [rag, benchmark, threshold-weakness, validation]
---

Validator enforces aggregate thresholds (hit_at_5 >= 0.5, citation >= 0.5, rubric >= 0.8) but allows 10/22 questions to fail; production-eng and standards slices drop to 0.2–0.25 while gate stays green. Root cause: snippet extraction prefers early lines and truncates at 600 chars, losing later-page facts even when correct page is retrieved.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
