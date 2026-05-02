# Session Closeout — Worktree/Branch Hygiene and Preserved PR Sweep

Date: 2026-05-01 20:19 CDT
Repo: `/mnt/local-analysis/workspace-hub`
Primary branch: `main`
Closeout owner: Hermes Agent

## Executive status

- `main` is pushed to `origin/main`.
- PR #2579 is merged into `main` and contained in `origin/main`.
- Branch `plan/issue-2380-batch-pack-3-tier-a` was deleted locally and remotely after merge.
- Earlier inherited branch/worktree debt was reduced by deleting only branches already merged to `origin/main` and preserving all branches with unique commits.
- The preserved-branch PR sweep is not complete; continue one branch at a time.
- Unrelated/generated dirty state appeared during closeout. It was preserved in local git stashes before writing this closeout artifact; do not treat it as discarded.

## Verified repository evidence

Latest live verification before this artifact:

```text
branch=main
HEAD=e18c881280a349a810453707b69f26c209af04d1
origin/main=e18c881280a349a810453707b69f26c209af04d1
ahead/behind=0/0
PR #2579 merge commit contained in origin/main=yes
```

Recent commits at verification time:

```text
e18c88128 review(gtm): Adv-D2 round-2 link-check — 13/13 dual-UA CLEAN
baa83a6dc docs(closeout): record PR 2579 merge cleanup
c435869b3 fix(gtm): apply matrix §3b human-judgment decisions — Otto Candies P2->P1
a974b4b5c Merge pull request #2579 from vamseeachanta/plan/issue-2380-batch-pack-3-tier-a
bb456e42a chore(sync): auto-sync 2026-05-01
b41ca788b Merge branch 'main' into plan/issue-2380-batch-pack-3-tier-a
641d96dac docs(#2567): add steering gear source crosswalk
8d42297e4 feat(#2544): add woodfibre corpus pointer page
0e148288f ci(enforcement): install uv and expose src path
```

## PR #2579 evidence

- PR: <https://github.com/vamseeachanta/workspace-hub/pull/2579>
- Head branch: `plan/issue-2380-batch-pack-3-tier-a`
- Original plan commit: `84570eb12 docs(plan): draft plan for #2380`
- Base CI fix: `0e148288f ci(enforcement): install uv and expose src path`
- Branch update commit: `b41ca788b Merge branch 'main' into plan/issue-2380-batch-pack-3-tier-a`
- Merge commit: `a974b4b5c6d49327fd27584f819cc138eea8a2d1`
- Merged at: `2026-05-02T01:03:58Z`
- Final state before merge: `MERGEABLE`, `CLEAN`
- Final required checks recorded passing in the PR sweep ledger:
  - `Run Tests`
  - `claude-review`
  - `Stage Prompt Drift Guard`
  - `Code Quality`
  - `Review Evidence Check`
  - `Governance Checks`
  - `Plan Approval Check`
  - `Compliance Dashboard`
  - `GitGuardian Security Checks`

## Why stale files/branches/worktrees accumulated

Root causes observed from log/repo review:

1. **Issue closeout was not atomic.** Some issue flows treated merge/close as separate from push, branch deletion, worktree removal, and clean-state proof. That creates stale branches and stale filesystem state even when issue work is done.
2. **Concurrent agents wrote to the same control checkout.** Claude/Codex/Gemini/session hooks generated `.claude/state`, provider reports, and GSD/plugin files while closeout was being verified.
3. **Registered worktree cleanup missed broken filesystem worktrees.** `git worktree list` can be clean while `.claude/worktrees/*` contains broken/unregistered directories pointing to missing `.git/worktrees/*` entries.
4. **Preserved branches were not all merged or deleted.** Branches with unique commits must be handled via PR, not bulk-deleted. The initial cleanup correctly preserved these, but that means a PR sweep remains.
5. **Evidence was sometimes truncated or not committed in the same operation.** When tool output truncates, later sessions need to re-run exact commands and record ledger evidence.

## Closeout rule to enforce going forward

When an issue/PR is closed, perform this as one transaction under `.git/agent-closeout.lock`:

1. Revalidate issue/PR state and branch ancestry.
2. Run required tests/checks or verify required GitHub checks are green.
3. Commit all intended evidence/artifacts.
4. Push to `origin`.
5. Merge only if GitHub reports mergeable/clean and required checks pass.
6. Delete the merged local and remote branch.
7. Remove the owned worktree.
8. Verify `HEAD == origin/main`, ahead/behind `0/0`, and `git status --short --branch` clean.
9. Only then close or mark the issue complete.

