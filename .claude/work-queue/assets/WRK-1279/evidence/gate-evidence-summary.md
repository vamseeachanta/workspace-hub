# Gate Evidence Summary (WRK-1279, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=dev-primary, execution_workstations=dev-primary |
| Stage evidence gate | FAIL | stage_evidence_ref missing in WRK frontmatter |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: skills.core_used must include at least 3 core skills |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | FAIL | none |
| Integrated test gate | FAIL | execute evidence missing (required: evidence/execute.yaml) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work evidence absent (legacy item — WARN) |
| Resource-intelligence update gate | FAIL | resource-intelligence-update.yaml missing |
| User-review close gate | FAIL | user-review-close.yaml missing |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | user-review-browser-open.yaml absent — skip elapsed check |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | no review files found — skip codex keyword check (handled by cross-review gate) |
| Publish commit uniqueness gate | PASS | user-review-publish.yaml absent — skip commit uniqueness check |
| Stage evidence paths gate | PASS | stage-evidence.yaml absent — skip path existence check |
| Done/pending contradiction gate | PASS | stage-evidence.yaml absent — skip done/pending check |
| Plan publish predates approval gate | PASS | user-review-publish.yaml absent — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
