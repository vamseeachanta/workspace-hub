# Ecosystem Sync — Operator Runbook for Next Wave

Date: 2026-04-20
Context: follow-on execution after Stage 1 completion through Task 11
Target runtime: `/mnt/local-analysis/workspace-hub` on `ace-linux-1` main checkout

## Goal
Turn the handoff artifacts into a low-risk execution sequence for the next operator wave.

## Recommended order of operations

### 1. Preserve the handoff artifacts
Commit the coordination docs from this worktree before any production-topology work:
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-follow-up-issues.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-stage2-authorization.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-deploy-readiness-checklist.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-enforcement-fix-note.md`
- `docs/plans/2026-04-20-aceengineer-ecosystem-sync-operator-runbook.md`

Why:
- preserves the review-derived next wave
- avoids touching completed Stage 1 feature code
- gives the ace-linux-1 operator a single bundle of guidance

### 2. Promote the enforcement fix first
Recommended first code promotion outside this worktree handoff:
- commit `07e7e7d07`
- summary: `fix(enforcement): avoid plan-gate false negative with many markers`

Why first:
- it fixed a verified blocker, not a hypothetical cleanup item
- it protects all later plan-gated work, not just ecosystem-sync
- it already has targeted validation in `tests/hooks/test-require-plan-approval.sh`

Promotion guidance:
- keep this promotion narrow
- do not bundle unrelated ecosystem-sync feature commits if the objective is fast governance risk reduction

### 3. Use Stage 2 authorization as a hard scope boundary
Authorized work only:
- Task 12 — README heading audit
- Task 13 — label creation/verification
- Task 14 — state backfill
- Task 15 — doctor validation on real topology
- Task 16 — dry-run burn-in
- Task 17 — timer/service enablement

Not authorized by this wave:
- redoing Tasks 7–11
- broad feature refactors under `scripts/ecosystem-sync/`
- production activation from the feature worktree

### 4. Execute Stage 2 on ace-linux-1 main checkout only
Do not treat the feature-worktree smoke result as deploy validation.

Required working directory:
- `/mnt/local-analysis/workspace-hub`

Required git topology:
- branch `main`
- `git pull --ff-only origin main` must succeed before wrapper-based validation is trusted

### 5. Run Stage 2 in the safest sequence

#### Task 12 — README heading audit
Check all 6 configured repos for at least one expected section heading:
- `Capabilities`
- `Features`
- `What it does`

Decision rule:
- if a repo lacks all supported headings, record it and do not over-trust Signal 3 for that repo until remediated

#### Task 13 — label verification/creation
Ensure upstream repos have both labels:
- `showcase`
- `website`

Decision rule:
- if labels are absent, create them before expecting Signal 5 to produce useful output

#### Task 14 — initial state backfill
Backfill `.claude/state/ecosystem-sync/last-sync.yaml` with current tags, README hashes, case-study inventory, and closed labeled issues.

Decision rule:
- do not interpret dry-run volume until this backfill exists; otherwise first-run noise is expected

#### Task 15 — doctor validation
Run both:
- `uv run python -m scripts.ecosystem_sync.run --doctor`
- `bash .claude/cron/ecosystem-sync.sh --doctor`

Decision rule:
- both must pass from the main checkout before any enablement discussion

#### Task 16 — dry-run burn-in
Run:
- `bash .claude/cron/ecosystem-sync.sh --dry-run`

Decision rule:
- wrapper must reach `run.py`
- logs must be created
- output must be credible for a post-backfill run

#### Task 17 — enable timer/service
Enable only after the deploy-readiness checklist is fully green.

### 6. Keep the deploy-readiness checklist as the operational gate
The most important go/no-go conditions are:
- main checkout is valid and up to date
- `07e7e7d07` is present before depending on plan-gated commit flows
- all 6 repo paths in config exist and are git repos
- `gh auth status` is healthy
- digest/log/state paths are writable by the runtime user
- dry-run from main checkout is sane after backfill

### 7. Open the 3 hardening issues after documentation is preserved
Recommended order:
1. fixture autobuild / graceful skip
2. fenced-code-aware README extraction
3. annotated tagger-date release freshness

Rationale:
- first improves test reliability and onboarding for future operators
- second reduces false positives in README-diff detection
- third corrects release-age semantics for annotated tags

### 8. Stop conditions
Stop and record evidence if any of the following occur:
- `git pull --ff-only origin main` fails on ace-linux-1 main checkout
- `run.py --doctor` fails
- wrapper `--doctor` fails
- source-repo labels/README prerequisites are missing in a way that invalidates interpretation
- dry-run flood shows Task 14 backfill is incomplete or wrong
- a new code defect is verified with reproducible evidence

Required evidence when stopping:
- exact command
- exit code
- relevant log tail
- classification: topology/config, prerequisite gap, auth/env, or code defect

## Short recommendation summary
1. Commit the docs handoff bundle.
2. Promote `07e7e7d07` as a repo-wide enforcement fix.
3. Execute Tasks 12–17 only, on ace-linux-1 main checkout.
4. Use doctor + dry-run + checklist as the gate before timer enablement.
5. File the 3 review-derived hardening issues after the docs are preserved.
