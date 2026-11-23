# Ecosystem Sync — Stage 2 Authorization Memo (Tasks 12–17 Only)

Date: 2026-04-20
Branch/context: `feat/ecosystem-sync` in `/mnt/local-analysis/workspace-hub/.claude/worktrees/ecosystem-sync`
Authoring basis:
- `docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-hermes-handback.md`

## Decision
Recommend Stage 2 authorization for Tasks 12–17 only.

Stage 1 should be treated as implementation-complete through Task 11. This memo does not reopen Tasks 7–11 and does not authorize feature-code churn on already-completed Stage 1 work unless a new verified blocker is found.

## What Stage 2 covers
Authorized scope from the approved plan:
- Task 12 — audit source repos for README heading consistency
- Task 13 — create `showcase` / `website` labels on the 6 source repos
- Task 14 — backfill initial ecosystem-sync state file
- Task 15 — run `--doctor` against the real target topology
- Task 16 — execute the dry-run burn-in sequence
- Task 17 — enable the systemd timer/service on `ace-linux-1`

## Preconditions before execution
1. Validate from the intended runtime topology, not from this feature worktree.
   - The worktree smoke test already proved wrapper/logging mechanics only.
   - The feature-worktree failure at `git pull --ff-only origin main` is expected and is not the deployment topology.
2. Use the main checkout on `ace-linux-1` for Stage 2 validation and rollout.
3. Keep Stage 2 changes scoped to:
   - preparatory scripts/utilities
   - state/bootstrap artifacts
   - deployment/ops validation evidence
   - coordination docs
4. Do not bypass hooks.
5. Do not push from this handback session.

## Why Stage 2 is reasonable now
- Stage 1 finished through Task 11 and already includes:
  - signal 5 detector
  - digest renderer + golden tests
  - issue opener with dedupe + retry-once
  - orchestrator with `--dry-run` and `--doctor`
  - cron wrapper with flock + one-shot rebase
- The only verified code blocker discovered during Stage 1 was the plan-gate false negative, and that was fixed in `07e7e7d07` without bypass.
- The remaining MAJOR findings from review are follow-up hardening issues, not blockers to Stage 2 validation itself:
  - fixture autobuild/skip behavior
  - fenced-code-block README parsing
  - annotated tagger-date freshness semantics

## Stage 2 guardrails
- Treat Tasks 12–14 as environment-prep / backfill work, not an excuse to revisit finished Stage 1 code.
- Treat Task 15 as the first real deploy-topology gate.
- Treat Task 16 as mandatory burn-in, not ceremonial validation.
- Only proceed to Task 17 if:
  - `run.py --doctor` passes on the real main checkout
  - the wrapper path is validated from the same topology
  - dry-run output is judged sane
  - source-repo label/readme/state prerequisites are satisfied

## Explicit non-authorization
This memo does not authorize:
- re-implementing Tasks 7–11
- broad refactors inside `scripts/ecosystem-sync/`
- pushing any branch from this session
- hook bypasses
- production enablement directly from the feature worktree

## Approval recommendation
Approve Stage 2 for Tasks 12–17 only, with execution anchored to `ace-linux-1` main checkout and with the deploy-readiness checklist used as the operator gate before Task 17.
