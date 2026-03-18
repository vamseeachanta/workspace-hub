#!/usr/bin/env bash
# whats-next.sh — Refresh and display the prioritised "run now" work list.
# Scans pending/working/blocked WRK items, resolves blocker archive status,
# and outputs a categorised table with parallel execution hints.
# Usage: bash scripts/work-queue/whats-next.sh [--category <name>] [--subcategory <name>]

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
THIS_HOST=$(hostname -s)
FILTER_CATEGORY="harness"   # default: harness-focused view
FILTER_SUBCATEGORY=""
SHOW_ALL=false
MED_LIMIT=20
_CATEGORY_EXPLICIT=false
_DEBUG=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --category)     FILTER_CATEGORY="$2"; _CATEGORY_EXPLICIT=true; shift 2 ;;
    --subcategory)  FILTER_SUBCATEGORY="$2"; shift 2 ;;
    --all)          SHOW_ALL=true; FILTER_CATEGORY=""; shift ;;
    --limit)        MED_LIMIT="$2"; shift 2 ;;
    --debug)        _DEBUG=true; shift ;;
    *) shift ;;
  esac
done
# --subcategory alone clears the default category filter (cross-category search)
[[ -n "$FILTER_SUBCATEGORY" && "$_CATEGORY_EXPLICIT" == false ]] && FILTER_CATEGORY=""

get_field() { grep -m1 "^$2:" "$1" 2>/dev/null | sed "s/^$2: *//" | tr -d '"' || true; }

read_index_status() {
  # Returns status from wrk-status-index.json, or empty string if absent.
  local _id="$1"
  local _idx="${QUEUE_DIR}/wrk-status-index.json"
  [[ -f "$_idx" ]] || return
  python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(d.get(sys.argv[2], {}).get('status', ''))
except Exception:
    pass
" "$_idx" "$_id" 2>/dev/null
}

is_archived() {
  local num="$1"
  find "$QUEUE_DIR/archive" "$QUEUE_DIR/archived" -name "WRK-${num}.md" 2>/dev/null | grep -qc . 2>/dev/null
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

has_recent_session_lock() {
  local wrk_id="$1"
  local lock="$QUEUE_DIR/assets/$wrk_id/evidence/session-lock.yaml"
  [[ ! -f "$lock" ]] && return 1
  local locked_at
  locked_at=$(get_field "$lock" "locked_at")
  [[ -z "$locked_at" ]] && return 1
  local now lock_ts age
  now=$(date +%s)
  lock_ts=$(date -d "$locked_at" +%s 2>/dev/null) || return 1
  age=$(( now - lock_ts ))
  # Reject future-dated locks (clock skew) and stale locks (>2h)
  [[ $age -gt -86400 && $age -lt 7200 ]]
}

# Returns current_stage from checkpoint.yaml (empty string if no checkpoint).
get_checkpoint_stage() {
  local wrk_id="$1"
  local cp="$QUEUE_DIR/assets/$wrk_id/checkpoint.yaml"
  [[ ! -f "$cp" ]] && return
  get_field "$cp" "current_stage"
}

# Returns session_pid from evidence/session-lock.yaml (empty if absent/missing field).
get_session_pid() {
  local wrk_id="$1"
  local lock="$QUEUE_DIR/assets/$wrk_id/evidence/session-lock.yaml"
  [[ ! -f "$lock" ]] && return
  get_field "$lock" "session_pid"
}

# Maps stage number → Status label: WAITING (hard gates 1/5/7/17) / START / READY (no stage).
derive_status() {
  local stage="$1"
  [[ -z "$stage" ]] && echo "READY" && return
  case "$stage" in 1|5|7|17) echo "WAITING" ;; *) echo "START" ;; esac
}

declare -a WORKING_ITEMS WORKING_PARKED UNCLAIMED_ACTIVE NEWLY_UNBLOCKED HIGH_UNBLOCKED MED_UNBLOCKED EXT_BLOCKED COORDINATING_ITEMS
declare -A WRK_NOTES WRK_NOT_BEFORE WRK_URGENCY

