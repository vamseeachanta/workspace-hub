#!/usr/bin/env bash
# Shared read-only GitHub helpers. Issue #1308 requires repo and auth discovery.
# Bash exit conventions: success=0, failure=1, incorrect usage=2.

github_error() {
    printf 'Error: %s\n' "$*" >&2
    return 1
}

github_require_tool() {
    if ! command -v "$1" >/dev/null 2>&1; then
        github_error "Required tool '$1' is missing; install it and retry."
        return 1
    fi
}

github_read_pr() {
    local repository payload
    local -a selection=("$@")
    local fields='number,state,statusCheckRollup,reviewDecision,reviewRequests,reviews'

    github_require_tool gh || return 1
    # Suppress upstream diagnostics: they may contain sensitive context.
    if ! gh auth status >/dev/null 2>&1; then
        github_error 'GitHub authentication is unavailable; run gh auth login and retry.'
        return 1
    fi
    if ! repository=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null) ||
        [[ ! "$repository" =~ ^[^[:space:]/]+/[^[:space:]/]+$ ]]; then
        github_error 'Cannot detect the repository; run from a GitHub checkout and retry.'
        return 1
    fi
    # An empty selection lets gh resolve the PR for the current branch.
    if ! payload=$(gh pr view "${selection[@]}" --repo "$repository" --json "$fields" 2>/dev/null); then
        github_error 'Cannot read the PR; check its number, current branch and repository access, then retry.'
        return 1
    fi
    printf '%s\n' "$payload"
}
