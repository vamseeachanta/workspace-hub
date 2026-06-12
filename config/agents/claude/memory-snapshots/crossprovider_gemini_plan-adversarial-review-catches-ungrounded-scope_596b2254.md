---
name: crossprovider gemini plan-adversarial-review-catches-ungrounded-scope
description: Plan adversarial review catches ungrounded scope
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [planning-discipline, code-review]
---

Adversarial reviews surface when plans claim scope without grounding in current repo surfaces (file paths, existing code names, real test names). Plans that say 'modify X' without naming the actual file get flagged. This discipline prevents scope creep and implementation surprise.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