# ── Pre-compute urgency scores (single Python call) ──────────────────
_urgency_json=$(uv run --no-project python "$REPO_ROOT/scripts/work-queue/urgency_score.py" --all --json --queue-dir "$QUEUE_DIR" 2>/dev/null || echo "[]")
while IFS='	' read -r _uid _uscore; do
  [[ -n "$_uid" ]] && WRK_URGENCY["$_uid"]="$_uscore"
done < <(python3 -c "
import json, sys
for item in json.loads(sys.argv[1]):
    print(item['id'] + '\t' + str(item['score']))
" "$_urgency_json" 2>/dev/null)

process_file() {
  local f="$1" loc="$2"
  local id status priority subcategory category blocked_by computer title

  id=$(get_field "$f" "id"); [[ -z "$id" ]] && return
  status=$(get_field "$f" "status")
  local wrk_type_early
  wrk_type_early=$(get_field "$f" "type")
  # Coordinating feature WRKs bypass category/subcategory filters so they always appear
  if [[ "$status" != "coordinating" || "$wrk_type_early" != "feature" ]]; then
    category=$(get_field "$f" "category")
    [[ -n "$FILTER_CATEGORY" && "$category" != *"$FILTER_CATEGORY"* ]] && return
    subcategory=$(get_field "$f" "subcategory")
    [[ -n "$FILTER_SUBCATEGORY" && "$subcategory" != *"$FILTER_SUBCATEGORY"* ]] && return
  fi
  category=${category:-$(get_field "$f" "category")}
  subcategory=${subcategory:-$(get_field "$f" "subcategory")}
  priority=$(get_field "$f" "priority")
  computer=$(get_field "$f" "computer")
  title=$(get_field "$f" "title" | cut -c1-48)
  local _idx_status _idx_source
  _idx_status=$(read_index_status "$id")
  _idx_source="scan"
  [[ -n "$_idx_status" ]] && _idx_source="index"
  [[ "$_DEBUG" == "true" ]] && title="${title} (${_idx_source})"
  if [[ -n "$_idx_status" ]]; then
    status="$_idx_status"   # index is primary source
  fi
  blocked_by=$(grep -m1 "^blocked_by:" "$f" 2>/dev/null | sed 's/^blocked_by: *//' || echo "[]")

  local cp_stage item_status item_pid note not_before
  cp_stage=$(get_checkpoint_stage "$id")
  item_status=$(derive_status "$cp_stage")
  item_pid=$(get_session_pid "$id")
  note=$(get_field "$f" "note")
  not_before=$(get_field "$f" "not_before")
  WRK_NOTES["$id"]="$note"
  WRK_NOT_BEFORE["$id"]="$not_before"
  local row="$id|$priority|$subcategory|$computer|$title|$cp_stage|$item_status|$item_pid"

  if [[ "$loc" == "working" ]]; then
    local wrk_type
    wrk_type=$(get_field "$f" "type")
    if [[ "$status" == "coordinating" && "$wrk_type" == "feature" ]]; then
      # Count child progress
      local children_raw total_children archived_children pending_children done_children
      children_raw=$(grep -m1 "^children:" "$f" 2>/dev/null | sed 's/^children: *//' | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' || true)
      total_children=0; archived_children=0; pending_children=0; done_children=0
      while IFS= read -r child; do
        [[ -z "$child" ]] && continue
        (( total_children++ ))
        local cnum; cnum=$(echo "$child" | grep -oE '[0-9]+' || true)
        if is_archived "$cnum" 2>/dev/null; then
          (( archived_children++ ))
        elif find "$QUEUE_DIR/working" -name "${child}.md" 2>/dev/null | grep -qc .; then
          (( pending_children++ ))  # working = in progress, counted as pending for simplicity
        else
          (( pending_children++ ))
        fi
      done <<< "$children_raw"
      local all_done=false
      [[ $total_children -gt 0 && $archived_children -eq $total_children ]] && all_done=true
      local progress="${archived_children}/${total_children} archived"
      [[ "$all_done" == "true" ]] && progress="ALL DONE — ready to close"
      COORDINATING_ITEMS+=("$id|$priority|$subcategory|$computer|$title|$progress")
      return
    fi
    [[ -n "$note" ]] && WORKING_PARKED+=("$row") || WORKING_ITEMS+=("$row")
    return
  fi

  local bstatus
  bstatus=$(check_blockers "$blocked_by") || true

  if [[ "$status" == "blocked" ]]; then
    EXT_BLOCKED+=("$row|${bstatus#active:}"); return
  fi

  # Detect misplaced items: status=working but file still in pending/ (claim-item.sh was skipped).
  if [[ "$status" == "working" && "$loc" == "pending" ]]; then
    UNCLAIMED_ACTIVE+=("$row"); return
  fi

  # Guard: skip pending items already in archive (ghost copies).
  if [[ "$loc" == "pending" ]]; then
    local _num; _num=$(echo "$id" | grep -oE '[0-9]+')
    if [[ -n "$_num" ]] && find "$QUEUE_DIR/archive" "$QUEUE_DIR/archived" -name "WRK-${_num}.md" 2>/dev/null | grep -qc .; then
      return
    fi
  fi

  # Skip periodic-review items (standing + cadence) from ready-to-start buckets only.
  # Items in working/ or blocked/ always display regardless of standing+cadence.
  if [[ "$loc" == "pending" ]]; then
    local _standing _cadence
    _standing=$(get_field "$f" "standing")
    _cadence=$(get_field "$f" "cadence")
    [[ "$_standing" == "true" && -n "$_cadence" ]] && return
  fi

  if [[ "$bstatus" == "clear" ]]; then
    # Check for unclaimed active session: recent lock OR checkpoint present
    if has_recent_session_lock "$id" || [[ -n "$cp_stage" ]]; then
      UNCLAIMED_ACTIVE+=("$row"); return
    fi
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

# ── Sort ready arrays by urgency score (descending) ──────────────────
sort_by_urgency() {
  local -n __arr="$1"
  [[ ${#__arr[@]} -le 1 ]] && return
  local -a scored=()
  for row in "${__arr[@]}"; do
    local _id; _id="${row%%|*}"
    local _sc="${WRK_URGENCY[$_id]:-0}"
    scored+=("${_sc}|${row}")
  done
  local -a sorted_rows=()
  while IFS= read -r line; do
    sorted_rows+=("${line#*|}")  # strip score prefix
  done < <(printf '%s\n' "${scored[@]}" | sort -t'|' -k1 -rn)
  __arr=("${sorted_rows[@]}")
}
sort_by_urgency HIGH_UNBLOCKED
sort_by_urgency NEWLY_UNBLOCKED
sort_by_urgency MED_UNBLOCKED

# ── Render (box-drawing tables) ───────────────────────────────────────────────

TABLE_WIDTH=120

# draw_table <section_label> <colour> <emoji> <col_widths> <headers> <rows[]> [notes_prefix]
# col_widths / headers: pipe-separated strings.  rows: newline-separated, pipe-delimited.
# Renders uniform box-drawing tables: ┌─┬─┐ top, │ cells, ├─┼─┤ after header, └─┴─┘ bottom.
draw_table() {
  local label="$1" colour="$2" emoji="$3" col_widths_str="$4" headers_str="$5"
  shift 5
  local -a rows=("$@")
  [[ ${#rows[@]} -eq 0 ]] && return

  IFS='|' read -ra widths <<< "$col_widths_str"
  IFS='|' read -ra headers <<< "$headers_str"
  local ncols=${#widths[@]}

  # Build horizontal rules
  local top_rule="" mid_rule="" bot_rule=""
  for (( i=0; i<ncols; i++ )); do
    local seg; seg=$(printf '%*s' "${widths[$i]}" '' | tr ' ' '─')
    if [[ $i -eq 0 ]]; then
      top_rule="┌─${seg}─"; mid_rule="├─${seg}─"; bot_rule="└─${seg}─"
    elif [[ $i -eq $((ncols-1)) ]]; then
      top_rule+="┬─${seg}─┐"; mid_rule+="┼─${seg}─┤"; bot_rule+="┴─${seg}─┘"
    else
      top_rule+="┬─${seg}─"; mid_rule+="┼─${seg}─"; bot_rule+="┴─${seg}─"
    fi
  done

  # Section header (coloured full-width)
  echo ""
  printf "${colour}%s  %s\033[0m\n" "$emoji" "$label"
  echo "$top_rule"

  # Column headers
  local hdr_line=""
  for (( i=0; i<ncols; i++ )); do
    hdr_line+="│ $(printf "%-${widths[$i]}s" "${headers[$i]}") "
  done
  hdr_line+="│"
  printf "\033[1m%s\033[0m\n" "$hdr_line"
  echo "$mid_rule"

  # Data rows
  for row in "${rows[@]}"; do
    # Check for special merged rows (annotations)
    if [[ "$row" == _NOTE_:* ]]; then
      local note_text="${row#_NOTE_:}"
      local inner_w=$(( ${#top_rule} - 4 ))
      printf "│ \033[2m%-${inner_w}s\033[0m │\n" "↳ $note_text"
      continue
    fi
    if [[ "$row" == _MERGED_:* ]]; then
      local merged_text="${row#_MERGED_:}"
      local inner_w=$(( ${#top_rule} - 4 ))
      printf "│ %-${inner_w}s │\n" "$merged_text"
      continue
    fi
    IFS='|' read -ra cells <<< "$row"
    local cell_line=""
    for (( i=0; i<ncols; i++ )); do
      local val="${cells[$i]:-}"
      # Truncate to column width
      val="${val:0:${widths[$i]}}"
      cell_line+="│ $(printf "%-${widths[$i]}s" "$val") "
    done
    cell_line+="│"
    echo "$cell_line"
  done
  echo "$bot_rule"
}

# has_mixed_machines <arr_name> — returns 0 if rows span multiple machines
has_mixed_machines() {
  local -n __arr="$1"
  declare -A _seen
  for row in "${__arr[@]}"; do
    IFS='|' read -r _id _pri _sub cpu _rest <<< "$row"
    [[ -n "$cpu" ]] && _seen["$cpu"]=1
  done
  [[ ${#_seen[@]} -gt 1 ]]
}

# partition_rows <arr_name> — sets _local_rows, _remote_ids, _remote_rows
partition_rows() {
  local -n __src="$1"
  _local_rows=(); _remote_ids=(); _remote_rows=()
  for row in "${__src[@]}"; do
    IFS='|' read -r id _pri _sub cpu _rest <<< "$row"
    if [[ "$cpu" == "$THIS_HOST" ]]; then
      _local_rows+=("$row")
    else
      _remote_ids+=("$id")
      _remote_rows+=("$row")
    fi
  done
}

# render_working_section <label> <colour> <emoji> <arr_name>
# Columns: Icon | WRK | Priority | Stage | PID | Title
render_working_section() {
  local label="$1" colour="$2" emoji="$3" arr_name="$4"
  local -n _warr="$arr_name"
  [[ ${#_warr[@]} -eq 0 ]] && return

  local widths="4|10|10|9|11|60" hdrs="ICON|WRK|PRI|STAGE|PID|TITLE"
  local -a table_rows=()

  partition_rows "$arr_name"
  local has_local=$(( ${#_local_rows[@]} > 0 ))
  local has_remote=$(( ${#_remote_ids[@]} > 0 ))
  [[ $has_local -eq 1 && $has_remote -eq 1 ]] && \
    table_rows+=("_MERGED_:[this machine: $THIS_HOST]")

  for row in "${_local_rows[@]}"; do
    IFS='|' read -r id pri sub cpu ttl cpstage status pid _rest <<< "$row"
    local stage_disp; [[ -n "$cpstage" ]] && stage_disp="Stage $cpstage" || stage_disp="—"
    local pid_disp;   [[ -n "$pid" ]]     && pid_disp="PID $pid"         || pid_disp="—"
    table_rows+=("$emoji|$id|$pri|$stage_disp|$pid_disp|$ttl")
    local _note="${WRK_NOTES[$id]:-}" _nb="${WRK_NOT_BEFORE[$id]:-}"
    [[ -n "$_note" ]] && table_rows+=("_NOTE_:$_note")
    [[ -n "$_nb" ]]   && table_rows+=("_NOTE_:not before: $_nb")
  done

  if [[ $has_remote -eq 1 ]]; then
    if [[ $has_local -eq 1 ]]; then
      table_rows+=("_MERGED_:[other machines: ${_remote_ids[*]}]")
    else
      for row in "${_remote_rows[@]}"; do
        IFS='|' read -r id pri sub cpu ttl cpstage status pid _rest <<< "$row"
        local stage_disp; [[ -n "$cpstage" ]] && stage_disp="Stage $cpstage" || stage_disp="—"
        local pid_disp;   [[ -n "$pid" ]]     && pid_disp="PID $pid"         || pid_disp="—"
        table_rows+=("$emoji|$id|$pri|$stage_disp|$pid_disp|$ttl")
      done
    fi
  fi

  draw_table "$label" "$colour" "$emoji" "$widths" "$hdrs" "${table_rows[@]}"
}

# render_ready_section <label> <colour> <emoji> <arr_name>
# Columns: Icon | WRK | Priority | [Machine] | Title — Machine only if mixed
render_ready_section() {
  local label="$1" colour="$2" emoji="$3" arr_name="$4"
  local -n _rarr="$arr_name"
  [[ ${#_rarr[@]} -eq 0 ]] && return

  local mixed=false widths hdrs
  has_mixed_machines "$arr_name" && mixed=true

  if [[ "$mixed" == "true" ]]; then
    widths="4|10|10|15|68" hdrs="ICON|WRK|PRI|MACHINE|TITLE"
  else
    widths="4|10|10|83" hdrs="ICON|WRK|PRI|TITLE"
  fi

  local -a table_rows=()
  partition_rows "$arr_name"
  local has_local=$(( ${#_local_rows[@]} > 0 ))
  local has_remote=$(( ${#_remote_ids[@]} > 0 ))
  [[ $has_local -eq 1 && $has_remote -eq 1 ]] && \
    table_rows+=("_MERGED_:[this machine: $THIS_HOST]")

  for row in "${_local_rows[@]}"; do
    IFS='|' read -r id pri sub cpu ttl _rest <<< "$row"
    if [[ "$mixed" == "true" ]]; then
      table_rows+=("$emoji|$id|$pri|$cpu|$ttl")
    else
      table_rows+=("$emoji|$id|$pri|$ttl")
    fi
    local _note="${WRK_NOTES[$id]:-}" _nb="${WRK_NOT_BEFORE[$id]:-}"
    [[ -n "$_note" ]] && table_rows+=("_NOTE_:$_note")
    [[ -n "$_nb" ]]   && table_rows+=("_NOTE_:not before: $_nb")
  done

  if [[ $has_remote -eq 1 ]]; then
    if [[ $has_local -eq 1 ]]; then
      table_rows+=("_MERGED_:[other machines: ${_remote_ids[*]}]")
    else
      for row in "${_remote_rows[@]}"; do
        IFS='|' read -r id pri sub cpu ttl _rest <<< "$row"
        if [[ "$mixed" == "true" ]]; then
          table_rows+=("$emoji|$id|$pri|$cpu|$ttl")
        else
          table_rows+=("$emoji|$id|$pri|$ttl")
        fi
      done
    fi
  fi

  draw_table "$label" "$colour" "$emoji" "$widths" "$hdrs" "${table_rows[@]}"
}

# render_coordinating — Icon | WRK | Priority | Title | Child Progress
render_coordinating() {
  [[ ${#COORDINATING_ITEMS[@]} -eq 0 ]] && return
  local widths="4|10|10|50|30" hdrs="ICON|WRK|PRI|TITLE|CHILD PROGRESS"
  local -a table_rows=()
  for crow in "${COORDINATING_ITEMS[@]}"; do
    IFS='|' read -r cid cpri csub ccpu cttl cprogress <<< "$crow"
    table_rows+=("◈|$cid|$cpri|$cttl|$cprogress")
  done
  draw_table "COORDINATING — feature WRKs managing children" "\033[35m" "◈" \
    "$widths" "$hdrs" "${table_rows[@]}"
}

# render_blocked — Icon | WRK | Subcategory | Blocked By
render_blocked() {
  [[ ${#EXT_BLOCKED[@]} -eq 0 ]] && return
  local widths="4|10|26|70" hdrs="ICON|WRK|SUBCATEGORY|BLOCKED BY"
  local -a table_rows=()
  for row in "${EXT_BLOCKED[@]}"; do
    IFS='|' read -r id _pri sub _cpu _ttl _cpstage _status _pid reason <<< "$row"
    local display_reason="$reason"
    [[ "$display_reason" == "clear" || -z "$display_reason" ]] && display_reason="external (no WRK deps)"
    table_rows+=("✗|$id|$sub|$display_reason")
  done
  draw_table "EXTERNALLY BLOCKED" "\033[31m" "✗" \
    "$widths" "$hdrs" "${table_rows[@]}"
}

# ── Main output ──────────────────────────────────────────────────────────────

echo ""
scope_label="${FILTER_CATEGORY:-all categories}"
echo "\033[1m╔══════════════════════════════════════════════╗\033[0m"
printf "\033[1m║   WHAT'S NEXT  %-30s║\033[0m\n" "$(date '+%Y-%m-%d %H:%M')     "
printf "\033[1m║   scope: %-36s║\033[0m\n" "$scope_label"
echo "\033[1m╚══════════════════════════════════════════════╝\033[0m"

render_coordinating
render_working_section "WORKING — in progress"                                    "\033[36m" "🔄" WORKING_ITEMS
render_working_section "PARKED — deferred / awaiting input"                       "\033[90m" "⏸"  WORKING_PARKED
render_working_section "IN-PROGRESS UNCLAIMED — session active, not yet claimed"  "\033[33m" "⚠"  UNCLAIMED_ACTIVE
render_ready_section   "HIGH PRIORITY — ready to start"                           "\033[32m" "★"  HIGH_UNBLOCKED
render_ready_section   "NEWLY UNBLOCKED — blockers cleared"                       "\033[33m" "↑"  NEWLY_UNBLOCKED
# Cap medium section
if [[ ${#MED_UNBLOCKED[@]} -gt $MED_LIMIT ]]; then
  MED_DISPLAY=("${MED_UNBLOCKED[@]:0:$MED_LIMIT}")
  MED_OVERFLOW=$(( ${#MED_UNBLOCKED[@]} - MED_LIMIT ))
else
  MED_DISPLAY=("${MED_UNBLOCKED[@]}")
  MED_OVERFLOW=0
fi
render_ready_section "MEDIUM — ready" "\033[0m" "·" MED_DISPLAY
[[ $MED_OVERFLOW -gt 0 ]] && echo "  … and $MED_OVERFLOW more (use --limit N or --category to narrow)"

render_blocked

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
echo "Summary: \033[35m${#COORDINATING_ITEMS[@]} coordinating\033[0m · \033[36m${#WORKING_ITEMS[@]} working\033[0m · \033[90m${#WORKING_PARKED[@]} parked\033[0m · \033[33m${#UNCLAIMED_ACTIVE[@]} unclaimed\033[0m · \033[32m${#HIGH_UNBLOCKED[@]} high ready\033[0m · \033[33m${#NEWLY_UNBLOCKED[@]} newly unblocked\033[0m · ${#MED_UNBLOCKED[@]} medium · \033[31m${#EXT_BLOCKED[@]} blocked\033[0m"
echo ""
