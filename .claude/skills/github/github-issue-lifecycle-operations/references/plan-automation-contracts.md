# Archived Skill: `plan-automation-contracts`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-automation-contracts`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-automation-contracts`
Consolidation date: 2026-04-29

---

---
name: plan-automation-contracts
description: Tighten plans for scheduled/reporting workflows and multi-source detectors so adversarial review can verify runtime, publication, and normalization behavior.
version: 1.0.0
category: coordination
tags: [planning, review, automation, cron, reporting, data-contracts]
related_skills:
  - issue-planning-mode
  - gh-work-planning
---

# Plan Automation Contracts

Use when drafting or revising a plan that includes any of the following:
- scheduled tasks / cron jobs
- report generators that write files into the repo
- detectors that merge multiple inventories or registries
- coverage/comparison tooling where one record may appear in multiple sources
- workflows that may publish generated artifacts back to git

## Why this exists
A plan can be architecturally sound and still fail adversarial review if it leaves operational contracts implicit. In practice, reviewers will correctly reject plans that do not specify how runs behave when inputs are missing, when multiple inventories contain the same logical record, or when scheduled publication happens from a dirty checkout.

## Required contracts to include in the plan

### 1. Required-input prechecks
List the exact files/data that must exist before the run.
Examples:
- `test -f data/document-index/index.jsonl`
- `test -f data/design-codes/code-registry.yaml`

Do not claim a required artifact exists unless it is attested or otherwise verified. If existence is not durable enough to assert in the plan, turn it into a precheck in the manual/scheduled execution contract.

### 2. Exit-code contract
Define what exit codes mean for at least:
- clean success
- degraded-but-reportable success
- fail-closed / missing required inputs / schema failure

If the plan mentions `degraded` or `fail-closed`, it must state how those states surface in CLI exit behavior and how approval/readiness interprets them.

### 3. Multi-source dedup / merge policy
If the same logical record can appear in more than one source surface, specify:
- dedup key (usually canonical `doc_key`)
- which source wins for conflicting fields
- whether counts are computed before or after dedup
- whether duplicates become warnings, degraded diagnostics, or blockers

Without this, per-domain counts and gap reports are not trustworthy.

### 4. Cross-domain matching policy
If coverage is grouped by domain/bucket, explicitly define whether a match in the wrong domain counts as:
- covered
- gap
- degraded diagnostic / mismatch warning

A global key match without domain policy can silently corrupt per-domain reporting.

### 5. Source vs coverage vs reporting surfaces
Separate these explicitly:
- source-side gap candidates
- coverage-providing artifacts
- reporting/context aids

Do not mix them in one vague allowlist. Reviewers will flag boundary drift.

### 6. Publication semantics for generated artifacts
If scheduled execution writes repo files, define whether output is:
- local-only
- committed locally
- committed and pushed

If the task publishes back to git, also define safeguards:
- clean-worktree precondition
- single-run / locking / exclusivity rule
- what happens on dirty checkout or concurrent runner

### 7. Output-directory reconciliation
If the tool writes rolling outputs like `reports/<domain>.yaml`, specify:
- whether stale files are deleted
- which non-domain files are preserved (`README.md`, `_summary.md`, etc.)
- filename normalization / slugging rules

### 8. Heterogeneous-source field mapping
For each supplemental source, list the authoritative fields for:
- identity
- title
- source path/reference
- domain/discipline
- availability tier

If a field is absent, say whether that becomes `identity-unresolved`, `domain-unresolved`, degraded status, or fail-closed.

## Practical drafting pattern
When revising a plan after MAJOR review:
1. Extract every blocker into one of the contract buckets above.
2. Patch the plan text, not just the pseudocode comments.
3. Update the test list to prove the new contract.
4. Re-run adversarial review.
5. Keep the issue out of `status:plan-review` until the new wave is no longer MAJOR.

## Common failure patterns
- claiming current-state inputs exist without attested evidence
- saying an input is optional while also relying on it for completeness-critical counts
- leaving `degraded` mentioned but undefined
- handling duplicate wiki keys or duplicate source records only partially
- publishing scheduled reports without defining clean-worktree or locking behavior
- using one field name in internal records and another in output schema without mapping

## Minimal checklist
Before sending a plan for review, ask:
- Are required inputs prechecked?
- Are clean/degraded/fail-closed exit codes defined?
- Is dedup/merge policy explicit?
- Is cross-domain matching policy explicit?
- Are scheduled publication safeguards explicit?
- Are output cleanup/preservation rules explicit?

If any answer is no, the plan is probably not ready for adversarial review.
