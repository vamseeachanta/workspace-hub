Revision brief for #2046 plan

Revise the #2046 plan to make the audit falsifiable and evidence-driven rather than artifact-presence-driven.

Required revisions
1. Strengthen the evidence model:
- replace simple has_plan / has_review / has_plan-approved checks with a per-issue evidence matrix recording:
  - plan artifact
  - review artifacts with parsed verdict/date
  - status:plan-review timeline event
  - status:plan-approved timeline event
  - local approval marker
  - implementation evidence
  - bypass/session evidence when available
- define confidence levels: compliant / non-compliant / indeterminate

2. Verify chronology, not just presence:
- prove status:plan-review happened
- prove adversarial review completed before approval
- prove approval evidence existed before any implementation evidence
- do not rely on commit timestamps alone; incorporate session logs and bypass evidence when available
- scope cohorts by when issues entered planning, not only issue creation date

3. Add explicit label/state sequencing rules:
- define the authoritative policy matrix for engineering-critical, non-engineering, mixed, and legacy issues
- verify both status:plan-review and status:plan-approved behavior
- surface plan-file / GitHub / marker drift as a finding

4. Make outputs reproducible and falsifiable:
- require included issue list
- excluded issue list with reasons
- per-issue evidence summary
- separate compliant / non-compliant / indeterminate counts by cohort
- reconcile with existing docs/reports/2026-04-09-planning-workflow-compliance-audit.md instead of treating this as greenfield

5. Expand fixtures/tests for false positives and false negatives:
- retroactive labels
- malformed or post-approval review artifacts
- marker without timeline proof
- label without marker
- commits without issue refs
- local/session evidence of work before approval
- phantom plan/index entries
- legacy issues that entered planning after rollout
