# Archived Skill: `memory-bridge-commit-fallbacks`

Original path: `/home/vamsee/.hermes/skills/coordination/memory-bridge-commit-fallbacks`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/memory-bridge-commit-fallbacks`
Consolidation date: 2026-04-29

---

---
name: memory-bridge-commit-fallbacks
description: Fallback procedures when the Hermes ↔ Claude memory bridge writes .claude/memory outputs but the internal git commit/push path fails because of dirty, stale, or broken submodule state.
---

# Memory Bridge Commit Fallbacks

## When to use

Use when running `scripts/memory/pre-bridge-quality.sh --fix` or `scripts/memory/bridge-hermes-claude.sh --commit` in workspace-hub and the bridge successfully updates `.claude/memory/` files, but its internal commit/push phase fails due to unrelated dirty repo state, stale/broken submodule status, or errors such as:

- `fatal: 'git status --porcelain=2' failed in submodule ...`
- `error: status died of signal 15`
- bridge output shows files updated, then fails while stashing/pulling/committing

This is a fallback for landing the bridge outputs only; do not use it to commit unrelated repo churn.

## Procedure

1. Confirm the quality gate passed and was not a degenerate-memory abort.
   - If score `< 50`, do **not** bridge.
   - If score `>= 50`, continue only if `.claude/memory/` outputs were written.

2. Verify remote relationship before creating a manual commit:

```bash
cd /mnt/local-analysis/workspace-hub
git fetch origin main
git rev-list --left-right --count origin/main...HEAD
```

Expected safe case: `0 0` or only local bridge work pending. If behind, avoid broad rebase/stash in a dirty checkout; resolve upstream state first or use a clean worktree.

3. Inspect only memory outputs, not repo-wide churn:

```bash
git diff --cached --name-only -- .claude/memory
git status --short --ignore-submodules=all -- .claude/memory
```

4. Commit with an explicit pathspec so unrelated staged/dirty files are excluded:

```bash
git commit -m "chore(memory): auto-refresh memory bridge ($(date +%F))" -- .claude/memory
```

5. Push and verify remote HEAD:

```bash
git push origin main
git rev-parse HEAD
git ls-remote origin refs/heads/main | cut -f1
```

6. Verify the bridge succeeded semantically:

```bash
bash scripts/memory/check-memory-drift.sh
```

Expected result: `In sync — no drift detected` and exit code `0`.

7. Report honestly:
   - quality score
   - drift count from the initial drift check
   - `.claude/memory/` files updated with line counts
   - that the internal script commit failed and the path-limited fallback commit/push was used
   - final commit SHA and drift recheck result

## Pitfalls

- Do not run broad `git stash`, `git add .`, or repo-wide `git commit` in workspace-hub when unrelated agent/session churn is present.
- Do not trust repo-wide `git status` if submodules are broken; use `--ignore-submodules=all` and path-limited checks for `.claude/memory/`.
- Do not rerun the bridge repeatedly after outputs were written; repeated runs can change timestamps and expand the diff.
- This skill overlaps with `memory-bridge-operation`; prefer updating that canonical skill when it is editable.
