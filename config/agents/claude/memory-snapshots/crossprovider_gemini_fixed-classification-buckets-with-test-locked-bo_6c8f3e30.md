---
name: crossprovider gemini fixed-classification-buckets-with-test-locked-bo
description: Fixed classification buckets with test-locked boundaries
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [taxonomy, testing, governance, regression-prevention]
---

Use predetermined, enumerated categories (not runtime judgment heuristics) for classifying entities (stale references, artifact types, runtime debt). Lock each bucket via deterministic test assertions so future reintroductions fail automatically. Prevents taxonomy churn and makes governance testable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
