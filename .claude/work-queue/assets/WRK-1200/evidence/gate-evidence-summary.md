# Gate Evidence Summary (WRK-1200, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stages must be a list |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: skills.core_used must include at least 3 core skills |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | FAIL | none |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests must be a list |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work.yaml: empty recommendations and no_follow_ups_rationale missing |
| Resource-intelligence update gate | FAIL | resource-intelligence-update.yaml missing |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | PASS | user-review-browser-open.yaml absent — skip elapsed check |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | FAIL | user-review-capture.yaml.reviewed_at: date-only value '2026-03-14' — time component required |
| Codex keyword in review gate | PASS | no review files found — skip codex keyword check (handled by cross-review gate) |
| Publish commit uniqueness gate | PASS | user-review-publish.yaml absent — skip commit uniqueness check |
| Stage evidence paths gate | PASS | stages not a list — skip |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | user-review-publish.yaml absent — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
