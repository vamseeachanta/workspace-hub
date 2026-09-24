---
name: crossprovider codex review-state-bookkeeping-must-be-verified-agains
description: Review-state bookkeeping must be verified against actual artifact files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-gates, evidence-verification, artifact-integrity]
---

Empty or missing review artifacts need explicit handling rules in the plan. Don't trust claimed verdicts ('Codex | MAJOR', 'Gemini | PENDING') without verifying the actual files exist and contain the expected content. When review-state text contradicts file reality (e.g., says 'empty' for a 985-byte file), the review gate is untrustable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
