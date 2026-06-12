---
name: crossprovider hermes multi-provider-review-verdicts-require-synthesis
description: Multi-provider review verdicts require synthesis; disagreement artifact is the primary signal
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, multi-provider, review-synthesis, plan-review]
---

Claude, Codex, and Gemini reviews of #2665 each identified non-overlapping defect classes (governance/approval, concurrency, schema/TDD-alignment). No single provider verdict was authoritative; synthesis of all three verdicts plus the disagreement artifact was necessary to identify true blockers. Dispatch all three in parallel and treat the consolidated disagreement artifact, not individual verdicts, as the decision input.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
