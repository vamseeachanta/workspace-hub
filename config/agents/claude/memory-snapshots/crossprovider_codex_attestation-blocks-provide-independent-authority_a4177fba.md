---
name: crossprovider codex attestation-blocks-provide-independent-authority
description: Attestation blocks provide independent authority to break plan-vs-reality ties
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [verification, evidence, plan-review]
---

Use `scripts/review/attest-plan-claims.sh` to independently verify file existence and issue states at a specific commit. When a plan claims 'file X exists' or 'issue #N is CLOSED', prefer attestation results over plan text. Attestation is verified by shell output, not reinterpretation, making it the authority when conflicts arise.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
