# Plan for #2489: Continuous Planning Pipeline for AFK Issue Throughput

> **Status:** plan-approved
> **Complexity:** T3
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2489
> **Review artifacts:** Required before approval-ready status for the current plan SHA: `scripts/review/results/2026-04-26-plan-2489-claude.md` | `scripts/review/results/2026-04-26-plan-2489-codex.md` | `scripts/review/results/2026-04-26-plan-2489-gemini.md` | `scripts/review/results/2026-04-26-plan-2489-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/ai/provider-work-queue.py` already builds a provider-routed queue from open GitHub issues, but its `execution_ready` logic is label-only (`status:plan-approved`). It does not verify canonical plan files, review artifacts, or `.planning/plan-approved/<issue>.md` markers.
- `tests/analysis/test_provider_work_queue.py` provides the nearest fixture/unit-test pattern for queue classification and rendering.
- `scripts/automation/generate_issue_prompts.py` already generates prompts from approved issues and can remain the downstream dispatch mechanism once #2489 produces a trustworthy Lane B list.
- `.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` enforce local approval markers for implementation writes/commits. This confirms label-only execution readiness is unsafe.
- `scripts/review/plan-review-fanout.sh` is the canonical plan-review fanout wrapper, intended to create per-provider artifacts under `scripts/review/results/`. Live re-review found provider CLIs can sometimes exit with empty stdout or unavailable output; #2489's consumer must treat empty/missing provider files as UNAVAILABLE-equivalent and must not infer approval from a populated disagreement file alone.
- Gap: no script/report computes Lane A/B/C/D/E with all evidence: open issue, labels, plan file, review verdicts, approval marker, review freshness evidence, posted approval-request evidence, active dispatch/lease state, PR/QA handoff state, and stale/contradictory warnings.
- Gap: no morning approval/QA packet and no buffer-threshold report for the desired 5-10 Lane A, 5-10 Lane B, and 10-20 Lane C targets, nor caps for Lane E review load.
- Cross-review input: an ongoing Claude autonomous routine wave (`565cae05-779f-49b7-9225-34a1444fdbef`) scheduled paced remote execution/check-in/wrap-up routines for #2471/#2126/#2369/#2124/#2227/#2373/#2125. It contributes useful executor-side gating and pacing, but also proves that remote routine state must be mirrored into GitHub/repo evidence and cannot itself authorize Lane B execution.

### Documents consulted
- #2489 issue body and ASCII lane model comments — defines continuous planning / execution-readiness pipeline.
- #1839 — workflow hard-stops and session governance.
- #2129 — broader issue-state drift/redundancy audit; #2489 should consume/integrate signals but not duplicate it.
- #2255 — label-vs-marker reconciliation; #2489 should depend on or consume it, not generate markers itself.
- `docs/reports/issue-2489-continuous-pipeline-cross-review.md` — cross-review synthesis comparing #2489 with the Claude autonomous wave; adds strict control-plane authority order, Lane D/E, dispatch-state/lease lifecycle, dependency requeue, Lane E handoff, and throughput caps.
- `docs/plans/README.md` — canonical workflow and batch-session rule: draft plans / `status:plan-review` when user absent; implement only `status:plan-approved` work.
- `docs/plans/_template-issue-plan.md` — required plan sections.
- `docs/standards/HARD-STOP-POLICY.md` — user plan approval before implementation and adversarial review after implementation.
- `docs/work-queue-workflow.md` — GitHub issues are the canonical work tracking model; legacy local queues are not canonical.

