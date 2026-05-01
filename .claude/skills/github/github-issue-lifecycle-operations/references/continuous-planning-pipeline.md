# Archived Skill: `continuous-planning-pipeline`

Original path: `/home/vamsee/.hermes/skills/coordination/continuous-planning-pipeline`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/continuous-planning-pipeline`
Consolidation date: 2026-04-29

---

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

Maintain these lanes in reports and prompt packs.

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

Do not treat GitHub labels alone as sufficient approval. Verify marker evidence from a checkout that is current with the execution base: after `git fetch`, if the active worktree is behind `origin/main`, inspect `origin/main` directly or create/freshen an isolated worktree before declaring a marker missing. A stale governance worktree can undercount committed `.planning/plan-approved/NNN.md` files and misroute approved work back to approval drift. If a workflow uses revision-bound approval comments/plan branches instead of local numeric markers, treat that as `approval-drift` unless/until the repo hooks and approval scripts have an approved policy recognizing that exact schema. Remote routine state or session transcripts never upgrade an issue into Lane B.

### Lane C — planning feedstock

High-value issues eligible for planning-only workers.

Typical evidence:
- issue is open
- no current complete plan/review/approval evidence
- priority/domain labels indicate value
- no obvious duplicate or already-completed state
- safe to assign to planning workers that write unique artifacts

### Lane D — active dispatch / execution state

Issues already scheduled or running must be excluded from new implementation dispatch until reconciled. Do not use one overloaded `active` bucket; track sub-states:
- D1 `scheduled`: routine/cron created but no start evidence yet
- D2 `running`: start comment or heartbeat exists
- D3 `blocked` / `failed` / `no-fire` / `stale`: requires morning-loop decision before requeue

Each dispatch needs a durable idempotency key, routine/job id, owner, scheduled/start/last-seen timestamps, dependency gates, lease scope, and expected output. Remote trigger state must be mirrored into GitHub/repo artifacts; it is not source-of-truth by itself.

### Lane E — implementation QA / review

Implementation output exists but is not done. Sub-states:
- E1 `open-pr`: branch/PR exists but QA handoff is incomplete
- E2 `review-ready`: mandatory handoff exists and item is ready for human/provider review

Required Lane E handoff fields: issue, PR/branch, dispatch id, routine id, plan path/SHA, approval marker, changed files, tests/CI results, artifacts/screenshots where relevant, risks, blockers, adversarial implementation-review status, recommended human action, estimated review effort, and priority reason.

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

## Visualization / confidence artifact

When the user asks for confidence in the lane model or approval flow, produce a compact ASCII flowchart and post it to the durable GitHub issue using `--body-file`.

Recommended sections:
- full continuous pipeline from user idea/intake through Lane C planning feedstock, planning pipeline, Lane A approval candidates, Lane B execution-ready work, TDD execution, code/artifact review, morning QA, close/follow-up/refill
- compact lane view: `Lane C -> Scope/Resource Intel/Repo Intel/Compliance Fit/Plan/TDD/Plan Review -> Lane A -> user approval -> Lane B -> TDD Implementation/Code Review/Morning QA`
- confidence gates:
  - Can we plan? requires scope + resource intel + repo intel
  - Can user approve? requires plan + TDD path + adversarial plan review
  - Can agent implement? requires `status:plan-approved` + local marker + clean/isolated worktree
  - Can we trust result? requires tests + committed diff + adversarial code/artifact review
  - Can user close/accept? requires morning QA packet + evidence + follow-up capture

This visual artifact helps the user validate the workflow contract before implementation and is useful as a review target in the issue thread.

## Next-step pattern after concept approval

If the user says the model looks good and asks for the next logical step, start formal planning on the pipeline issue rather than jumping to code. Post a concise planning-intake comment with:
- complexity classification, typically T3 for workflow/governance + automation/reporting
- primary deliverable
- key constraints: hard-stop gates, TDD, adversarial plan/code review, explicit user approval, local approval markers, zero git contention
- next step: resource intelligence across workflow docs, scripts, hooks, plan artifacts, and related issues

Then proceed through `gh-work-planning` Step 2 resource intelligence and canonical plan drafting.

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

## Plan-review artifact validation

For continuous-planning issues, do not treat a plan-review fanout run as valid merely because the wrapper exits 0 or writes a disagreement report.

Before moving an issue to `status:plan-review`, verify:
- the canonical plan file exists from the same shell/filesystem context that will run review tooling
- the plan index row exists exactly once in `docs/plans/README.md`
- provider-specific review artifacts exist for the intended issue/date, for example:
  - `scripts/review/results/YYYY-MM-DD-plan-NNN-claude.md`
  - `scripts/review/results/YYYY-MM-DD-plan-NNN-codex.md`
  - `scripts/review/results/YYYY-MM-DD-plan-NNN-gemini.md`
- each provider artifact contains a real verdict/findings section, not an empty or unavailable stub
- each provider artifact is bound to the current plan revision when possible, preferably with a `Plan-SHA256: <sha256sum-of-canonical-plan>` header
- the disagreement/synthesis artifact references those provider results and the same `Plan-SHA256`

Failure mode seen in live use: `scripts/review/plan-review-fanout.sh` returned success and wrote only `YYYY-MM-DD-plan-NNN-disagreement.md`, with an empty provider table and no Claude/Codex/Gemini artifacts. Treat that as `INVALID / INCOMPLETE REVIEW RUN`, preserve that fact in the artifact, and rerun through a side-effect-safe path before applying `status:plan-review`.

When the fanout path is unreliable, use a manual side-effect-safe rerun pattern:
1. Compute the canonical plan SHA: `sha256sum docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`.
2. Build a fresh reviewer prompt from the current on-disk plan; do not reuse an old prompt.
3. Run Claude/Codex/Gemini in read-only or side-effect-safe review mode and save provider-specific artifacts.
4. Add `Plan-SHA256: <sha>` and an explicit `## Verdict` block to every provider artifact.
5. Write a disagreement/synthesis artifact with the same plan SHA and final gate decision.
6. Re-check all provider artifacts are non-empty, current-SHA tagged, and have verdicts of `APPROVE` or `MINOR` before posting the issue update or applying `status:plan-review`.

