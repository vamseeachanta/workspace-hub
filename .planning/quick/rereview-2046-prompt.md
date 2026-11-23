# Adversarial Re-Review Request: Issue #2046

You are an independent adversarial reviewer. This plan was revised after prior MAJOR findings. Evaluate the revised plan on its current text only. Find any remaining gaps, risks, missing edge cases, unclear scope boundaries, or workflow/governance violations. Do NOT rubber-stamp.

Return verdict as one of: APPROVE, MINOR, MAJOR.

Required output format:
1. Verdict
2. Ready for user approval: Yes/No
3. Retrieval adequacy: adequate/insufficient
4. Top blockers (numbered)
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Context:
- Repository: workspace-hub
- Review type: plan-stage adversarial re-review
- Focus on whether the revised plan is now actually approval-ready.

GitHub issue metadata:
- Issue: #2046
- Title: Audit compliance of strict issue planning workflow after rollout
- URL: https://github.com/vamseeachanta/workspace-hub/issues/2046
- Labels: priority:medium, cat:ai-orchestration, cat:operations, status:plan-review

GitHub issue body:
After the new strict planning workflow has been used for a short period, audit compliance across agent activity.

Audit focus:
- Was `issue-planning-mode` used for all issues?
- Were plans created in `docs/plans/` using the template?
- Were adversarial reviews completed before user review?
- Were labels `status:plan-review` and `status:plan-approved` used correctly?
- Did any agent begin coding before approval?

Deliverables:
- Markdown report under `docs/reports/`
- Compliance summary with examples
- Gaps, failure modes, and recommendations
- Decision: keep current approach or escalate enforcement

Suggested trigger:
- Run after 1-2 weeks of usage or after at least 10 issues have gone through the new workflow


Plan under review (docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md):
# Plan for #2046: Audit Compliance of Strict Issue Planning Workflow After Rollout

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2046
> **Review artifacts:** scripts/review/results/2026-04-14-plan-2046-codex.md | scripts/review/results/2026-04-14-plan-2046-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/workflow-compliance-audit/` already documents a broader evidence model than the previous plan used.
- Found: `.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` are enforcement surfaces whose logs/state should be treated as audit evidence where available.
- Found: `docs/plans/README.md` defines status ordering and plan-review/plan-approved semantics that this audit must verify explicitly.
- Found: `.planning/plan-approved/<issue>.md` marker files are local evidence only and must be reconciled against GitHub timeline state rather than treated as sufficient on their own.
- Found: `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` already exists as the canonical report surface and should be refreshed, not duplicated.
- Gap: there is still no script that builds a per-issue evidence matrix proving chronology between review, approval, and implementation.

### Standards
- `AGENTS.md` — hard-gate order and TDD expectation.
- `docs/plans/README.md` — planning workflow contract and status precedence.
- `docs/standards/HARD-STOP-POLICY.md` — engineering-critical enforcement policy.
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — adversarial review expectations.

### Documents consulted
- GitHub issue #2045 — onboarding baseline / rollout origin
- GitHub issue #2047 — likely escalation path if audit fails
- `docs/plans/README.md`
- `docs/standards/HARD-STOP-POLICY.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `docs/governance/TRUST-ARCHITECTURE.md`
- `docs/reports/2026-04-09-planning-workflow-compliance-audit.md`
- `.claude/skills/coordination/workflow-compliance-audit/SKILL.md`
- `.claude/hooks/plan-approval-gate.sh`
- `scripts/enforcement/require-plan-approval.sh`

### Gaps identified
- Current plan logic still over-relies on artifact presence and commit timestamps instead of chronology and evidence confidence.
- No authoritative policy matrix is yet defined for engineering-critical, non-engineering, mixed, and legacy issue cohorts.
- No fixture corpus yet covers retroactive labels, malformed review artifacts, marker/label mismatches, or commits without issue references.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
| Audit script | `scripts/enforcement/audit-planning-compliance.sh` or equivalent implementation path chosen during execution |
| Fixture corpus | `tests/fixtures/planning-compliance/` |
| Script tests | `tests/enforcement/test_audit_planning_compliance.py` |
| Canonical report | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` |
| Workflow audit reference | `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` |
| Review artifacts | `scripts/review/results/2026-04-14-plan-2046-codex.md` and `scripts/review/results/2026-04-14-plan-2046-gemini.md` |

---

## Deliverable

A reproducible compliance-audit plan that defines a per-issue evidence matrix, verifies timeline sequencing for plan-review/review/approval/implementation, and produces a canonical report with explicit included/excluded issue lists and compliant/non-compliant/indeterminate outcomes by cohort.

---

## Pseudocode

```text
load all candidate issues and classify them by cohort policy matrix:
    engineering-critical
    non-engineering
    mixed / legacy
