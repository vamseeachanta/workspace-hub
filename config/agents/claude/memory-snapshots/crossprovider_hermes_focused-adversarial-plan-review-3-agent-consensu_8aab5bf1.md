---
name: crossprovider hermes focused-adversarial-plan-review-3-agent-consensu
description: Focused adversarial plan review: 3-agent consensus before user approval
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-workflow, gate-discipline, cross-provider]
---

For engineering-critical issues, run three independent adversarial reviews (Claude/Codex/Gemini); they surface non-overlapping defects. Move to user approval gate only after consensus (all three return APPROVE or MINOR with no blocking findings). Sessions on #2760 yielded APPROVE/APPROVE/MINOR consensus, allowing clean approval-gate transition.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
