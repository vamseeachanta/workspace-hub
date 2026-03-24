# Gate Evidence Summary (workspace-hub-1345, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[dev-primary], execution_workstations=[dev-primary] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stage order 10 must be done\|n/a before close (found in_progress) |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=complete, p1_count=0, core_skills=3 |
| Activation gate | FAIL | activation.yaml: set_active_wrk must be true |
| Agent log gate | WARN | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log (optional — no multi-agent indicators) |
| GitHub issue gate | PASS | github_issue_ref OK: https://github.com/vamseeachanta/workspace-hub/issues/1345 |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | FAIL | none |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests must have 3+ unique tests (found 1) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work evidence absent (legacy item — WARN) |
| Resource-intelligence update gate | FAIL | resource-intelligence-update.yaml missing |
| User-review close gate | FAIL | user-review-close.yaml: missing fields: ['reviewed_at'] |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | FAIL | timestamp ordering violation: execute.executed_at (2026-03-24T14:30:00Z) >= user-review-close.confirmed_at (2026-03-24T14:30:00Z) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (4 file(s) checked) |
| Stage evidence paths gate | PASS | all stage evidence paths verified |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
