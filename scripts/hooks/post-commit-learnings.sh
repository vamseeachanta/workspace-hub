#!/usr/bin/env bash
# Learning pipeline, invoked by the installed post-commit learning entry point.
# Git 2.43 git-cat-file: execute only regular blobs from the pinned commit.
# Optional absent steps retain their previous skip semantics. A failing present
# step is returned to the entry point, which records the lost invocation.
set -euo pipefail

pipeline_git() (
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_PREFIX
    unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
    git "$@"
)

root=${1:-$(pipeline_git rev-parse --show-toplevel)}
snapshot=${2:-$(pipeline_git -C "$root" rev-parse --verify 'HEAD^{commit}')}
failed=0
for step in scripts/hooks/track-skill-patches.sh scripts/learnings/extract-learnings.sh; do
    mode=$(pipeline_git -C "$root" ls-tree "$snapshot" -- "$step")
    [[ -n $mode ]] || continue
    case "$mode" in
        '100644 blob '*|'100755 blob '*) ;;
        *) echo "post-commit: non-regular learning step refused: $step" >&2; failed=1; continue ;;
    esac
    if ! payload=$(pipeline_git -C "$root" cat-file blob "$snapshot:$step"); then
        failed=1
        continue
    fi
    # Preserve active-worktree context while keeping executable bytes immutable.
    if ! (cd "$root" && bash -c "$payload" "$step" "$snapshot"); then
        echo "post-commit: learning step failed: $step" >&2
        failed=1
    fi
done
exit "$failed"
