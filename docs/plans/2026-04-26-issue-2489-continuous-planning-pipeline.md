# Plan for #2489: Continuous Planning Pipeline for AFK Issue Throughput

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2489
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2489-claude.md | scripts/review/results/2026-04-26-plan-2489-codex.md | scripts/review/results/2026-04-26-plan-2489-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/ai/provider-work-queue.py` already builds a provider-routed queue from open GitHub issues, but its `execution_ready` logic is label-only (`status:plan-approved`). It does not verify canonical plan files, review artifacts, or `.planning/plan-approved/<issue>.md` markers.
- `tests/analysis/test_provider_work_queue.py` provides the nearest fixture/unit-test pattern for queue classification and rendering.
- `scripts/automation/generate_issue_prompts.py` already generates prompts from approved issues and can remain the downstream dispatch mechanism once #2489 produces a trustworthy Lane B list.
- `.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` enforce local approval markers for implementation writes/commits. This confirms label-only execution readiness is unsafe.
- `scripts/review/plan-review-fanout.sh` is the canonical plan-review fanout wrapper, intended to create per-provider artifacts under `scripts/review/results/`.
- Gap: no script/report computes Lane A/B/C with all evidence: open issue, labels, plan file, review verdicts, approval marker, and stale/contradictory warnings.
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

discover_plan_files(plans_dir):
    scan docs/plans/YYYY-MM-DD-issue-NNN-*.md and map issue -> newest plan

discover_review_artifacts(results_dir):
    scan scripts/review/results/*-plan-NNN-*.md
    parse provider and verdict APPROVE/MINOR/MAJOR/FAIL/UNAVAILABLE
    unknown or unavailable verdicts are not clean approvals

discover_approval_markers(marker_dir):
    scan .planning/plan-approved/*.md
    numeric marker names are issue-specific; non-numeric markers are session-level only

classify_issue(issue, plans, reviews, markers):
    warn if dual status labels, approved-no-marker, approved-no-plan, approved-no-clean-review
    if open + status:plan-approved + numeric marker + plan + clean review: Lane B
    else if plan + clean review and awaiting approval/status:plan-review: Lane A
    else: Lane C
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
| Create/update | `config/ai-tools/continuous-planning-pipeline.json` | Machine-readable latest snapshot. |
| Create/update | `docs/reports/continuous-planning-pipeline.md` | User-facing morning/overnight packet. |
| Update | `docs/plans/README.md` | Index this plan. |
| Optional update | `scripts/ai/provider-work-queue.py` | Link to the readiness report if needed; do not broaden provider queue into reconciliation. |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_lane_b_requires_label_plan_review_and_marker` | Lane B requires all evidence | Approved issue + plan + clean reviews + marker | Lane B |
| `test_approved_without_marker_not_lane_b` | Prevents label-only dispatch | Approved issue without marker | warning `approved_no_marker`; not Lane B |
| `test_approved_without_plan_not_lane_b` | Prevents stale labels | Approved issue + marker but no plan | warning `approved_no_plan`; not Lane B |
| `test_plan_review_with_clean_reviews_is_lane_a` | Approval candidates surface correctly | Plan + APPROVE/MINOR reviews + `status:plan-review` | Lane A |
| `test_major_review_blocks_lane_a` | MAJOR reviews block approval | Plan + MAJOR artifact | blocked/warning |
| `test_open_unplanned_priority_issue_is_lane_c` | Feedstock classification | Priority issue without plan/review/approval | Lane C |
| `test_dual_status_labels_flagged` | Contradictory labels detected | Both `status:plan-review` and `status:plan-approved` | warning |
| `test_non_numeric_marker_not_issue_specific` | Session marker does not approve issue | `session.md` marker only | not Lane B |
| `test_unavailable_review_not_clean` | Provider failure is not approval | UNAVAILABLE artifact | warning; not clean |
| `test_buffer_health_flags_empty_lane_a` | Detects approval starvation | 0 Lane A items | below-minimum warning |
| `test_markdown_has_morning_and_overnight_sections` | User packet is usable | Mixed lanes | required sections present |
| `test_json_schema_is_deterministic` | Agents can consume output | Mixed fixture | stable sorted JSON |
| `test_fail_under_buffer_exit_code` | Optional cron gate works | below-minimum with flag | exit code 2 |

---

## Acceptance Criteria
- [ ] CLI exists: `scripts/ai/continuous-planning-pipeline.py --help`.
- [ ] CLI supports offline fixture input for deterministic tests.
- [ ] Lane B requires open issue + `status:plan-approved` + canonical plan + issue-specific local marker + no MAJOR/FAIL/UNAVAILABLE review blocker.
- [ ] Lane A requires canonical plan + clean adversarial review evidence and awaits user approval.
- [ ] Lane C excludes closed issues and issues cleanly classified into Lane A/B.
- [ ] Report includes target buffer checks: Lane A 5-10, Lane B 5-10, Lane C 10-20.
- [ ] Report flags dual status labels, approved-without-marker, approved-without-plan, missing/MAJOR/UNAVAILABLE reviews, marker-without-open-approved-issue.
- [ ] Report emits JSON and Markdown.
- [ ] Markdown includes morning user approval packet and overnight dispatch packet sections.
- [ ] Implementation does not change labels, create approval markers, or close issues; it is read-only/reporting except writing configured report artifacts.
- [ ] Scope does not duplicate #2129 issue-hygiene analysis or #2255 marker reconciliation; it can consume their outputs/signals when present.
- [ ] Tests pass: `uv run pytest tests/analysis/test_continuous_planning_pipeline.py -v`.
- [ ] Existing provider queue tests pass: `uv run pytest tests/analysis/test_provider_work_queue.py -v`.
- [ ] Adversarial plan review artifacts exist and any MAJOR findings are resolved before moving #2489 to `status:plan-review`.

---

## Adversarial Review Summary
Formal multi-provider plan review attempted on 2026-04-26, but the first fanout run produced only an empty disagreement artifact and no provider-specific #2489 artifacts. Treat that output as invalid. Re-run review using an artifact-inline/no-tools or otherwise side-effect-safe route before applying `status:plan-review`.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Needs side-effect-safe re-review. |
| Codex | PENDING | Needs side-effect-safe re-review. |
| Gemini | PENDING | Needs side-effect-safe re-review. |

**Overall result:** PENDING — keep #2489 in draft until valid reviews exist.

---

## Risks and Open Questions
- **Risk:** Existing provider queue may keep overstating readiness by label-only logic. Mitigate by documenting that provider queue is routing-oriented while #2489 Lane B is readiness/evidence-oriented.
- **Risk:** Review artifact parsing can be inconsistent across historical artifacts. Treat unknown verdicts conservatively.
- **Risk:** Current live state has 48 approved labels and 0 plan-review labels. Avoid encouraging execution until marker/plan/review evidence is verified.
- **Risk:** Scope creep into #2129/#2255. Keep #2489 focused on lane readiness, buffer health, and morning/overnight packets.
- **Open:** Should Lane A require all three providers, or allow two APPROVE/MINOR with one UNAVAILABLE? Conservative default blocks on UNAVAILABLE.
- **Open:** Should buffer underfill fail cron by default? Proposed: no; only fail with `--fail-under-buffer`.

---

## Complexity: T3
**T3** — governance/workflow automation across live GitHub state, local canonical plans, adversarial review artifacts, approval-marker gates, deterministic reports, and day/night operating contracts.
