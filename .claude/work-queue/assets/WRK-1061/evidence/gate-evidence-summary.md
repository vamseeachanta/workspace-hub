# Gate Evidence Summary (WRK-1061, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=WRK-1061-lifecycle.html, confirmation=confirmation block incomplete — confirmed_by, confirmed_at, decision=missing (need 'passed') |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stages[1] order must be integer |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | FAIL | routing:missing-actions=['work_queue_skill', 'work_wrapper_complete'] ; plan:missing-actions=['plan_draft_complete', 'plan_wrapper_complete'] ; execute:missing-actions=['execute_wrapper_complete', 'tdd_eval'] ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1061/review.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=3 (all passing) |
| Legal gate | FAIL | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1061/legal-scan.md, result=missing |
| Claim gate | WARN | claim-evidence.yaml: metadata_version='' (legacy schema — WARN only) |
| Future-work gate | FAIL | future-work.yaml: recommendations[1] disposition must be existing-updated\|spun-off-new |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=2 |
| User-review close gate | FAIL | user-review-close.yaml missing |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | FAIL | cross-review.yaml.reviewed_at: date-only value '2026-03-09' — time component required |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (4 file(s) checked) |
| Publish commit uniqueness gate | PASS | insufficient commit data — skip uniqueness check |
| Stage evidence paths gate | PASS | all stage evidence paths verified |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan_draft publish event not found — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
