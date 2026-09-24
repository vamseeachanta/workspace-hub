---
name: crossprovider codex adversarial-review-verdict-as-a-mandatory-blocke
description: Adversarial review verdict as a mandatory blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, test-driven-development, gating]
---

MAJOR verdicts block advancement to the next task. Do not apply ad-hoc patches; instead, dispatch a fresh fix agent with the exact defect class list and rerun the RED/GREEN cycle. After the fixed commit lands, rerun adversarial review before proceeding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