### Evidence
- Live snapshot at 2026-04-26T12:40:57Z: 48 open issues labeled `status:plan-approved`; 0 open issues labeled `status:plan-review`.
- Interpretation: Lane B has apparent label supply, but must be evidence-filtered by plan/review/marker checks before unattended implementation. Lane A approval-candidate buffer is empty and needs continuous refill.
- Verified existing files: `scripts/ai/provider-work-queue.py`, `tests/analysis/test_provider_work_queue.py`, `scripts/automation/generate_issue_prompts.py`, `.claude/hooks/plan-approval-gate.sh`, `scripts/enforcement/require-plan-approval.sh`, `scripts/review/plan-review-fanout.sh`, `docs/plans/README.md`, `docs/standards/HARD-STOP-POLICY.md`.
- New files proposed by this plan: `scripts/ai/continuous-planning-pipeline.py`, `tests/analysis/test_continuous_planning_pipeline.py`, `config/ai-tools/continuous-planning-pipeline.json`, `docs/reports/continuous-planning-pipeline.md`.
- New schema references proposed by the stricter control-plane model: `docs/reports/continuous-work/dispatch-ledger-YYYY-MM-DD.{json,md}` as an optional external dispatch mirror. #2489 v1 consumes existing ledger evidence when present and reports `ledger_missing` / `ledger_untrusted` when absent or malformed; it must not create scheduler-state rows, launch routines, or imply that missing ledger equals no active work.
- Scope boundary sharpened by review: #2489 is a read/report pipeline. It may read issue, plan, review, label, and approval-marker evidence, but must not write GitHub labels, create/edit approval markers, close issues, or perform #2129/#2255 reconciliation side effects.

---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md` |
| Tests | `tests/analysis/test_continuous_planning_pipeline.py` |
| Implementation | `scripts/ai/continuous-planning-pipeline.py` |
| Machine-readable report | `config/ai-tools/continuous-planning-pipeline.json` |
| Human report | `docs/reports/continuous-planning-pipeline.md` |
| Optional dispatch/lease ledger input schema | `docs/reports/continuous-work/dispatch-ledger-YYYY-MM-DD.{json,md}` |
| Cross-review synthesis | `docs/reports/issue-2489-continuous-pipeline-cross-review.md` |
| Plan review artifacts | `scripts/review/results/2026-04-26-plan-2489-*.md` |

---

## Deliverable
A tested continuous-planning control-plane report command that classifies open GitHub issues into Lane A approval candidates, Lane B execution-ready work, Lane C planning feedstock, Lane D active dispatch/execution, and Lane E implementation QA/review using evidence from GitHub labels, canonical plan files, adversarial review artifacts, local approval markers, optional dispatch/lease mirrors, PR state, and Lane E handoff evidence; emits JSON + Markdown morning/overnight queue packets with buffer-health warnings, review-load caps, and approval-drift warnings. V1 is read-only/reporting: it defines and validates the control-plane contract but does not launch remote routines, create scheduler ledger rows, write approval markers, or pretend absent ledger state proves no active work.

---

## Pseudocode
```text
load_live_issues(repo, offline_json):
    read fixture or call gh issue list for open issues with number/title/url/labels/updatedAt/body
    for issues already carrying status:plan-review, call gh issue view <n> --json comments with a configurable max-comment-checks limit (default 20)
    posted approval-request evidence means a comment after the latest plan file date/update with a canonical block: plan path, Plan-SHA256 or plan commit, review artifact paths/verdicts, explicit Approve / Revise / Hold choices, and a direct statement that execution remains unauthorized until approval marker creation
    fuzzy comments or comments outside the fetch window are not Lane A evidence; they produce approval_comment_ambiguous or comment_window_insufficient and a suggested action to repost a canonical approval-request comment
    if comment retrieval fails or rate limits are hit, classify as needs-evidence rather than Lane A

discover_plan_files(plans_dir):
    scan docs/plans/YYYY-MM-DD-issue-<digits>-*.md and map issue -> newest plan
    reuse the existing plan-file parser semantics ([0-9]+ issue ids), not a literal NNN glob
    compute plan_sha256 from the plan body when artifact metadata is available; otherwise use plan path/date as legacy freshness evidence with a warning

