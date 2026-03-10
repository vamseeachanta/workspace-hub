# Gate Evidence Summary (WRK-693, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=False, approved=False, artifact=missing, confirmation=plan artifact missing |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | FAIL | stage-evidence.yaml: stage order 17 must be done\|n/a before close (found pending) |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | FAIL | activation.yaml missing |
| Agent log gate | PASS | pre-cutoff backfill (id=693, created_at=2026-03-03T00:00:00Z) — log gate skipped |
| User-review HTML-open gate | FAIL | user-review-browser-open.yaml missing |
| User-review publish gate | FAIL | user-review-publish.yaml missing |
| Cross-review gate | FAIL | artifact=none |
| TDD gate | FAIL | none |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=3 (all passing) |
| Legal gate | FAIL | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-693/legal-scan.md, result=missing |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | PASS | future-work.yaml: recommendations=2 |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: additions=1 |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | FAIL | timestamp ordering violation: claim-evidence.claimed_at (2026-03-10T00:00:00Z) >= execute.executed_at (2026-03-10T00:00:00Z) |
| Midnight UTC sentinel gate | FAIL | midnight UTC sentinel detected in user-review-close.yaml.reviewed_at: 2026-03-10T00:00:00Z |
| Browser open elapsed time gate | PASS | user-review-browser-open.yaml absent — skip elapsed check |
| Sentinel values gate | FAIL | claim-evidence.yaml: route='' (empty) |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | no review files found — skip codex keyword check (handled by cross-review gate) |
| Publish commit uniqueness gate | PASS | user-review-publish.yaml absent — skip commit uniqueness check |
| Stage evidence paths gate | FAIL | stage-evidence.yaml: stage[5] evidence path not found: .claude/work-queue/assets/WRK-693/evidence/user-review-common-draft.yaml |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | PASS | user-review-publish.yaml absent — skip |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
