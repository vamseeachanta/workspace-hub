#!/usr/bin/env bash
set -euo pipefail

# Normalize review text into APPROVE|MINOR|MAJOR|NO_OUTPUT|ERROR.

infile="${1:-}"
if [[ -z "$infile" || ! -f "$infile" ]]; then
    echo "Usage: normalize-verdicts.sh <review-file>" >&2
    exit 2
fi

text="$(tr '[:upper:]' '[:lower:]' < "$infile")"

# Prefer explicit verdict headers over free-text mentions in issue sections.
# Ignore template lines that contain option lists (e.g. "APPROVE | REQUEST_CHANGES | REJECT").
verdict_line="$(
    grep -Ei '^(#{1,6}[[:space:]]*)?verdict[[:space:]]*:' "$infile" \
    | tr '[:upper:]' '[:lower:]' \
    | awk '!/\|/{v=$0} END{print v}' \
    || true
)"
if [[ -n "$verdict_line" ]]; then
    case "$verdict_line" in
        *conditional_pass*|*conditional-pass*|*conditional\ pass*)
            echo "CONDITIONAL_PASS"
            exit 0
            ;;
        *request_changes*|*request-changes*|*request\ changes*|*reject*|*major*)
            echo "MAJOR"
            exit 0
            ;;
        *minor*)
            echo "MINOR"
            exit 0
            ;;
        *approve*|*approved*|*pass*)
            echo "APPROVE"
            exit 0
            ;;
        *no_output*|*no\ output*)
            echo "NO_OUTPUT"
            exit 0
            ;;
    esac
fi

# Fallback markers for machine-generated stubs and transport failures.
if grep -Eq '^# codex returned no_output|^# codex review failed|^# codex cli not found' <<< "$text"; then
    echo "NO_OUTPUT"
elif grep -q "conditional.pass\|conditional_pass" <<< "$text"; then
    echo "CONDITIONAL_PASS"
elif grep -Eq '^# (claude|gemini) review failed|timed out' <<< "$text"; then
    echo "NO_OUTPUT"
else
    echo "ERROR"
fi
