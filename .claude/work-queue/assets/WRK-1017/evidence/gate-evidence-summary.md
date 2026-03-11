# Gate Evidence Summary (WRK-1017, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=20, contract=20-stage |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | pre-cutoff backfill (id=1017, created_at=2026-03-05T00:00:00Z) — log gate skipped |
| User-review HTML-open gate | PASS | user-review-browser-open.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| User-review publish gate | PASS | user-review-publish.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1017/review-synthesis.md |
| TDD gate | PASS | test files=['ac-test-matrix.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=4 (all passing) |
| Legal gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1017/legal-scan.md, result=pass |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=claude, quota=available(null) |
| Future-work gate | PASS | future-work.yaml: recommendations=1 |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: no_additions_rationale=present |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=plan_draft: approval confirmed only -62s after browser open (min 300s required) |
| Sentinel values gate | FAIL | activation.yaml: session_id='unknown' |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (2 file(s) checked) |
| Publish commit uniqueness gate | PASS | publish commits appear unique across stages |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[8] evidence path not found: .claude/work-queue/assets/WRK-1017/evidence/claim.yaml |
| Done/pending contradiction gate | FAIL | stage-evidence.yaml: stage[1] (order=1) status=done but comment contains contradiction: 'WRK created in pending queue with baseline metadata.' |
| Plan publish predates approval gate | FAIL | plan_draft published_at (2026-03-06T10:56:44Z) < reviewed_at (2026-03-06T23:01:20Z): publish predates approval |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
