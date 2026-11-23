# Archived Skill: `blocked-branch-preserve-tag-cleanup`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/blocked-branch-preserve-tag-cleanup`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/blocked-branch-preserve-tag-cleanup`
Consolidation date: 2026-04-29

---

---
name: blocked-branch-preserve-tag-cleanup
description: Safely clean stale local branches that cannot be merged by preserving them with local tags before deletion
version: 1.0.0
source: session-learned
---

# Blocked Branch Preserve-Tag Cleanup

Use when cleaning many repos and some stale local branches cannot be merged safely into the default branch.

## Trigger conditions
- `git merge` fails with `refusing to merge unrelated histories`
- branch has no matching remote branch
- branch has shared history but the diff is extremely large / artifact-heavy / conflict-heavy, making opportunistic cleanup riskier than preservation
- repo hygiene is the goal, not historical branch recovery work

## Safe disposition workflow
1. Inspect the blocked branch:
   - confirm default branch
   - check whether a matching remote branch exists
   - check whether histories are unrelated via failed merge or missing merge-base
   - estimate branch size with `git diff --shortstat <default>...<branch>` when histories are related
2. Classify the branch:
   - `mergeable` if small and clean
   - `preserve-only` if unrelated history, no remote, or very large/conflict-heavy
   - `active/worktree-backed` if the branch is attached to a live worktree; do not delete yet
3. For `preserve-only` branches, create a local recovery tag before deletion:
   - `git tag preserve/<branch>-$(date +%Y%m%d) <branch>`
4. Delete the local branch after tagging:
   - `git branch -D <branch>`
5. Do not push the preservation tag by default. Keep it local unless the user explicitly wants remote archival.

## Why this works
This gives you a reversible cleanup path: branch clutter is removed, but the exact tip commit remains recoverable through the tag.

## Practical heuristics
- Unrelated-history branches with no remote are usually stale/orphan branches; do not force `--allow-unrelated-histories` unless the user explicitly wants content salvage.
- If a branch diff is huge (for example thousands of files, generated assets, or vendored environments), prefer preserve-only cleanup over ad hoc conflict resolution.
- If a conflict is in legacy control-plane files (`.agent-os`, old instructions, generated environments), that is usually a sign the branch is not worth opportunistic merging during hygiene work.
- Worktree-backed branches must be handled after their worktrees are removed or confirmed inactive.

## Verification
After cleanup, verify:
- `git branch -vv` no longer lists the stale branch
- `git tag --list 'preserve/*'` contains the recovery tag
- default branch remains checked out and clean/up to date
