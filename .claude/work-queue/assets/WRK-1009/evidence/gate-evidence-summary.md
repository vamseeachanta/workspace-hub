# Gate Evidence Summary (WRK-1009, phase=claim)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=workflow-final-review.html, confirmation=confirmation block incomplete — confirmed_by, confirmed_at, decision=missing (need 'passed') |
| Workstation contract gate | PASS | plan_workstations=ace-linux-1, execution_workstations=ace-linux-1 |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=5 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | pre-cutoff backfill (id=1009, created_at=2026-03-04T12:42:00Z) — log gate skipped |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final'] |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=claim) |
| Midnight UTC sentinel gate | FAIL | midnight UTC sentinel detected in user-review-plan-draft.yaml.reviewed_at: 2026-03-10T00:00:00Z |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Stage1 capture gate | FAIL | user-review-capture.yaml missing |
