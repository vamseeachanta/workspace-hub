#!/usr/bin/env bash
# Combined statusline for workspace-hub (#2893).
#
# The project statusLine is the vendored GSD statusline
# (.claude/hooks/gsd-statusline.js), which shows milestone/phase/task but NO
# AI-quota or weekly-reset info. This wrapper runs BOTH the GSD statusline and
# the "usage tail" from statusline-command.sh (the C:|O:|G:|H=O segment with the
# #2992 weekly-reset countdown, plus cost + context) and joins them — so the
# reset countdown is visible while working in workspace-hub.
#
# Why a wrapper and not an edit to gsd-statusline.js: that file is vendored
# (carries a `gsd-hook-version` header) and is overwritten by GSD framework
# bumps, so any edit there would be clobbered. This wrapper is repo-owned and
# survives bumps. The weekly-reset logic lives in exactly one place
# (statusline-command.sh::reset_days) — this only composes, never re-implements.
#
# No `set -e`: a composing wrapper must tolerate either child failing and still
# print something, never a blank statusline.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input=$(cat)

# GSD statusline (base). Tolerate missing node / script error → empty.
gsd=""
if command -v node >/dev/null 2>&1 && [[ -f "$DIR/hooks/gsd-statusline.js" ]]; then
    gsd=$(printf '%s' "$input" | node "$DIR/hooks/gsd-statusline.js" 2>/dev/null) || gsd=""
fi

# Usage tail: quota/reset + cost + context, from the canonical statusline script
# in its --usage-tail segment mode (single source of truth for reset_days).
usage=""
if [[ -f "$DIR/statusline-command.sh" ]]; then
    usage=$(printf '%s' "$input" | bash "$DIR/statusline-command.sh" --usage-tail 2>/dev/null) || usage=""
fi

sep=" │ "
if [[ -n "$gsd" && -n "$usage" ]]; then
    printf '%s%s%s' "$gsd" "$sep" "$usage"
elif [[ -n "$gsd" ]]; then
    printf '%s' "$gsd"
elif [[ -n "$usage" ]]; then
    printf '%s' "$usage"
else
    # Last-resort fallback — never blank the statusline entirely.
    printf '%s' "$(printf '%s' "$input" | jq -r '.model.display_name // "Claude"' 2>/dev/null || echo "Claude")"
fi
