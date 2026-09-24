---
name: crossprovider gemini pre-review-attestation-required-for-sandboxed-re
description: Pre-review attestation required for sandboxed reviewers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [review-infrastructure, sandboxing, verification]
---

Sandboxed review providers (Codex, Gemini) cannot access repo state to verify plan claims. Attestation (gh issue view, ls, grep output) must run locally and be embedded in the dispatch prompt before the plan reaches the provider. Without pre-attestation, reviewers consistently cite unverified claims.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
