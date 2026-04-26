---
name: continuous-planning-pipeline
description: Maintain a standing day/night GitHub issue pipeline so agents always have planned, reviewed, user-approved work for overnight execution and next-day QA/approval.
version: 1.0.0
author: Hermes Agent
category: coordination
triggers:
  - User asks for continuous planning or continually working agents
  - User wants AFK / overnight issue throughput without queue starvation
  - User references maintaining a buffer of planned/reviewed/approved issues
related_skills:
  - gh-work-planning
  - overnight-parallel-agent-prompts
  - github-issues
  - multi-provider-adversarial-review
tags: [github, planning, overnight, afk-agents, issue-pipeline, adversarial-review]
---

# Continuous Planning Pipeline

Use this when the user wants agents to keep working continuously rather than running a one-off planning or implementation batch.

The core idea: maintain a standing buffer of GitHub issues in distinct readiness lanes so planning, implementation, review, and user approval can proceed in parallel across day/night cycles without violating plan gates.

## Operating model

### Day shift

- Intake and clarify issues.
- Perform resource intelligence.
- Draft canonical plans under `docs/plans/`.
- Run adversarial plan review.
- Prepare a focused user approval shortlist.
- QA overnight implementation artifacts / PRs.
- Create follow-up issues from blockers, QA findings, and deferred scope.

### Night shift

- Implement only issues that are truly execution-ready.
- If execution-ready work is insufficient, run planning-only workers instead.
- Run code/artifact adversarial review for every implementation output.
- Produce morning artifacts: approval shortlist, QA pack, blocker list, next-wave dispatch pack.

### Morning review

- User reviews QA artifacts and approval candidates.
- Approved plans move into the execution-ready lane.
- Revised/rejected plans go back to planning.
- The next overnight batch is launched from refreshed queue state.

## Queue lanes

Maintain three lanes in reports and prompt packs.

### Lane A — approval candidates

Issues ready for user approval / revision / rejection.

Required evidence:
- issue is open
- canonical plan exists, typically `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`
- adversarial review artifacts and synthesis exist
- latest valid review state has no MAJOR / FAIL / UNAVAILABLE blockers
- issue is labeled `status:plan-review` or otherwise clearly awaiting approval

### Lane B — execution-ready

Issues safe for unattended implementation.

Required evidence:
- issue is open
- issue has `status:plan-approved`
- canonical plan exists
- local approval marker exists and is committed, for example `.planning/plan-approved/NNN.md`
- worktree / repo state is clean or isolated
- target files are not owned by another active worker

Do not treat GitHub labels alone as sufficient approval.

### Lane C — planning feedstock

High-value issues eligible for planning-only workers.

Typical evidence:
- issue is open
- no current complete plan/review/approval evidence
- priority/domain labels indicate value
- no obvious duplicate or already-completed state
- safe to assign to planning workers that write unique artifacts

## Target buffers

For workspace-hub-style plan-gated repos, aim to maintain:

- 5-10 Lane A issues for morning user approval.
- 5-10 Lane B issues for overnight implementation.
- 10-20 Lane C issues for continuous planning.

If Lane B is empty, do not improvise implementation. Launch Lane C planning-only workers or Lane A approval-pack synthesis.

## Standard first response

When the user proposes a new continuous-throughput operating idea:

1. Check for existing related GitHub issues to avoid duplicates.
2. If no durable tracker exists, create or update a GitHub issue capturing the operating model.
3. Include the external reference if provided.
4. Encode lanes, target buffers, approval-surface checks, and adversarial-review requirements.
5. Verify the created/updated issue.
6. Save a compact durable user preference if it changes future behavior.

## GitHub issue body checklist

A durable pipeline issue should include:

- Summary of continuous planning / execution-readiness pipeline.
- Why the queue starves today.
- Day shift / night shift / morning review loop.
- Lane A/B/C definitions.
- Target buffers.
- Required artifacts for each lane.
- Acceptance criteria for a queue audit/report.
- Requirement to verify GitHub labels, canonical plan files, review artifacts, and local approval markers.
- Requirement for adversarial review at both plan-review and code/artifact-review stages.
- Links to related issues and workflows.

## Prompt-pack implications

Overnight prompt packs should state explicitly whether each worker is:

- implementation-only from Lane B,
- planning-only from Lane C,
- approval-pack synthesis from Lane A,
- QA / verify-close from overnight outputs.

Each worker still needs:

- self-contained context,
- allowed paths,
- forbidden paths / negative write boundaries,
- exact output artifact path,
- no user questions,
- no label changes unless explicitly authorized,
- adversarial review expectations.

## Pitfalls

- Treating a continuous pipeline request as a one-off overnight batch.
- Letting implementation agents pull from unapproved Lane C work.
- Trusting stale `status:plan-approved` labels without local marker and plan evidence.
- Failing to leave a focused morning approval/QA pack.
- Creating plans without a mechanism to keep the approval and execution buffers filled.
- Skipping follow-up issue creation for blockers and deferred scope discovered during QA.
