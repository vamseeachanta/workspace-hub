# Gate Evidence Summary (WRK-1061, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stage order 14 must be done\|n/a before close (found in_progress) |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_wrapper_complete'], plan:['plan_draft_complete'], execute:['execute_wrapper_complete', 'tdd_eval'], cross-review:['agent_cross_review', 'review_wrapper_complete'] |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['close_review'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1061/review.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=3 (all passing) |
| Legal gate | FAIL | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1061/legal-scan.md, result=missing |
| Claim gate | WARN | claim-evidence.yaml: metadata_version='' (legacy schema — WARN only) |
| Future-work gate | FAIL | future-work.yaml: recommendations[1] captured must be true before close |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=2 |
| User-review close gate | FAIL | user-review-close.yaml missing |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | FAIL | user-review-capture.yaml.reviewed_at: date-only value '2026-03-09' — time component required |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (4 file(s) checked) |
| Publish commit uniqueness gate | WARN | plan_draft and plan_final share commit '94e4a90ce6f0d46123e479b1ade9583b80d628b8' — possible placeholder (WARN) |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[1] evidence path not found: evidence/user-review-capture.yaml |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | WARN | cannot parse reviewed_at: '2026-03-09' |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
