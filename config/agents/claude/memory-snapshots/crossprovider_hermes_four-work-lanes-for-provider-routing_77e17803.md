---
name: crossprovider hermes four-work-lanes-for-provider-routing
description: Four work lanes for provider routing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [work-lanes, provider-routing, github-workflow]
---

Lane A (planning feedstock): unclear issues, capability gaps, stale hygiene. Lane B (plan review candidates): plan exists, reviewed, no MAJOR findings. Lane C (execution-ready): issue open, `status:plan-approved`, clean worktree, no collision. Lane D (QA/closeout): finished work needing verification. Provider fit varies by lane: Gemini for recon, Claude for synthesis, Codex for implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
