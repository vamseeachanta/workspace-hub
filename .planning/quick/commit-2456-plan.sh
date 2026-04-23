#!/usr/bin/env bash
set -euo pipefail

REPO=/mnt/local-analysis/workspace-hub
BRANCH=nightly/2454-2457-planwave
PLAN_PATH=docs/plans/2026-04-23-issue-2456-lazy-wave-riser-semantic-proof.md
SRC=$REPO/.planning/quick/2026-04-23-issue-2456-plan.md

BLOB=$(git -C "$REPO" hash-object -w "$SRC")
echo "blob=$BLOB"

INDEX_TMP=$REPO/.planning/quick/plan-2456-index
rm -f "$INDEX_TMP"

# Use the branch tree as the baseline
export GIT_INDEX_FILE=$INDEX_TMP
git -C "$REPO" read-tree "$BRANCH"
git -C "$REPO" update-index --add --cacheinfo "100644,$BLOB,$PLAN_PATH"

NEW_TREE=$(git -C "$REPO" write-tree)
echo "new_tree=$NEW_TREE"
unset GIT_INDEX_FILE

PARENT=$(git -C "$REPO" rev-parse "$BRANCH")
echo "parent=$PARENT"

COMMIT=$(GIT_AUTHOR_NAME="Vamsee Achanta" \
  GIT_AUTHOR_EMAIL="vamsee.achanta@aceengineer.com" \
  GIT_COMMITTER_NAME="Vamsee Achanta" \
  GIT_COMMITTER_EMAIL="vamsee.achanta@aceengineer.com" \
  git -C "$REPO" commit-tree "$NEW_TREE" -p "$PARENT" \
  -m "plan(#2456): add lazy-wave riser semantic proof plan (worker-3)")
echo "commit=$COMMIT"

git -C "$REPO" update-ref "refs/heads/$BRANCH" "$COMMIT" "$PARENT"
echo "ref updated"

rm -f "$INDEX_TMP"
git -C "$REPO" log --oneline "$BRANCH" -3
