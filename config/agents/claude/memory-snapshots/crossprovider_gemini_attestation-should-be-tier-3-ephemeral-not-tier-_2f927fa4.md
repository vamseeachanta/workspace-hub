---
name: crossprovider gemini attestation-should-be-tier-3-ephemeral-not-tier-
description: Attestation should be tier-3 ephemeral, not tier-1 durable
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tier-assignment, ephemeral-artifacts, attestation]
---

Attestation is generated per-review run against a specific commit and sent to the provider; it should not be persisted as a tier-1 (authoritative) artifact. Saving attestation creates false durability and couples verification to a point-in-time. If the plan is amended, saved attestation becomes stale and misleading. Pattern: generate at dispatch, pass to provider, discard—if reproducibility needed, re-run attestation against pinned commit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
