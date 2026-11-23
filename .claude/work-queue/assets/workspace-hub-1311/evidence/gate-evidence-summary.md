# Gate Evidence Summary (workspace-hub-1311, phase=archive)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | FAIL | plan_workstations=missing, execution_workstations=missing |
| Resource-intelligence gate | FAIL | resource-intelligence evidence absent (legacy item — WARN) |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | WARN | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log (optional — no multi-agent indicators) |
| GitHub issue gate | PASS | github_issue_ref OK: https://github.com/vamseeachanta/workspace-hub/issues/1311 |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=archive) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Archive readiness gate | FAIL | archive-tooling.yaml: legal_scan_ref='.claude/work-queue/assets/WRK-5125/legal-scan.md' not found on disk |
