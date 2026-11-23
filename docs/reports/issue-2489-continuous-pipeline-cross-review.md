# Cross-review synthesis for #2489: continuous work pipeline + Claude autonomous wave

> Date: 2026-04-26
> Scope: Cross-review the #2489 continuous-planning pipeline against the ongoing Claude autonomous routine wave, then propose a combined operating model for continuous AFK throughput.
> Status: draft synthesis for adversarial cross-review; not an implementation change; does not approve #2489.

## 1. Evidence reviewed

### #2489 continuous planning pipeline

- Issue: https://github.com/vamseeachanta/workspace-hub/issues/2489
- Current state: open, `status:plan-review`.
- Canonical plan: `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md`.
- Final plan SHA: `b6747b140e7076bd059965f30d4f955974262d0a621b9fcc1718c8aa37055e2c`.
- Final plan review: Claude `MINOR`, Codex `MINOR`, Gemini `APPROVE`; no MAJOR blockers.
- Core contract: classify issues into Lane A/B/C with evidence checks; labels alone never authorize implementation; implementation remains blocked until explicit user approval and local `.planning/plan-approved/<issue>.md` marker.

### Claude autonomous wave observed in session `565cae05-779f-49b7-9225-34a1444fdbef`

- The Claude session scheduled a wave of one-shot remote routines and recurring routines using Anthropic remote triggers.
- Representative wave routines:
  - 13:00 UTC: execute #2471 v3.
  - 16:00 UTC: check #2471 PR state.
  - 17:00 UTC: execute #2126 v6.
  - 18:00 UTC: execute #2369 v5.
  - 19:00 UTC: execute #2124 v3, critical path for #2103.
  - 20:00 UTC: execute #2227 v5.
  - 21:00 UTC: execute #2373 v3.
  - 22:30 UTC: end-of-day wrap-up consolidating issue/PR outcomes and drafting a fresh handoff.
  - 2026-04-27 13:00 UTC: extract learnings from the planning session.
  - 2026-04-27 14:00 UTC: execute #2125 v3, gated on #2124 merge.
- Recurring routines include a weekly plan-drainer and weekly intake triage.
- Claude's own summary says each routine prompt encodes gate logic, upstream merge checks, SHA verification, drift detection, safe checkout via `git switch --discard-changes`, and an end-of-day live-state wrap-up.

### Live state spot checks at synthesis time

- #2471 has an open PR: https://github.com/vamseeachanta/workspace-hub/pull/2492.
- #2471 issue comment shows execution started and completed, but its generated timestamp literal is `2026-04-26T00:00:00Z`, confirming Claude's noted cosmetic template bug.
- Several wave issues have `status:plan-approved` labels and approval comments, but no simple numeric `.planning/plan-approved/<issue>.md` marker was visible for #2471/#2126/#2369/#2124/#2227/#2373/#2125 on current `main`. This may be because the wave uses revision-bound approval comments/branches and #2460 rules; nevertheless it is a critical gap for any automated Lane B classifier that expects local numeric markers.
- Some issues have no local canonical plan file discoverable by `docs/plans/*issue-<n>-*.md` from current `main`, even though issue comments reference plan branches/SHAs. That implies the pipeline must support both main-committed plan evidence and revision-bound plan-branch evidence, or else it must explicitly exclude such issues from Lane B.

## 2. Cross-review: what Claude's wave gets right

1. **Executor-side gating is concrete.** The routine prompts do not merely say "execute approved work"; they specify upstream merge checks, SHA verification, branch/plan revision identity, and skip/block behavior.
2. **Pacing is staged.** Runs are spaced across the day/night window, avoiding front-loaded quota burn and reducing git contention.
3. **End-of-day wrap-up is essential.** The 22:30 UTC wrap-up agent re-derives live PR/issue state and writes a handoff, which is exactly what a continuous pipeline needs for next-day review.
4. **Dependency awareness exists.** #2125 is gated on #2124; #2124 is critical path for #2103; several routines gate on #2471.
5. **Failure categories are explicit.** The wrap-up classifies MERGED / OPEN-PR / BLOCKED / NO-FIRE / MID-EXEC / N/A, which is stronger than a vague progress summary.

