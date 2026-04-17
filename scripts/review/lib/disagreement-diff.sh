#!/usr/bin/env bash
# disagreement-diff.sh — summarize verdict + per-provider unique findings
# across the per-provider artifacts produced by plan-review-fanout.sh.
#
# Usage: disagreement-diff.sh <results-dir> <date> <issue-num>
# Reads files matching <results-dir>/<date>-plan-<issue-num>-<provider>.md and
# writes a markdown report on stdout.

set -euo pipefail

RESULTS_DIR="${1:?results-dir required}"
DATE="${2:?date required}"
ISSUE="${3:?issue-num required}"

# Extract the verdict line (first non-empty line under ## Verdict).
extract_verdict() {
  local file="$1"
  awk '
    /^## Verdict/ { in_verdict=1; next }
    in_verdict && /^## / { exit }
    in_verdict && NF { print; exit }
  ' "$file"
}

# Extract the findings block (content between ## Findings and the next ## heading).
extract_findings() {
  local file="$1"
  awk '
    /^## Findings/ { in_findings=1; next }
    in_findings && /^## / { in_findings=0 }
    in_findings { print }
  ' "$file"
}

# ── Collect artifacts ────────────────────────────────────────────────────
declare -a PROVIDERS=()
declare -A VERDICTS=()
declare -A FINDINGS=()

for file in "$RESULTS_DIR/$DATE-plan-$ISSUE-"*.md; do
  [[ -e "$file" ]] || continue
  local_base="$(basename "$file" .md)"
  # Skip the disagreement file itself.
  [[ "$local_base" == *-disagreement ]] && continue
  # Extract the trailing <provider> token.
  prov="${local_base##*-plan-$ISSUE-}"
  PROVIDERS+=("$prov")
  VERDICTS[$prov]="$(extract_verdict "$file")"
  FINDINGS[$prov]="$(extract_findings "$file")"
done

# ── Emit markdown ────────────────────────────────────────────────────────
echo "# Disagreement report — plan #${ISSUE} (${DATE})"
echo ""
echo "## Verdicts"
echo ""
echo "| Provider | Verdict |"
echo "|---|---|"
for prov in "${PROVIDERS[@]}"; do
  echo "| $prov | ${VERDICTS[$prov]:-UNKNOWN} |"
done
echo ""

echo "## Findings unique to each provider"
echo ""
echo "A finding is 'unique to X' if its text appears in X's artifact but not"
echo "verbatim in any other provider's artifact."
echo ""

for prov in "${PROVIDERS[@]}"; do
  echo "### ${prov}"
  echo ""
  # Build an \"others\" blob of concatenated findings excluding this provider.
  others_blob=""
  for other in "${PROVIDERS[@]}"; do
    [[ "$other" == "$prov" ]] && continue
    others_blob+="${FINDINGS[$other]}"$'\n'
  done
  # For each non-empty line in this provider's findings, check presence in others_blob.
  found_any=0
  while IFS= read -r line; do
    [[ -z "${line// }" ]] && continue
    # Strip leading list markers and surrounding whitespace for a lenient match.
    stripped="$(echo "$line" | sed -E 's/^[[:space:]]*(-|[0-9]+\.)[[:space:]]*//')"
    if [[ -z "${stripped// }" ]]; then continue; fi
    if ! grep -qF -- "$stripped" <<<"$others_blob"; then
      echo "- $stripped"
      found_any=1
    fi
  done <<<"${FINDINGS[$prov]}"
  (( found_any == 0 )) && echo "(no findings unique to this provider)"
  echo ""
done
