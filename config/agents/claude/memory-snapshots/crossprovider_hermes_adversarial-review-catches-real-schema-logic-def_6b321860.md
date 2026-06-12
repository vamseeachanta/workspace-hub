---
name: crossprovider hermes adversarial-review-catches-real-schema-logic-def
description: Adversarial review catches real schema/logic defects independent of unit tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-process, testing, quality-gate]
---

Two independent adversarial reviewers of llm-wiki #77 both returned MAJOR and surfaced four non-overlapping defects (ambiguous wikilinks, URL encoding bypass, nullish edges, validator drift) that unit tests did not catch. The tests passed because they used simplified/synthetic data. Discipline: always run adversarial review before closing; test parity with real data.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
