# Ecosystem Sync — Deploy Readiness Checklist for ace-linux-1 Main Checkout

Date: 2026-04-20
Target topology: `/mnt/local-analysis/workspace-hub` on `ace-linux-1`, main checkout
Purpose: validate production topology before Stage 2 Tasks 15–17

## 1. Checkout and git topology
- [ ] Run from the main checkout, not `.claude/worktrees/ecosystem-sync`.
- [ ] `git status --short --branch` is clean or intentionally understood.
- [ ] `git branch --show-current` reports `main`.
- [ ] `git fetch origin --prune` succeeds.
- [ ] `git pull --ff-only origin main` succeeds from `/mnt/local-analysis/workspace-hub`.
- [ ] Commit `07e7e7d07` is present on the validating checkout before relying on plan-gated commit flows.

## 2. Code + artifact presence
- [ ] `scripts/ecosystem-sync/run.py` exists.
- [ ] `scripts/ecosystem-sync/signals.py` exists.
- [ ] `scripts/ecosystem-sync/digest.py` exists.
- [ ] `scripts/ecosystem-sync/issues.py` exists.
- [ ] `.claude/cron/ecosystem-sync.sh` exists in the main checkout.
- [ ] `.claude/state/ecosystem-sync/last-sync.yaml` exists or there is an explicit Task 14 plan to generate it before dry-run interpretation.
- [ ] `docs/sync-reports/` exists and is writable from the main checkout user context.

## 3. Source-repo prerequisites (Tasks 12–14)
- [ ] All 6 configured repos exist at the paths referenced by `scripts/ecosystem-sync/config.yaml`:
  - `digitalmodel`
  - `assethold`
  - `assetutilities`
  - `CAD-DEVELOPMENTS`
  - `doris`
  - `frontierdeepwater`
- [ ] README-heading audit has been run or intentionally deferred with evidence.
- [ ] Repos missing all target headings have a remediation plan before relying on Signal 3.
- [ ] `showcase` and `website` labels exist on the 6 upstream repos before expecting Signal 5 to be meaningful.
- [ ] Initial state backfill is completed before judging dry-run noise level.

## 4. Local runtime health
- [ ] `uv run python -m scripts.ecosystem_sync.run --doctor` returns exit code 0 from the main checkout.
- [ ] `bash .claude/cron/ecosystem-sync.sh --doctor` returns exit code 0 from the main checkout.
- [ ] `gh auth status` is healthy for the runtime user.
- [ ] The runtime user has write access to:
  - `docs/sync-reports/`
  - `logs/ecosystem-sync/`
  - `.claude/state/ecosystem-sync/`
- [ ] `flock` is available on the host.
- [ ] All configured source-repo paths are valid git repositories.

## 5. Dry-run validation
- [ ] Run `bash .claude/cron/ecosystem-sync.sh --dry-run` from the main checkout.
- [ ] Confirm the wrapper reaches `run.py` rather than failing early at `git pull --ff-only origin main`.
- [ ] Confirm a same-day log entry appears under `logs/ecosystem-sync/`.
- [ ] Confirm digest/log output is interpretable and not dominated by obvious false positives.
- [ ] If dry-run occurs after backfill, expected outcome is either no signals or only real same-day upstream events.
- [ ] If dry-run still floods due to known preexisting state, stop and finish Task 14 rather than enabling the timer.

## 6. Follow-up review findings awareness
These are not automatic Stage 2 blockers, but the operator should know they remain open unless separately fixed:
- [ ] tests currently rely on manually built local git fixtures unless hardened later
- [ ] `_extract_section()` is not yet fence-aware unless later patched
- [ ] release freshness currently uses commit date semantics unless later patched

## 7. Enablement gate for Task 17
Only enable the systemd timer if all of the following are true:
- [ ] main-checkout `git pull --ff-only origin main` works in the real runner topology
- [ ] doctor passes both directly and through the bash wrapper
- [ ] backfill state is present and sane
- [ ] label and README prerequisites are addressed
- [ ] at least one dry-run from the main checkout produced credible output
- [ ] no new verified blocker was discovered during validation

## 8. If validation fails
- Stop before Task 17.
- Record the exact failing command, exit code, and log evidence.
- Classify the failure as one of:
  - topology/configuration issue
  - missing prerequisite data/labels/readme prep
  - code defect requiring a scoped bugfix
  - auth/environment issue
- Open or update a concrete follow-up artifact before retrying.
