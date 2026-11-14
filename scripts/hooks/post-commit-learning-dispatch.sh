#!/usr/bin/env bash
# Installed learning-step payload. Git 2.43 githooks, post-commit: the commit
# has already succeeded. Fail open, but record every lost learning invocation.
# Trust boundary: execute regular blobs from one pinned HEAD, never checkout bytes.
set -uo pipefail

learning_git() (
    unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_PREFIX
    unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
    git "$@"
)

learning_dispatch() {
    local root common snapshot helper payload mode rc log failures
    root=$(learning_git rev-parse --show-toplevel) || {
        echo 'post-commit: learning failed; repository root unavailable' >&2
        return 0
    }
    common=$(learning_git -C "$root" rev-parse --path-format=absolute --git-common-dir) || {
        echo 'post-commit: learning failed; common directory unavailable' >&2
        return 0
    }
    log="$common/post-commit-learning-failures.log"
    rc=0
    helper=scripts/hooks/post-commit-learnings.sh
    snapshot=$(learning_git -C "$root" rev-parse --verify 'HEAD^{commit}') || rc=$?
    if ((rc == 0)); then
        mode=$(learning_git -C "$root" ls-tree "$snapshot" -- "$helper") || rc=$?
        case "$mode" in
            '100644 blob '*|'100755 blob '*) ;;
            *) rc=1 ;;
        esac
    fi
    if ((rc == 0)); then
        payload=$(learning_git -C "$root" cat-file blob "$snapshot:$helper") || rc=$?
    fi
    if ((rc == 0)); then
        (cd "$root" && bash -c "$payload" -- "$root" "$snapshot") \
            >> "$common/post-commit-learning-output.log" 2>&1 || rc=$?
    fi
    if ((rc != 0)); then
        if printf 'failure rc=%s commit=%s\n' "$rc" "${snapshot:-unavailable}" >> "$log"; then
            failures=$(grep -c '^failure ' "$log")
            printf 'post-commit: learning failed; failures=%s log=%s\n' "$failures" "$log" >&2
        else
            echo 'post-commit: learning failed; failure log is not writable; count unavailable' >&2
        fi
    fi
    return 0
}
learning_dispatch
# Git 2.43 githooks: post-commit cannot change the outcome of git commit.
exit 0
