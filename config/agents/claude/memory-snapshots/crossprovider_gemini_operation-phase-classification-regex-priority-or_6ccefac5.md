---
name: crossprovider gemini operation-phase-classification-regex-priority-or
description: Operation phase classification: regex priority ordering is critical
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [incident-classification, keyword-matching, priority]
---

First regex match wins in priority-ordered _PHASE_KEYWORD_MAP. Overlapping keywords (e.g., 'loading' for both cargo and generic) resolve by list position. Case-insensitive (re.IGNORECASE) handles maritime report text variation. Order is not a detail — it is the classifier.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
