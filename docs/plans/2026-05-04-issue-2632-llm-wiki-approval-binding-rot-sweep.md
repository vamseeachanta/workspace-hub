# Issue #2632: llm-wiki approval-binding rot sweep

> **Status:** plan-review
> **Date:** 2026-05-04
> **Complexity:** T2 — governance reconciliation / report
> **Review artifacts:** `scripts/review/results/2026-05-04-plan-2632-claude.md`, `scripts/review/results/2026-05-04-plan-2632-gemini.md`

## Problem Statement

Issue #2632 will reconcile approval-binding rot for #2368, #2124, and #2125 where GitHub labels, issue comments, local plan files, and approval markers may disagree. The work will report and recommend dispositions; it will not self-create approval markers, self-approve, or mutate approval labels without normal governance authorization.

- `/mnt/ace` raw corpora will remain outside git; approved implementation will promote only curated summaries, metadata, cross-links, and provenance fields.
- No plan will self-approve, create approval markers, or move an issue to `status:plan-approved`; this plan will stop at `status:plan-review` for user approval.
- Codex adversarial review remains unavailable due #2479 unless verified fixed; this plan will not block solely on Codex.

## Resource Intelligence Summary

| Source | Evidence | Impact |
|---|---|---|
| `docs/plans/README.md` | Defines plan-review / plan-approved workflow and marker expectations | Supplies hard-stop rules. |
| #2368/#2124/#2125 live issue state | Targets have materially different label/comment/marker conditions | Requires case-by-case disposition rather than one generic missing-marker rule. |

## Governance Decision Table

| Case | Evidence state | Allowed disposition | Prohibited action |
|---|---|---|---|
| A | Label + marker + matching plan blob | Treat as bound after verification | Rewriting marker without user approval |
| B | Label + explicit revision-bound issue comment but no marker | Report as comment-bound; recommend marker recreation only after user-approved governance action | Creating marker in this issue |
| C | Label only, no valid revision-bound evidence | Recommend downgrade to `status:plan-review` or re-plan path | Treating label as sufficient approval |
| D | Stale/missing local plan artifact | Report stale artifact and recommend redraft/review | Inferring approval from stale local state |
| E | Implementation already occurred under disputed binding | Preserve evidence and escalate for user disposition | Retroactively manufacturing approval |

## Scope

### In Scope
- Produce a reconciliation report classifying #2368/#2124/#2125 separately.
- Post report-link/disposition comments only.
- Recommend label changes, marker recreation, re-plan, or deferral without executing self-approval actions.

### Out of Scope
- Creating `.planning/plan-approved/*.md` markers.
- Moving any issue to `status:plan-approved`.
- Implementing underlying llm-wiki deliverables.
- Building an approval-binding checker in this issue; checker work will be a separate optional follow-up.

## Proposed Deliverable

The approved implementation will write `docs/reports/llm-wiki-approval-binding-rot-sweep-2026-05-04.md` with per-issue evidence, classification, and recommended disposition. It may post report-link comments to #2368/#2124/#2125/#2632, but it will not create markers or mutate approval labels unless separately authorized.

## Pseudocode / TDD Contract

```python
def test_report_classifies_each_target_issue():
    for n in [2368, 2124, 2125]:
        assert report[n].classification in {"bound", "comment-bound", "label-only", "stale-local", "escalate"}
        assert report[n].evidence.links_to_issue_and_local_state

def test_no_self_approval_side_effects():
    assert not creates_plan_approved_markers
    assert not adds_status_plan_approved
```

## Files to Change

| Action | Path | Purpose |
|---|---|---|
| Create | `docs/reports/llm-wiki-approval-binding-rot-sweep-2026-05-04.md` | Evidence-backed reconciliation report |
| Comment | GitHub issues #2368/#2124/#2125/#2632 | Report-link comments only; no self-approval markers |

## Acceptance Criteria

- [ ] Report will classify #2368/#2124/#2125 separately using live evidence.
- [ ] Report will define precedence for labels, local markers, local plans, and issue-comment approvals.
- [ ] Recommended label/marker actions will require user/governance authorization.
- [ ] No approval marker or `status:plan-approved` label will be created by this issue.
- [ ] Optional checker work will remain a separate follow-up.

## Adversarial Review Summary

| Reviewer | Verdict | Notes |
|---|---|---|
| Claude internal | MAJOR → RESOLVED | Findings required target-specific evidence, governance precedence cases, and separation of checker implementation scope. Applied; artifact: `scripts/review/results/2026-05-04-plan-2632-claude.md`. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Rerun path recorded in `scripts/review/results/2026-05-04-plan-2632-gemini.md`. |
| Codex | UNAVAILABLE | Codex remains unavailable due #2479. |

**Overall result:** APPROVAL-READY FOR USER REVIEW; stop at `status:plan-review`.
