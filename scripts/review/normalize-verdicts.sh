#!/usr/bin/env bash
set -euo pipefail

# Normalize review text into APPROVE|MINOR|MAJOR|NO_OUTPUT|INVALID_OUTPUT|ERROR.

infile="${1:-}"
if [[ -z "$infile" || ! -f "$infile" ]]; then
    echo "Usage: normalize-verdicts.sh <review-file>" >&2
    exit 2
fi

text="$(tr '[:upper:]' '[:lower:]' < "$infile")"
trimmed_text="$(tr -d '[:space:]' <<< "$text")"
if [[ -z "$trimmed_text" ]]; then
    echo "ERROR"
    exit 0
fi

# Prefer explicit verdict headers over free-text mentions in issue sections.
# Ignore template lines that contain option lists (e.g. "APPROVE | REQUEST_CHANGES | REJECT").
verdict_line="$(
    grep -Ei '^(#{1,6}[[:space:]]*)?verdict[[:space:]]*:' "$infile" \
    | tr '[:upper:]' '[:lower:]' \
    | awk '!/\|/{v=$0} END{print v}' \
    || true
)"
if [[ -n "$verdict_line" ]]; then
    issues_text="$(grep -Ei '\[p[123]\]' "$infile" | tr '[:upper:]' '[:lower:]' || true)"
    if [[ "$verdict_line" == *request_changes* || "$verdict_line" == *request-changes* || "$verdict_line" == *request\ changes* ]]; then
        if grep -q '\[p1\]\|\[p2\]' <<< "$issues_text"; then
            echo "MAJOR"
            exit 0
        elif grep -q '\[p3\]' <<< "$issues_text"; then
            echo "MINOR"
            exit 0
        fi
    fi
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
    validation="$("$(cd "$(dirname "$0")" && pwd)/validate-review-output.sh" "$infile" 2>/dev/null || echo "ERROR")"
    if [[ "$validation" == "INVALID_OUTPUT" ]]; then
        echo "INVALID_OUTPUT"
    elif [[ "$validation" == "NO_OUTPUT" ]]; then
        echo "NO_OUTPUT"
    else
        echo "ERROR"
    fi
fi
