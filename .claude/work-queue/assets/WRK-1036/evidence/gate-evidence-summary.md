# Gate Evidence Summary (WRK-1036, phase=claim)

| Gate | Status | Details |
|---|---|---|
| Plan gate | FAIL | reviewed=True, approved=True, artifact=plan.md, confirmation=confirmation block incomplete — confirmed_by, confirmed_at, decision=missing (need 'passed') |
| Workstation contract gate | PASS | plan_workstations=[dev-primary], execution_workstations=[dev-primary] |
| Resource-intelligence gate | PASS | resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3 |
| Activation gate | PASS | activation.yaml: activation evidence OK |
| Agent log gate | PASS | pre-cutoff backfill (id=1036, created_at=2026-03-08T00:00:00Z) — log gate skipped (optional — no multi-agent indicators) |
| GitHub issue gate | FAIL | github_issue_ref missing from frontmatter |
| Cross-review gate | PASS | artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1036/review.md |
| Claim gate | PASS | claim-evidence.yaml: version=1, owner=claude, quota=available(null) |
| Reclaim gate | WARN | reclaim.yaml absent (no reclaim triggered — WARN) |
| Approval ordering gate | PASS | approval ordering OK (phase=claim) |
| Midnight UTC sentinel gate | PASS | no midnight UTC sentinel found |
| Sentinel values gate | FAIL | activation.yaml: session_id='unknown' |
| Claim artifact path gate | FAIL | no claim artifact found (expected evidence/claim-evidence.yaml) |
| ISO datetime format gate | PASS | all timestamp fields have time components |
| Stage1 capture gate | FAIL | user-review-capture.yaml missing |
