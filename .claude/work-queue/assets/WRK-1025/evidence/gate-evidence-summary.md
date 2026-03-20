# Gate Evidence Summary (WRK-1025, phase=archive)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[dev-primary], execution_workstations=[dev-primary] |
| Resource-intelligence gate | FAIL | resource-intelligence evidence absent (legacy item — WARN) |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | PASS | pre-cutoff backfill (id=1025, created_at=2026-03-06T00:00:00Z) — log gate skipped |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=archive) |
| Midnight UTC sentinel gate | FAIL | midnight UTC sentinel detected in user-review-close.yaml.confirmed_at: 2026-03-12T00:00:00Z |
| Browser open elapsed time gate | PASS | user-review-browser-open.yaml absent — skip elapsed check |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Archive readiness gate | FAIL | archive-tooling.yaml absent: /mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1025/evidence/archive-tooling.yaml |
