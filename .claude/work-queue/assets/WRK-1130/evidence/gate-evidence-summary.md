# Gate Evidence Summary (WRK-1130, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=20, contract=20-stage |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | FAIL | execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['close_review'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1130/review-synthesis.md |
| TDD gate | FAIL | none |
| Integrated test gate | FAIL | execute evidence missing (required: evidence/execute.yaml) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Future-work gate | FAIL | future-work evidence absent (legacy item — WARN) |
| Resource-intelligence update gate | FAIL | resource-intelligence-update.yaml missing |
| User-review close gate | FAIL | user-review-close.yaml: missing fields: ['reviewer', 'reviewed_at'] |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (2 file(s) checked) |
| Publish commit uniqueness gate | WARN | plan_draft and plan_final share commit 'f1c157c8' — possible placeholder (WARN) |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[4] evidence path not found: specs/wrk/WRK-1130/plan.md |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan publish ordering OK (published=2026-03-12T00:30:00Z, reviewed=2026-03-12T00:30:00Z) |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
