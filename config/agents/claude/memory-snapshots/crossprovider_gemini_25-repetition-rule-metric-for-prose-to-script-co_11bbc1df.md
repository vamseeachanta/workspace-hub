---
name: crossprovider gemini 25-repetition-rule-metric-for-prose-to-script-co
description: 25% Repetition Rule: metric for prose-to-script conversion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [automation, prose-to-script, repetition-rule, metrics]
---

When a prose operation (counting items, iterating over repos, parsing configs, filtering by criteria) appears in ≥25% of skills/rules/docs, convert it to a deterministic script. Classify candidates as existing-script, new-one-liner, new-utility, or llm-only to prioritize implementation work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
