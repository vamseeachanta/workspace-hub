# Plan for #2489: Continuous Planning Pipeline for AFK Issue Throughput

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2489
> **Review artifacts:** Expected after plan-review gate: `scripts/review/results/2026-04-26-plan-2489-claude.md` | `scripts/review/results/2026-04-26-plan-2489-codex.md` | `scripts/review/results/2026-04-26-plan-2489-gemini.md` | `scripts/review/results/2026-04-26-plan-2489-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/ai/provider-work-queue.py` already builds a provider-routed queue from open GitHub issues, but its `execution_ready` logic is label-only (`status:plan-approved`). It does not verify canonical plan files, review artifacts, or `.planning/plan-approved/<issue>.md` markers.
- `tests/analysis/test_provider_work_queue.py` provides the nearest fixture/unit-test pattern for queue classification and rendering.
- `scripts/automation/generate_issue_prompts.py` already generates prompts from approved issues and can remain the downstream dispatch mechanism once #2489 produces a trustworthy Lane B list.
- `.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` enforce local approval markers for implementation writes/commits. This confirms label-only execution readiness is unsafe.
- `scripts/review/plan-review-fanout.sh` is the canonical plan-review fanout wrapper, intended to create per-provider artifacts under `scripts/review/results/`. Live re-review found provider CLIs can sometimes exit with empty stdout or unavailable output; #2489's consumer must treat empty/missing provider files as UNAVAILABLE-equivalent and must not infer approval from a populated disagreement file alone.
- Gap: no script/report computes Lane A/B/C with all evidence: open issue, labels, plan file, review verdicts, approval marker, review freshness evidence, posted approval-request evidence, and stale/contradictory warnings.
- Gap: no morning approval/QA packet and no buffer-threshold report for the desired 5-10 Lane A, 5-10 Lane B, and 10-20 Lane C targets.

### Documents consulted
- #2489 issue body and ASCII lane model comments — defines continuous planning / execution-readiness pipeline.
- #1839 — workflow hard-stops and session governance.
- #2129 — broader issue-state drift/redundancy audit; #2489 should consume/integrate signals but not duplicate it.
- #2255 — label-vs-marker reconciliation; #2489 should depend on or consume it, not generate markers itself.
- `docs/plans/README.md` — canonical workflow and batch-session rule: draft plans / `status:plan-review` when user absent; implement only `status:plan-approved` work.
- `docs/plans/_template-issue-plan.md` — required plan sections.
- `docs/standards/HARD-STOP-POLICY.md` — user plan approval before implementation and adversarial review after implementation.
- `docs/work-queue-workflow.md` — GitHub issues are the canonical work tracking model; legacy local queues are not canonical.

### Evidence
- Live snapshot at 2026-04-26T12:40:57Z: 48 open issues labeled `status:plan-approved`; 0 open issues labeled `status:plan-review`.
- Interpretation: Lane B has apparent label supply, but must be evidence-filtered by plan/review/marker checks before unattended implementation. Lane A approval-candidate buffer is empty and needs continuous refill.
- Verified existing files: `scripts/ai/provider-work-queue.py`, `tests/analysis/test_provider_work_queue.py`, `scripts/automation/generate_issue_prompts.py`, `.claude/hooks/plan-approval-gate.sh`, `scripts/enforcement/require-plan-approval.sh`, `scripts/review/plan-review-fanout.sh`, `docs/plans/README.md`, `docs/standards/HARD-STOP-POLICY.md`.
- New files proposed by this plan: `scripts/ai/continuous-planning-pipeline.py`, `tests/analysis/test_continuous_planning_pipeline.py`, `config/ai-tools/continuous-planning-pipeline.json`, `docs/reports/continuous-planning-pipeline.md`.
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
| Plan review artifacts | `scripts/review/results/2026-04-26-plan-2489-*.md` |

---

## Deliverable
A tested continuous-planning pipeline report command that classifies open GitHub issues into Lane A approval candidates, Lane B execution-ready work, and Lane C planning feedstock using evidence from GitHub labels, canonical plan files, adversarial review artifacts, and local approval markers; emits JSON + Markdown morning/overnight queue packets with buffer-health warnings.

---

