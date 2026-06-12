---
name: crossprovider hermes synthetic-answer-injection-substring-validation-
description: Synthetic answer injection + substring validation creates false positives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [evaluation-pitfall, test-design, metrics]
---

When `synthesize_answer()` injects `required_facts` into the answer string, then `score_question()` checks for those facts via substring search, you're not measuring grounding—you're measuring artifact truthfulness. Fact/rubric pass rates become tautological.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
