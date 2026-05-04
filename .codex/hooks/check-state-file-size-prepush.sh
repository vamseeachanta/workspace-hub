#!/usr/bin/env bash
# check-state-file-size-prepush.sh — Block pushes containing oversized state blobs
# Issue: #2070 (https://github.com/vamseeachanta/workspace-hub/issues/2070)
# Plan:  docs/plans/2026-04-16-issue-2070-state-size-guard.md
#
# Why a SEPARATE pre-push hook (not just pre-commit):
#   The pre-commit guard inspects the staged index. By the time `git push` runs,
#   the index is empty — but oversized blobs already in HEAD will still be pushed.
#   This hook scans the commit range being pushed and blocks the push if any blob
#   under WATCH_PATHS exceeds BLOCK_MB.
#
# Stdin format (per git pre-push hook spec):
#   <local_ref> <local_sha> <remote_ref> <remote_sha>\n  (one line per ref)
#
# Env overrides (testing):
#   STATE_SIZE_BLOCK_MB   — override block threshold (default 75)
#   STATE_SIZE_WATCH_PATH — override watch path glob (default .claude/state/session-signals/)
set -uo pipefail

BLOCK_MB="${STATE_SIZE_BLOCK_MB:-75}"
WATCH_PREFIX="${STATE_SIZE_WATCH_PATH:-.claude/state/session-signals/}"
ZERO_OID="0000000000000000000000000000000000000000"

FAIL=0
SAW_VALID_REF=0

is_oid() {
    [[ "${1:-}" =~ ^[0-9a-fA-F]{40}$ ]]
}

check_push_ref() {
    local local_ref="${1:-}"
    local local_sha="${2:-}"
    local remote_ref="${3:-}"
    local remote_sha="${4:-}"

    [[ -z "$local_sha" ]] && return 0
    is_oid "$local_sha" || return 2
    # Branch deletion has local_sha == ZERO_OID — nothing to inspect
    [[ "$local_sha" == "$ZERO_OID" ]] && return 0

    if [[ "$remote_sha" == "$ZERO_OID" ]] || ! is_oid "$remote_sha"; then
        # New branch — inspect the full commit reachable from local that is not
        # yet on any remote. Falls back to just $local_sha if no other refs.
        range_args=("$local_sha" "--not" "--remotes")
    else
        range_args=("${remote_sha}..${local_sha}")
    fi

    # Walk every blob in the range; format: "<oid> <objsize> <path>"
    while read -r oid size path; do
        [[ -z "$path" ]] && continue
        [[ "$path" != "$WATCH_PREFIX"* ]] && continue
        size_mb=$(( size / 1048576 ))
        if (( size_mb > BLOCK_MB )); then
            echo "BLOCKED at push: ${path} in commit range is ${size_mb}MB (limit ${BLOCK_MB}MB)." >&2
            echo "  Run scripts/state/rotate-cost-tracking.sh, amend or rotate, then re-push." >&2
            FAIL=1
        fi
    done < <(
        git rev-list --objects "${range_args[@]}" 2>/dev/null \
          | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' 2>/dev/null \
          | awk '$1 == "blob" { $1=""; sub(/^ /, ""); print }'
    )
}

infer_current_push_ref() {
    local local_ref local_sha remote_ref remote_sha upstream

    local_sha="$(git rev-parse HEAD 2>/dev/null || true)"
    is_oid "$local_sha" || return 0

    local_ref="$(git symbolic-ref -q HEAD 2>/dev/null || echo HEAD)"
    upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
    if [[ -n "$upstream" ]]; then
        remote_ref="$upstream"
        remote_sha="$(git rev-parse "$upstream" 2>/dev/null || echo "$ZERO_OID")"
    else
        remote_ref=""
        remote_sha="$ZERO_OID"
    fi

    check_push_ref "$local_ref" "$local_sha" "$remote_ref" "$remote_sha"
}

while read -r local_ref local_sha remote_ref remote_sha _extra; do
    if is_oid "$local_sha"; then
        SAW_VALID_REF=1
        check_push_ref "$local_ref" "$local_sha" "$remote_ref" "$remote_sha"
    fi
done

if (( SAW_VALID_REF == 0 )); then
    infer_current_push_ref
fi

exit $FAIL
