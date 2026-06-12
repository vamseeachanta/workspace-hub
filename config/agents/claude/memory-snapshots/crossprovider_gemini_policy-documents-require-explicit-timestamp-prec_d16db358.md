---
name: crossprovider gemini policy-documents-require-explicit-timestamp-prec
description: Policy documents require explicit timestamp/precedence contracts, not prose wording
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [policy, timestamps, enforcement-gates]
---

Enforcement and control-gate policies must encode precise timestamp semantics (UTC RFC3339 normalization, tie-break rules, precedence cascades) as concrete logic rather than descriptive text. #2289 required 9 revisions because timestamp contracts across git committer-date, GitHub API events, and marker filesystem mtime were underspecified.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