## Pseudocode
```text
load_live_issues(repo, offline_json):
    read fixture or call gh issue list for open issues with number/title/url/labels/updatedAt/body
    for issues already carrying status:plan-review, call gh issue view <n> --json comments with a configurable max-comment-checks limit (default 20)
    posted approval-request evidence means a comment after the latest plan file date/update that names the canonical plan path, summarizes adversarial review, and explicitly asks the user to approve/revise/hold
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
    for workspace-hub Lane B, issue-specific markers are numeric <issue>.md files with committed/non-self-approved evidence when available
    inherit plan-approval-gate.sh semantics: self-approved markers and recent/uncommitted markers do not qualify for Lane B
    non-numeric markers are non-issue-keyed or cross-repo/workstream scoped and out of scope for workspace-hub issue-keyed Lane B unless an explicit repo/workstream mapping is configured
    marker content quality is classified: revision-bound marker > minimal marker > missing/self-approved/uncommitted marker

classify_issue(issue, plans, reviews, markers):
    warn if dual status labels, approved-no-marker, approved-no-plan, approved-no-clean-review, sha-mismatch-review, legacy-review-no-sha, disagreement-only-review, marker-without-open-approved-issue, self-approved-marker, uncommitted-marker, gate-allows-but-lane-b-denies, comment-check-failed
    if open + status:plan-approved + workspace-hub issue marker + plan + clean review: Lane B
    else if open + status:plan-review + plan + clean review + latest plan was posted/commented for user approval: Lane A
    else: Lane C, blocked, or needs-planning depending on missing evidence
    return lane item with evidence, missing_requirements, warnings, suggested_action

compute_buffer_health(lanes):
    check Lane A 5-10, Lane B 5-10, Lane C 10-20
    recommend plan-more, request-approvals, dispatch-implementation, or QA/close

render_json_and_markdown(snapshot):
    include generated_at, thresholds, lanes, warning summary, morning approval packet, overnight dispatch packet
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
| `test_self_approved_marker_not_lane_b` | Mirrors plan-approval-gate self-approval rejection | marker containing self/auto-approved language | warning `self_approved_marker`; not Lane B |
| `test_uncommitted_marker_not_lane_b` | Mirrors plan-approval-gate recent/uncommitted marker rejection | recent marker with no git history | warning `uncommitted_marker`; not Lane B |
| `test_marker_content_quality_classified` | Marker existence is not the only signal | minimal marker vs revision-bound marker | content quality surfaced in evidence |
| `test_orphan_marker_flagged` | Orphan local marker is reported | marker exists but issue missing/closed/not approved | warning `marker_without_open_approved_issue` |
| `test_open_unplanned_priority_issue_is_lane_c` | Feedstock classification | Priority issue without plan/review/approval | Lane C |
| `test_dual_status_labels_flagged` | Contradictory labels detected | Both `status:plan-review` and `status:plan-approved` | warning |
| `test_non_numeric_marker_handled_as_cross_repo_out_of_scope` | Cross-repo/non-issue-keyed markers are not treated as workspace-hub issue approvals | `aces-2.md` marker with no repo-prefix config | excluded from workspace-hub Lane B with explicit out-of-scope evidence |
| `test_workstream_level_marker_handled_as_non_issue_keyed` | Workstream markers do not approve a numbered issue by accident | `ecosystem-sync.md` marker | classified as non-issue-keyed/workstream evidence, not Lane B |
| `test_buffer_health_flags_empty_lane_a` | Detects approval starvation | 0 Lane A items | below-minimum warning |
| `test_markdown_has_morning_and_overnight_sections` | User packet is usable | Mixed lanes | required sections present |
| `test_json_schema_is_deterministic` | Agents can consume output | Mixed fixture | stable sorted JSON |
| `test_fail_under_buffer_exit_code` | Optional cron gate works without colliding with argparse | below-minimum with flag | exit code 3 |

---

## Acceptance Criteria
- [ ] CLI exists: `scripts/ai/continuous-planning-pipeline.py --help`.
- [ ] CLI supports offline fixture input for deterministic tests.
- [ ] Lane B requires open issue + `status:plan-approved` + canonical plan + issue-specific local marker + current clean review evidence.
- [ ] Lane A requires open issue + `status:plan-review` + canonical plan + current clean adversarial review evidence + a posted plan/comment for user approval.
- [ ] Clean review means all configured required provider artifacts for the current plan are `APPROVE` or `MINOR`; default required provider set is Claude + Codex + Gemini, with `--required-providers` as an explicit operator override. `MAJOR`, `UNAVAILABLE`, unknown verdicts, sha-mismatched artifacts, missing/empty files, or disagreement-only evidence are not clean. Legacy artifacts without `Plan-SHA256` are allowed only with explicit `--allow-legacy-review-artifacts` and must be reported as lower-confidence transition evidence.
- [ ] Lane C excludes closed issues and issues cleanly classified into Lane A/B.
- [ ] Report includes target buffer checks: Lane A 5-10, Lane B 5-10, Lane C 10-20.
- [ ] Report flags dual status labels, approved-without-marker, approved-without-plan, missing/empty/MAJOR/UNAVAILABLE/sha-mismatched reviews, legacy-review-no-sha transition evidence, disagreement-only review evidence, marker-without-open-approved-issue, self-approved/uncommitted markers, gate-allows-but-Lane-B-denies mismatches, comment-check failures, and out-of-scope non-issue-keyed markers.
- [ ] Report emits JSON and Markdown.
- [ ] Markdown includes morning user approval packet and overnight dispatch packet sections.
- [ ] Implementation does not change labels, create approval markers, or close issues; it is read-only/reporting except writing configured report artifacts.
- [ ] Implementation does not write `.planning/plan-approved/`, mutate `docs/plans/` for other issues, or perform reconciliation side effects owned by #2129/#2255.
- [ ] Scope does not duplicate #2129 issue-hygiene analysis or #2255 marker reconciliation; it can consume their outputs/signals when present.
- [ ] Tests pass: `uv run pytest tests/analysis/test_continuous_planning_pipeline.py -v`.
- [ ] Existing provider queue tests pass: `uv run pytest tests/analysis/test_provider_work_queue.py -v`.
- [ ] Adversarial plan review artifacts exist for the current revised plan and any MAJOR findings are resolved before moving #2489 to `status:plan-review`.

---

## Adversarial Review Summary
Formal multi-provider plan review on 2026-04-26 initially returned MAJOR findings from Claude and Codex plus Gemini `UNAVAILABLE`. The plan was revised to address the blockers before requesting final `status:plan-review`:

- Corrected the review-artifact model: provider artifacts are parsed separately from `*-disagreement.md` synthesis files, and review evidence must be current to the plan revision/fingerprint.
- Removed the previously proposed extra verdict name that no current review producer emits; parser/test scope is `APPROVE`, `MINOR`, `MAJOR`, and `UNAVAILABLE` unless existing tooling adds another documented verdict later.
- Resolved the UNAVAILABLE policy contradiction: conservative default is that `UNAVAILABLE` is not a clean review for Lane A/B.
- Fixed plan-file discovery language to support any digit-length issue id, aligned with the existing parser.
- Corrected approval-marker semantics: workspace-hub Lane B uses workspace-hub issue markers; non-numeric markers are non-issue-keyed/cross-repo/workstream scoped and out of scope unless a repo/workstream mapping is configured.
- Added marker content quality, self-approved/uncommitted marker rejection, orphan-marker warnings, and read-only/non-reconciliation scope boundaries.
- Changed `--fail-under-buffer` planned exit code from 2 to 3 to avoid `argparse` error-code collision.

| Provider | Verdict | Key findings / disposition |
|---|---|---|
| Claude | MAJOR on first pass | Blockers addressed in this revision: prior artifact narrative, UNAVAILABLE policy, verdict vocabulary, cross-repo marker semantics. |
| Codex | MAJOR on first pass | Blockers addressed in this revision: canonical artifact/index state, provider-vs-synthesis parsing, stale review binding, Lane A label/comment evidence, marker validation. |
| Gemini | UNAVAILABLE on first pass | Fanout needs trusted-directory env/flag; this plan treats UNAVAILABLE conservatively and should be re-reviewed after rerun. |

**Overall result:** revised after MAJOR findings; final rerun required before applying `status:plan-review`.

---

## Risks and Open Questions
- **Risk:** Existing provider queue may keep overstating readiness by label-only logic. Mitigate by documenting that provider queue is routing-oriented while #2489 Lane B is readiness/evidence-oriented.
- **Risk:** Review artifact parsing can be inconsistent across historical artifacts. Treat unknown verdicts conservatively.
- **Risk:** Current live state has 48 approved labels and 0 plan-review labels. Avoid encouraging execution until marker/plan/review evidence is verified.
- **Risk:** Scope creep into #2129/#2255. Keep #2489 focused on lane readiness, buffer health, and morning/overnight packets.
- **Open (implementation tuning):** Keep the default required provider set as Claude + Codex + Gemini for maximum assurance; use `--required-providers` only as an explicit operator override when a provider is documented unavailable.
- **Open:** Should buffer underfill fail cron by default? Proposed: no; only fail with `--fail-under-buffer` returning exit code 3.

---

## Complexity: T3
**T3** — governance/workflow automation across live GitHub state, local canonical plans, adversarial review artifacts, approval-marker gates, deterministic reports, and day/night operating contracts.
