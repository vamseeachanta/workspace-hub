---
name: crossprovider codex naive-token-matching-for-api-coverage-detection-
description: Naive token-matching for API coverage detection produces false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [documentation-drift, regex-matching, API-coverage]
---

Grepping for bare symbol names in prose docs matches generic methods (fetch, score, main, compute) appearing naturally in sentences, inflating coverage scores. Durable fix: token boundaries (`\b`), symbol-kind weighting (exclude private dunders), optional code-fence markers for short names, and separate weighting for changelog mentions vs. core docs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
