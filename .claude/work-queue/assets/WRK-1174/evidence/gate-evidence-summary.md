# Gate Evidence Summary (WRK-1174, phase=archive)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=ace-linux-1, execution_workstations=ace-linux-1 |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | FAIL | activation.yaml: set_active_wrk must be true |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | FAIL | timestamp ordering violation: claim-evidence.claimed_at (2026-03-14 12:00:00+00:00) >= execute.executed_at (2026-03-14 12:00:00+00:00) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | user-review-browser-open.yaml absent — skip elapsed check |
| Sentinel values gate | FAIL | claim-evidence.yaml: route='' (empty) |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Archive readiness gate | FAIL | archive-tooling.yaml absent: /mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1174/evidence/archive-tooling.yaml |
