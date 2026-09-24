---
name: crossprovider codex attested-evidence-overrides-plan-text-claims-in-
description: Attested evidence overrides plan-text claims in review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, verification]
---

When reviewing plans, attested evidence blocks (produced by `attest-plan-claims.sh` using `gh issue view`, `ls -la`, `git ls-tree` at a recorded commit SHA) are authoritative and override plan narrative claims. Contradictions between plan text and attestation should be flagged as findings; attestation-verified facts do not need re-verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
