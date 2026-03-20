# Gate Evidence Summary (WRK-1030, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=dev-primary, execution_workstations=dev-primary |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=20, contract=20-stage |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_wrapper_complete'], plan:['plan_wrapper_complete'], execute:['execute_wrapper_complete'], cross-review:['review_wrapper_complete'] |
| User-review HTML-open gate | PASS | user-review-browser-open.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| User-review publish gate | PASS | user-review-publish.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1030/review.md |
| TDD gate | PASS | test files=['test-results.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=4 (all passing) |
| Legal gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1030/legal-scan.md, result=PASS |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Future-work gate | PASS | future-work.yaml: recommendations=2 |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=2 |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | FAIL | timestamp ordering violation: execute.executed_at (2026-03-07T00:00:00Z) >= user-review-close.confirmed_at (2026-03-07T00:00:00Z) |
| Midnight UTC sentinel gate | FAIL | midnight UTC sentinel detected in user-review-plan-draft.yaml.reviewed_at: 2026-03-07T00:00:00Z |
| Browser open elapsed time gate | FAIL | stage=plan_draft: approval confirmed only 0s after browser open (min 300s required) |
| Sentinel values gate | FAIL | activation.yaml: session_id='unknown'; activation.yaml: orchestrator_agent='unknown' |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | FAIL | cross-review.yaml: reviewer=claude only (no codex) |
| Publish commit uniqueness gate | FAIL | all three publish stages share commit 'ac544ce16e82e36c68b0438e13317004e48b350a' (likely placeholder) |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[4] evidence path not found: specs/wrk/WRK-1030/plan.md |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan publish ordering OK (published=2026-03-07T00:00:00Z, reviewed=2026-03-07T00:00:00Z) |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
