---
name: crossprovider codex string-only-classification-misses-case-variants-
description: String-only classification misses case variants and synonyms
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [classification, data-quality, robustness]
---

Substring/exact-match markers miss case variations and synonym forms (e.g., `e-certificate` vs `e-certificates` vs `e-certificate-online-database`). Use case-insensitive sets or regex with synonym groups. Brittle classification cascades into routing errors and under-coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
