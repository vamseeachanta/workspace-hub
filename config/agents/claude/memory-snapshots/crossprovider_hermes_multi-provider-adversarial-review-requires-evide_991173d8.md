---
name: crossprovider hermes multi-provider-adversarial-review-requires-evide
description: Multi-provider adversarial review requires evidence quality gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, multi-provider, quality-gates]
---

Codex and Gemini find non-overlapping defects but quality diverges: Gemini can return quota-poisoned output (429 errors mixed with unrelated noise) or timeout. Pattern: run both providers but validate each result independently—don't auto-trust single provider MAJOR verdicts without checking evidence coherence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
