# Ecosystem Sync — Clean Integration Command Bundle

Date: 2026-04-20
Purpose: land the validated ecosystem-sync work from `feat/ecosystem-sync` without touching the dirty main checkout directly.
Integration base captured from `/mnt/local-analysis/workspace-hub` at generation time:
- main HEAD: `e34093282c673cb163395d452a8e796a01d0959b`
- integration worktree path: `/mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration`
- integration branch name: `integration/ecosystem-sync-stage1-stage2-handoff`

## Guardrails
- No hook bypass
- No push as part of this command bundle
- Do not use the dirty main checkout for landing
- Exclude planning-marker commit `c55d8f4af`

## Wave A — enforcement fix only
```bash
cd /mnt/local-analysis/workspace-hub

git fetch origin --prune

git worktree add \
  -b integration/ecosystem-sync-stage1-stage2-handoff \
  /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration \
  e34093282c673cb163395d452a8e796a01d0959b

cd /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration

git status --short --branch

git cherry-pick 07e7e7d07

bash tests/hooks/test-require-plan-approval.sh

git status --short --branch
git log --oneline -3
```

## Wave B — ecosystem-sync Stage 1 implementation
Cherry-pick in dependency order:
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration

git cherry-pick \
  5a37abf87 \
  53f9e841c \
  87147eb35 \
  e2496a4d4 \
  ca2b12b55 \
  8b8b0a9a5 \
  03cafa6f6 \
  45308cee4 \
  8ab684c0e \
  ffedadc0f \
  f73b10c22
```

Targeted validation after Wave B:
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration

uv run pytest tests/ecosystem-sync -q
bash tests/hooks/test-require-plan-approval.sh

git status --short --branch
git log --oneline -15
```

## Wave C — docs / handoff bundle
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration

git cherry-pick \
  10d23b37d \
  c4dd792c5 \
  ac9fdd9c2 \
  826604216 \
  c94563182 \
  9e954d725 \
  fb0063396
```

Validation after Wave C:
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration

git status --short --branch

uv run pytest tests/ecosystem-sync -q
bash tests/hooks/test-require-plan-approval.sh
```

## Post-integration Stage 2 readiness checks
Only after Waves A/B/C are green:
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration

for p in \
  scripts/ecosystem-sync/run.py \
  scripts/ecosystem-sync/signals.py \
  scripts/ecosystem-sync/digest.py \
  scripts/ecosystem-sync/issues.py \
  .claude/cron/ecosystem-sync.sh \
  .claude/state/ecosystem-sync/last-sync.yaml \
  docs/sync-reports
  do
    if [ -e "$p" ]; then echo PRESENT "$p"; else echo MISSING "$p"; fi
  done

uv run scripts/ecosystem-sync/run.py --doctor || true
bash .claude/cron/ecosystem-sync.sh --doctor || true
bash .claude/cron/ecosystem-sync.sh --dry-run || true
```

## Conflict handling
If any cherry-pick conflicts:
```bash
git status
# resolve only the intended files
git add <resolved-files>
git cherry-pick --continue
```

If the landing attempt should be abandoned:
```bash
git cherry-pick --abort
```

If the entire integration worktree should be discarded:
```bash
cd /mnt/local-analysis/workspace-hub
git worktree remove /mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration
```

## Expected outcome
After Waves A/B/C, the clean integration worktree should contain:
- enforcement reliability fix `07e7e7d07`
- full Stage 1 ecosystem-sync implementation
- Stage 2/operator handoff docs
- no planning-marker commit

At that point the next operator decision is whether to:
1. keep validating in the integration worktree, or
2. push/merge later with explicit approval for side effects.
