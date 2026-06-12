---
name: crossprovider hermes symbolic-reads-misclassified-as-missing-file-rea
description: Symbolic reads misclassified as missing-file reads in provider audit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, audit, read-classification]
---

Hermes audit shows 533 prompt-like reads and 639 blank reads classified as 'false missing files' when they should be 'symbolic_reference' (skill names, prompt placeholders, environment variable names). Current heuristic (no slash + no ~ = symbolic) is too weak. Strengthen with symbol registry and context-aware classification to reduce audit false-positives.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