## 3. Cross-review: what Claude's wave does not solve by itself

1. **It is a scheduled wave, not a self-refilling queue.** The wave drains a known list of approved issues. It does not continuously maintain Lane A/B/C buffers.
2. **Approval evidence is not normalized.** The routines use revision-bound comments/SHAs, while #2489's v1 Lane B model expects local committed approval markers. Without a compatibility contract, one agent may call work execution-ready while another blocks it.
3. **Remote-trigger state is outside GitHub.** Trigger IDs, schedules, and prompts live in the remote routine system and session transcripts. GitHub Issues see only comments after execution starts/completes. The durable coordination layer is therefore incomplete unless the schedule ledger is mirrored into repo/GitHub artifacts.
4. **No central lease/lock ledger.** Safe checkout reduces local contamination, but it does not prevent two remote agents from choosing overlapping files/issues unless the prompt itself is perfectly scoped.
5. **Code/artifact review after implementation is not guaranteed by the schedule alone.** The wave can open PRs, but a separate review lane must ensure post-implementation adversarial review and morning QA before closure.
6. **Template drift has already occurred.** The literal `2026-04-26T00:00:00Z` timestamp bug is cosmetic, but it proves prompts are generated manually enough to drift.
7. **GitHub PR search by issue number can be noisy.** A search for `#2227` surfaced the #2471 PR because the PR body references #2227. Wrap-up logic must distinguish direct execution PRs from incidental references, preferably by branch naming, title pattern, and execution-start comments.

## 4. Recommended integrated solution: Control Tower + Evidence Classifier + Executors

The good solution is not to replace Claude's autonomous routines with #2489, nor to let routines bypass #2489. Use a layered control-tower model:

### Layer 0 — Source of truth: GitHub + repo evidence

GitHub Issues remain the durable coordination layer. Repo evidence remains the local truth for plan files, review artifacts, and approval markers. Remote trigger state is operational state that must be mirrored back into a GitHub/repo ledger.

### Layer 1 — Evidence-aware queue classifier (from #2489)

A read-only classifier produces the live lanes:

- **Lane A / approval candidates:** open issue + canonical/revision-bound plan evidence + current adversarial plan review with no MAJOR blockers + awaiting user approval.
- **Lane B / execution-ready:** open issue + `status:plan-approved` + explicit user approval evidence + approval marker or validated revision-bound approval record + current plan/review evidence + no stale/dual-state warnings + no active lease conflict.
- **Lane C / planning feedstock:** open high-value issue lacking enough plan/review/approval evidence but safe for planning-only workers.
- **Lane D / active execution:** issue has an active remote routine, active branch/PR, or active lease; excluded from new dispatch until wrap-up resolves it.
- **Lane E / QA-review:** implementation PR/branch exists and needs tests, adversarial code/artifact review, merge/close decision, or follow-up creation.

The #2489 plan should keep v1 read-only, but the steady-state design should explicitly include Lane D/E so autonomous routines do not disappear from the queue model after dispatch.

### Layer 2 — Dispatch planner

A dispatch planner consumes the classifier report and creates one of four prompt packs:

1. Lane B implementation pack: only for issues with normalized approval evidence and no active lease.
2. Lane C planning-only pack: draft plans and resource intel, no implementation.
3. Lane A approval pack: concise user review shortlist with risk/impact and links.
4. Lane E QA pack: review PRs/branches produced by overnight agents, run tests, request adversarial implementation review, create follow-ups.

The planner should pace jobs across the available window and preserve Codex for daytime interactive work when requested.

### Layer 3 — Executor routines

Claude remote routines are a good executor backend, but should be launched only from the dispatch planner. Each routine prompt must include:

