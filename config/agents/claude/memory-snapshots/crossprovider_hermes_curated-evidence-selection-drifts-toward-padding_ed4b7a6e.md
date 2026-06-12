---
name: crossprovider hermes curated-evidence-selection-drifts-toward-padding
description: Curated evidence selection drifts toward padding to meet coverage targets
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [curation, evidence-selection, quality-drift]
---

When curation aims for count/coverage requirements, weaker adjacent evidence gets included while stronger direct evidence is omitted. E.g., #2508: non-semiconductor roles included to hit count; stronger Analog Devices semiconductor row omitted. Define explicit 'high-relevance' rules to prevent count-driven padding.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
