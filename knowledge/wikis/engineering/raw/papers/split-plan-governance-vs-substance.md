# Archived Skill: `split-plan-governance-vs-substance`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/split-plan-governance-vs-substance`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/split-plan-governance-vs-substance`
Consolidation date: 2026-04-29

---

---
name: split-plan-governance-vs-substance
description: When repeated adversarial plan reviews keep returning MAJOR findings about validator mechanics, evidence bookkeeping, or governance traceability rather than the core product or mission decision, stop tightening the monolithic plan and split it into a content/decision packet and a tooling/enforcement packet.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, adversarial-review, governance, plan-splitting, workspace-hub]
---

# Split a plan when MAJOR findings converge on governance, not substance

## When to use

Use this when a plan survives multiple adversarial review waves and:
- the core decision or scope is stable
- one provider starts treating it as substantively ready
- repeated Claude/Codex MAJOR findings keep focusing on:
  - validator semantics
  - review-artifact bookkeeping
  - evidence attestation
  - parser/test harness details
  - CI follow-up mechanics
  - self-referential plan-governance wording

This is a signal the plan is over-coupling two different concerns.

## Key pattern

Separate:
1. the normative/content decision
2. the enforcement/validator/governance machinery

Do NOT keep tightening the same monolithic plan indefinitely once MAJOR findings stop being about the business/architecture decision itself.

## Trigger criteria

Split when most of these are true:
- 3+ review waves already completed
- MAJOR findings are recurring but narrow to governance/tooling concerns
- the mission/content/architecture direction is no longer the disputed part
- the plan is accumulating bookkeeping complexity (many review waves, artifact tables, attestation caveats, validator semantics)
- continued iteration is creating self-referential governance churn

## Recommended split shape

### Packet A — normative contract / mission / content
Keep only:
- canonical contract or decision artifact
- document reconciliation
- glossary / non-goals / role map
- bounded cross-links required to make the contract navigable
- explicit deferrals for out-of-scope follow-ons

Remove from Packet A:
- advanced validator/parser semantics
- exhaustive review-wave bookkeeping as acceptance criteria
- CI enforcement requirements as approval blockers
- brittle invariance checks that are about implementation machinery, not decision quality

### Packet B — validator / governance enforcement
Move here:
- validator script design
- test harness design
- fixture coverage for parser/normalization behavior
- CI integration / hooks / enforcement follow-up
- immutable-file checks or attestation-heavy guardrails

## How to explain the split

Use wording like:
- "The remaining MAJOR findings are no longer about the core mission/architecture decision."
- "They are about enforcement mechanics, evidence bookkeeping, and validator semantics."
- "That means the plan should be split rather than tightened indefinitely."

## Practical execution steps

1. Review the latest provider artifacts and classify findings into:
   - substantive decision/content blockers
   - governance/enforcement/tooling blockers
2. If substantive blockers are mostly gone, stop rerunning the monolithic plan.
3. Write a short decision artifact explaining why the split is now higher leverage.
4. Draft Packet A from the stable decision/content material.
5. Draft Packet B from the validator/governance material.
6. Do not surface the original monolithic draft as approval-ready.

## Evidence from live use

Observed on workspace-hub issue `#1525` (workspace-hub mission/control-plane contract):
- repeated adversarial waves converged on MAJORs about:
  - review-wave bookkeeping
  - validator semantics
  - artifact/evidence consistency
  - AGENTS immutability enforcement
- while the underlying mission contract itself had become substantively stable
- correct response: recommend splitting into:
  - mission-contract packet
  - validator/enforcement packet

## Anti-pattern to avoid

Do not keep adding more validator semantics, review-artifact tables, and governance caveats to the same content plan after reviewers have stopped disputing the actual content decision. That increases fragility without increasing approval readiness.
