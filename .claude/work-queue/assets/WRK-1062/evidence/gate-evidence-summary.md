# Gate Evidence Summary (WRK-1062, phase=claim)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['plan_draft', 'plan_final'] |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=claim) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | FAIL | claim-evidence.yaml: route='' (empty) |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Stage1 capture gate | PASS | stage1 capture gate passed: reviewer=vamsee, confirmed_at=2026-03-09 06:30:00+00:00 |
