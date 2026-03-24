#!/usr/bin/env bash
# check-acs-pass.sh WRK-NNN [--queue-dir <path>]
# Verify all acceptance criteria in a WRK file are marked [x].
# Exit 0: all ACs complete (or no AC section — with warning)
# Exit 1: incomplete ACs found (lists them)
# Exit 2: WRK file not found
set -euo pipefail

WRK_ID="${1:?Usage: check-acs-pass.sh WRK-NNN [--queue-dir <path>]}"
shift

# Parse optional --queue-dir
QUEUE_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --queue-dir) QUEUE_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$QUEUE_DIR" ]]; then
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
  QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
fi

# Find WRK file across queue directories
WRK_FILE=""
for dir in working pending blocked; do
  candidate="$QUEUE_DIR/$dir/${WRK_ID}.md"
  if [[ -f "$candidate" ]]; then
    WRK_FILE="$candidate"
    break
  fi
done

if [[ -z "$WRK_FILE" ]]; then
  echo "ERROR: ${WRK_ID} not found in working/pending/blocked" >&2
  exit 2
fi

# Extract lines after "## Acceptance Criteria" until next heading or EOF
in_ac=false
incomplete=()
complete_count=0

while IFS= read -r line; do
  if [[ "$line" =~ ^##[[:space:]]+Acceptance[[:space:]]+Criteria ]]; then
    in_ac=true
    continue
  fi
  if $in_ac && [[ "$line" =~ ^## ]]; then
    break
  fi
  if $in_ac; then
    if [[ "$line" =~ ^-[[:space:]]+\[x\] ]]; then
      complete_count=$((complete_count + 1))
    elif [[ "$line" =~ ^-[[:space:]]+\[[[:space:]]\] ]]; then
      # Strip the checkbox prefix to get the AC text
      ac_text="${line#*] }"
      incomplete+=("$ac_text")
    fi
  fi
done < "$WRK_FILE"

total=$(( complete_count + ${#incomplete[@]} ))

if [[ "$total" -eq 0 ]]; then
  echo "WARNING: No acceptance criteria found in ${WRK_ID} (warning: no AC section)" >&2
  exit 0
fi

if [[ ${#incomplete[@]} -eq 0 ]]; then
  echo "OK: All $complete_count ACs complete in ${WRK_ID}"
  exit 0
fi

echo "INCOMPLETE: ${#incomplete[@]} of $total ACs not done in ${WRK_ID}:" >&2
for ac in "${incomplete[@]}"; do
  echo "  - [ ] $ac" >&2
done
exit 1