If file writes appear inconsistent between file tools and shell tools, immediately re-check with shell commands from the repo root before dispatching review:
- `pwd`
- `git status --short`
- `test -f docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`
- `grep -n 'issue-NNN-<slug>' docs/plans/README.md`

## Material revision / approval-drift closeout

When a continuous-pipeline plan is materially revised after cross-review or after comparing it with another autonomous-agent workflow, treat all prior approval/readiness state as potentially stale until resynced.

Required closeout pattern:

1. Revise the canonical plan first, then rerun adversarial review from the latest on-disk plan.
2. If a first rerun returns MAJOR findings, patch the plan and rerun again; do not preserve the old `status:plan-review` or approval narrative as if it still applies.
3. Sync all three surfaces before posting back to GitHub:
   - canonical plan `## Adversarial Review Summary`
   - provider artifacts under `scripts/review/results/`
   - issue labels/comment state
4. If updating the plan's review-summary section after reviewers have already reviewed the substantive plan, the final plan SHA may differ from the reviewed-substance SHA. Make that explicit in artifacts with both fields, for example:
   - `Reviewed-Plan-SHA256: <sha-reviewed-by-providers>`
   - `Plan-SHA256: <final-sha-after-summary-sync>`
   - short note that the final SHA differs only due to review-summary synchronization
5. If the issue currently has `status:plan-approved` but no valid committed `.planning/plan-approved/NNN.md`, and the plan has materially changed, remove `status:plan-approved` and restore `status:plan-review`. This is approval drift, not execution authority.
6. Post the final GitHub update with explicit decision choices: Approve / Revise / Hold, and state that implementation remains blocked until explicit user approval plus marker creation.
7. Commit only the target plan/review files; in dirty repos verify the targeted artifact set with `git status --short -- <files>` and ensure no unrelated churn is staged.

## Exit handoff / future issue pattern

When the user asks to “create future issues, document, and prepare to exit” after a continuous-pipeline plan-review wave:

1. Convert remaining MINOR review findings and deferred control-plane risks into concrete follow-up GitHub issues. Use `gh issue create --body-file`; do not post markdown-rich bodies inline.
2. Verify duplicates first with a broad `gh issue list --state all --search ...`, but do not block creation just because the parent pipeline issue appears in the search results.
3. Recommended follow-up issue families from a matured continuous-work pipeline:
   - review-artifact metadata / stale-SHA handling
   - canonical approval-request comment schema and backfill
   - dispatch-ledger trust contract and lease lifecycle writer
   - golden-output contract for morning approval / QA packet
   - Lane E implementation handoff readiness validator
