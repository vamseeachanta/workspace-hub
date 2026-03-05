---
name: workflow-gatepass
description: >
  Enforce WRK lifecycle gatepass from session start through close/archive with
  machine-checkable evidence requirements and explicit no-bypass rules.
version: 1.0.4
updated: 2026-03-05
category: workspace-hub
triggers:
  - workflow gatepass
  - wrk gate enforcement
  - lifecycle gate
  - close gate evidence
related_skills:
  - workspace-hub/session-start
  - coordination/workspace/work-queue
  - workspace-hub/session-end
  - workspace-hub/wrk-lifecycle-testpack
capabilities:
  - lifecycle-gate-enforcement
  - evidence-contract
  - close-readiness-audit
requires:
  - .claude/work-queue/process.md
  - scripts/work-queue/verify-gate-evidence.py
  - scripts/work-queue/parse-session-logs.sh
  - scripts/review/orchestrator-variation-check.sh
invoke: workflow-gatepass
---
# Workflow Gatepass

Use this skill whenever a WRK item is being progressed through execution and close.
It makes the lifecycle sequence explicit and blocks bypass behavior.

## Required Lifecycle Chain

1. Capture.
2. Resource Intelligence.
3. Triage.
4. Plan Draft.
5. User Review - Plan (Draft) as an agent-user interactive plan-mode session:
   ask tough clarifying questions, challenge weak assumptions, think hard, and
   research hard; then open completed HTML in default browser and push review docs to `origin`.
6. Cross-Review.
7. User Review - Plan (Final) with completed HTML opened in default browser and review docs pushed to `origin`.
8. Claim / Activation.
9. Work-Queue Routing Skill (`/work` path).
10. Work Execution.
11. Artifact Generation.
12. TDD / Eval.
13. Agent Cross-Review (implementation evidence review).
14. Verify Gate Evidence.
15. Future Work Synthesis.
16. Resource Intelligence Update.
17. User Review - Implementation (close package) with completed HTML opened in default browser and review docs pushed to `origin`.
18. Reclaim (conditional when continuity breaks).
19. Close.
20. Archive.

## Stage 15 to Stage 17 Rule (Next-Work Disposition)

Before Stage 17 (User Review - Implementation), any "next work" discovered from the
current WRK must be captured using one of these paths:

1. Update an existing WRK item with revised scope and set status to `pending`
   (or another appropriate non-closed status).
2. Spin off a new WRK item with explicit scope and links back to the source WRK.

The agent chooses the path, but the decision is mandatory evidence and must be
recorded in:
- `assets/WRK-<id>/evidence/future-work.yaml`
- stage ledger order 15 evidence reference (`stage-evidence.yaml`)

Use `specs/templates/future-work-template.yaml` for the canonical YAML artifact.
Optional human-readable mirror: `specs/templates/future-work-recommendations-template.md`.

When documenting next work in markdown artifacts, use a table with an explicit
`Captured` column:
- `yes`/`✓` when captured as `existing-updated` or `spun-off-new`
- `no`/`✗` when identified but not yet captured (must be cleared before Stage 17)

## Route Consistency (A/B/C)

- All routes use the same canonical 20-stage lifecycle.
- Common mandatory gates for A/B/C: 1-9, 13-17, 19-20.
- Route A: lighter execution depth in stages 10-12 with one cross-review pass.
- Route B: standard execution depth in stages 10-12 with multi-provider cross-review.
- Route C: deeper execution/testing in stages 10-12 with stricter cross-review finding closure.

## No-Bypass Rules

- No implementation before WRK item + plan + explicit WRK approval.
- No user-review acceptance unless the completed HTML was opened in the default browser.
- No stage-5 completion unless the interactive question-and-decision loop is
  captured in the plan evidence (including explicit tough-question outcomes).
- No user-review acceptance unless relevant review artifacts are pushed to `origin`
  for distributed review (repo-local + remote visibility).
- No close without a per-WRK stage ledger in assets (`stage_evidence_ref`) covering stages 1-20.
- No close without gate evidence and `integrated_repo_tests` count in `[3,5]`.
- No archive when queue validation fails or merge/sync evidence is missing.

## Close Gate Minimum

Before close, require all of:

- `plan gate` passed
- `TDD gate` passed
- `integrated test gate` passed (3-5 pass records)
- `legal gate` passed
- `cross-review gate` passed
- `user-review html-open gate` passed for each user-review checkpoint
- `user-review publish gate` passed for each user-review checkpoint
- `resource-intelligence gate` passed
- `reclaim gate` evaluated (pass or n/a with reason)
- `future-work gate` passed
- `archive-readiness gate` passed or deferred with follow-up WRK
- `stage evidence gate` passed (`stage_evidence_ref` file exists and includes stages 1-20)

## Evidence Locations

All stage evidence is stored under:

`assets/WRK-<id>/evidence/`

Recommended files:
- `resource-intelligence.yaml`
- `resource-intelligence-update.yaml`
- `claim.yaml`
- `execute.yaml`
- `reclaim.yaml`
- `future-work.yaml`
- `user-review-browser-open.yaml`
- `user-review-publish.yaml`
- `stage-evidence.yaml`
- `close.yaml`
- `archive.yaml`

## Reusable Scripts

| Script | Purpose |
|--------|---------|
| `scripts/work-queue/verify-gate-evidence.py WRK-NNN` | Check all gates pass before close |
| `scripts/work-queue/parse-session-logs.sh WRK-NNN ...` | Read Claude/Codex/Gemini logs; emit session-log-review.md |
| `scripts/review/orchestrator-variation-check.sh --wrk WRK-NNN --orchestrator <provider> --scripts "..."` | Run scripts and emit variation-test-results.md |
| `scripts/work-queue/claim-item.sh WRK-NNN` | Atomic claim + stage-8 auto-progress |
| `scripts/work-queue/close-item.sh WRK-NNN` | Atomic close + stage-19 auto-progress + auto final HTML generation |
| `scripts/work-queue/archive-item.sh WRK-NNN` | Atomic archive + stage-20 auto-progress |

`parse-session-logs.sh` handles JSONL (Claude) and plain-text (Codex/Gemini) formats;
also checks native stores (`~/.codex/sessions/`, `~/.gemini/tmp/`).

`orchestrator-variation-check.sh` is provider-agnostic — set `--orchestrator` to
`claude`, `codex`, or `gemini`; the runner field in `variation-test-results.md`
reflects this value for cross-provider comparisons.

## Operational Lessons (WRK-690)

- Gatepass compliance requires **explicit signal emission**, not only artifact
  presence. Shared scripts must log lifecycle signals as they execute.
- Inferred signals are **not** measured signals. Only explicit, machine-logged
  stage signals count toward coverage and gatepass metrics.
- User-review stages must emit both stage signal and browser-open signal; do not
  collapse these into one event.
- Keep close/archive signals distinct (`close_item`, `archive_item`) and also
  emit terminal aggregation (`close_or_archive`) for weekly reporting.
- Validate signal logging with both unit tests and shell smoke tests before
  trusting weekly analytics.
- In multi-agent parallel repos, out-of-scope side effects from other agents are
  non-blocking for the active WRK. Do not revert them unless directed; document
  them in the active WRK under `Out-of-Scope Side Effects`.
