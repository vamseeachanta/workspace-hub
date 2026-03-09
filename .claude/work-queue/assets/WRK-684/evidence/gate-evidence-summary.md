# Gate Evidence Summary (WRK-684, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=plan-review-final.html, confirmation=confirmation block incomplete — confirmed_by, confirmed_at, decision=missing (need 'passed') |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=19, contract=19-stage |
| Resource-intelligence gate | FAIL | resource-intelligence-summary.md: user_decision missing (legacy summary — WARN) |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | FAIL | routing:missing-log ; plan:missing-log ; execute:missing-log ; cross-review:missing-log |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-684/review.html |
| TDD gate | PASS | test files=['variation-test-results.md'] |
| Integrated test gate | FAIL | execute evidence missing (required: evidence/execute.yaml) |
| Legal gate | FAIL | artifact=missing, none |
| Claim gate | WARN | claim-evidence.yaml: metadata_version='' (legacy schema — WARN only) |
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
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[2] evidence path not found: .claude/work-queue/assets/WRK-684/evidence/resource-intelligence.yaml |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | user-review-publish.yaml absent — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
