# Gate Evidence Summary (WRK-1161, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmation block incomplete — decision=approved (need 'passed') |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stages must be a list |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_wrapper_complete'], plan:['plan_wrapper_complete'], execute:['tdd_eval'], cross-review:['review_wrapper_complete'] |
| User-review HTML-open gate | PASS | user-review-browser-open.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| User-review publish gate | PASS | user-review-publish.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1161/review.md |
| TDD gate | PASS | test files=['test-results.md'] |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests[1] scope must be integrated\|repo |
| Legal gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1161/legal-scan.md, result=PASS |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | PASS | future-work.yaml: no_follow_ups_rationale=present |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: no_additions_rationale=present |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=close_review: approval confirmed only 240s after browser open (min 300s required) |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | FAIL | cross-review artifacts present but none mention 'codex' |
| Publish commit uniqueness gate | FAIL | all three publish stages share commit 'cab4cb5a' (likely placeholder) |
| Stage evidence paths gate | PASS | stages not a list — skip |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | user-review-plan-draft.yaml absent — skip ordering check |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
