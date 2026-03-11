# Gate Evidence Summary (WRK-1014, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=20, contract=20-stage |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | pre-cutoff backfill (id=1014, created_at=2026-03-05T05:15:00Z) — log gate skipped |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final', 'close_review'] |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | FAIL | none |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests[1] missing fields: ['artifact_ref'] |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work.yaml: empty recommendations and no_follow_ups_rationale missing |
| Resource-intelligence update gate | FAIL | resource-intelligence-update.yaml: add additions[] or no_additions_rationale |
| User-review close gate | FAIL | user-review-close.yaml missing |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | FAIL | timestamp ordering violation: claim-evidence.claimed_at (2026-03-10T00:00:00Z) >= execute.executed_at (2026-03-10T00:00:00Z) |
| Midnight UTC sentinel gate | FAIL | midnight UTC sentinel detected in user-review-plan-draft.yaml.reviewed_at: 2026-03-10T00:00:00Z |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | FAIL | claim-evidence.yaml: route='' (empty) |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (1 file(s) checked) |
| Publish commit uniqueness gate | PASS | user-review-publish.yaml absent — skip commit uniqueness check |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[5] evidence path not found: .claude/work-queue/assets/WRK-1014/plan-html-review-draft.md |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | user-review-publish.yaml absent — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
