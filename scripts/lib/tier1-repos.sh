#!/usr/bin/env bash
# Single source of truth reader for the tier-1 Python repo list (#3023).
# Source this file to populate the TIER1_PYTHON_REPOS array from
# config/tier1-python-repos.txt — do NOT hardcode the repo list anywhere else.
#
# Usage:
#   source "<path>/scripts/lib/tier1-repos.sh"
#   for repo in "${TIER1_PYTHON_REPOS[@]}"; do ...; done
#
# Resolution order for the canonical file:
#   1. $TIER1_REPOS_FILE (explicit override — used by tests)
#   2. $REPO_ROOT/config/tier1-python-repos.txt (if REPO_ROOT is set)
#   3. derived from this file's own location (lib/ -> repo root)
#   4. git rev-parse --show-toplevel

_tier1_repos_resolve_file() {
    if [[ -n "${TIER1_REPOS_FILE:-}" ]]; then
        printf '%s' "$TIER1_REPOS_FILE"; return
    fi
    if [[ -n "${REPO_ROOT:-}" && -f "${REPO_ROOT}/config/tier1-python-repos.txt" ]]; then
        printf '%s' "${REPO_ROOT}/config/tier1-python-repos.txt"; return
    fi
    local self_dir root
    self_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # scripts/lib
    root="$(cd "${self_dir}/../.." && pwd)"                     # repo root
    if [[ -f "${root}/config/tier1-python-repos.txt" ]]; then
        printf '%s' "${root}/config/tier1-python-repos.txt"; return
    fi
    root="$(git -C "$self_dir" rev-parse --show-toplevel 2>/dev/null)" || root=""
    printf '%s' "${root:+${root}/config/tier1-python-repos.txt}"
}

# Populate TIER1_PYTHON_REPOS as an array of repo slugs.
TIER1_PYTHON_REPOS=()
{
    _t1_file="$(_tier1_repos_resolve_file)"
    if [[ -n "$_t1_file" && -f "$_t1_file" ]]; then
        while IFS= read -r _t1_line || [[ -n "$_t1_line" ]]; do
            _t1_line="${_t1_line%%#*}"                 # strip comments
            _t1_line="${_t1_line//[[:space:]]/}"       # strip all whitespace
            [[ -n "$_t1_line" ]] && TIER1_PYTHON_REPOS+=("$_t1_line")
        done < "$_t1_file"
    fi
    unset _t1_file _t1_line
}

# Fail loudly if the list is empty — a silent empty list would make gates no-op.
if [[ "${#TIER1_PYTHON_REPOS[@]}" -eq 0 ]]; then
    echo "tier1-repos.sh: ERROR — could not read tier-1 repo list (config/tier1-python-repos.txt)" >&2
    return 1 2>/dev/null || exit 1
fi
