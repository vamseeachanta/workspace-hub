#!/usr/bin/env bash
# Check knowledge entries for staleness based on TTL
# Usage: check-staleness.sh [--fix] [--json]
#   --fix   : update last_validated to today for entries you confirm
#   --json  : output as JSON instead of human-readable table
#   (no args): report stale entries to stdout
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
INDEX="$REPO_ROOT/.claude/knowledge/index.json"

FIX=false; JSON_OUT=false
for arg in "$@"; do
  case "$arg" in
    --fix) FIX=true ;; --json) JSON_OUT=true ;;
    *) echo "Unknown flag: $arg" >&2; exit 2 ;;
  esac
done

# Cross-platform date-to-epoch: GNU date -> BSD date -> Python fallback
date_to_epoch() {
  date -d "$1" +%s 2>/dev/null \
    || date -j -f "%Y-%m-%d" "$1" +%s 2>/dev/null \
    || uv run --no-project python -c "import datetime,sys; print(int(datetime.datetime.strptime(sys.argv[1],'%Y-%m-%d').timestamp()))" "$1"
}

TODAY=$(date +%Y-%m-%d); TODAY_EPOCH=$(date_to_epoch "$TODAY")

# Default TTLs by type (days)
default_ttl() {
  case "$1" in
    decision|pattern) echo 365 ;; gotcha|tip) echo 180 ;; *) echo 180 ;;
  esac
}

# Extract ttl_days from YAML frontmatter of a .md file
extract_ttl() {
  [[ -f "$1" ]] && sed -n '/^---$/,/^---$/p' "$1" | grep '^ttl_days:' | head -1 | sed 's/[^0-9]//g' || true
}

# Parse index.json into tab-separated lines
ENTRIES=$(uv run --no-project python - "$INDEX" <<'PY'
import json, sys
with open(sys.argv[1]) as f: data = json.load(f)
for e in data['entries']:
    print('\t'.join([e['id'], e['type'], e['title'], e.get('last_validated',''), e.get('status','active'), e.get('file','')]))
PY
)

STALE_COUNT=0; TABLE_LINES=(); JSON_ITEMS=()

while IFS=$'\t' read -r id etype title validated status file; do
  [[ -z "$id" ]] && continue
  # Determine TTL
  ttl=""
  [[ "$etype" == "resource" && -n "$file" ]] && ttl=$(extract_ttl "$REPO_ROOT/$file")
  [[ -z "$ttl" ]] && ttl=$(default_ttl "$etype")
  # Calculate age in days
  if [[ -n "$validated" ]]; then
    age=$(( (TODAY_EPOCH - $(date_to_epoch "$validated")) / 86400 ))
  else
    age=9999
  fi
  # Staleness label
  if (( age > ttl )); then label="STALE"; STALE_COUNT=$((STALE_COUNT + 1)); else label="OK"; fi
  # Truncate title for display
  short="${title:0:40}"; [[ ${#title} -gt 40 ]] && short="${short:0:37}..."
  TABLE_LINES+=("$(printf "%-9s %-9s %-40s %-12s %4d %4d  %s" "$id" "$etype" "$short" "$validated" "$ttl" "$age" "$label")")
  jtitle=$(uv run --no-project python -c "import json,sys;print(json.dumps(sys.argv[1]))" "$title")
  JSON_ITEMS+=("{\"id\":\"$id\",\"type\":\"$etype\",\"title\":$jtitle,\"last_validated\":\"$validated\",\"ttl_days\":$ttl,\"age_days\":$age,\"status\":\"$label\"}")
  # --fix: prompt to revalidate stale entries
  if $FIX && [[ "$label" == "STALE" ]]; then
    read -rp "Revalidate $id ($short)? [y/N] " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
      sed -i.bak "s/last_validated:.*/last_validated: \"$TODAY\"/" "$REPO_ROOT/$file"
      rm -f "$REPO_ROOT/$file.bak"
      uv run --no-project python - "$INDEX" "$id" "$TODAY" <<'PY'
import json, sys
index_path, entry_id, today = sys.argv[1], sys.argv[2], sys.argv[3]
with open(index_path) as f: data = json.load(f)
for e in data['entries']:
    if e['id'] == entry_id: e['last_validated'] = today
with open(index_path, 'w') as f: json.dump(data, f, indent=2); f.write('\n')
PY
      echo "  -> $id revalidated to $TODAY"
    fi
  fi
done <<< "$ENTRIES"

# Output results
if $JSON_OUT; then
  echo "["
  for i in "${!JSON_ITEMS[@]}"; do
    sep=","; (( i == ${#JSON_ITEMS[@]} - 1 )) && sep=""
    echo "  ${JSON_ITEMS[$i]}$sep"
  done
  echo "]"
else
  printf "%-9s %-9s %-40s %-12s %4s %4s  %s\n" "ID" "TYPE" "TITLE" "VALIDATED" "TTL" "AGE" "STATUS"
  printf '%0.s-' {1..90}; echo
  for line in "${TABLE_LINES[@]}"; do echo "$line"; done
  echo ""; echo "Total: ${#TABLE_LINES[@]} entries, $STALE_COUNT stale"
fi

# Exit code: 1 if any stale entries found
(( STALE_COUNT > 0 )) && exit 1
exit 0
