#!/usr/bin/env bash
# attest-plan-claims.sh — independently verify a plan's cited issues and file paths
# and emit a "## Attested Evidence" block for cross-review dispatchers (#2405).
#
# Usage: attest-plan-claims.sh <plan-file-under-docs-plans>
#
# Env:
#   SOURCE_DATE_EPOCH   If set, used as the attestation timestamp source
#                       (reproducibility aid — matches widely-used convention).
set -euo pipefail

PLAN_FILE="${1:-}"

# Single allowlist definition — match kept identical in Deliverable text, Threat Model,
# and this script (see v3 plan). Subdirectories under docs/plans/ are out of scope.
ALLOWLIST_REGEX='^docs/plans/[^/]+\.md$'

[[ "$PLAN_FILE" =~ $ALLOWLIST_REGEX ]] || { echo "ERROR: plan path outside allowlist" >&2; exit 1; }
[[ -f "$PLAN_FILE" ]] || { echo "ERROR: plan not found" >&2; exit 1; }

# Preserve full extraction lists so budget-exhaustion counts are correct (v3 Gemini fix).
# \b anchor guards against false matches inside longer digit strings like #9999999
# (v3-plan regex `#[0-9]{3,5}` without \b would mis-extract that as #99999).
ALL_ISSUES=$(grep -oE '#[0-9]{3,5}\b' "$PLAN_FILE" | sort -u || true)
ALL_PATHS=$(grep -oE '`[a-zA-Z0-9._/\-]+\.(py|md|yaml|yml|sh|json|toml)`' "$PLAN_FILE" \
  | sed 's/`//g' | sort -u || true)

ISSUE_COUNT_FULL=$(printf '%s\n' "$ALL_ISSUES" | grep -c . || true)
PATH_COUNT_FULL=$(printf '%s\n' "$ALL_PATHS" | grep -c . || true)

ISSUE_NUMBERS=$(printf '%s\n' "$ALL_ISSUES" | head -20)
FILE_PATHS=$(printf '%s\n' "$ALL_PATHS" | head -40)

if [[ -n "${SOURCE_DATE_EPOCH:-}" ]]; then
  TS=$(date -u -d "@${SOURCE_DATE_EPOCH}" +%Y-%m-%dT%H:%M:%SZ)
else
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
fi
COMMIT=$(git rev-parse HEAD)

PAYLOAD=$(cat <<EOF
## Attested Evidence (verified ${TS} at repo commit ${COMMIT})

**Issue states** (via \`gh issue view --json number,state,title\` — title+state only, no body):
$(for n in $ISSUE_NUMBERS; do
    num="${n#\#}"
    gh issue view "$num" --json number,state,title --jq '"- #\(.number) \(.state) \(.title)"' 2>/dev/null \
      || echo "- $n (gh-lookup-failed or private)"
  done)$([ "$ISSUE_COUNT_FULL" -gt 20 ] && printf '\n_(%d citations in plan; first 20 shown; remainder skipped: budget exhausted)_' "$ISSUE_COUNT_FULL" || true)

**File existence** (via \`ls -la -- "\$f"\` with flag-injection guard):
$(for f in $FILE_PATHS; do
    if [[ -L "$f" ]]; then
      target=$(readlink -- "$f")
      ls_out=$(ls -la -- "$f" 2>&1 | head -1)
      echo "- SYMLINK: $f -> $target  ($ls_out)"
    elif [[ -e "$f" ]]; then
      ls_out=$(ls -la -- "$f" 2>&1 | head -1)
      echo "- EXISTS: $f  ($ls_out)"
    else
      echo "- MISSING: $f"
    fi
  done)$([ "$PATH_COUNT_FULL" -gt 40 ] && printf '\n_(%d paths in plan; first 40 shown; remainder skipped: budget exhausted)_' "$PATH_COUNT_FULL" || true)
EOF
)

# SHA of PAYLOAD text exactly (no trailing newline) — v3 Identity Contract.
# Plan pseudocode wrote "$PAYLOAD_SHA_" which bash parses as $PAYLOAD_SHA_ (undefined under
# set -u); we use ${PAYLOAD_SHA}_ to close the variable name before the literal underscore.
PAYLOAD_SHA=$(printf '%s' "$PAYLOAD" | sha256sum | awk '{print $1}')

printf '%s\n' "$PAYLOAD"
echo ""
echo "_Attestation payload sha256: ${PAYLOAD_SHA}_"
