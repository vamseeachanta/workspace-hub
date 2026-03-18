# Gate Evidence Summary (WRK-1323, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stages[1] stage missing |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_queue_skill', 'work_wrapper_complete'], plan:['plan_draft_complete', 'plan_wrapper_complete'], execute:['execute_wrapper_complete', 'tdd_eval'], cross-review:['agent_cross_review', 'review_wrapper_complete'] |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1323/review.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=3 (all passing) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work.yaml: recommendations[1] status missing |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: no_additions_rationale=present |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (3 file(s) checked) |
| Publish commit uniqueness gate | PASS | insufficient commit data — skip uniqueness check |
| Stage evidence paths gate | PASS | all stage evidence paths verified |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan_draft publish event not found — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
