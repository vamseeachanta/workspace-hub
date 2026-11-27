---
name: prereset-branch-port-check
description: Decide whether a branch that exists only on pre-reset history still carries work missing from the lean main, and port it by content when it does. Use before retiring an old clone after a history reset.
version: 1.0.0
---

# Pre-reset branch port check

## When to use

A repository's history was reset (new root commit) and an old clone still holds a local branch, a detached HEAD or a stash whose tip is not on the new history. The clone cannot be retired until each such tip is classified. Ancestry cannot answer the question, because no pre-reset commit is an ancestor of the lean main. Branch names cannot answer it either. Only path content can.

The old clone is never pushed from and never merged. Work moves to the lean main by **copying file content**, never by merge, rebase or cherry-pick of old commits.

## 1. Capture each tip

In the old clone, write each tip to a verified bundle under a temporary ref, then delete the temporary ref:

```sh
git -C OLD update-ref refs/port/NAME TIP
git -C OLD bundle create BUNDLES/NAME.bundle refs/port/NAME
git bundle verify BUNDLES/NAME.bundle
git -C OLD update-ref -d refs/port/NAME
```

Keep the bundles under the machine's `_pm/` or `_backups/` folder until the check is complete. A bundle is also the recovery copy if the clone is later removed.

## 2. Work in a fresh lean clone

Use a fresh shallow clone of the lean default branch, not the old clone. Fetch each bundle into it as a local ref only:

```sh
git -C LEAN fetch BUNDLES/NAME.bundle refs/port/NAME:refs/port/NAME
```

## 3. Find the branch's own paths

The branch's own change set is `git diff --name-status BASE refs/port/NAME`, where `BASE` is the merge base with the **old** default branch (from the old clone's `origin/<default>` reflog; the bundle history contains it). If no usable base exists, take the path list from the clone review and compare each path at the tip with the lean main. Include deletions and both sides of renames.

## 4. Classify every path

| Class | Test | Action |
|---|---|---|
| `ALREADY-ON-MAIN` | The tip blob equals the lean-main blob (`git rev-parse refs/port/NAME:PATH` and `origin/main:PATH`). | None. |
| `SUPERSEDED` | Lean main has a different, later version that contains the branch's change, or the file was moved out of Git and the lean manifest records its SHA-256 and size. Name the landing commit or manifest entry. | None. |
| `MISSING` | Neither of the above. | Port. |

Match PRs by **head SHA**, not branch name: `gh pr list --state all --search <sha>` or the merged-PR list's `headRefOid`. A merged PR for the same branch name is supporting evidence, not proof: the local tip may carry commits made after the merge. Record the PR number, its merged head and the tip; a differing head requires the path comparison.

The same classes apply to stashes and dirty working files: compare each stash entry's files and each modified or untracked file with the lean main the same way. Ignore cache noise (`__pycache__`, `.pytest_cache`, `node_modules`, virtual environments) only after listing it.

For data moved to a manifest-and-fetch store, hash the tip's bytes and compare them with the manifest's SHA-256 and byte count. Say whether the stored copy itself was checked; a manifest match does not prove the store holds the file.

## 5. Port what is missing

Work in a fresh worktree `_wt/<repo-short>--<slug>` on `origin/main`. Two methods, in order of preference:

- **Patch.** In the old clone, `git format-patch --stdout BASE..refs/port/NAME -- <MISSING paths> > NAME.patch`; in the lean worktree, `git am --3way NAME.patch`. Three-way apply keeps the lean main's later edits and stops on a real conflict. Generate patches with `format-patch`, not by saving `git diff` text: hand-saved diff text has produced corrupt patches.
- **Copy.** Where the patch does not apply cleanly, copy the tip's version of each `MISSING` path, or apply only the branch's own hunks when the lean file has moved on.

Either method creates new commits on the lean history; no old commit object enters it. Keep the lean main's unrelated content. Run the repository's tests for the touched area. The commit message names the original branch and tip SHA. In a public repository, check every ported file for client names, personal names, email addresses, host names and private paths before committing, and leave out any file that carries one.

## 6. Record the result

For each tip, record: the bundle and its verification, the base used and how it was found, every path with its class and both blob IDs, the landing commit or manifest entry for each `SUPERSEDED` path, tests run and their result, the port branch and commit if any, and anything not established. Keep the record beside the machine's cleanup receipts in the private operations repository. Only a tip whose every path is `ALREADY-ON-MAIN` or `SUPERSEDED`, or whose port has merged, stops blocking the clone's retirement. The retirement itself follows the machine-readiness skill.

## Prompt to paste

```text
Read workspace-hub/.claude/skills/operations/prereset-branch-port-check/SKILL.md.
Bundles are in BUNDLES; the repositories are cloned fresh from the lean main.
Classify every path of every tip, port only MISSING paths by content, no push.
Write RESULT.md with blob IDs, landing commits, tests and anything not established.
```
