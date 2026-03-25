# Gate Evidence Summary (workspace-hub-1355, phase=archive)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | FAIL | plan_workstations=missing, execution_workstations=missing |
| Resource-intelligence gate | FAIL | resource-intelligence evidence absent (legacy item — WARN) |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | WARN | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log (optional — no multi-agent indicators) |
| GitHub issue gate | FAIL | github_issue_ref missing from frontmatter |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=archive) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Archive readiness gate | FAIL | archive-tooling.yaml absent: /mnt/local-analysis/workspace-hub/.claude/work-queue/assets/workspace-hub-1355/evidence/archive-tooling.yaml |
