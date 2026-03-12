# Gate Evidence Summary (WRK-1153, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage_evidence_ref missing in WRK frontmatter |
| Resource-intelligence gate | FAIL | resource-intelligence.yaml: invalid completion_status |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | FAIL | routing:missing-provider ; plan:missing-provider ; execute:missing-provider ; cross-review:missing-provider |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml: missing required stages ['plan_final'] |
| User-review publish gate | FAIL | user-review-publish.yaml: missing required stages ['plan_final'] |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | FAIL | none |
| Integrated test gate | FAIL | execute.yaml: integrated_repo_tests count must be 3-5 (found 0) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | FAIL | future-work.yaml: recommendations[1] disposition must be existing-updated\|spun-off-new |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=3 |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=close_review: approval confirmed only 0s after browser open (min 300s required) |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | codex keyword found in review artifacts (1 file(s) checked) |
| Publish commit uniqueness gate | PASS | publish commits appear unique across stages |
| Stage evidence paths gate | PASS | all stage evidence paths verified |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | plan publish ordering OK (published=2026-03-12T20:42:00Z, reviewed=2026-03-12T20:27:00Z) |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
