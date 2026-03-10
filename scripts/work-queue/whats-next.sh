#!/usr/bin/env bash
# whats-next.sh — Refresh and display the prioritised "run now" work list.
# Scans pending/working/blocked WRK items, resolves blocker archive status,
# and outputs a categorised table with parallel execution hints.
# Usage: bash scripts/work-queue/whats-next.sh [--category <name>]

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
FILTER_CATEGORY="harness"   # default: harness-focused view
SHOW_ALL=false
MED_LIMIT=20
while [[ $# -gt 0 ]]; do
  case "$1" in
    --category)  FILTER_CATEGORY="$2"; shift 2 ;;
    --all)       SHOW_ALL=true; FILTER_CATEGORY=""; shift ;;
    --limit)     MED_LIMIT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

get_field() { grep -m1 "^$2:" "$1" 2>/dev/null | sed "s/^$2: *//" | tr -d '"' || true; }

is_archived() {
  local num="$1"
  find "$QUEUE_DIR/archive" -name "WRK-${num}.md" 2>/dev/null | grep -qc . 2>/dev/null
  return $?
}

# Returns 0 if all blockers are archived (or list is empty), 1 otherwise.
# Writes active (unresolved) blockers to stdout when returning 1.
check_blockers() {
  local raw="$1"
  local ids active=""
  ids=$(echo "$raw" | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' || true)
  while IFS= read -r dep; do
    [[ -z "$dep" ]] && continue
    local num; num=$(echo "$dep" | grep -oE '[0-9]+' || true)
    [[ -z "$num" ]] && continue
    if ! is_archived "$num" 2>/dev/null; then
      active="$active,$dep"
    fi
  done <<< "$ids"
  active="${active#,}"
  if [[ -z "$active" ]]; then
    echo "clear"
    return 0
  else
    echo "active:$active"
    return 1
  fi
}

declare -a WORKING_ITEMS NEWLY_UNBLOCKED HIGH_UNBLOCKED MED_UNBLOCKED EXT_BLOCKED

process_file() {
  local f="$1" loc="$2"
  local id status priority subcategory category blocked_by computer title

  id=$(get_field "$f" "id"); [[ -z "$id" ]] && return
  category=$(get_field "$f" "category")
  [[ -n "$FILTER_CATEGORY" && "$category" != *"$FILTER_CATEGORY"* ]] && return

  status=$(get_field "$f" "status")
  priority=$(get_field "$f" "priority")
  subcategory=$(get_field "$f" "subcategory")
  computer=$(get_field "$f" "computer")
  title=$(get_field "$f" "title" | cut -c1-48)
  blocked_by=$(grep -m1 "^blocked_by:" "$f" 2>/dev/null | sed 's/^blocked_by: *//' || echo "[]")

  local row="$id|$priority|$subcategory|$computer|$title"

  if [[ "$loc" == "working" ]]; then
    WORKING_ITEMS+=("$row"); return
  fi

  local bstatus
  bstatus=$(check_blockers "$blocked_by") || true

  if [[ "$status" == "blocked" ]]; then
    EXT_BLOCKED+=("$row|${bstatus#active:}"); return
  fi

  if [[ "$bstatus" == "clear" ]]; then
    # Was it previously blocked (had WRK deps that are now cleared)?
    local raw_ids
    raw_ids=$(echo "$blocked_by" | tr -d '[]' | tr -d ' ' | grep -v '^$' || true)
    if [[ "$priority" == "high" ]]; then
      HIGH_UNBLOCKED+=("$row")
    elif [[ -n "$raw_ids" ]]; then
      NEWLY_UNBLOCKED+=("$row")
    else
      MED_UNBLOCKED+=("$row")
    fi
  fi
}

for f in "$QUEUE_DIR/working"/*.md;  do [[ -f "$f" ]] && process_file "$f" working;  done
for f in "$QUEUE_DIR/pending"/*.md;  do [[ -f "$f" ]] && process_file "$f" pending;  done
for f in "$QUEUE_DIR/blocked"/*.md;  do [[ -f "$f" ]] && process_file "$f" blocked;  done

# ── Render ────────────────────────────────────────────────────────────────────

HR=$(printf '%0.s─' {1..88})

print_section() {
  local label="$1" colour="$2" arr_name="$3"
  local -n _arr="$arr_name"
  [[ ${#_arr[@]} -eq 0 ]] && return
  echo ""
  printf "${colour}%s\033[0m\n" "$label"
  printf "%-12s %-8s %-26s %-15s %s\n" "WRK" "PRI" "SUBCATEGORY" "MACHINE" "TITLE"
  echo "$HR"
  for row in "${_arr[@]}"; do
    IFS='|' read -r id pri sub cpu ttl _rest <<< "$row"
    printf "%-12s %-8s %-26s %-15s %s\n" "$id" "$pri" "$sub" "$cpu" "$ttl"
  done
}

echo ""
scope_label="${FILTER_CATEGORY:-all categories}"
echo "\033[1m╔══════════════════════════════════════════════╗\033[0m"
printf "\033[1m║   WHAT'S NEXT  %-30s║\033[0m\n" "$(date '+%Y-%m-%d %H:%M')     "
printf "\033[1m║   scope: %-36s║\033[0m\n" "$scope_label"
echo "\033[1m╚══════════════════════════════════════════════╝\033[0m"

print_section "▶  WORKING — in progress"              "\033[36m" WORKING_ITEMS
print_section "★  HIGH PRIORITY — ready to start"     "\033[32m" HIGH_UNBLOCKED
print_section "↑  NEWLY UNBLOCKED — blockers cleared" "\033[33m" NEWLY_UNBLOCKED
# Cap medium section
if [[ ${#MED_UNBLOCKED[@]} -gt $MED_LIMIT ]]; then
  MED_DISPLAY=("${MED_UNBLOCKED[@]:0:$MED_LIMIT}")
  MED_OVERFLOW=$(( ${#MED_UNBLOCKED[@]} - MED_LIMIT ))
else
  MED_DISPLAY=("${MED_UNBLOCKED[@]}")
  MED_OVERFLOW=0
fi
print_section "·  MEDIUM — ready"                     "\033[0m"  MED_DISPLAY
[[ $MED_OVERFLOW -gt 0 ]] && echo "  … and $MED_OVERFLOW more (use --limit N or --category to narrow)"

if [[ ${#EXT_BLOCKED[@]} -gt 0 ]]; then
  echo ""; printf "\033[31m%s\033[0m\n" "✗  EXTERNALLY BLOCKED"
  printf "%-12s %-26s %s\n" "WRK" "SUBCATEGORY" "BLOCKED BY"
  echo "$HR"
  for row in "${EXT_BLOCKED[@]}"; do
    IFS='|' read -r id _pri sub _cpu _ttl reason <<< "$row"
    display_reason="$reason"
    [[ "$display_reason" == "clear" || -z "$display_reason" ]] && display_reason="external (no WRK deps)"
    printf "%-12s %-26s %s\n" "$id" "$sub" "$display_reason"
  done
fi

# ── Parallel hints ────────────────────────────────────────────────────────────
echo ""; echo "\033[1m── Parallel hints ──\033[0m"

declare -A machine_map
for row in "${HIGH_UNBLOCKED[@]}" "${NEWLY_UNBLOCKED[@]}"; do
  IFS='|' read -r id _pri _sub cpu _ttl <<< "$row"
  [[ -n "$cpu" ]] && machine_map["$cpu"]+="$id "
done

if [[ ${#machine_map[@]} -gt 1 ]]; then
  echo "Items on different machines — safe to run in parallel:"
  for m in "${!machine_map[@]}"; do printf "  %-18s %s\n" "$m" "${machine_map[$m]}"; done
else
  all_ready=()
  for row in "${HIGH_UNBLOCKED[@]}" "${NEWLY_UNBLOCKED[@]}"; do
    IFS='|' read -r id _ <<< "$row"; all_ready+=("$id")
  done
  if [[ ${#all_ready[@]} -ge 2 ]]; then
    echo "Top ready: ${all_ready[*]:0:4} — verify target_repos before running in parallel"
  else
    echo "No parallel opportunities detected in current ready set."
  fi
fi

echo ""
echo "Summary: \033[36m${#WORKING_ITEMS[@]} working\033[0m · \033[32m${#HIGH_UNBLOCKED[@]} high ready\033[0m · \033[33m${#NEWLY_UNBLOCKED[@]} newly unblocked\033[0m · ${#MED_UNBLOCKED[@]} medium · \033[31m${#EXT_BLOCKED[@]} blocked\033[0m"
echo ""
