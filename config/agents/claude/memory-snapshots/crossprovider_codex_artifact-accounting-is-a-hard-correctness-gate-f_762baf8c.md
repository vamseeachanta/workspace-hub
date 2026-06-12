---
name: crossprovider codex artifact-accounting-is-a-hard-correctness-gate-f
description: Artifact accounting is a hard correctness gate for plan approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, evidence, approval-gates]
---

Plans that misreport provider review-artifact state (e.g., claiming Codex artifact is valid when attested `ls` evidence shows 0 bytes) fail approval. Attested file-existence evidence from `ls -la` is the source of truth, not the plan's assertion about which artifact is 'latest valid' or empty.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
