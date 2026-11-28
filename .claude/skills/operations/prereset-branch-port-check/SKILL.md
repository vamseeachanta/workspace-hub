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

Set OLD and BUNDLES to absolute directories. Set NAME to a fresh single-component name and TIP to the revision to capture. Record the printed SHA with the bundle.

```sh
(
    set -euC
    tip=$(git -C "$OLD" rev-parse --verify "${TIP}^{commit}")
    ref=refs/port/"$NAME"
    bundle="$BUNDLES/$NAME.bundle"
    printf '%s\n' "$tip"
    if test -e "$bundle" || test -L "$bundle"; then
        echo "Bundle path already exists" >&2
        exit 1
    fi
    git -C "$OLD" update-ref "$ref" "$tip" ''
    git -C "$OLD" bundle create - "$ref" > "$bundle"
    git -C "$OLD" bundle verify "$bundle"
    head=$(git -C "$OLD" bundle list-heads "$bundle" "$ref")
    test "$head" = "$tip $ref"
    current=$(git -C "$OLD" rev-parse --verify "$ref")
    test "$current" = "$tip"
    git -C "$OLD" update-ref -d "$ref" "$tip"
)
```

If capture fails, keep the ref and any partial bundle for inspection.

Keep the bundles under the machine's `_pm/` or `_backups/` folder until the check is complete. A bundle is also the recovery copy if the clone is later removed.

## 2. Work in a fresh lean clone

Set LEAN to the absolute path of a fresh shallow clone of the lean default branch. Fetch the bundle there. Record the default branch commit once for this check.

```sh
git -C "$LEAN" fetch "$BUNDLES/$NAME.bundle" "refs/port/$NAME:refs/port/$NAME"
LEAN_SHA=$(git -C "$LEAN" rev-parse --verify refs/remotes/origin/HEAD^{commit})
```

## 3. Find the branch's own paths

List the branch's own changes in LEAN.

```sh
git -C "$LEAN" diff --name-status "$BASE" "refs/port/$NAME"
```

Set BASE to the merge base with the **old** default branch (from the old clone's `origin/<default>` reflog; the bundle history contains it). If no usable base exists, take the path list from the clone review and compare each path at the tip with the lean main. Include deletions and both sides of renames.

## 4. Classify every path

Compare each repository-relative path in LEAN. Both commands must succeed. Empty output means the path is absent.

```sh
git --literal-pathspecs -C "$LEAN" ls-tree "refs/port/$NAME" -- "$path"
git --literal-pathspecs -C "$LEAN" ls-tree "$LEAN_SHA" -- "$path"
```

| Class | Test | Action |
|---|---|---|
| `ALREADY-ON-MAIN` | Both entries have the same mode and object ID, or both are absent. | None. |
| `SUPERSEDED` | Lean main has a different, later version that contains the branch's change, or the file was moved out of Git and the lean manifest records its SHA-256 and size. Name the landing commit or manifest entry. | None. |
| `MISSING` | Neither of the above. | Port. |

A missing executable bit is `MISSING` even when the blob IDs match. Match PRs by **head SHA** using the merged PR list's `headRefOid`. A merged PR for the same branch name is supporting evidence, not proof: the local tip may carry commits made after the merge. Record the PR number, its merged head and the tip; a differing head requires the path comparison.

Inventory the old index, working tree and untracked files separately.

```sh
git -C "$OLD" diff --cached --name-status
git -C "$OLD" diff --name-status
git -C "$OLD" ls-files --others --exclude-standard
```

Save each changed index entry from the index, even if its working copy was deleted. Record its mode and object ID and export its blob to a fresh backup file. Save working copies and untracked files separately with their modes and symlinks intact. Record deletions in each inventory. Verify the saved copies before classifying them.

For each captured stash, compare its first parent with its second parent for staged changes, then its second parent with its tip for working-tree changes. For a stash made with `-u`, also list the third parent's files. Classify each version separately. Ignore cache noise only after listing it.

```sh
git -C "$LEAN" diff --name-status "refs/port/$NAME^1" "refs/port/$NAME^2"
git -C "$LEAN" diff --name-status "refs/port/$NAME^2" "refs/port/$NAME"
# For a stash with untracked files:
git -C "$LEAN" ls-tree -r "refs/port/$NAME^3"
```

For data moved to a manifest-and-fetch store, hash the tip's bytes and compare them with the manifest's SHA-256 and byte count. Say whether the stored copy itself was checked; a manifest match does not prove the store holds the file.

## 5. Port what is missing

Create the port branch in a fresh worktree at the recorded LEAN_SHA. Set WORKTREE to its absolute path.

**Patch.** Generate the mailbox in LEAN from the fetched ref. Set PATCH to a fresh absolute file path and pass the missing paths after the range.

```sh
git -C "$LEAN" format-patch --stdout "$BASE..refs/port/$NAME" -- "$path" > "$PATCH"
```

After screening, apply the mailbox in the port worktree.

```sh
git -C "$WORKTREE" am --3way "$PATCH"
```

**Copy.** If the patch does not apply cleanly, copy the missing change by content. Preserve mode changes and deletions. Apply only the branch's own hunks when the lean file has moved on.

Either method creates new commits on the lean history; no old commit object enters it. Keep the lean main's unrelated content. Run the repository's tests for the touched area. The commit message names the original branch and tip SHA. In a public repository, check every ported file for client names, personal names, email addresses, host names and private paths before committing, and leave out any file that carries one.

Before clearing a tip, read back each missing change against the resulting lean tree, including changes made only during merge resolution.

On Windows PowerShell 5.1, use `--output-directory` with a fresh directory instead of redirecting stdout, then apply the patch files in order.

For public repositories, screen the whole patch series before applying it and check each resulting commit before publication.

## 6. Record the result

For each tip, record: the bundle and its verification, the base used and how it was found, every path with its class and both tree entries (mode and object ID, or absent), the landing commit or manifest entry for each `SUPERSEDED` path, tests run and their result, the port branch and commit if any, and anything not established. Keep the record beside the machine's cleanup receipts in the private operations repository. Only a tip whose every path is `ALREADY-ON-MAIN` or `SUPERSEDED`, or whose port has merged, stops blocking the clone's retirement. The retirement itself follows the machine-readiness skill.

## Prompt to paste

```text
Read workspace-hub/.claude/skills/operations/prereset-branch-port-check/SKILL.md.
Bundles are in BUNDLES; the repositories are cloned fresh from the lean main.
Classify every path of every tip, port only MISSING paths by content, no push.
Write RESULT.md with tree entries or absence, landing commits, tests and anything not established.
```
