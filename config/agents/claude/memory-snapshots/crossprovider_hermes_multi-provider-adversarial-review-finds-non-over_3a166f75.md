---
name: crossprovider hermes multi-provider-adversarial-review-finds-non-over
description: Multi-provider adversarial review finds non-overlapping defects
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review, quality, multi-provider]
---

Claude→Codex→Gemini serial reviews on the same code (especially concurrency-sensitive code) each surface different defect classes. R1 finds logic bugs, R2 finds subtle nits, R3 finds race conditions. Cost is justified for high-risk infrastructure (e.g., fanout, dispatch) where silent failures are expensive.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
