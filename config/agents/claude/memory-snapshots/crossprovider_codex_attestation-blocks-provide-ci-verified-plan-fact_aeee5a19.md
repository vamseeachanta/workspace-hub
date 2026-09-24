---
name: crossprovider codex attestation-blocks-provide-ci-verified-plan-fact
description: Attestation blocks provide CI-verified plan facts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, attestation, evidence-authority]
---

Plan review attestation blocks (produced by independent script at dispatch time) independently verify issue states and file existence via `gh` and `ls`, shifting burden from unverifiable plan-text claims to CI-verified evidence. Contradictions between plan text and attestation are strong signals for review findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
