# Gate Evidence Summary (WRK-1086, phase=claim)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_queue_skill'], plan:['plan_draft_complete'] |
| User-review HTML-open gate | PASS | user-review-browser-open.yaml: stages=['plan_draft', 'plan_final'] |
| User-review publish gate | PASS | user-review-publish.yaml: stages=['plan_draft', 'plan_final'] |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=claim) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=plan_draft: approval confirmed only 0s after browser open (min 300s required) |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Stage1 capture gate | PASS | stage1 capture gate passed: reviewer=vamsee, confirmed_at=2026-03-12T08:20:00Z |
