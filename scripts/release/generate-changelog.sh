#!/usr/bin/env bash
set -euo pipefail

# generate-changelog.sh <repo-path> <version> <since-ref>
# Emits a Keep-a-Changelog formatted block for conventional commits
# in the range <since-ref>..HEAD of the given repo.

usage() {
    echo "Usage: $0 <repo-path> <version> <since-ref>" >&2
    exit 1
}

[[ $# -lt 3 ]] && usage

REPO_PATH="$1"
VERSION="$2"
SINCE_REF="$3"
TODAY="$(date +%Y-%m-%d)"

# Collect commits in range
mapfile -t commits < <(git -C "$REPO_PATH" log \
    --pretty=format:"%s" "${SINCE_REF}..HEAD" 2>/dev/null || true)

declare -a feats=()
declare -a fixes=()
declare -a docs=()
declare -a others=()

for msg in "${commits[@]}"; do
    # Strip trailing whitespace
    msg="${msg%$'\r'}"
    [[ -z "$msg" ]] && continue

    prefix="${msg%%:*}"
    # Extract body after "type: " or "type(scope): "
    body="${msg#*: }"

    case "$prefix" in
        feat|feat\(*\))
            feats+=("$body") ;;
        fix|fix\(*\))
            fixes+=("$body") ;;
        docs|docs\(*\))
            docs+=("$body") ;;
        refactor|refactor\(*\)|test|test\(*\)|perf|perf\(*\)|chore|chore\(*\))
            others+=("$body") ;;
        *)
            # Non-conventional commit: include in Others
            others+=("$msg") ;;
    esac
done

echo "## [${VERSION}] - ${TODAY}"
echo ""

if [[ ${#feats[@]} -eq 0 && ${#fixes[@]} -eq 0 && ${#docs[@]} -eq 0 && ${#others[@]} -eq 0 ]]; then
    echo "### Other"
    echo "- (no notable changes)"
    exit 0
fi

if [[ ${#feats[@]} -gt 0 ]]; then
    echo "### Features"
    for item in "${feats[@]}"; do
        echo "- ${item}"
    done
    echo ""
fi

if [[ ${#fixes[@]} -gt 0 ]]; then
    echo "### Bug Fixes"
    for item in "${fixes[@]}"; do
        echo "- ${item}"
    done
    echo ""
fi

if [[ ${#docs[@]} -gt 0 ]]; then
    echo "### Documentation"
    for item in "${docs[@]}"; do
        echo "- ${item}"
    done
    echo ""
fi

if [[ ${#others[@]} -gt 0 ]]; then
    echo "### Other"
    for item in "${others[@]}"; do
        echo "- ${item}"
    done
    echo ""
fi
