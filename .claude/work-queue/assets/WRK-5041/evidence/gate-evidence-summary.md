# Gate Evidence Summary (WRK-5041, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[dev-primary], execution_workstations=[dev-primary] |
| Stage evidence gate | FAIL | stage-evidence.yaml: missing stage orders [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | FAIL | activation.yaml: orchestrator_agent missing |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests count must be 3-5 (found 1) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work.yaml: recommendations[1] must be an object |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=4 |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | FAIL | claim-evidence.yaml: route='' (empty) |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | FAIL | cross-review artifacts present but none mention 'codex' |
| Publish commit uniqueness gate | PASS | insufficient commit data — skip uniqueness check |
| Stage evidence paths gate | PASS | all stage evidence paths verified |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan_draft publish event not found — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
