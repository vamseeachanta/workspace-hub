# Archived Skill: `plan-governance-vs-execution-boundary-for-adversarial-review`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/plan-governance-vs-execution-boundary-for-adversarial-review`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/plan-governance-vs-execution-boundary-for-adversarial-review`
Consolidation date: 2026-04-29

---

---
name: plan-governance-vs-execution-boundary-for-adversarial-review
description: Keep stale-approval/governance remediation out of execution-path pseudocode, TDD, files-to-change, and deliverable acceptance when hardening a GitHub issue plan under adversarial review.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, governance, adversarial-review, github, workspace-hub]
---

# Plan governance vs execution boundary for adversarial review

Use when a plan has stale approval-state drift (`status:plan-approved`, `.planning/plan-approved/*.md`, stale README row) and you are hardening the plan through repeated adversarial review waves.

## Core rule

Keep two concerns separate:
1. Deliverable/execution contract
2. Governance/review-state cleanup

If you mix them, adversarial reviewers will correctly flag the plan as internally inconsistent or unexecutable.

## What belongs in execution-path sections

These sections must talk only about the final deliverables and how implementation will validate them:
- `## Pseudocode` / `implement_with_tdd()`
- `validate_contract_docs()`
- `## Files to Change`
- `## TDD Test List`
- `## Acceptance Criteria`

Allowed content there:
- contract/checklist/doc requirements
- exact strings/thresholds/links the deliverables must contain
- test files to add/update
- target pytest commands
- discovery-surface updates like `docs/README.md`

Do NOT put these there:
- removing/relabeling GitHub `status:*` labels
- deleting/replacing `.planning/plan-approved/<issue>.md`
- review-artifact posting requirements
- tests that parse the plan text itself
- assertions about current branch/review/governance state
- conditional logic like "if fresh review still returns MAJOR..." inside implementation pseudocode

## What belongs in a separate governance section

Create a dedicated section such as:
- `## Governance Precondition Before Any Future Approval Reuse`

Put all stale-approval remediation there:
- stale live labels
- stale local approval markers
- review-artifact posting/state reconciliation
- README row hygiene as secondary to real approval gates

Explicitly label it as:
- a review/governance requirement
- not a TDD execution test

## If stale approval surfaces already exist

State the present-tense rule clearly:
- the live approval surfaces are already stale for this draft revision
- they must be removed, superseded, or revision-bound before the draft can be treated as approved again

If allowing revision-binding, require an immutable binding that names:
- exact approved plan file path
- exact approved plan git commit SHA or SHA256 hash
- exact approved review-artifact paths plus provider verdicts
- exact approval-storage surface used

## Evidence hardening pattern

When claiming approval drift, include concrete evidence in the plan itself:
- live label evidence from `gh issue view`
- local marker contents
- marker mtime
- current plan mtime
- latest provider verdicts

Avoid vague claims like "approval is stale" without the evidence mechanism.

## Common reviewer-triggering mistakes

Reviewers repeatedly flag these as MAJOR/MINOR:
- governance cleanup inside `implement_with_tdd()`
- governance assertions in `validate_contract_docs()`
- TDD rows expecting `plan text` as test input
- acceptance criteria that require review posting or label cleanup
- artifact-map table corruption during iterative edits
- stale review-summary text after the underlying issue was already fixed

## Safe structure

1. `Resource Intelligence Summary`
2. `Artifact Map`
3. `Deliverable`
4. `Pseudocode` — deliverables only
5. `Files to Change` — actual files only
6. `TDD Test List` — deliverable tests only
7. `Acceptance Criteria` — deliverable acceptance only
8. `Governance Precondition ...` — stale approval/review-state cleanup only
9. `Adversarial Review Summary`
10. `Risks and Open Questions`

## Verification checklist before rerun

Before sending the next adversarial review wave, verify:
- no governance items remain in Pseudocode/TDD/Acceptance
- no plan-text tests remain in the TDD list
- no pseudo-file/governance rows remain in Files to Change
- governance section contains all stale approval-surface cleanup
- review summary reflects the latest actual rerun, not older stale findings
- artifact map rows still render as valid markdown table rows
