---
name: crossprovider codex attested-evidence-pattern-for-plan-verification
description: Attested Evidence pattern for plan verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, verification, correctness-gate]
---

Use `scripts/review/attest-plan-claims.sh` to verify plan facts (issue states, file existence) at review dispatch time; include attestation payload with sha256 integrity check. Reviewers strongly prefer attested evidence over plan-text assertions. Plans that contradict attestation are treated as claims requiring fixes, not facts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
