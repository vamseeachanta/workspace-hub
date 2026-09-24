---
name: crossprovider codex attestation-driven-review-verify-plan-claims-aga
description: Attestation-driven review: verify plan claims against live repo state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, verification, process]
---

When reviewing plans, use `gh issue view` and `ls -la` to independently verify plan assertions about issue state and file existence rather than trusting plan text. Contradictions between plan assertions and attested evidence are findings. This prevents stale review cycles on outdated claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
