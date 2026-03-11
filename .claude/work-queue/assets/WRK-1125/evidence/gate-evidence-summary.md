# Gate Evidence Summary (WRK-1125, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=20, contract=20-stage |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_queue_skill', 'work_wrapper_complete'], plan:['plan_draft_complete', 'plan_wrapper_complete'], execute:['execute_wrapper_complete', 'tdd_eval'], cross-review:['agent_cross_review', 'review_wrapper_complete'] |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['close_review'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1125/review.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests must be a list |
| Legal gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1125/legal-scan.md, result=PASS |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=claude, quota=available(null) |
| Future-work gate | FAIL | future-work evidence absent (legacy item — WARN) |
| Resource-intelligence update gate | FAIL | resource-intelligence-update.yaml missing |
| User-review close gate | FAIL | user-review-close.yaml: missing fields: ['reviewer', 'reviewed_at'] |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | WARN | bypass: Route A inline review — no separate browser review session required (stage=plan_draft, delta=0s) |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (2 file(s) checked) |
| Publish commit uniqueness gate | WARN | plan_draft and plan_final share commit '20a2d3e64ec1fe62afce4ba41b918e2e42cc4a3a' — possible placeholder (WARN) |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[4] evidence path not found: specs/wrk/WRK-1125/plan.md |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan publish ordering OK (published=2026-03-11T13:00:00Z, reviewed=2026-03-11T13:00:00Z) |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