- issue number, exact plan path or plan branch+SHA,
- exact approval evidence and marker/revision-bound approval record,
- expected branch name and file boundaries,
- dependency gates and live re-check commands,
- active lease creation/comment behavior,
- TDD-first steps,
- mandatory post-implementation summary with PR/branch link,
- mandatory code/artifact review handoff.

### Layer 4 — Schedule/lease ledger

Add a durable ledger artifact so tomorrow's agents and humans do not need to mine Claude transcripts to know what was scheduled:

- `docs/reports/continuous-work/dispatch-ledger-YYYY-MM-DD.md` for human-readable schedule and outcomes.
- `docs/reports/continuous-work/dispatch-ledger-YYYY-MM-DD.json` for machine-readable routine IDs, issue IDs, scheduled time, lane source, gates, expected output, and observed outcome.
- GitHub comments on parent/issue with routine IDs and schedule.

A minimal ledger row:

| Field | Meaning |
|---|---|
| `issue` | GitHub issue number |
| `lane_source` | B implementation / C planning / A approval-pack / E QA |
| `routine_id` | remote trigger ID or local cron job ID |
| `scheduled_at_utc` | planned fire time |
| `required_plan_sha` | exact plan/revision SHA |
| `approval_evidence` | marker path or revision-bound approval comment URL |
| `lease_scope` | files/modules/issue dependencies locked by this run |
| `expected_output` | PR, branch, comment, plan file, review artifact, handoff |
| `observed_outcome` | pending / merged / open-pr / blocked / no-fire / mid-exec |

### Layer 5 — Morning control loop

Every morning/day-start run:

1. Rebuild lanes from live evidence.
2. Reconcile dispatch ledger outcomes with GitHub issue/PR state.
3. Produce:
   - user approval shortlist from Lane A,
   - QA/review shortlist from Lane E,
   - blocker list from failed routines,
   - next-night dispatch candidates from Lane B,
   - planning candidates from Lane C.
4. File or reopen follow-up issues for systemic defects, not every symptom.
5. Never implement unapproved work to keep agents busy; if Lane B is empty, run planning/QA only.

## 5. Immediate policy refinements for #2489 before next step

1. **Add Lane D/E to the conceptual model.** #2489 currently captures A/B/C; Claude's wave proves active execution and QA-review are first-class states.
2. **Normalize revision-bound approval evidence.** Either require `.planning/plan-approved/<issue>.md` for every Lane B item, or define a validated alternative for plan-branch/approval-comment/commit-SHA evidence. Do not let both coexist ambiguously.
3. **Mirror remote routine state.** A dispatch ledger is mandatory for continuous operations; session transcripts are not a sufficient source of truth.
4. **Lease before dispatch.** Use issue comments/labels or ledger entries to mark active execution and prevent duplicate scheduling.
5. **Separate scheduler from classifier.** The classifier remains read-only; the scheduler/dispatcher is a separate, explicit action that can be reviewed and gated.
6. **Treat scheduled waves as outputs of the pipeline, not the pipeline itself.** Claude's wave is the execution backend; #2489 is the governance/control plane.
7. **Make morning QA unavoidable.** Every implementation output transitions to Lane E until tests, artifact review, and user review are complete.

## 6. Proposed next step after adversarial review

If this synthesis survives adversarial cross-review, revise #2489's plan or add a follow-up comment to incorporate:

- Lane D active-execution and Lane E QA-review.
- Dispatch ledger artifact schema.
- Revision-bound approval compatibility rules.
- Active lease/conflict model.
- Morning control-loop report requirements.

Then ask the user to approve the updated #2489 plan for implementation. Do not create `.planning/plan-approved/2489.md` or implement until approval is explicit.


---

# Revision after adversarial cross-review

Adversarial reviewers returned **MAJOR** on the first synthesis. The direction was accepted, but the first draft was not approval-ready because it left authority, lease, durable scheduler state, approval normalization, and morning QA too vague. This section supersedes any looser language above.

