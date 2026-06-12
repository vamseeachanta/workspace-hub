---
name: crossprovider gemini attestation-payloads-are-ephemeral-tier-3-transi
description: Attestation payloads are ephemeral, tier-3 transient
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [review-workflow, harness, attestation-design]
---

Attestation output is generated fresh per review dispatch and lives only in transient tier-3 (not git-tracked, not durable). SHA256 hash the attestation payload text itself to enable dispatcher→reviewer cross-verification that saved artifacts match what was sent, without persisting attestation in git.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
