#!/usr/bin/env bash
set -euo pipefail

# Classify a review artifact as VALID | NO_OUTPUT | INVALID_OUTPUT | ERROR.

infile="${1:-}"
if [[ -z "$infile" || ! -f "$infile" ]]; then
    echo "ERROR"
    exit 2
fi

size="$(wc -c < "$infile" | tr -d ' ')"
if [[ -z "$size" || "$size" -eq 0 ]]; then
    echo "NO_OUTPUT"
    exit 0
fi

text="$(tr '[:upper:]' '[:lower:]' < "$infile")"

if grep -Eq '^# (claude|codex|gemini).*(failed|not found)|timed out|no_output' <<< "$text"; then
    echo "NO_OUTPUT"
    exit 0
fi

has_verdict="$(
    grep -Ei '^(#{1,6}[[:space:]]*)?verdict[[:space:]]*:' "$infile" \
    | awk '!/\|/{print; found=1} END{exit(found?0:1)}' 2>/dev/null || true
)"

missing=0
for section in "summary" "issues found" "suggestions" "questions for author"; do
    if ! grep -Eiq "^#{1,6}[[:space:]]*${section}" "$infile"; then
        missing=$((missing + 1))
    fi
done

if [[ -n "$has_verdict" && "$missing" -eq 0 ]]; then
    echo "VALID"
    exit 0
fi

echo "INVALID_OUTPUT"
