---
name: crossprovider codex attestation-preconditions-must-be-verified-befor
description: Attestation preconditions must be verified before approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gate, evidence, workspace-process]
---

If a plan's success depends on a specific artifact existing (uv.lock, index.jsonl, approval markers), the attested evidence block must confirm it on the target commit. Plans claiming 'repo has X' without attestation verification are approval-blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
