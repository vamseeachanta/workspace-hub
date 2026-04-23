# Ecosystem Sync — Push Approval Checklist

Date: 2026-04-20
Landing source:
- worktree: `/mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration`
- branch: `integration/ecosystem-sync-stage1-stage2-handoff`

Purpose:
- final human approval gate before any push/landing side effects
- confirm we are landing from the clean integration worktree, not from dirty `main`

## 1. Source-of-truth check
- [ ] Push will be performed from `/mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration`
- [ ] Push will NOT be performed from `/mnt/local-analysis/workspace-hub`
- [ ] Integration worktree is clean: `git status --short --branch`
- [ ] Feature worktree docs state matches expectations; no required artifact is missing

## 2. Commit-set check
Approved landing set should include these validated commits above base:

### Wave A — governance reliability
- [ ] `d82230a10` `fix(enforcement): avoid plan-gate false negative with many markers`

### Wave B — Stage 1 ecosystem-sync implementation
- [ ] `7e299341a` scaffold package with Signal dataclass
- [ ] `a19826430` config loader + production config
- [ ] `9db8b7e59` state load/save with change detection
- [ ] `c36d44a67` release tag detector + fixtures
- [ ] `7e73f4b8f` case-study detector
- [ ] `f03e1d8d9` README diff detector
- [ ] `5ccf7be24` labeled closed-issue detector
- [ ] `6d70dcbb9` digest renderer + golden tests
- [ ] `23cdc394d` issue opener with dedupe + retry-once
- [ ] `27a2d3a13` orchestrator with `--dry-run` and `--doctor`
- [ ] `c3df50876` cron wrapper with flock + one-shot rebase
- [ ] `83abb519e` invoke orchestrator as module

### Wave C — docs / handoff bundle
- [ ] `2d0e2b0e3` review handback
- [ ] `c3b24b336` next-wave handoff bundle
- [ ] `699619413` issue creation packets
- [ ] `eb93a4a9d` gh issue create commands
- [ ] `1bd66834b` enforcement promotion procedure
- [ ] `5bf99d9c1` operator command bundle
- [ ] `a62cc6f17` issue label taxonomy alignment

### Explicit exclusion
- [ ] `c55d8f4af` planning-marker commit is NOT included

## 3. Validation evidence check
- [ ] `bash tests/hooks/test-require-plan-approval.sh` passed in integration worktree
- [ ] `bash tests/ecosystem-sync/fixtures/repos/build_fixtures.sh` completed successfully enough to support tests
- [ ] `uv run pytest tests/ecosystem-sync -q` passed with `35 passed`
- [ ] `uv run python -m scripts.ecosystem_sync.run --doctor` passed
- [ ] Invocation-path fix `83abb519e` is included in the landing set

## 4. Known caveat acknowledgment
- [ ] We understand wrapper `--doctor` / `--dry-run` has NOT been fully validated from the integration worktree because `.claude/cron/ecosystem-sync.sh` intentionally runs `git pull --ff-only origin main`
- [ ] We will perform wrapper validation only after landing onto the real main checkout topology

## 5. Post-push required follow-through
After push/landing, perform on real main checkout:
- [ ] `git pull --ff-only origin main`
- [ ] `bash .claude/cron/ecosystem-sync.sh --doctor`
- [ ] `bash .claude/cron/ecosystem-sync.sh --dry-run`
- [ ] inspect `logs/ecosystem-sync/<today>.log`
- [ ] confirm no new verified blocker before any Stage 2 enablement work

## 6. Approval statement
Use this as the human go/no-go line:

- [ ] I approve push/landing from `integration/ecosystem-sync-stage1-stage2-handoff` with the validated commit set above, understanding that final wrapper validation must still occur on real `main` after landing.