discover_review_artifacts(results_dir):
    scan scripts/review/results/*-plan-<issue>-<provider>.md for known providers only
    ignore synthesis files such as *-disagreement.md when computing provider verdicts
    parse provider and verdict APPROVE/MINOR/MAJOR/UNAVAILABLE
    empty or missing provider artifacts are UNAVAILABLE-equivalent blockers, not ignorable files
    if Plan-SHA256 metadata exists, require it to match the current plan; if metadata is absent, classify as legacy_review_no_sha and allow only with --allow-legacy-review-artifacts for audit/transition reports
    clean_review(issue) requires all configured required providers (default: claude,codex,gemini) to have APPROVE or MINOR artifacts tied to the current plan by sha when available or explicit legacy allowance; sha-mismatch, MAJOR, unknown, disagreement-only, missing, empty, or UNAVAILABLE artifacts are blockers/warnings

discover_approval_markers(marker_dir):
    scan .planning/plan-approved/*.md
    for workspace-hub Lane B v1, issue-specific markers are numeric <issue>.md files with committed/non-self-approved evidence when available
    require marker binding to issue number, plan path or branch, plan commit/SHA or Plan-SHA256, user approval comment URL/timestamp, approving user/source, and marker commit SHA when available
    inherit plan-approval-gate.sh semantics: self-approved markers and recent/uncommitted markers do not qualify for Lane B
    non-numeric markers are non-issue-keyed or cross-repo/workstream scoped and out of scope for workspace-hub issue-keyed Lane B unless an explicit repo/workstream mapping is configured
    revision-bound approval comments/plan branches without a valid local marker are approval_drift / approval_evidence_incomplete, not Lane B authority
    marker content quality is classified: revision-bound marker > minimal marker > missing/self-approved/uncommitted marker

discover_dispatch_state(dispatch_dir, github_state):
    read docs/reports/continuous-work/dispatch-ledger-*.json if present and normalize rows by dispatch_id
    if no trusted ledger exists, emit ledger_missing / ledger_untrusted and downgrade active-dispatch confidence; missing ledger never means no active work
    #2489 v1 must not create candidate/scheduled/running rows; those belong to a follow-up dispatch-ledger writer/lease issue
    ledger is an operational mirror only; it never upgrades approval readiness
    valid states are candidate, scheduled, running, blocked, open-pr, qa-ready, failed, no-fire, stale, cancelled, superseded, merged, closed
    stale scheduled rows are rows past scheduled_at_utc + 45 minutes with no start evidence
    stale running rows are rows with no heartbeat for 2 hours unless state is open-pr/terminal
    active conflicts are non-terminal rows for the same issue or overlapping lease_scope

discover_lane_e_pr_state(issue):
    inspect direct PR links/branches/titles and issue execution comments, not only broad PR body references
    PR match precedence: explicit execution/start/completion comment URL > branch name containing issue slug/number > PR title closing the issue > direct issue-closing keyword; incidental body-only references are weak evidence and must not alone classify Lane E
    classify open implementation output as Lane E open-pr unless mandatory handoff fields are present
    mandatory handoff fields: issue, PR/branch, dispatch id/routine id, plan path/SHA, approval marker, changed files, tests/CI, risks, artifacts, adversarial implementation-review status, recommended human action, estimated review effort, priority reason

classify_issue(issue, plans, reviews, markers, dispatch_state, pr_state):
    warn if dual status labels, approved-no-marker, approved-no-plan, approved-no-clean-review, sha-mismatch-review, legacy-review-no-sha, disagreement-only-review, marker-without-open-approved-issue, self-approved-marker, uncommitted-marker, gate-allows-but-lane-b-denies, comment-check-failed, approval-drift, active-lease-conflict, lane-e-handoff-missing, lane-e-saturated, dependency-blocked
    if open PR/branch/output exists for the issue: Lane E (open-pr or review-ready depending on handoff completeness)
    else if active non-terminal dispatch/lease exists: Lane D (scheduled, running, blocked/failed/no-fire/stale sub-state)
    else if open + status:plan-approved + workspace-hub issue marker + plan + clean review + no active lease conflict: Lane B
    else if open + status:plan-review + plan + clean review + latest plan was posted/commented for user approval: Lane A
    else: Lane C, blocked, approval-drift, or needs-planning depending on missing evidence
    return lane item with evidence, missing_requirements, warnings, suggested_action

compute_buffer_health(lanes):
    check Lane A 5-10, Lane B 5-10, Lane C 10-20
    check Lane E review-load caps: default max 3 new implementation PRs/night and max 5 total Lane E items awaiting human review
    if Lane E is saturated, recommend planning/QA only and stop implementation dispatch
    recommend plan-more, request-approvals, dispatch-implementation, QA/close, dependency-recheck, or approval-drift-reconciliation

render_json_and_markdown(snapshot):
    include generated_at, thresholds, lanes, warning summary, morning approval packet, overnight dispatch packet
    markdown starts with a top-actions-today section capped at 5 items: blocked critical-path fixes, merge-ready low-effort Lane E, high-impact Lane A approvals, then planning feedstock
    each issue shows one primary blocker/decision plus secondary notes; do not dump all warnings at equal priority
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `scripts/ai/continuous-planning-pipeline.py` | Lane classifier and report generator. |
| Create | `tests/analysis/test_continuous_planning_pipeline.py` | TDD coverage for classification, evidence, warnings, thresholds, deterministic output. |
| Create | `tests/analysis/fixtures/continuous_planning_pipeline_issues.json` | Offline GitHub issue/comment fixture corpus for deterministic tests. |
| Create | `tests/analysis/fixtures/continuous_planning_pipeline_markers/` | Marker fixtures covering revision-bound, minimal, self-approved, uncommitted, orphan, and non-issue-keyed markers. |
| Create/update | `config/ai-tools/continuous-planning-pipeline.json` | Machine-readable latest snapshot. |
| Create/update | `docs/reports/continuous-planning-pipeline.md` | User-facing morning/overnight packet. |
| Consume only | `docs/reports/continuous-work/dispatch-ledger-YYYY-MM-DD.{json,md}` | Optional external dispatch mirror input; v1 validates/flags missing or untrusted ledger state but does not write scheduler-state rows. |
| Update | `docs/plans/README.md` | Index this plan. |
| Optional future issue | `scripts/review/plan-review-fanout.sh` | Not required for #2489 v1; separate hardening should add metadata headers, empty-stdout fallback to `UNAVAILABLE`, and provider-specific trust/permission handling so future review artifacts are easier to consume. |
| Optional update | `scripts/ai/provider-work-queue.py` | Link to the readiness report if needed; do not broaden provider queue into reconciliation. |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_lane_b_requires_label_plan_review_and_marker` | Lane B requires all evidence | Approved issue + plan + clean reviews + marker | Lane B |
| `test_approved_without_marker_not_lane_b` | Prevents label-only dispatch | Approved issue without marker | warning `approved_no_marker`; not Lane B |
| `test_approved_without_plan_not_lane_b` | Prevents stale labels | Approved issue + marker but no plan | warning `approved_no_plan`; not Lane B |
| `test_plan_review_with_clean_reviews_is_lane_a` | Approval candidates surface correctly | Plan + current APPROVE/MINOR reviews + `status:plan-review` + posted plan marker/comment evidence | Lane A |
| `test_major_review_blocks_lane_a` | MAJOR reviews block approval | Plan + MAJOR artifact | blocked/warning |
| `test_unavailable_review_not_clean` | Provider failure is not approval | UNAVAILABLE artifact | warning; not clean |
| `test_empty_review_artifact_not_clean` | Empty stdout provider artifact is a review failure | zero-byte provider artifact | warning `empty_review`; not clean |
| `test_disagreement_artifact_not_provider_verdict` | Summary files are excluded from provider verdict aggregation | `*-disagreement.md` plus provider artifacts | disagreement ignored for clean-review calculation |
| `test_stale_review_does_not_approve_revised_plan` | Review artifacts must match the current plan sha256 when metadata exists | old APPROVE artifact + modified plan | warning `sha_mismatch_review`; not clean |
| `test_legacy_review_without_sha_requires_explicit_allowance` | Day-one legacy artifacts are visible rather than silently trusted | artifact without Plan-SHA256 | warning `legacy_review_no_sha`; clean only with explicit legacy flag |
| `test_comment_retrieval_failure_blocks_lane_a` | Comment evidence API failures do not silently approve Lane A | status:plan-review issue + comments call failure | warning `comment_check_failed`; not Lane A |
| `test_ambiguous_approval_comment_not_lane_a` | Fuzzy/non-canonical approval comments do not promote issue | comment lacks plan SHA/artifact verdicts/approve-revise-hold block | warning `approval_comment_ambiguous`; not Lane A |
| `test_comment_window_insufficient_requests_repost` | Comment cap does not silently hide ready approvals | approval evidence beyond fetched window | warning `comment_window_insufficient`; suggested repost canonical comment |
| `test_self_approved_marker_not_lane_b` | Mirrors plan-approval-gate self-approval rejection | marker containing self/auto-approved language | warning `self_approved_marker`; not Lane B |
| `test_uncommitted_marker_not_lane_b` | Mirrors plan-approval-gate recent/uncommitted marker rejection | recent marker with no git history | warning `uncommitted_marker`; not Lane B |
| `test_marker_content_quality_classified` | Marker existence is not the only signal | minimal marker vs revision-bound marker | content quality surfaced in evidence |
| `test_orphan_marker_flagged` | Orphan local marker is reported | marker exists but issue missing/closed/not approved | warning `marker_without_open_approved_issue` |
| `test_open_unplanned_priority_issue_is_lane_c` | Feedstock classification | Priority issue without plan/review/approval | Lane C |
| `test_dual_status_labels_flagged` | Contradictory labels detected | Both `status:plan-review` and `status:plan-approved` | warning |
| `test_non_numeric_marker_handled_as_cross_repo_out_of_scope` | Cross-repo/non-issue-keyed markers are not treated as workspace-hub issue approvals | `aces-2.md` marker with no repo-prefix config | excluded from workspace-hub Lane B with explicit out-of-scope evidence |
| `test_workstream_level_marker_handled_as_non_issue_keyed` | Workstream markers do not approve a numbered issue by accident | `ecosystem-sync.md` marker | classified as non-issue-keyed/workstream evidence, not Lane B |
| `test_revision_bound_approval_without_marker_is_approval_drift` | Claude-wave style comments/plan branches do not authorize Lane B v1 | `status:plan-approved` + revision approval comment but no numeric marker | warning `approval_drift`; not Lane B |
| `test_active_dispatch_excludes_issue_from_lane_b` | Scheduled/running routines are not re-dispatched | clean Lane B evidence + non-terminal dispatch row | Lane D with active lease warning |
| `test_stale_dispatch_requires_morning_decision_before_requeue` | No-fire/stale rows do not silently return to Lane B | scheduled row past TTL | Lane D3 stale/no-fire suggested action |
| `test_open_pr_moves_issue_to_lane_e` | Implementation output becomes QA/review work | direct PR/branch evidence | Lane E open-pr |
| `test_incidental_pr_body_reference_is_weak_lane_e_evidence` | Broad issue-number mentions do not create false Lane E | unrelated PR body references issue | weak evidence warning; not Lane E by itself |
| `test_lane_e_requires_handoff_for_review_ready` | Open PR is not morning-ready without handoff | PR without required fields | Lane E open-pr + `lane_e_handoff_missing` |
| `test_lane_e_review_ready_handoff_schema` | Complete handoff becomes review-ready | PR + all required handoff fields | Lane E review-ready |
| `test_dependency_blocked_requeues_deterministically` | Blocked dependencies produce safe next action | upstream PR open/closed/merged cases | blocked/requeue/replan decisions |
| `test_throughput_caps_stop_new_implementation_when_lane_e_saturated` | User review capacity is protected | 5+ Lane E items | no implementation dispatch recommendation |
| `test_existing_lane_e_backlog_counts_against_nightly_cap` | Existing PR backlog protects user review capacity before recommending new work | stale/open Lane E items + Lane B supply | planning/QA-only recommendation |
| `test_missing_ledger_is_unknown_not_no_active_work` | Absent ledger is not interpreted as safe dispatch | no ledger + approved issue | `ledger_missing` confidence warning |
| `test_markdown_top_actions_capped_and_prioritized` | Morning packet is decision-oriented | mixed lanes/warnings | <=5 top actions in required priority order |
| `test_warnings_collapse_to_primary_blocker` | User report avoids warning spam | issue with many warnings | one primary blocker plus secondary notes |
| `test_buffer_health_flags_empty_lane_a` | Detects approval starvation | 0 Lane A items | below-minimum warning |
| `test_markdown_has_morning_and_overnight_sections` | User packet is usable | Mixed lanes | required sections present |
| `test_json_schema_is_deterministic` | Agents can consume output | Mixed fixture | stable sorted JSON |
| `test_fail_under_buffer_exit_code` | Optional cron gate works without colliding with argparse | below-minimum with flag | exit code 3 |

---

## Acceptance Criteria
- [ ] CLI exists: `scripts/ai/continuous-planning-pipeline.py --help`.
- [ ] CLI supports offline fixture input for deterministic tests.
- [ ] Lane B requires open issue + `status:plan-approved` + canonical plan + issue-specific local marker + current clean review evidence.
- [ ] Lane A requires open issue + `status:plan-review` + canonical plan + current clean adversarial review evidence + a canonical posted approval-request comment containing plan path, Plan-SHA256/commit, review artifact paths/verdicts, explicit Approve / Revise / Hold choices, and an execution-not-authorized-until-marker statement.
- [ ] Clean review means all configured required provider artifacts for the current plan are `APPROVE` or `MINOR`; default required provider set is Claude + Codex + Gemini, with `--required-providers` as an explicit operator override. `MAJOR`, `UNAVAILABLE`, unknown verdicts, sha-mismatched artifacts, missing/empty files, or disagreement-only evidence are not clean. Legacy artifacts without `Plan-SHA256` are allowed only with explicit `--allow-legacy-review-artifacts` and must be reported as lower-confidence transition evidence.
- [ ] Lane C excludes closed issues and issues cleanly classified into Lane A/B/D/E.
- [ ] Lane D classifies active scheduled/running/blocked/failed/no-fire/stale dispatch state from dispatch ledger/GitHub evidence and excludes those issues from duplicate implementation dispatch.
- [ ] Lane E classifies open implementation PR/branch output into `open-pr` vs `review-ready` based on a mandatory handoff schema: issue, PR/branch, dispatch/routine id, plan SHA, approval marker/evidence, changed files, tests/CI, artifacts, risks, implementation-review status, recommended human action, review effort, and priority reason.
- [ ] Missing/untrusted dispatch ledger is reported as unknown/low-confidence active-state evidence; it is never interpreted as proof that no active work exists.
- [ ] PR association uses strict precedence; incidental PR body references are weak evidence and cannot by themselves create Lane E.
- [ ] Report includes target buffer checks: Lane A 5-10, Lane B 5-10, Lane C 10-20.
- [ ] Report enforces review-load caps in recommendations: default max 3 new implementation PRs/night and max 5 Lane E items awaiting human review; if saturated, recommend planning/QA only.
- [ ] Report flags dual status labels, approved-without-marker, approved-without-plan, missing/empty/MAJOR/UNAVAILABLE/sha-mismatched reviews, legacy-review-no-sha transition evidence, disagreement-only review evidence, marker-without-open-approved-issue, self-approved/uncommitted markers, gate-allows-but-Lane-B-denies mismatches, comment-check failures, approval drift from revision-bound comments without local markers, active lease conflicts, stale/no-fire dispatch rows, Lane E handoff gaps, dependency-blocked states, and out-of-scope non-issue-keyed markers.
- [ ] Report emits JSON and Markdown.
- [ ] Markdown includes morning user approval packet and overnight dispatch packet sections.
- [ ] Markdown begins with a capped `Top actions today` section of at most 5 prioritized decisions, and each issue has one primary blocker/decision plus secondary notes.
- [ ] Implementation does not change labels, create approval markers, schedule/launch remote routines, or close issues; it is read-only/reporting except writing configured report artifacts.
- [ ] Implementation does not write `.planning/plan-approved/`, mutate `docs/plans/` for other issues, or perform reconciliation side effects owned by #2129/#2255.
- [ ] Scope does not duplicate #2129 issue-hygiene analysis or #2255 marker reconciliation; it can consume their outputs/signals when present.
- [ ] Tests pass: `uv run pytest tests/analysis/test_continuous_planning_pipeline.py -v`.
- [ ] Existing provider queue tests pass: `uv run pytest tests/analysis/test_provider_work_queue.py -v`.
- [ ] Adversarial plan review artifacts exist for the current revised plan and any MAJOR findings are resolved before moving #2489 to `status:plan-review`.

---

## Adversarial Review Summary
The plan underwent cross-review against the ongoing Claude autonomous routine wave and then two adversarial re-review passes after material revision.

Material changes incorporated before the final pass:

- Adds Lane D active dispatch/execution and Lane E implementation QA/review as first-class states.
- Makes the authority order explicit: repo hard gates/hooks > GitHub issue state > repo plan/review/approval evidence > dispatch ledger mirror > remote trigger state.
- Tightens Lane B v1 to require a committed numeric `.planning/plan-approved/<issue>.md` marker; revision-bound comments/plan branches without that marker are approval drift, not execution authority.
- Adds dispatch state machine, lease lifecycle, dependency requeue rules, Lane E handoff schema, and review-load caps.
- Clarifies v1 remains read-only/reporting and must not schedule/launch remote routines.
- Post-MAJOR tightening after the first re-review pass: canonical Lane A approval-comment schema; optional-ledger/missing-ledger semantics; strict PR association precedence; top-actions/noise-budget report requirements; existing Lane E backlog counts against nightly implementation recommendations; dispatch ledger rows are consume-only in v1.

Final adversarial re-review results:

| Provider / perspective | Verdict | Key findings / disposition |
|---|---|---|
| Governance/source-of-truth | MINOR | No approval-blocking issue remains; flagged implementation-time care around stale prior-SHA artifacts, degraded-observability messaging, timestamp precedence, and report publication provenance. |
| Scheduler/executor reliability | MINOR | Earlier duplicate-dispatch and untrusted-ledger blockers are resolved; remaining concerns are follow-up-quality issues around ledger trust criteria, lease-scope normalization, and evidence-conflict tests. |
| User-review/productivity | MINOR | Morning-packet usability blockers are resolved by top-actions/noise-budget requirements; remaining risk is over-conservative output if repo evidence is sparse. |

**Overall result:** READY FOR `status:plan-review` / explicit user approval. No MAJOR blockers remain. Implementation remains blocked until explicit user approval and a valid `.planning/plan-approved/2489.md` marker exist.

---

## Risks and Open Questions
- **Risk:** Existing provider queue may keep overstating readiness by label-only logic. Mitigate by documenting that provider queue is routing-oriented while #2489 Lane B is readiness/evidence-oriented.
- **Risk:** Claude remote routines can appear successful in transcripts while GitHub/repo evidence is incomplete. Mitigate by treating remote trigger state as non-authoritative until mirrored into dispatch ledger/GitHub evidence.
- **Risk:** Approval evidence split-brain between local markers and revision-bound comments could restart execution without repo gates recognizing approval. Mitigate by requiring numeric committed local markers for Lane B v1 and flagging revision-bound-only evidence as approval drift.
- **Risk:** Continuous execution can overwhelm next-day user review. Mitigate with Lane E caps and recommendations that switch saturated nights to planning/QA-only work.
- **Risk:** Review artifact parsing can be inconsistent across historical artifacts. Treat unknown verdicts conservatively.
- **Risk:** Current live state has 48 approved labels and 0 plan-review labels. Avoid encouraging execution until marker/plan/review evidence is verified.
- **Risk:** Scope creep into #2129/#2255. Keep #2489 focused on lane readiness, buffer health, and morning/overnight packets.
- **Open (implementation tuning):** Keep the default required provider set as Claude + Codex + Gemini for maximum assurance; use `--required-providers` only as an explicit operator override when a provider is documented unavailable.
- **Open:** Should buffer underfill fail cron by default? Proposed: no; only fail with `--fail-under-buffer` returning exit code 3.

---

## Complexity: T3
**T3** — governance/workflow automation across live GitHub state, local canonical plans, adversarial review artifacts, approval-marker gates, deterministic reports, and day/night operating contracts.
