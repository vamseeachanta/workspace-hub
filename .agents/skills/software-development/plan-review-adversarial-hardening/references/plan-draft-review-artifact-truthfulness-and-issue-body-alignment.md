# Archived Skill: `plan-draft-review-artifact-truthfulness-and-issue-body-alignment`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/plan-draft-review-artifact-truthfulness-and-issue-body-alignment`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/plan-draft-review-artifact-truthfulness-and-issue-body-alignment`
Consolidation date: 2026-04-29

---

---
name: plan-draft-review-artifact-truthfulness-and-issue-body-alignment
description: Keep plan drafts truthful during adversarial review loops by verifying real provider artifact state on disk and aligning the GitHub issue body to the bounded plan tranche before claiming approval-readiness.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [planning, review, github, issue-workflow, truthfulness]
---

# Plan draft review-artifact truthfulness and issue-body alignment

Use when:
- A GitHub issue plan is being iteratively hardened through multiple adversarial review waves
- Provider review artifacts are regenerated multiple times
- The issue body is broader than the bounded tranche the plan can honestly deliver
- Reviewers are flagging stale/misreported artifact state or plan-vs-issue scope mismatch

## Core lesson
Two things must stay truthful at all times during plan hardening:
1. The plan's review summary must match the actual provider artifacts on disk right now
2. The GitHub issue body must match the bounded tranche the plan is actually proposing

If either drifts, reviewers will keep returning MAJOR even when the technical plan is mostly sound.

## Required workflow

### 1. Verify provider artifact reality before summarizing it
Before updating `## Adversarial Review Summary`, inspect the actual files under `scripts/review/results/`.
Do not rely on memory or a prior turn summary.

Minimum checks:
- file exists
- file is non-empty
- read the artifact content and extract the real verdict
- if the artifact is empty, mark it INVALID rather than inventing findings

Practical rule:
- never summarize provider findings from a 0-byte artifact
- if a rerun times out or produces an empty file, say so explicitly
- if you need 3-provider review, do not lower the acceptance bar to 2 just to get unstuck unless the workflow/policy explicitly allows that

### 2. Align the issue body before trying to force plan approval
If the issue body sounds like full remediation, but the plan can only honestly deliver a bounded tranche, edit the GitHub issue body first.

Good pattern:
- change the issue body to say this tranche removes the current first blocker(s)
- explicitly say the work is expected to expose the next failure surface
- explicitly say broader debt remains in follow-up tracking

This removes the plan-vs-issue contradiction that reviewers will otherwise keep flagging.

### 3. Keep the success condition precise
Avoid vague phrases like:
- "meaningfully green"
- "advances past blockers"

Prefer:
- exact workflow/job/step names
- exact narrowed CI gate
- exact evidence expected after the run
- explicit statement whether the workflow is expected to be fully green or only to expose the next failure surface

### 4. For workflow-only verification, prefer deterministic inspection over brittle YAML-parsing pytest files
If the plan only needs to verify that a workflow keeps specific invariants, a deterministic command in the plan can be better than inventing workflow-specific pytest files.

Examples of good invariants:
- smoke step still appears before lint and mypy
- smoke command remains single-line/shell-neutral
- both flake8 commands use the intended target scope

But make the check strict enough:
- prefer counting exact occurrences instead of substring presence
- include the actual command block in the plan, not an ellipsis placeholder

### 5. Make local verification match the planned CI contract
If local evidence uses flags like `--follow-imports=silent` or extra stub packages, the plan must include those same flags/packages in the planned CI command.
Do not claim success on a different local command than the workflow will actually run.

### 6. Evidence all scope-boundary follow-up issues
If the plan says certain excluded surfaces are safely deferred to follow-up issues, embed live issue evidence for those issues:
- issue number
- title
- state

Do not just mention them prose-only.

If child/follow-up issues have already been created during an iterative hardening loop, update the plan from "Create issue #NNN" to "Link existing issue #NNN" and re-check live issue state before the next review. Stale create-language for already-created children is enough for adversarial reviewers to keep the plan in REQUEST_CHANGES.

### 7. Treat transient evidence as draft-only unless materialized
If a correctness-critical inventory or proof lives only in `/tmp`, a terminal buffer, or an uncommitted local file outside the target repo, label it as transient draft evidence. Do not present it as approval-grade evidence.

Good pattern:
- cite `/tmp/...` only as a local draft source
- require a durable raw/grouped inventory artifact in the relevant repo before child implementation approval
- if the target code is in a nested repo, name that repo/worktree explicitly and do not imply the workspace-hub root commit can carry nested-repo artifacts

### 8. After handoff triage, post a GitHub state-sync comment
When resuming from a handoff and tightening a plan without making it approval-ready, leave a short GitHub comment that states:
- the plan remains draft / not approval-ready
- what stale claims were corrected locally
- current provider verdicts / unavailable artifacts
- the next blocking action (usually fresh substantive adversarial re-review)

This prevents the GitHub thread from lagging behind local cleanup and stops later agents from treating old comments as current review state.

## Fast checklist before the next review wave
- [ ] Issue body matches the bounded tranche or parent/child closure contract
- [ ] Review summary matches actual artifact files on disk
- [ ] Empty/quota/unavailable artifacts are marked INVALID/UNAVAILABLE, not summarized as substantive reviews
- [ ] Success condition is explicit and falsifiable
- [ ] Local proof commands match planned CI commands
- [ ] Follow-up/child issues used as scope boundaries are evidenced with live state
- [ ] Already-created child issues are listed as existing links, not future creations
- [ ] Any `/tmp`/transient evidence has a required durable artifact path before approval
- [ ] Workflow verification commands are concrete and strict
- [ ] A GitHub state-sync comment was posted if local plan state changed but approval-readiness did not

## Anti-patterns to avoid
- Reusing stale review summary text after reruns
- Claiming a provider returned MAJOR/MINOR when its artifact is empty
- Letting the issue body promise full remediation while the plan only covers the next blocker-removal tranche
- Lowering review-evidence requirements ad hoc just because one provider is flaky
- Using `...` placeholders in acceptance commands that are supposed to be executable
