---
name: crossprovider hermes adversarial-review-convergence-on-schema-defects
description: Adversarial review convergence on schema defects is high-confidence signal
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review-methodology, defect-confidence, cross-reviewer-signal]
---

When 3+ independent adversarial reviewers (Claude, Codex, Gemini) all flag the same schema-level issue (e.g., missing `additionalProperties: false`, weak enum enforcement), it's a P0 blocker, not a style disagreement. Convergence across providers indicates the defect is unambiguous and structural, not subjective. Use convergence to triage and prioritize review findings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
