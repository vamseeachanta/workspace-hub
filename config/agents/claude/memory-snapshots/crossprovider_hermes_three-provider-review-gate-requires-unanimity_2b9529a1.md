---
name: crossprovider hermes three-provider-review-gate-requires-unanimity
description: Three-provider review gate requires unanimity
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-governance, approval-gate, cross-provider]
---

Cross-provider adversarial review (Codex, Gemini, Claude) blocks pre-approval if ANY provider is missing, even if others APPROVE. Missing a single rerun (e.g., no Claude v9 while Codex v9=APPROVE, Gemini v9=MINOR) fails the approval gate despite partial coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
