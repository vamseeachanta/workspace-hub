# Gate Evidence Summary (WRK-1018, phase=close)

| Gate | Status | Details |
|---|---|---|
| Plan gate | PASS | reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed |
| Workstation contract gate | PASS | plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1] |
| Stage evidence gate | PASS | stage-evidence.yaml: stages=20, contract=20-stage |
| Resource-intelligence gate | FAIL | resource-intelligence evidence absent (legacy item — WARN) |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | pre-cutoff backfill (id=1018, created_at=2026-03-05T00:00:00Z) — log gate skipped |
| User-review HTML-open gate | PASS | user-review-browser-open.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| User-review publish gate | PASS | user-review-publish.yaml: stages=['close_review', 'plan_draft', 'plan_final'] |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1018/review.md |
| TDD gate | PASS | test files=['test-results.md'] |
| Integrated test gate | PASS | execute.yaml: integrated_repo_tests=3 (all passing) |
| Legal gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1018/legal-scan.md, result=PASS |
| Claim gate | WARN | claim evidence absent (legacy item — WARN) |
| Future-work gate | PASS | future-work.yaml: no_follow_ups_rationale=present |
| Resource-intelligence update gate | PASS | resource-intelligence-update.yaml: no_additions_rationale=present |
| User-review close gate | PASS | user-review-close.yaml: decision=approved |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=close) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Browser open elapsed time gate | FAIL | stage=close_review: approval confirmed only 0s after browser open (min 300s required) |
| Sentinel values gate | PASS | no sentinel values found |
| Claim artifact path gate | PASS | canonical claim artifact found: claim-evidence.yaml |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Codex keyword in review gate | PASS | no review files found — skip codex keyword check (handled by cross-review gate) |
| Publish commit uniqueness gate | FAIL | all three publish stages share commit '71c367c0' (likely placeholder) |
| Stage evidence paths gate | PASS | all stage evidence paths verified |
| Done/pending contradiction gate | PASS | no done/pending contradictions found |
| Plan publish predates approval gate | FAIL | plan_draft published_at (2026-03-10T23:30:00Z) < reviewed_at (2026-03-10T23:35:00Z): publish predates approval |
| Workstation contract (strict) gate | PASS | workstation contract fields present |
| Reclaim n/a gate | WARN | n/a: Stage 18 is n/a and no reclaim log exists |
