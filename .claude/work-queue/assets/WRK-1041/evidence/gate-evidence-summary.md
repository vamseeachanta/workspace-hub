# Gate Evidence Summary (WRK-1041, phase=claim)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=ace-linux-1, execution_workstations=ace-linux-1 |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: skills.core_used must include at least 3 core skills |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | pre-cutoff backfill (id=1041, created_at=2026-03-08T14:45:00Z) — log gate skipped |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_draft', 'plan_final'] |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=unknown, quota=available(null) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=claim) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | browser open elapsed time OK |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Stage1 capture gate | FAIL | user-review-capture.yaml: confirmed_at missing |
