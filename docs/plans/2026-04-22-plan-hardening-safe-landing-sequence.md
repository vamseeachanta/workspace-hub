# Safe landing sequence for plan-hardening edits (#2443, #2444, #2289)

Repo
- `/mnt/local-analysis/workspace-hub`
- current branch at preparation time: `main`
- base commit at preparation time: `53d64cff7585ec3509f8c6b4f3733028c3cf25f8`

Goal
- land ONLY the plan-hardening artifacts for:
  - `#2443`
  - `#2444`
  - `#2289`
- avoid mixing in unrelated dirty files already present in the main checkout

Target file set
- `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md`
- `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
- `docs/plans/README.md`
- `docs/plans/2026-04-22-overnight-3-terminal-plan-resubmit-prompts.md`
- `docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-1-issue-2443.md`
- `docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-2-issue-2444.md`
- `docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-3-issue-2289.md`

Recommended path: fresh integration worktree

## 1. Preflight from dirty main checkout
```bash
cd /mnt/local-analysis/workspace-hub

TARGETS=(
  docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md
  docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md
  docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md
  docs/plans/README.md
  docs/plans/2026-04-22-overnight-3-terminal-plan-resubmit-prompts.md
  docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-1-issue-2443.md
  docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-2-issue-2444.md
  docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-3-issue-2289.md
)

printf 'Base branch: '; git rev-parse --abbrev-ref HEAD
printf 'Base sha: '; git rev-parse HEAD
printf '\nDirty state (full repo):\n'; git status --short
printf '\nTarget-file state only:\n'; git status --short -- "${TARGETS[@]}"
printf '\nTarget-file diff stat:\n'; git diff --stat -- "${TARGETS[@]}"
```

Decision rule:
- if target-file state is non-empty: continue with worktree-copy flow below
- if target-file state is empty: stop and verify whether the edits already landed elsewhere before doing any commit work

## 2. Create fresh worktree from clean base
```bash
cd /mnt/local-analysis/workspace-hub
BASE=$(git rev-parse HEAD)
WT=/mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289
BR=integration/plan-hardening-2443-2444-2289

mkdir -p /mnt/local-analysis/worktrees
git worktree add -b "$BR" "$WT" "$BASE"
```

## 3. Copy ONLY target files from dirty main into the clean worktree
Run this from the dirty main checkout:
```bash
cd /mnt/local-analysis/workspace-hub
WT=/mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289

for f in "${TARGETS[@]}"; do
  mkdir -p "$WT/$(dirname "$f")"
  cp "$f" "$WT/$f"
done
```

## 4. Validate inside the clean worktree
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289

git status --short -- "${TARGETS[@]}"
git diff --stat -- "${TARGETS[@]}"

grep -n "2443 |" docs/plans/README.md
grep -n "2444 |" docs/plans/README.md
grep -n "2289 |" docs/plans/README.md

grep -n "python3" docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md || true
grep -n "disable the violating rule\|disable.*floor rule\|OR disable" docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md || true

grep -n "no TDD\|not in the strict sense\|no unit-test TDD" docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md || true
grep -n "uv.lock" docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md | sed -n '1,20p'

grep -n "## Pseudocode\|## TDD Test List\|## Adversarial Review Summary" docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md
grep -n "auth_failed\|ls-remote\|selected push remote\|advisor-only rollback/recovery mechanism" docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md
```

Expected outcomes
- `#2443` plan has no bare `python3`
- `#2444` plan has no live TDD-waiver language in current-state sections
- `#2289` plan includes the missing required headings and tightened auth/offline handling
- README has rows for `2443`, `2444`, and `2289` reflecting draft / rerun-review-needed state

## 5. Commit only the clean landing set
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289

git add \
  docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md \
  docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md \
  docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md \
  docs/plans/README.md \
  docs/plans/2026-04-22-overnight-3-terminal-plan-resubmit-prompts.md \
  docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-1-issue-2443.md \
  docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-2-issue-2444.md \
  docs/plans/overnight-prompts/2026-04-22-ci-plan-resubmit-wave/terminal-3-issue-2289.md

git diff --cached --stat

git commit -m "docs(plans): harden 2443 2444 2289 for fresh adversarial rerun"
```

## 6. Optional push sequence
Only do this if you actually want the integration branch pushed:
```bash
cd /mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289
git push -u origin integration/plan-hardening-2443-2444-2289
```

## 7. Optional cleanup after landing/cherry-pick
```bash
cd /mnt/local-analysis/workspace-hub
git worktree remove /mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289
```

Optional fallback: path-limited stash instead of copy
Use only if you explicitly want to clear the target edits out of dirty main temporarily.

### Stash just the target files
```bash
cd /mnt/local-analysis/workspace-hub

git stash push -m "plan-hardening-2443-2444-2289" -- "${TARGETS[@]}"
```

### Create clean worktree and pop only that stash there
```bash
cd /mnt/local-analysis/workspace-hub
BASE=$(git rev-parse HEAD)
WT=/mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289
BR=integration/plan-hardening-2443-2444-2289

git worktree add -b "$BR" "$WT" "$BASE"
cd "$WT"
git stash list
# identify the stash entry, then:
git stash pop stash@{0}
```

Why copy-first is safer than stash-first here
- the main checkout already has lots of unrelated dirt
- copying specific files into a clean worktree avoids stash-index mistakes
- path-limited stash is fine, but easier to misuse if more edits appear while you work

Abort / recovery commands
```bash
# discard copied changes in the integration worktree only
cd /mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289
git restore --source=HEAD --worktree --staged -- .

# remove the worktree entirely if needed
cd /mnt/local-analysis/workspace-hub
git worktree remove /mnt/local-analysis/worktrees/workspace-hub-plan-hardening-2443-2444-2289 --force
```

Final recommendation
- use the fresh worktree + copy-only-target-files path
- do not commit from dirty main
- do not use broad `git add .`
- verify target-file diff in the worktree before committing
