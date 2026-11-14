#!/usr/bin/env bash
# Git 2.43: git-worktree DETAILS; git-sparse-checkout INTERNALS / SPARSE INDEX.
# A sparse index still represents tracked leaves; absent materialization is valid.

worktree_git() (
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_PREFIX
    unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
    git "$@"
)

# Discovery always uses worktree_git. Only an explicitly selected staged reader
# may retain an alternate index belonging to the caller's repository context.
worktree_select_index() {
    WORKTREE_ACTIVE_INDEX=
    [[ ${GIT_INDEX_FILE+x} ]] || return 0
    local expected actual root caller expected_common actual_common
    expected=$(worktree_git -C "$1" rev-parse --absolute-git-dir) || return 2
    actual=$(git rev-parse --absolute-git-dir 2>/dev/null) || return 0
    root=$(worktree_git -C "$1" rev-parse --show-toplevel) || return 2
    caller=$(git rev-parse --show-toplevel 2>/dev/null) || return 0
    expected_common=$(worktree_git -C "$1" rev-parse --path-format=absolute --git-common-dir) || return 2
    actual_common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || return 0
    # Common-directory equality is insufficient: linked worktrees have separate
    # indexes. Compare all repository bindings before selecting caller content.
    [[ $(realpath -m -- "$expected") == "$(realpath -m -- "$actual")" &&
       $(realpath -m -- "$root") == "$(realpath -m -- "$caller")" &&
       $(realpath -m -- "$expected_common") == "$(realpath -m -- "$actual_common")" ]] || return 0
    if [[ -z $GIT_INDEX_FILE || ! -f $GIT_INDEX_FILE || ! -r $GIT_INDEX_FILE ]]; then
        echo 'worktree-index: selected index unavailable; inspection refused' >&2
        return 2
    fi
    # Resolve relative to the caller before any content read changes directory.
    WORKTREE_ACTIVE_INDEX=$(realpath -m -- "$GIT_INDEX_FILE") || return 2
}

worktree_index_git() (
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_PREFIX
    unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
    if [[ -n ${WORKTREE_ACTIVE_INDEX:-} ]]; then
        export GIT_INDEX_FILE=$WORKTREE_ACTIVE_INDEX
    fi
    git "$@"
)

worktree_index_preflight() (
    set -euo pipefail
    local root=${1:-.} fresh=${2:-} git_read=${3:-worktree_git} head_count index_count deleted_count skip_count entry
    case "$fresh" in ''|--fresh) ;; *) echo 'worktree-index: unknown option' >&2; return 2 ;; esac
    case "$git_read" in
        worktree_git|worktree_index_git) ;;
        *) echo 'worktree-index: unknown content reader' >&2; return 2 ;;
    esac
    # NUL counting preserves whitespace and newline filenames (git-ls-files -z).
    # Zero means no entries, not an engineering acceptance threshold.
    if ! "$git_read" -C "$root" rev-parse --verify 'HEAD^{tree}' >/dev/null; then
        echo 'worktree-index: HEAD tree unavailable; inspection refused' >&2
        return 2
    fi
    head_count=$("$git_read" -C "$root" ls-tree -r -z --name-only HEAD | tr -cd '\000' | wc -c | tr -d ' ') || return 2
    index_count=$("$git_read" -C "$root" ls-files --cached -z | tr -cd '\000' | wc -c | tr -d ' ') || return 2
    if ((head_count > 0 && index_count == 0)); then
        echo 'worktree-index: empty index with nonempty HEAD; stop and recreate the owned worktree after checking active processes; no automatic repair' >&2
        return 1
    fi
    if [[ $fresh == --fresh ]] && ((head_count > 0)); then
        deleted_count=$("$git_read" -C "$root" diff --cached --no-renames --diff-filter=D --name-only -z HEAD -- | tr -cd '\000' | wc -c | tr -d ' ') || return 2
        if ((deleted_count == head_count)); then
            echo 'worktree-index: fresh worktree has whole-tree deletions; recreate after ownership checks' >&2
            return 1
        fi
    fi
    skip_count=0
    while IFS= read -r -d '' entry; do
        if [[ $entry == 'S '* ]]; then skip_count=$((skip_count + 1)); fi
    done < <("$git_read" -C "$root" ls-files -t -z)
    printf 'worktree-index: head=%s index=%s skip-worktree=%s OK\n' "$head_count" "$index_count" "$skip_count"
)
