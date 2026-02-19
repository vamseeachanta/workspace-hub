#!/usr/bin/env bash
# check-commit-msg.sh — Enforce WRK-NNN reference in feat/fix/refactor commits
# Install: git config core.hooksPath .claude/hooks
# Or copy to: .git/hooks/commit-msg

MSG_FILE="$1"
[[ -z "$MSG_FILE" ]] && exit 0
msg=$(cat "$MSG_FILE" 2>/dev/null || true)

# Extract conventional commit type
type=$(echo "$msg" | grep -oE '^[a-z]+' | head -1)

# Types that never need a WRK reference
EXEMPT_TYPES="chore|style|merge|revert|wip|ci|build"
if echo "${type:-}" | grep -qE "^($EXEMPT_TYPES)$"; then
    exit 0
fi

# Merge commits (start with "Merge ")
if echo "$msg" | grep -qE '^Merge '; then
    exit 0
fi

# Check for WRK-NNN anywhere in the message
if echo "$msg" | grep -qE 'WRK-[0-9]+'; then
    exit 0
fi

# docs: warn only (don't block)
if [[ "${type:-}" == "docs" ]]; then
    echo "Warning: docs commit without WRK-NNN reference (non-blocking)" >&2
    exit 0
fi

# test: warn only (test-only changes may not have a direct WRK item)
if [[ "${type:-}" == "test" ]]; then
    echo "Warning: test commit without WRK-NNN reference (non-blocking)" >&2
    exit 0
fi

# feat, fix, refactor, perf — block without WRK ref
echo "Error: '${type:-unknown}' commit requires WRK-NNN reference" >&2
echo "  Format: ${type:-feat}(scope): WRK-NNN — description" >&2
echo "  Add 'WRK-NNN' anywhere in the commit message to pass this check." >&2
echo "  To skip enforcement: use 'chore:' prefix for housekeeping commits." >&2
exit 1
