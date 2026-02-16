#!/usr/bin/env bash
set -euo pipefail

# Normalize review text into APPROVE|MINOR|MAJOR|NO_OUTPUT|ERROR.

infile="${1:-}"
if [[ -z "$infile" || ! -f "$infile" ]]; then
    echo "Usage: normalize-verdicts.sh <review-file>" >&2
    exit 2
fi

text="$(tr '[:upper:]' '[:lower:]' < "$infile")"

if grep -q "conditional.pass\|conditional_pass" <<< "$text"; then
    echo "CONDITIONAL_PASS"
elif grep -q "no_output\|no output" <<< "$text"; then
    echo "NO_OUTPUT"
elif grep -q "\bmajor\b" <<< "$text"; then
    echo "MAJOR"
elif grep -q "\bminor\b" <<< "$text"; then
    echo "MINOR"
elif grep -q "approve\|approved\|pass" <<< "$text"; then
    echo "APPROVE"
else
    echo "ERROR"
fi
