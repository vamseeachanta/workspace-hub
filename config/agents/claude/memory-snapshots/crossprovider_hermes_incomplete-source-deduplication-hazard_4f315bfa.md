---
name: crossprovider hermes incomplete-source-deduplication-hazard
description: Incomplete-source deduplication hazard
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [deduplication, incomplete-data, classification-logic]
---

When deduplicating by fingerprint, an inaccessible source with an incomplete tree can cause complete peers to be misclassified as exact-duplicates if their visible trees match. Conservative handling must filter incomplete sources BEFORE grouping, not only mark them as incomplete after.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
