# Gate Evidence Summary (WRK-1244, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage_evidence_ref missing in WRK frontmatter |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | FAIL | activation.yaml: set_active_wrk must be true |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1244/review.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests must be a list |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work.yaml: empty recommendations and no_follow_ups_rationale missing |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=4 |
| User-review close gate | FAIL | user-review-close.yaml: missing fields: ['reviewed_at'] |
| Reclaim gate | FAIL | reclaim.yaml: invalid reclaim_decision=missing |
| Approval ordering gate | FAIL | timestamp ordering violation: plan-final-review.confirmed_at (2026-03-16T21:10:00Z) >= claim-evidence.claimed_at (2026-03-16T21:10:00Z) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | user-review-browser-open.yaml absent — skip elapsed check |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (4 file(s) checked) |
| Publish commit uniqueness gate | PASS | user-review-publish.yaml absent — skip commit uniqueness check |
| Stage evidence paths gate | PASS | stage-evidence.yaml absent — skip path existence check |
| Done/pending contradiction gate | PASS | stage-evidence.yaml absent — skip done/pending check |
| Plan publish predates approval gate | PASS | user-review-publish.yaml absent — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | FAIL | reclaim.yaml: invalid reclaim_decision=missing |