4. Write a durable exit handoff under `docs/reports/` summarizing:
   - parent issue and current status label
   - plan SHA and latest plan/review commit
   - review artifact verdicts
   - approval-marker state
   - newly created follow-up issue links
   - next restart sequence
   - explicit “do not implement until approval marker exists” warning
5. Commit and push the handoff as a narrow docs-only commit. In dirty repos, preserve unrelated churn with stashes rather than forcing it into the handoff commit.
6. Post the handoff summary back to the parent issue using `--body-file`, then immediately re-verify parent labels and marker state. Automation or concurrent agents may re-add `status:plan-approved`; if no valid committed marker exists after a material revision, restore `status:plan-review`.
7. Final exit verification should report: HEAD/upstream equality, working-tree cleanliness or named stashes preserving unrelated dirt, parent labels, marker presence/absence, and follow-up issue URLs.

## Capability / data-readiness audit batch pattern

When the user asks to revisit repo features/issues to understand capabilities, data completeness, scheduler/source readiness, or what work can run overnight, treat it as a **planning/audit batch**, not implementation.

Recommended workflow:
1. Inspect live repo state first: `git status`, `gh repo view`, `gh issue list --state open`, labels, existing `docs/plans/`, review artifacts, and `.planning/plan-approved/` markers.
2. Ground the audit in repo artifacts before creating issues: README, module/capability indexes, manifest files, data catalogs, source-tree module directories, tests, docs, examples/notebooks, scheduler configs, and refresh scripts.
3. Compare advertised capabilities against live evidence. Explicitly record mismatches such as "module index says N modules, data catalog contains M modules", empty/sample-only datasets, stale docs, missing scheduler coverage, or public CLI examples that require data/credentials.
4. Create a small set of bounded audit/planning issues rather than one broad umbrella. Useful issue families:
   - capability/module readiness matrix
   - data completeness and freshness scorecard
   - scheduler/source-refresh runtime readiness matrix
   - CLI/examples/notebook smoke matrix
5. For each audit issue, define durable report outputs under `docs/reports/`, a machine-readable companion artifact when useful, acceptance criteria with explicit evidence paths, and a strict boundary of "no implementation / no unbounded downloads" unless separately approved.
6. Write and commit a single overnight handoff report under `docs/reports/` containing:
   - new issue links
   - existing high-value issues to revisit
   - evidence anchors from repo inspection
   - per-worker self-contained prompts
   - guardrails for approvals, unbounded downloads, data credentials, and runtime-vs-repo remediation splits
7. Post a concise comment to each new audit issue linking the handoff artifact, then verify issue URLs, labels, comment presence, clean/pushed git state, and report existence.

Important guardrails:
- A GitHub `status:plan-approved` label without a committed `.planning/plan-approved/<issue>.md` marker remains approval drift, not unattended execution authority.
- For data-heavy repos, classify long refresh commands before running them: no-op audit, endpoint probe, bounded sample, full refresh, credential-blocked, or unsafe/unbounded.
- After a scheduler/source-readiness audit, run only safe follow-up probes before any full refresh: trivial interpreter startup, CLI `--help`/`status`/config validation, bounded endpoint HEAD/GET calls, and explicitly time-boxed dry-runs. Prefer a small Python subprocess runner with per-command timeouts and a durable markdown report over one Bash script with a single outer timeout; otherwise the first hung import/CLI call can block the whole evidence pack.
- If even trivial `uv run python` or scheduler import/no-op commands time out, create a blocker issue for local execution/import readiness and keep refresh/implementation work blocked until that is diagnosed. Do not spend overnight cycles on full refreshes while no-op commands hang.
- If the audit discovers fixable bugs, create/link follow-up issues or draft plans; do not silently patch code from an audit-only batch.
- Keep prompt packs self-contained so overnight workers do not need current-chat context.

## Pitfalls

- Treating a continuous pipeline request as a one-off overnight batch.
- Letting implementation agents pull from unapproved Lane C work.
- Trusting stale `status:plan-approved` labels without local marker and plan evidence.
- Treating an empty disagreement report as a valid adversarial plan-review pass.
- Applying `status:plan-review` before provider-specific review artifacts exist and contain real verdicts.
- Failing to leave a focused morning approval/QA pack.
- Creating plans without a mechanism to keep the approval and execution buffers filled.
- Skipping follow-up issue creation for blockers and deferred scope discovered during QA.