## A. Non-negotiable authority model

The continuous-work control tower must use this precedence order:

1. **Repo hard gates and hooks** are authoritative for whether implementation is allowed.
2. **GitHub issue state** is the durable coordination surface for user-facing status.
3. **Repo-tracked plan/review/approval evidence** is authoritative for Lane A/B readiness.
4. **Dispatch ledger** is an operational mirror of scheduled/running work, not approval authority.
5. **Remote trigger state** is never authoritative by itself; it must be mirrored into GitHub/repo artifacts.

Consequence: a remote routine may execute only if the repo-recognized approval contract is satisfied. A remote trigger, handoff note, or old session transcript cannot upgrade an issue into Lane B.

## B. Single approval-evidence contract for Lane B

For #2489 v1, Lane B must require a committed numeric local marker:

- `.planning/plan-approved/<issue>.md`

Revision-bound approval comments/plan branches may be reported as **approval-evidence-incomplete**, but must not authorize automated Lane B execution until one of these happens:

1. the local marker is created and committed, or
2. a separate approved policy issue extends `require-plan-approval.sh` / hooks to recognize a specific revision-bound approval schema.

A valid marker must bind to:

- issue number,
- plan file path or plan branch,
- plan commit/SHA or `Plan-SHA256`,
- user approval comment URL or explicit approval timestamp,
- approving user/source,
- marker commit SHA.

Any issue with `status:plan-approved` but no valid marker is **not Lane B**; it is **approval-drift** and should go to a reconciliation queue.

## C. Durable dispatch state machine

The dispatch ledger is advisory/operational, but mandatory for observability. It must use explicit states:

| State | Meaning | Next valid states |
|---|---|---|
| `candidate` | selected from Lane B/C/A/E but not scheduled | `scheduled`, `rejected` |
| `scheduled` | routine/cron created; not yet known fired | `running`, `no-fire`, `cancelled`, `superseded` |
| `running` | routine posted start comment or heartbeat | `blocked`, `open-pr`, `completed-no-pr`, `failed`, `stale` |
| `blocked` | dependency/gate stopped execution safely | `candidate`, `superseded`, `closed` |
| `open-pr` | PR/branch produced; needs Lane E QA | `qa-ready`, `merged`, `needs-fix`, `closed` |
| `qa-ready` | Lane E handoff complete and reviewable | `merged`, `needs-fix`, `closed` |
| `failed` | routine crashed or produced unusable output | `candidate`, `superseded`, `closed` |
| `no-fire` | schedule time passed without start evidence | `candidate`, `cancelled`, `superseded` |
| `stale` | no heartbeat/update beyond TTL | `candidate`, `superseded`, `closed` |

Required machine fields:

- `dispatch_id` stable idempotency key: `<date>-<issue>-<lane>-<attempt>`.
- `issue`, `lane_source`, `state`, `owner`, `routine_id`.
- `created_at_utc`, `scheduled_at_utc`, `started_at_utc`, `last_seen_at_utc`, `finished_at_utc`.
- `attempt`, `max_attempts`, `supersedes`, `superseded_by`.
- `required_plan_sha`, `approval_marker`, `approval_comment_url`.
- `dependency_gates` with issue/PR/state predicates.
- `lease_scope`, `expected_output`, `observed_output`, `outcome_comment_url`, `pr_url`.

## D. Lease lifecycle

A lease is not a label-only hint. It is a ledger row plus a GitHub start comment.

Lease acquisition:

1. Rebuild live lanes.
2. Verify Lane B approval marker or Lane C/A/E non-implementation mode.
3. Check no non-terminal ledger row exists for same issue or overlapping `lease_scope`.
4. Write/update dispatch ledger row to `scheduled` with owner and TTL.
5. Post dispatch/start comment to the issue with `dispatch_id`, owner, scheduled time, and expected output.