Push-to-origin and cleanup are not follow-up chores. They must happen before/with issue closure.

## Current worktree/branch inventory at closeout start

Registered worktrees observed:

```text
/mnt/local-analysis/workspace-hub                                      main                                  e18c881280
/mnt/local-analysis/agent-worktrees/workspace-hub-integration-main-2544-2567 integration/main-2544-2567     641d96dac
/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2544           codex/issue-2544-woodfibre-pointer-v2 ec1a3d728
/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2567           codex/issue-2567-standards-rudder-v2  781510448
```

Local branch counts before this closeout artifact:

```text
local branches total: 36
merged into origin/main excluding main: 1
not merged into origin/main excluding main: 34
```

Open PR observed before this closeout artifact:

```text
#2495 exec/issue-2126-markdown-conversion-qa — mergeability/check state UNKNOWN at query time
```

## Preserved dirty state

Before writing this closeout artifact, unrelated/generated dirty state was preserved in git stash instead of mixed into the closeout commit:

```text
stash@{0}: On main: session-closeout-preserve-concurrent-provider-dirt-20260501T202141-0500
stash@{1}: On main: session-closeout-preserve-remaining-generated-dirt-20260501T201907-0500
stash@{2}: On main: session-closeout-preserve-unrelated-claude-gsd-state-20260501T201845-0500
stash@{3}: On main: git-safe-auto-stash
```

Stashed paths included generated `.claude/state`, GSD command/plugin files, GSD agent/hook files, provider telemetry/report churn, and untracked GTM review notes such as `docs/sessions/2026-05-01-gtm-review-A2-html-round2.md`, `docs/sessions/2026-05-01-gtm-review-B2-gemini-round2.md`, and `docs/sessions/2026-05-01-gtm-review-C2-silent-failures-round2.md`. These were not deleted; they were preserved for a later owner to review, apply, commit, or discard intentionally.

## Next priorities

1. **Finish the preserved-branch PR sweep one branch at a time.** Rebuild live inventory first; do not rely on older TSV files if exact state matters.
2. **Resolve or intentionally discard the preserved stashes.** Inspect `stash@{0}` and `stash@{1}` before applying; do not blindly commit generated GSD/plugin files.
3. **Handle registered issue/integration worktrees intentionally.** Branches `integration/main-2544-2567`, `codex/issue-2544-woodfibre-pointer-v2`, and `codex/issue-2567-standards-rudder-v2` are clean but still registered.
4. **Reconstruct exact evidence for earlier PR sweep branches if needed.** Evidence for PR #2575, PR #2576, and issue-2105 was partly truncated in tool output.
5. **Keep force-push prohibited.** A previous `git push --force-with-lease` happened during issue-2105 reconciliation; do not repeat.

## Fresh-session prompt

Use this prompt to continue safely:

```text
Resume in /mnt/local-analysis/workspace-hub. First run live verification: git status --short --branch --untracked-files=normal, git rev-parse HEAD origin/main, git rev-list --left-right --count HEAD...origin/main, git worktree list --porcelain, and gh pr list for open PRs. Read docs/sessions/2026-05-01-session-closeout-worktree-pr-sweep.md and docs/sessions/2026-05-01-pr-sweep-ledger.md. Continue the preserved-branch PR sweep one branch at a time. Do not force-push, do not reset --hard, do not auto-resolve merge conflicts, and do not close issues before push+merge+branch/worktree cleanup+clean-state proof happen in the same transaction under .git/agent-closeout.lock. Inspect stashes session-closeout-preserve-* before applying or discarding any generated .claude/GSD state.
```

## Closeout verification checklist

To complete this session closeout after committing this file:

```bash
cd /mnt/local-analysis/workspace-hub
git status --short --branch --untracked-files=normal
git add docs/sessions/2026-05-01-session-closeout-worktree-pr-sweep.md
git commit -m "docs(closeout): record worktree PR sweep session handoff"
git push origin main
git fetch origin main
git rev-parse HEAD origin/main
git rev-list --left-right --count HEAD...origin/main
git status --short --branch --untracked-files=normal
git worktree list --porcelain
```
