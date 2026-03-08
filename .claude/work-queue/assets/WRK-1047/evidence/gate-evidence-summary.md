# Gate Evidence Summary (WRK-1047, phase=claim)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1, ace-linux-2, acma-ansys05] |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | FAIL | routing:missing-provider ; plan:missing-provider |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: events[1] must confirm default browser open |
| User-review publish gate | FAIL | user-review-publish.yaml: events[1] pushed_to_origin must be true |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=claim) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=plan_final: approval confirmed only 0s after browser open (min 300s required) |
| Sentinel values gate | FAIL | activation.yaml: orchestrator_agent='unknown' |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Stage1 capture gate | PASS | stage1 capture gate passed: reviewer=vamsee, confirmed_at=2026-03-08T12:00:00Z |
