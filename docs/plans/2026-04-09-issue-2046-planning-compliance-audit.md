# Plan for #2046: Audit Compliance of Strict Issue Planning Workflow After Rollout

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2046
> **Review artifacts:** scripts/review/results/2026-04-13-plan-2046-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/workflow-compliance-audit/` — existing audit skill and prior governance context.
- Found: `scripts/enforcement/require-plan-approval.sh` — pre-commit enforcement surface for plan approval.
- Found: `.claude/hooks/plan-approval-gate.sh` — PreToolUse enforcement hook.
- Found: `docs/plans/README.md` — plan index with local plan status tracking.
- Found: `.planning/plan-approved/<issue>.md` markers are the canonical local evidence that approval existed before implementation.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` explicitly states that valid implementation requires both `status:plan-approved` and the approval marker file.
- Found: `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` already exists, so this issue should standardize/refresh that report surface rather than invent a second reporting path.
- Gap: there is no automated script that combines issue timeline/events evidence, approval markers, review artifacts, and commit timing into a trustworthy compliance audit.

### Standards
N/A — operations/governance task

### Documents consulted
- Issue #2045 — onboarding task (prerequisite)
- Issue #2047 — enforcement escalation (follow-up if audit fails)
- `docs/standards/HARD-STOP-POLICY.md` — defines hard-stop compliance expectations
- `docs/governance/TRUST-ARCHITECTURE.md` — defines valid approval evidence (`status:plan-approved` + marker file)
- `docs/plans/README.md` — current plan index and status semantics
- Existing report `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` — proves a canonical report surface already exists

### Gaps identified
- No script exists to combine GitHub issue timeline/events evidence with local approval-marker and review-artifact evidence.
- No canonical denominator is defined for the compliance rate; the audit must explicitly scope to issues created after the rollout/onboarding date and classify engineering-critical vs non-engineering issues separately.
- No fixture-backed test corpus exists for timeline snapshots, marker presence, review-artifact presence, and implementation-before-approval ordering.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
| Audit script | `scripts/enforcement/audit-planning-compliance.sh` |
| Fixture corpus | `tests/fixtures/planning-compliance/` |
| Script tests | `tests/enforcement/test_audit_planning_compliance.py` |
| Audit report | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` |
| Review artifact | `scripts/review/results/2026-04-13-plan-2046-subagent.md` |

---

## Deliverable

A compliance audit script, fixture-backed test suite, and canonical report that measures planning-workflow compliance only for in-scope post-rollout issues, using issue timeline/events plus local approval-marker/review evidence to determine whether approval preceded implementation.

---

## Pseudocode

```
function audit_planning_compliance():
    issues = gh issue list --state all --limit N --json number,title,labels,createdAt
    eligible_issues = filter issues created on/after rollout cutoff from #2045
    for each eligible issue:
        timeline = gh api issue timeline/events for label/comment state transitions
        has_plan = check docs/plans/ for matching plan file
        has_review = check scripts/review/results/ for review artifacts tied to issue number
        has_plan_approved_label = prove via timeline that status:plan-approved was added
        has_approval_marker = check .planning/plan-approved/{issue.number}.md exists
        implementation_commits = git log --grep="#{issue.number}" --oneline --format with commit timestamps
        approval_precedes_implementation = compare first approved timestamp / marker evidence to first implementation commit timestamp
        classify issue into cohort:
            in-scope engineering-critical
            in-scope non-engineering
            legacy/pre-rollout excluded
            indeterminate (insufficient evidence)
        compliant = has_plan AND has_review AND has_plan_approved_label AND has_approval_marker AND approval_precedes_implementation
    generate canonical report with denominator by cohort
    calculate compliance rate only on in-scope eligible cohort
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/audit-planning-compliance.sh` | Automated compliance audit script |
| Create | `tests/fixtures/planning-compliance/` | frozen issue/timeline/marker/commit fixtures for trustworthy regression testing |
| Create | `tests/enforcement/test_audit_planning_compliance.py` | fixture-backed tests for denominator, timeline proof, and ordering logic |
| Update | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` | canonical audit results report |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_audit_finds_compliant_issue | script correctly identifies a post-rollout issue with plan+review+approval marker+approval-before-implementation | fixture issue/timeline/marker/commit set | compliant=true |
| test_audit_excludes_pre_rollout_issue | legacy issue before rollout cutoff is excluded from denominator | pre-rollout fixture | excluded cohort |
| test_audit_marks_indeterminate_without_timeline_proof | missing timeline evidence does not produce a false compliant result | fixture missing label-event history | indeterminate |
| test_audit_detects_implementation_before_approval | commit timestamp before approval evidence is flagged non-compliant | fixture with reversed ordering | compliant=false |
| test_audit_separates_engineering_and_non_engineering_cohorts | denominator and report split by cohort | mixed fixture set | separate cohort counts |
| test_audit_report_format | report has required sections and cohort-based compliance summary | audit output | contains summary, per-issue table, cohort rates |

---

## Acceptance Criteria

- [ ] Audit script runs and produces a canonical report.
- [ ] Report covers an explicit post-rollout in-scope cohort and documents excluded legacy issues separately.
- [ ] Compliance rate is calculated only for the defined eligible denominator.
- [ ] Non-compliant and indeterminate issues are listed with specific evidence gaps.
- [ ] Approval-before-implementation is proven using issue timeline/events plus local approval-marker and commit-timestamp evidence.
- [ ] Fixture-backed tests cover timeline-proof, cohort selection, and ordering logic.
- [ ] Report posted as GitHub issue comment on #2046.
- [ ] Results inform whether #2047 enforcement escalation is needed.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Subagent review | MAJOR | Historical-proof gap, weak fixture strategy, ambiguous denominator |

**Overall result:** MINOR (approval-ready after revision)

Revisions made based on review:
- replaced current-label-only logic with timeline/events plus marker/commit ordering proof
- defined post-rollout eligible cohort and legacy exclusions explicitly
- added fixture corpus and test suite requirements
- aligned the report path to the existing canonical audit report artifact

---

## Risks and Open Questions

- **Risk:** GitHub issue timeline/event access may be rate-limited or incomplete for older issues; the audit must classify such cases as indeterminate, not silently compliant/non-compliant.
- **Risk:** rollout cutoff selection may change the headline compliance rate; the report must show the denominator clearly.
- **Open:** none for plan approval readiness; remaining uncertainty is implementation-time data quality, not plan ambiguity.

---

## Complexity: T2

**T2** — new script with moderate logic, report generation, and integration with GitHub API.
