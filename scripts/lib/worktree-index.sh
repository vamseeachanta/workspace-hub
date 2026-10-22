#!/usr/bin/env bash
# Git 2.43: git-worktree DETAILS; git-sparse-checkout INTERNALS / SPARSE INDEX.
# A sparse index still represents tracked leaves; absent materialization is valid.

worktree_git() (
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_PREFIX
    unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
    git "$@"
)

worktree_index_preflight() (
    set -euo pipefail
    local root=${1:-.} fresh=${2:-} head_count index_count deleted_count skip_count entry
    case "$fresh" in ''|--fresh) ;; *) echo 'worktree-index: unknown option' >&2; return 2 ;; esac
    # NUL counting preserves whitespace and newline filenames (git-ls-files -z).
    # Zero means no entries, not an engineering acceptance threshold.
    if ! worktree_git -C "$root" rev-parse --verify 'HEAD^{tree}' >/dev/null; then
        echo 'worktree-index: HEAD tree unavailable; inspection refused' >&2
        return 2
    fi
    head_count=$(worktree_git -C "$root" ls-tree -r -z --name-only HEAD | tr -cd '\000' | wc -c | tr -d ' ') || return 2
    index_count=$(worktree_git -C "$root" ls-files --cached -z | tr -cd '\000' | wc -c | tr -d ' ') || return 2
    if ((head_count > 0 && index_count == 0)); then
        echo 'worktree-index: empty index with nonempty HEAD; stop and recreate the owned worktree after checking active processes; no automatic repair' >&2
        return 1
    fi
    if [[ $fresh == --fresh ]] && ((head_count > 0)); then
        deleted_count=$(worktree_git -C "$root" diff --cached --no-renames --diff-filter=D --name-only -z HEAD -- | tr -cd '\000' | wc -c | tr -d ' ') || return 2
        if ((deleted_count == head_count)); then
            echo 'worktree-index: fresh worktree has whole-tree deletions; recreate after ownership checks' >&2
            return 1
        fi
    fi
    skip_count=0
    while IFS= read -r -d '' entry; do
        if [[ $entry == 'S '* ]]; then skip_count=$((skip_count + 1)); fi
    done < <(worktree_git -C "$root" ls-files -t -z)
    printf 'worktree-index: head=%s index=%s skip-worktree=%s OK\n' "$head_count" "$index_count" "$skip_count"
)
