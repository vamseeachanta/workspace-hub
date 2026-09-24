---
name: crossprovider codex audit-classification-can-misrepresent-specificit
description: Audit classification can misrepresent specificity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, deduplication, classification]
---

Automated duplicate detection correctly identifies duplication but may misclassify specificity. When audit reports label pairs as "exact-duplicates," verify byte-identity before planning deletion—most will have divergent content requiring merge/reconciliation, not removal.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
