# Plan for #2046: Audit Compliance of Strict Issue Planning Workflow After Rollout

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2046
> **Review artifacts:** pending

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/workflow-compliance-audit/` — existing audit skill
- Found: `scripts/review/cross-review-gate.sh` — checks for review artifacts
- Found: `scripts/enforcement/require-plan-approval.sh` — pre-commit plan gate
- Found: `.claude/hooks/plan-approval-gate.sh` — PreToolUse enforcement hook
- Found: `docs/plans/README.md` — plan index with status tracking
- Gap: No automated script to audit planning compliance across all recent issues

### Standards
N/A — operations/governance task

### Documents consulted
- Issue #2045 — onboarding task (prerequisite)
- Issue #2047 — enforcement escalation (follow-up if audit fails)
- `docs/standards/HARD-STOP-POLICY.md` — defines what compliance means

### Gaps identified
- No script exists to scan recent GitHub issues and check: (a) plan file exists, (b) adversarial review done, (c) labels applied correctly, (d) approval marker exists before implementation
- No dashboard or report format for compliance metrics

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
| Audit script | `scripts/enforcement/audit-planning-compliance.sh` |
| Audit report | `docs/reports/2026-04-09-planning-compliance-audit.md` |

---

## Deliverable

A compliance audit script and report that measures what percentage of recent GitHub issues followed the mandatory planning workflow (plan file, adversarial review, labels, user approval before implementation).

---

## Pseudocode

```
function audit_planning_compliance():
    issues = gh issue list --state all --limit 50 --json number,title,labels,createdAt
    for each issue in issues:
        has_plan = check docs/plans/ for matching plan file
        has_review = check scripts/review/results/ for review artifacts
        has_plan_review_label = "status:plan-review" in issue.labels (current or historical)
        has_plan_approved_label = "status:plan-approved" in issue.labels
        has_approval_marker = check .planning/plan-approved/{issue.number}.md exists
        implementation_commits = git log --grep="#{issue.number}" --oneline
        compliant = has_plan AND (has_review OR is_non_engineering) AND has_approval
    generate_report(results)
    calculate_compliance_rate()
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/audit-planning-compliance.sh` | Automated compliance audit script |
| Create | `docs/reports/2026-04-09-planning-compliance-audit.md` | Audit results report |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_audit_finds_compliant_issue | script correctly identifies issue with plan+labels | issue #2045 with plan file | compliant=true |
| test_audit_finds_non_compliant_issue | script flags issue missing plan | issue without plan file | compliant=false |
| test_audit_report_format | report has required sections | audit output | contains summary, per-issue table, rate |

---

## Acceptance Criteria

- [ ] Audit script runs and produces a report
- [ ] Report covers at least 20 recent issues
- [ ] Compliance rate is calculated and reported
- [ ] Non-compliant issues are listed with specific gaps
- [ ] Report posted as GitHub issue comment on #2046
- [ ] Results inform whether #2047 enforcement escalation is needed

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Pending | — | Review not yet run |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** Audit may show 0% compliance for issues created before the onboarding (#2045) was complete
- **Open:** Should the audit only cover issues created after the onboarding date, or all recent issues?
- **Open:** How to handle issues that were implemented before the planning workflow existed?

---

## Complexity: T2

**T2** — new script with moderate logic, report generation, and integration with GitHub API.
