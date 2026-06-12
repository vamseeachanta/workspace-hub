---
name: crossprovider hermes plan-review-fanout-artifacts-must-be-git-tracked
description: Plan-review fanout artifacts must be Git-tracked, not ephemeral
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-workflow, review-gate, artifact-preservation, multi-provider]
---

Multi-round adversarial reviews (r2, r3) on GitHub issues generate review outputs and consensus findings. If stored only locally, they are lost on context boundary or session end; preserve all review artifacts as committed files in `docs/plans/` or issue comments to enable cross-provider review consensus and post-hoc audit of decision rationale.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
