#!/usr/bin/env bash
# Hermetic tests for resolve_tier1_repo_path (#3127).
# Two-level fixture so $(dirname REPO_ROOT) stays INSIDE the sandbox — never /tmp.
set -uo pipefail

THIS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${THIS}/../.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/lib/tier1-repos.sh" >/dev/null 2>&1 || true

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  ok   %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL %s\n' "$1"; }
eq()   { [[ "$2" == "$3" ]] && ok "$1" || { bad "$1 (got '$2' want '$3')"; }; }

MB="$(mktemp -d)"; trap 'rm -rf "$MB"' EXIT
mkdir -p "$MB/hub"
export REPO_ROOT="$MB/hub"
unset TIER1_REPOS_BASE 2>/dev/null || true

# Initialize each fixture independently, even when invoked from a Git hook.
fixture_git_init() (
    local bindings name
    bindings="$(git rev-parse --local-env-vars)" || return 1
    while IFS= read -r name; do
        unset "$name" || return 1
    done <<< "$bindings"
    git init -q "$1"
)

mkdir -p "$MB/hub/emptyrepo"
fixture_git_init "$MB/hub/nestedrepo"
fixture_git_init "$MB/siblingrepo"

eq "nested layout resolves"   "$(resolve_tier1_repo_path nestedrepo)"  "$MB/hub/nestedrepo"
eq "sibling layout resolves"  "$(resolve_tier1_repo_path siblingrepo)" "$MB/siblingrepo"

resolve_tier1_repo_path emptyrepo >/dev/null 2>&1; [[ $? -eq 1 ]] && ok "marker-less dir rejected" || bad "marker-less dir rejected"
resolve_tier1_repo_path absent    >/dev/null 2>&1; [[ $? -eq 1 ]] && ok "absent everywhere fails closed" || bad "absent everywhere fails closed"

# pyproject.toml is also a valid marker
mkdir -p "$MB/pyrepo"; : > "$MB/pyrepo/pyproject.toml"
eq "pyproject.toml marker resolves" "$(resolve_tier1_repo_path pyrepo)" "$MB/pyrepo"

# explicit TIER1_REPOS_BASE wins
fixture_git_init "$MB/extbase/basedrepo"
TIER1_REPOS_BASE="$MB/extbase" eq "TIER1_REPOS_BASE resolves" "$(TIER1_REPOS_BASE="$MB/extbase" resolve_tier1_repo_path basedrepo)" "$MB/extbase/basedrepo"

# both layouts present -> nested-first + stderr warning
fixture_git_init "$MB/hub/dup"
fixture_git_init "$MB/dup"
eq "both-present picks nested" "$(resolve_tier1_repo_path dup 2>/dev/null)" "$MB/hub/dup"
if resolve_tier1_repo_path dup 2>&1 >/dev/null | grep -q "multiple layouts"; then ok "both-present warns on stderr"; else bad "both-present warns on stderr"; fi

printf '\n[test_tier1_repo_resolver] PASS=%d FAIL=%d\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
