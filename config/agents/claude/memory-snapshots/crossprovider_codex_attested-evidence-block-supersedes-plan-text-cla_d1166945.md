---
name: crossprovider codex attested-evidence-block-supersedes-plan-text-cla
description: Attested Evidence block supersedes plan-text claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, attestation, plan-review]
---

When a plan review includes `## Attested Evidence` (produced by `scripts/review/attest-plan-claims.sh`), it independently verifies issue states via `gh issue view` and file existence via `ls -la` at a recorded commit SHA. Treat plan-asserted facts as claims to verify against the attestation block; if they contradict, cite the contradiction and rely on the attestation. Do not flag 'unverified claims' for facts already covered by attestation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