Lease TTL defaults:

- scheduled but no start evidence: stale after 45 minutes past scheduled time.
- running implementation: heartbeat required every 2 hours or stale.
- open PR: leaves execution lease and enters Lane E; no new implementation dispatch until QA resolves.

Lease release:

- `blocked`, `failed`, `no-fire`, or `stale` rows require a morning control-loop decision before requeue.
- `open-pr` releases implementation lease but creates Lane E QA obligation.
- `merged` or `closed` terminates the lease.

Conflict rule: issue-level conflicts block dispatch; file/module `lease_scope` conflicts block dispatch unless the scope is explicitly read-only planning/QA.

## E. Dependency requeue rules

Dependency gates are not one-shot skips. A blocked dependency must produce a deterministic next action:

- If upstream PR is open: `blocked`, recheck after upstream PR update or next morning loop.
- If upstream merged late: requeue as `candidate` for the next dispatch window.
- If upstream closed unmerged: send to Lane C replanning or Lane A user decision, not implementation.
- If dependency state is ambiguous: block, do not infer readiness.

## F. Lane D/E split into machine states

Do not use a single overloaded Lane D. Use:

- **Lane D1 scheduled:** routine created, not fired.
- **Lane D2 running:** start/heartbeat seen.
- **Lane D3 blocked/failed/stale:** requires morning control decision.
- **Lane E open-pr:** implementation output exists, QA not complete.
- **Lane E review-ready:** mandatory handoff is complete and prioritized for user/reviewer.

## G. Mandatory Lane E handoff schema

Every overnight implementation must produce a review-ready handoff before it can be called morning-ready:

- issue link and title,
- PR/branch link,
- dispatch id and routine id,
- plan path and exact plan SHA / marker path,
- approval evidence link,
- changed files/modules,
- tests run with exact commands and pass/fail status,
- CI state and failing check links if any,
- screenshots/reports/artifacts where relevant,
- risks and known limitations,
- dependency/blocker status,
- adversarial implementation-review status,
- recommended next human action: merge / review specific files / request fix / hold,
- estimated review effort: S/M/L,
- priority ordering reason.

If this handoff is absent, the item is **open-pr** but not **review-ready**.

## H. Throughput caps and noise controls

Default caps until the pipeline proves itself:

- maximum 3 new implementation PRs per night,
- maximum 5 total Lane E items awaiting human review,
- if Lane E is saturated, stop implementation dispatch and run planning/QA only,
- preserve Codex for daytime interactive work unless explicitly overridden.

Noise controls:

- one daily dispatch ledger Markdown + JSON artifact,
- GitHub comments only on dispatch scheduled/start, blocked/failure, PR produced, and final wrap-up,
- no repeated "still pending" comments unless a heartbeat is required or state changes,
- morning report must sort by: blocked critical path, merge-ready low-effort PRs, high-impact review-ready PRs, approval candidates, planning feedstock.

## I. Implementation-phasing impact

This synthesis should not silently expand #2489 v1 into a full scheduler. The safer path is:

1. **#2489 v1:** read-only evidence-aware classifier/report with explicit detection of approval drift, active execution hints, and QA-review hints. It may define the schemas above but should not schedule work.
2. **Follow-up issue:** dispatch ledger writer and lease lifecycle.
3. **Follow-up issue:** remote routine launcher that consumes only classifier-approved Lane B plus ledger locks.
4. **Follow-up issue:** morning control-loop report and Lane E handoff validator.

## J. Revised verdict after incorporating adversarial review

- The combined architecture is viable only as a **control-plane + executor-backend** split.
- Claude's scheduled remote routines are useful executor backends, not the source of truth.
- #2489 remains the right control-plane anchor, but it must explicitly reject label-only and transcript-only readiness.
- Immediate next step should be a #2489 plan update/comment incorporating this stricter model, followed by user approval decision. Implementation remains blocked until explicit approval and marker creation.
