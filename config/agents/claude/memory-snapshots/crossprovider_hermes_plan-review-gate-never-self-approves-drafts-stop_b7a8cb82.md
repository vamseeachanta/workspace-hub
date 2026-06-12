---
name: crossprovider hermes plan-review-gate-never-self-approves-drafts-stop
description: Plan-review gate never self-approves; drafts stop at status:plan-review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance-gates, plan-workflow, self-approval-ban]
---

Canonical plans stop at `status:plan-review` and never move to `status:plan-approved` by agents; user approval is required to progress. Codex is blocked (0.124 stdin regression since 2026-04-23); adversarial reviews route to Gemini + Claude-internal.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
