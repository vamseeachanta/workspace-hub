# Gate Evidence Summary (WRK-1139, phase=archive)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | matched routing:['work_queue_skill'], plan:['plan_draft_complete'], execute:['execute_wrapper_complete'], cross-review:['agent_cross_review', 'review_wrapper_complete'] |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: events[1] must confirm default browser open |
| User-review publish gate | FAIL | user-review-publish.yaml: events[1] documents must be a non-empty list |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=archive) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=close_review: approval confirmed only 0s after browser open (min 300s required) |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Archive readiness gate | WARN | archive-tooling.yaml: document_index_ref absent — exemption accepted: hub-only config change — no document-index entries affected |
