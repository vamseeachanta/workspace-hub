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

## Fast checklist before the next review wave
- [ ] Issue body matches the bounded tranche
- [ ] Review summary matches actual artifact files on disk
- [ ] Empty artifacts are marked INVALID, not summarized
- [ ] Success condition is explicit and falsifiable
- [ ] Local proof commands match planned CI commands
- [ ] Follow-up issues used as scope boundaries are evidenced in the plan
- [ ] Workflow verification commands are concrete and strict

## Anti-patterns to avoid
- Reusing stale review summary text after reruns
- Claiming a provider returned MAJOR/MINOR when its artifact is empty
- Letting the issue body promise full remediation while the plan only covers the next blocker-removal tranche
- Lowering review-evidence requirements ad hoc just because one provider is flaky
- Using `...` placeholders in acceptance commands that are supposed to be executable
