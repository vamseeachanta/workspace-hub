---
name: crossprovider hermes adversarial-review-across-three-providers-finds-
description: Adversarial review across three providers finds non-overlapping defect classes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review, multi-provider-review, adversarial-testing]
---

Claude, Codex, and Gemini reviewers of #2565 independently discovered DIFFERENT MAJOR defects: governance/artifact-chain (Claude), calculation correctness/sign-convention (Codex), Python-robustness/test-coverage (Gemini). Cross-provider review is necessary, not redundant.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