for each in-scope issue:
    retrieve issue timeline/events
    retrieve plan artifact and status
    retrieve review artifacts and parse verdict/date
    retrieve approval marker state
    retrieve implementation evidence:
        commits
        session evidence when available
        bypass evidence when available
    build per-issue evidence matrix
    verify chronology:
        status:plan-review before approval
        adversarial review before approval
        approval before implementation evidence
    classify result as:
        compliant
        non-compliant
        indeterminate
generate canonical report with:
    included issue list
    excluded issue list with reasons
    per-issue evidence summary
    cohort counts for compliant/non-compliant/indeterminate
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Rewrite | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | strengthen evidence model and chronology requirements |
| Create | `scripts/enforcement/audit-planning-compliance.sh` or equivalent implementation file | compliance audit implementation |
| Create | `tests/fixtures/planning-compliance/` | frozen issue/timeline/review/marker/commit fixtures |
| Create | `tests/enforcement/test_audit_planning_compliance.py` | falsifiable regression tests for chronology and cohort logic |
| Update | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` | canonical audit report output |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_evidence_matrix_records_all_required_signals` | each issue record contains plan/review/label/marker/implementation evidence fields | fixture issue set | complete evidence matrix |
| `test_status_plan_review_precedes_approval` | chronology proves plan-review happened before approval | timeline fixture | pass/fail |
| `test_review_precedes_approval` | adversarial review timestamps precede approval | review + timeline fixture | pass/fail |
| `test_marker_without_timeline_proof_is_not_auto_compliant` | marker alone is insufficient | marker-only fixture | indeterminate or non-compliant |
| `test_commit_only_signal_is_low_confidence` | commit timestamps alone do not overstate proof | commit-only fixture | indeterminate |
| `test_retroactive_label_is_flagged` | retroactive approval/review label drift is surfaced | retroactive label fixture | non-compliant or indeterminate |
| `test_commits_without_issue_reference_do_not_force_false_negative` | lack of #NNN in commit history does not wrongly prove compliance | no-issue-ref fixture | indeterminate |
| `test_report_emits_included_and_excluded_issue_lists` | report denominator is reproducible | mixed cohort fixture | explicit included/excluded lists |
| `test_report_splits_compliant_noncompliant_indeterminate_by_cohort` | headline metrics are cohort-aware and falsifiable | mixed fixture set | separate counts |

---

## Acceptance Criteria

- [ ] Audit logic uses a per-issue evidence matrix rather than simple artifact presence checks.
- [ ] The audit explicitly verifies chronology for `status:plan-review`, adversarial review, approval evidence, and implementation evidence.
- [ ] Engineering-critical, non-engineering, mixed, and legacy cohort rules are defined before implementation.
- [ ] Report output includes included issue list, excluded issue list with reasons, and per-issue evidence summary.
- [ ] Report output distinguishes compliant, non-compliant, and indeterminate issues by cohort.
- [ ] Fixture-backed tests cover retroactive labels, malformed/missing review artifacts, marker/label drift, and weak implementation evidence cases.
- [ ] Existing canonical report path is refreshed rather than replaced with a parallel reporting surface.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MAJOR | Evidence model too weak; chronology and denominator handling not strong enough |
| Gemini | MAJOR | Missing `status:plan-review` verification, weak skill-usage evidence, and weak rollout cohort logic |

**Overall result:** MAJOR — not approval-ready

Revisions required before approval:
- move from artifact-presence checks to evidence-matrix checks
- verify chronology explicitly
- define cohort policy matrix and indeterminate handling
- make report output reproducible and fixture-backed

---

## Risks and Open Questions

- **Risk:** GitHub timeline/event history may be incomplete for some historical issues; those cases must remain indeterminate rather than silently compliant.
- **Risk:** weak evidence sources such as commit timestamps can distort the audit if not explicitly treated as lower confidence.
- **Open:** none for approval readiness; chronology, cohort rules, and output reproducibility must be explicit before this plan returns to review.

---

## Complexity: T2

**T2** — moderate audit/reporting implementation with timeline parsing, evidence classification, and fixture-backed verification.


Review questions — address ALL:
1. Did the revision resolve the prior MAJOR blockers in a concrete way?
2. Is retrieval now adequate for the issue class?
3. Are files-to-change, TDD, acceptance criteria, and risks concrete and falsifiable?
4. Are there still unresolved scope/governance/status inconsistencies that should block approval?
5. Should this revised plan now be approved, revised again, or split?
