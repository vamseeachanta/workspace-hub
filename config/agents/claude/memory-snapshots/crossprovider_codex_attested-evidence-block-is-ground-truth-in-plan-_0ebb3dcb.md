---
name: crossprovider codex attested-evidence-block-is-ground-truth-in-plan-
description: Attested evidence block is ground truth in plan review
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review, evidence, attestation]
---

When a plan includes `## Attested Evidence` block (produced by `attest-plan-claims.sh`), treat plan claims as assertions to verify against the attestation. Attestation independently verifies file existence (`ls -la`) and issue state (`gh issue view`) at recorded commit SHA. Prefer attestation over plan text; cite contradictions as findings, not unverified claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
