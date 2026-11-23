# Plan for #2255: Reconcile GitHub Plan-Approval Labels with Local Marker Ledger

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2255
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2255-claude-overnight.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.planning/plan-approved/` -- 40 local approval markers (`.md` files named by issue number), each containing approval provenance (approved-by, date, authority)
- Found: `.claude/hooks/plan-approval-gate.sh` -- PreToolUse hook that checks for approval markers in `.planning/plan-approved/`; contains `has_approval()` and `is_self_approved()` functions; blocks writes and pushes without markers
- Found: `scripts/enforcement/require-plan-approval.sh` -- pre-commit gate that checks for plan approval evidence in `.planning/plan-approved/`, `.planning/phases/*/REVIEWS.md`, recent commit messages, and session logs
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` -- defines status precedence rules: `status:plan-approved` label > `.planning/plan-approved/NNN.md` marker > `status:plan-review` label > `docs/plans/README.md` row; includes detailed governance cleanup rules for state drift
- Gap: No reconciliation script or command exists that compares GitHub labels against local markers and flags contradictions

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Non-engineering governance automation issue |

### LLM Wiki pages consulted
- No relevant wiki pages -- this is an infrastructure/governance automation issue

### Documents consulted
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` -- "Status precedence and stale-state handling" section defines the 4-level precedence order and drift remediation rules; "Pending cross-review audit routine" section defines the 5-signal audit for open issues; "Fresh-review rollback rule" defines when to roll back stale approvals
- `docs/plans/README.md` -- "Status Meanings" table and Plan Index provide the local convenience view of issue states; notes that README can lag reality
- Issue #2129 (related) -- issue-state-drift-redundancy-audit plan exists at `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md`; covers broader stale-artifact audit but does not specifically implement label-vs-marker reconciliation
- Issue #2046 (related) -- planning-compliance-audit plan exists at `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md`; covers audit of agent compliance with planning workflow but not label/marker reconciliation specifically

### Gaps identified
- No automated reconciliation script comparing GitHub `status:plan-approved` / `status:plan-review` labels against `.planning/plan-approved/*.md` markers
- No detection of contradictory label combinations (e.g., both `status:plan-review` and `status:plan-approved` on the same issue)
- No mechanism to generate missing local markers when GitHub shows `status:plan-approved` but no local marker exists
- No queue snapshot integrating all state signals (labels, markers, README, review artifacts) into a single actionable report

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 6 (issue body, .planning/plan-approved/, plan-approval-gate.sh, SKILL.md, plans README, #2129 plan) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-16-issue-2255-reconcile-github-plan-approval-labels-with-local-marker-ledger.md |
| Tests | `scripts/enforcement/tests/test_reconcile_plan_labels.sh` |
| Implementation | `scripts/enforcement/reconcile-plan-labels.sh` |
| Plan review -- Claude | scripts/review/results/2026-04-16-plan-2255-claude-overnight.md |
| Plan review -- Codex | scripts/review/results/2026-04-16-plan-2255-codex.md |
| Plan review -- Gemini | scripts/review/results/2026-04-16-plan-2255-gemini.md |

---

## Deliverable

A `scripts/enforcement/reconcile-plan-labels.sh` script that queries GitHub issue labels via `gh`, compares them against local `.planning/plan-approved/*.md` markers, flags contradictory label combinations, generates missing markers with provenance, and outputs an implementation-ready queue snapshot -- suitable for session-start or governance audit integration.

---

## Pseudocode

```
function reconcile_plan_labels(repo_root, mode="report"):
    # Phase 1: Gather GitHub state
    approved_issues = gh_list_issues_with_label("status:plan-approved", state="open")
    review_issues = gh_list_issues_with_label("status:plan-review", state="open")
    
    # Phase 2: Gather local state
    local_markers = list_files_in(".planning/plan-approved/*.md")
    local_marker_ids = extract_issue_numbers(local_markers)
    
    # Phase 3: Detect contradictions
    contradictions = []
    for issue in all_labeled_issues:
        labels = get_labels(issue)
        if "status:plan-approved" in labels AND "status:plan-review" in labels:
            contradictions.append({"issue": issue, "type": "dual-status-labels"})
        if issue in approved_issues AND issue_number NOT in local_marker_ids:
            contradictions.append({"issue": issue, "type": "approved-no-marker"})
        if issue_number in local_marker_ids AND issue NOT in approved_issues:
            contradictions.append({"issue": issue, "type": "marker-no-label"})
    
    # Phase 4: Generate missing markers (if mode == "fix")
    if mode == "fix":
        for contradiction in contradictions where type == "approved-no-marker":
            create_marker(".planning/plan-approved/{issue_number}.md",
                         provenance="Generated by reconcile-plan-labels.sh",
                         source="GitHub label status:plan-approved",
                         timestamp=now())
    
    # Phase 5: Produce queue snapshot
    queue = {
        "ready_to_implement": approved_issues WITH local_markers,
        "approved_no_marker": approved_issues WITHOUT local_markers,
        "marker_no_label": local_markers WITHOUT approved_label,
        "contradictory_labels": dual_status_issues,
        "in_review": review_issues WITHOUT approved status,
    }
    print_report(queue)
    return exit_code (0 if clean, 1 if contradictions found)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/reconcile-plan-labels.sh` | Main reconciliation script: query GitHub labels, compare with local markers, flag contradictions, optionally generate missing markers, output queue snapshot |
| Create | `scripts/enforcement/tests/test_reconcile_plan_labels.sh` | TDD test suite for reconciliation logic: mock `gh` responses, test contradiction detection, test marker generation, test report output format |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_report_mode_no_contradictions | Clean state produces exit 0 and "no contradictions" message | Mocked `gh` output matching local markers exactly | exit 0, report with 0 contradictions |
| test_detect_approved_no_marker | Flags issue with `status:plan-approved` label but no `.planning/plan-approved/NNN.md` | Mocked `gh` with issue #9999 approved, no local marker | Report includes "approved-no-marker: #9999" |
| test_detect_marker_no_label | Flags local marker existing without corresponding GitHub label | Local marker for #8888, mocked `gh` without #8888 in approved list | Report includes "marker-no-label: #8888" |
| test_detect_dual_status_labels | Flags issue with both `status:plan-review` and `status:plan-approved` | Mocked `gh` with issue #7777 having both labels | Report includes "contradictory-labels: #7777" |
| test_fix_mode_creates_marker | Fix mode creates missing marker with provenance | Mocked `gh` with #9999 approved, no local marker, mode=fix | `.planning/plan-approved/9999.md` created with provenance header |
| test_fix_mode_marker_provenance | Generated marker includes reconciliation provenance | Mode=fix, marker generated | Marker contains "Generated by reconcile-plan-labels.sh" and timestamp |
| test_queue_snapshot_format | Queue snapshot output contains all required categories | Any state | Output contains "ready_to_implement", "approved_no_marker", "contradictory_labels", "in_review" sections |
| test_closed_issues_excluded | Closed issues are not included in the active queue snapshot | Mocked `gh` with closed issue having stale labels | Closed issue not in active queue (may appear in separate "stale" section) |
| test_exit_code_on_contradictions | Exit code is 1 when contradictions exist | Any contradictory state | exit 1 |

---

## Acceptance Criteria

- [ ] `scripts/enforcement/reconcile-plan-labels.sh` exists and is executable
- [ ] Script compares GitHub `status:plan-approved` and `status:plan-review` labels against `.planning/plan-approved/*.md` markers
- [ ] Script flags contradictory label combinations (both `status:plan-review` and `status:plan-approved` on same issue)
- [ ] Script reports issues with GitHub approval label but no local marker (`approved-no-marker`)
- [ ] Script reports local markers without corresponding GitHub approval label (`marker-no-label`)
- [ ] `--fix` mode generates missing local markers with provenance metadata (source: GitHub label, timestamp, generator script)
- [ ] Script produces an implementation-ready queue snapshot grouping issues by readiness category
- [ ] Script exits 0 when no contradictions found, 1 when contradictions exist
- [ ] Script can be integrated into session-start or governance audit flow (no interactive prompts, machine-readable output option)
- [ ] All tests pass: `bash scripts/enforcement/tests/test_reconcile_plan_labels.sh`
- [ ] No regression in existing enforcement scripts
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | overnight draft review |
| Codex | PENDING | awaiting routing |
| Gemini | PENDING | awaiting routing |

**Overall result:** PENDING

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk:** `gh` CLI must be authenticated and have access to the repository -- script should fail gracefully with a clear error if `gh` is not available or not authenticated
- **Risk:** Rate limiting on `gh api` calls if the repository has many labeled issues -- mitigate by using `gh issue list --label` which is paginated and efficient
- **Risk:** Local markers may exist for issues in other repositories or for non-existent issues -- script should validate that marker issue numbers correspond to real issues in the current repo
- **Open:** Should the script also reconcile `docs/plans/README.md` rows as a third state signal? The SKILL.md status precedence rules treat README as a convenience index that may lag; including it adds value but increases complexity. Plan proposes README reconciliation as a display-only addition (shown in report but not used for contradiction detection).
- **Open:** Should the `--fix` mode also clean up contradictory labels (remove `status:plan-review` when `status:plan-approved` is present)? Plan proposes reporting only for label cleanup, with `--fix` limited to marker generation, since label changes require explicit governance decisions per SKILL.md rules.
- **Dependency:** Related to #2129 (state-drift audit) which covers broader hygiene; this script is narrowly scoped to label-vs-marker reconciliation and can operate independently

---

## Complexity: T2

**T2** -- new script with multiple functions, TDD test suite, `gh` CLI integration, and file generation logic. Single-module scope but requires mock-based testing and multi-signal state comparison.
