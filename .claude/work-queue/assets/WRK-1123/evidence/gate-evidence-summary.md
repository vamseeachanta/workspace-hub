# Gate Evidence Summary (WRK-1123, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stage order 17 must be done\|n/a before close (found pending) |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=4 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_queue_skill'], plan:['plan_wrapper_complete'], execute:['tdd_eval'], cross-review:['agent_cross_review'] |
| User-review HTML-open gate | PASS | user-review-browser-open.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| User-review publish gate | PASS | user-review-publish.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1123/review.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=3 (all passing) |
| Legal gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1123/legal-scan.md, result=PASS — no violations found |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | PASS | future-work.yaml: recommendations=2 |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=4 |
| User-review close gate | FAIL | user-review-close.yaml missing |
| Reclaim gate | WARN | reclaim.yaml: status=n/a (Stage 18 not triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (4 file(s) checked) |
| Publish commit uniqueness gate | PASS | publish commits appear unique across stages |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[17] evidence path not found: .claude/work-queue/assets/WRK-1123/evidence/user-review-close.yaml |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | user-review-plan-draft.yaml absent — skip ordering check |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a; reclaim.yaml is placeholder |
