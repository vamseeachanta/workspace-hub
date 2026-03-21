#!/usr/bin/env bash
# whats-next.sh — Refresh and display the prioritised "run now" work list.
# Reads pre-computed data from wrk-status-index.json (built by rebuild-wrk-index.sh).
# Usage: bash scripts/work-queue/whats-next.sh [--category <name>] [--subcategory <name>]

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
THIS_HOST=$(hostname -s)
FILTER_CATEGORY="harness"   # default: harness-focused view
FILTER_SUBCATEGORY=""
SHOW_ALL=false
MED_LIMIT=20
COMPACT=false
_CATEGORY_EXPLICIT=false
_DEBUG=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --category)     FILTER_CATEGORY="$2"; _CATEGORY_EXPLICIT=true; shift 2 ;;
    --subcategory)  FILTER_SUBCATEGORY="$2"; shift 2 ;;
    --all)          SHOW_ALL=true; FILTER_CATEGORY=""; shift ;;
    --limit)        MED_LIMIT="$2"; shift 2 ;;
    --compact)      COMPACT=true; shift ;;
    --debug)        _DEBUG=true; shift ;;
    *) shift ;;
  esac
done
# --subcategory alone clears the default category filter (cross-category search)
[[ -n "$FILTER_SUBCATEGORY" && "$_CATEGORY_EXPLICIT" == false ]] && FILTER_CATEGORY=""

# ── Index-first data load (single python3 call) ──────────────────────────────
# Outputs TSV lines: section\tfield1\tfield2\t...
# Sections: COORDINATING, WORKING, PARKED, UNCLAIMED, HIGH, NEWLY_UNBLOCKED, MEDIUM, BLOCKED, DEFERRED
# Each section has its own field layout documented in the Python output.

_INDEX_FILE="${QUEUE_DIR}/wrk-status-index.json"
if [[ ! -f "$_INDEX_FILE" ]]; then
  echo "Error: wrk-status-index.json not found. Run: bash scripts/work-queue/rebuild-wrk-index.sh" >&2
  exit 1
fi

_TSV_DATA=$(python3 - "$_INDEX_FILE" "$FILTER_CATEGORY" "$FILTER_SUBCATEGORY" "$THIS_HOST" "$MED_LIMIT" <<'PYEOF'
import json, re, sys
from datetime import datetime, timezone

idx_path, filter_cat, filter_sub, this_host, med_limit_str = sys.argv[1:6]
med_limit = int(med_limit_str)
data = json.loads(open(idx_path).read())
now = datetime.now(timezone.utc)
today_epoch = int(now.timestamp())

archived_ids = {wid for wid, e in data.items() if e.get("status") == "archived"}

def fmt_age(created_at):
    if not created_at:
        return "—"
    try:
        dt = datetime.strptime(created_at.split(".")[0].strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days = max((now - dt).days, 0)
        if days < 30:
            return f"{days}d"
        elif days < 90:
            return f"{days // 7}w"
        else:
            return f"{days // 30}mo"
    except ValueError:
        return "—"

def fmt_gh(ref):
    if not ref or ref == "pending":
        return "—"
    m = re.search(r"/(\d+)$", ref)
    return f"#{m.group(1)}" if m else "—"

def fmt_urg(score):
    if score is None:
        return "—"
    return str(score)

def check_blockers(blocked_by_str):
    """Returns (is_clear, active_blockers_str)"""
    if not blocked_by_str or blocked_by_str == "[]":
        return True, ""
    deps = re.findall(r"WRK-(\d+)", blocked_by_str)
    active = [f"WRK-{d}" for d in deps if f"WRK-{d}" not in archived_ids]
    if not active:
        return True, ""
    return False, ",".join(active)

def not_before_future(nb):
    if not nb:
        return False
    try:
        dt = datetime.strptime(nb.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt.timestamp() > today_epoch
    except ValueError:
        return False

# Classify each entry
coordinating = []
working = []
parked = []
unclaimed = []
high_ready = []
newly_unblocked = []
medium_ready = []
blocked = []
deferred = []

for wid, e in data.items():
    status = e.get("status", "")
    if status in ("archived", "done"):
        continue

    cat = e.get("category", "")
    sub = e.get("subcategory", "")
    wrk_type = e.get("type", "")
    is_coordinating_feature = (status == "coordinating" and wrk_type == "feature")

    # Category/subcategory filter (coordinating features bypass)
    if not is_coordinating_feature:
        if filter_cat and filter_cat not in cat:
            continue
        if filter_sub and filter_sub not in sub:
            continue

    pri = e.get("priority", "")
    computer = e.get("computer", "")
    title = (e.get("title", "") or "")[:60]
    urg = fmt_urg(e.get("urgency_score"))
    gh = fmt_gh(e.get("github_issue_ref", ""))
    age = fmt_age(e.get("created_at", ""))
    cp_stage = e.get("checkpoint_stage", "")
    pid = e.get("session_pid", "")
    note = e.get("note", "")
    nb = e.get("not_before", "")
    standing = e.get("standing", "")
    cadence = e.get("cadence", "")
    bb_raw = e.get("blocked_by", "")
    is_clear, active_blockers = check_blockers(bb_raw)

    # Determine directory location from status
    if status == "working" or status == "coordinating":
        loc = "working"
    elif status == "blocked":
        loc = "blocked"
    else:
        loc = "pending"

    # Deferred: not_before in future (except working items)
    if nb and loc != "working" and not_before_future(nb):
        deferred.append((wid, pri, sub, computer, title, nb, urg, gh, age, cat))
        continue

    # Working items
    if loc == "working":
        if is_coordinating_feature:
            coordinating.append((wid, pri, sub, computer, title, "—", urg, gh, age, cat))
            continue
        if note:
            parked.append((wid, pri, sub, computer, title, cp_stage, pid, urg, gh, age, cat, note, nb))
        else:
            working.append((wid, pri, sub, computer, title, cp_stage, pid, urg, gh, age, cat, note, nb))
        continue

    # Blocked items
    if status == "blocked":
        reason = active_blockers if active_blockers else "external (no WRK deps)"
        blocked.append((wid, pri, sub, computer, title, reason, urg, gh, age, cat))
        continue

    # Pending items: skip standing+cadence
    if standing == "true" and cadence:
        continue

    # Unclaimed: status=working but in pending, or has checkpoint stage
    if status == "working" and loc == "pending":
        unclaimed.append((wid, pri, sub, computer, title, cp_stage, pid, urg, gh, age, cat, note, nb))
        continue
    if cp_stage:
        unclaimed.append((wid, pri, sub, computer, title, cp_stage, pid, urg, gh, age, cat, note, nb))
        continue

    # Ready items (blockers clear)
    if is_clear:
        has_deps = bool(re.findall(r"WRK-\d+", bb_raw))
        if pri == "high":
            high_ready.append((wid, pri, cat, computer, title, urg, sub, gh, age))
        elif has_deps:
            newly_unblocked.append((wid, pri, cat, computer, title, urg, sub, gh, age))
        else:
            medium_ready.append((wid, pri, cat, computer, title, urg, sub, gh, age))

# Sort ready arrays by urgency score (descending)
def sort_key(item):
    try:
        return -float(item[5]) if item[5] != "—" else 0
    except (ValueError, IndexError):
        return 0

high_ready.sort(key=sort_key)
newly_unblocked.sort(key=sort_key)
medium_ready.sort(key=sort_key)

# Output TSV — use "—" for empty fields to prevent bash read from collapsing consecutive tabs
def p(section, *fields):
    safe = [str(f) if f else "—" for f in fields]
    print(section + "\t" + "\t".join(safe))

for r in coordinating:
    p("COORDINATING", *r)
for r in working:
    p("WORKING", *r)
for r in parked:
    p("PARKED", *r)
for r in unclaimed:
    p("UNCLAIMED", *r)
for r in high_ready:
    p("HIGH", *r)
for r in newly_unblocked:
    p("NEWLY_UNBLOCKED", *r)
for r in medium_ready[:med_limit]:
    p("MEDIUM", *r)
p("META", "med_overflow", str(max(0, len(medium_ready) - med_limit)))
for r in blocked:
    p("BLOCKED", *r)
for r in deferred:
    p("DEFERRED", *r)
# Counts (use raw print to avoid "—" substitution for 0)
counts = [len(coordinating), len(working), len(parked), len(unclaimed),
          len(high_ready), len(newly_unblocked), len(medium_ready), len(blocked), len(deferred)]
print("COUNTS\t" + "\t".join(str(c) for c in counts))
PYEOF
)

# ── Parse TSV into bash arrays ────────────────────────────────────────────────
declare -a WORKING_ITEMS WORKING_PARKED UNCLAIMED_ACTIVE NEWLY_UNBLOCKED HIGH_UNBLOCKED MED_UNBLOCKED EXT_BLOCKED COORDINATING_ITEMS DEFERRED_ITEMS
declare -A WRK_NOTES WRK_NOT_BEFORE
MED_OVERFLOW=0
_COUNTS_LINE=""

while IFS=$'\t' read -r section rest; do
  case "$section" in
    COORDINATING)
      # wid|pri|sub|cpu|title|progress|urg|gh|age|cat
      IFS=$'\t' read -r wid pri sub cpu title progress urg gh age cat <<< "$rest"
      COORDINATING_ITEMS+=("$wid|$pri|$sub|$cpu|$title|$progress|$urg|$gh|$age|$cat")
      ;;
    WORKING)
      # wid|pri|sub|cpu|title|cpstage|pid|urg|gh|age|cat|note|nb
      IFS=$'\t' read -r wid pri sub cpu title cpstage pid urg gh age cat note nb <<< "$rest"
      WORKING_ITEMS+=("$wid|$pri|$sub|$cpu|$title|$cpstage|$pid|$urg|$gh|$age|$cat")
      [[ -n "$note" ]] && WRK_NOTES["$wid"]="$note"
      [[ -n "$nb" ]] && WRK_NOT_BEFORE["$wid"]="$nb"
      ;;
    PARKED)
      IFS=$'\t' read -r wid pri sub cpu title cpstage pid urg gh age cat note nb <<< "$rest"
      WORKING_PARKED+=("$wid|$pri|$sub|$cpu|$title|$cpstage|$pid|$urg|$gh|$age|$cat")
      [[ -n "$note" ]] && WRK_NOTES["$wid"]="$note"
      [[ -n "$nb" ]] && WRK_NOT_BEFORE["$wid"]="$nb"
      ;;
    UNCLAIMED)
      IFS=$'\t' read -r wid pri sub cpu title cpstage pid urg gh age cat note nb <<< "$rest"
      UNCLAIMED_ACTIVE+=("$wid|$pri|$sub|$cpu|$title|$cpstage|$pid|$urg|$gh|$age|$cat")
      ;;
    HIGH)
      # wid|pri|cat|cpu|title|urg|sub|gh|age
      IFS=$'\t' read -r wid pri cat cpu title urg sub gh age <<< "$rest"
      HIGH_UNBLOCKED+=("$wid|$pri|$cat|$cpu|$title|$urg|$sub|$gh|$age")
      ;;
    NEWLY_UNBLOCKED)
      IFS=$'\t' read -r wid pri cat cpu title urg sub gh age <<< "$rest"
      NEWLY_UNBLOCKED+=("$wid|$pri|$cat|$cpu|$title|$urg|$sub|$gh|$age")
      ;;
    MEDIUM)
      IFS=$'\t' read -r wid pri cat cpu title urg sub gh age <<< "$rest"
      MED_UNBLOCKED+=("$wid|$pri|$cat|$cpu|$title|$urg|$sub|$gh|$age")
      ;;
    BLOCKED)
      # wid|pri|sub|cpu|title|reason|urg|gh|age|cat
      IFS=$'\t' read -r wid pri sub cpu title reason urg gh age cat <<< "$rest"
      EXT_BLOCKED+=("$wid|$pri|$sub|$cpu|$title|$reason|$urg|$gh|$age|$cat")
      ;;
    DEFERRED)
      # wid|pri|sub|cpu|title|nb|urg|gh|age|cat
      IFS=$'\t' read -r wid pri sub cpu title nb urg gh age cat <<< "$rest"
      DEFERRED_ITEMS+=("$wid|$pri|$sub|$cpu|$title|$nb|$urg|$gh|$age|$cat")
      ;;
    META)
      IFS=$'\t' read -r key val <<< "$rest"
      [[ "$key" == "med_overflow" ]] && MED_OVERFLOW="$val"
      ;;
    COUNTS)
      _COUNTS_LINE="$rest"
      ;;
  esac
done <<< "$_TSV_DATA"

# Parse counts
IFS=$'\t' read -r _cnt_coord _cnt_work _cnt_park _cnt_uncl _cnt_high _cnt_newu _cnt_med _cnt_block _cnt_def <<< "$_COUNTS_LINE"

# ── Render (box-drawing tables) ───────────────────────────────────────────────

TABLE_WIDTH=120

# draw_table <section_label> <colour> <emoji> <col_widths> <headers> <rows[]>
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
# Enriched: ICON | WRK | PRI | URG | STAGE | PID | GH# | AGE | TITLE
# Compact:  ICON | WRK | PRI | STAGE | PID | TITLE
render_working_section() {
  local label="$1" colour="$2" emoji="$3" arr_name="$4"
  local -n _warr="$arr_name"
  [[ ${#_warr[@]} -eq 0 ]] && return

  local widths hdrs
  if [[ "$COMPACT" == "true" ]]; then
    widths="4|10|10|9|11|60" hdrs="ICON|WRK|PRI|STAGE|PID|TITLE"
  else
    widths="4|10|6|5|9|11|6|5|50" hdrs="ICON|WRK|PRI|URG|STAGE|PID|GH#|AGE|TITLE"
  fi
  local -a table_rows=()

  partition_rows "$arr_name"
  local has_local=$(( ${#_local_rows[@]} > 0 ))
  local has_remote=$(( ${#_remote_ids[@]} > 0 ))
  [[ $has_local -eq 1 && $has_remote -eq 1 ]] && \
    table_rows+=("_MERGED_:[this machine: $THIS_HOST]")

  for row in "${_local_rows[@]}"; do
    # wid|pri|sub|cpu|title|cpstage|pid|urg|gh|age|cat
    IFS='|' read -r id pri sub cpu ttl cpstage pid urg gh age cat <<< "$row"
    local stage_disp; [[ -n "$cpstage" ]] && stage_disp="Stage $cpstage" || stage_disp="—"
    local pid_disp;   [[ -n "$pid" ]]     && pid_disp="PID $pid"         || pid_disp="—"
    if [[ "$COMPACT" == "true" ]]; then
      table_rows+=("$emoji|$id|$pri|$stage_disp|$pid_disp|$ttl")
    else
      table_rows+=("$emoji|$id|$pri|$urg|$stage_disp|$pid_disp|$gh|$age|$ttl")
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
        IFS='|' read -r id pri sub cpu ttl cpstage pid urg gh age cat <<< "$row"
        local stage_disp; [[ -n "$cpstage" ]] && stage_disp="Stage $cpstage" || stage_disp="—"
        local pid_disp;   [[ -n "$pid" ]]     && pid_disp="PID $pid"         || pid_disp="—"
        if [[ "$COMPACT" == "true" ]]; then
          table_rows+=("$emoji|$id|$pri|$stage_disp|$pid_disp|$ttl")
        else
          table_rows+=("$emoji|$id|$pri|$urg|$stage_disp|$pid_disp|$gh|$age|$ttl")
        fi
      done
    fi
  fi

  draw_table "$label" "$colour" "$emoji" "$widths" "$hdrs" "${table_rows[@]}"
}

# render_ready_section <label> <colour> <emoji> <arr_name>
# Enriched: ICON | WRK | PRI | URG | CAT | SUB | GH# | AGE | [MACHINE] | TITLE
# Compact:  ICON | WRK | PRI | [MACHINE] | TITLE
render_ready_section() {
  local label="$1" colour="$2" emoji="$3" arr_name="$4"
  local -n _rarr="$arr_name"
  [[ ${#_rarr[@]} -eq 0 ]] && return

  local mixed=false widths hdrs
  has_mixed_machines "$arr_name" && mixed=true

  if [[ "$COMPACT" == "true" ]]; then
    if [[ "$mixed" == "true" ]]; then
      widths="4|10|10|15|68" hdrs="ICON|WRK|PRI|MACHINE|TITLE"
    else
      widths="4|10|10|83" hdrs="ICON|WRK|PRI|TITLE"
    fi
  else
    if [[ "$mixed" == "true" ]]; then
      widths="4|10|6|5|10|12|6|5|15|40" hdrs="ICON|WRK|PRI|URG|CAT|SUB|GH#|AGE|MACHINE|TITLE"
    else
      widths="4|10|6|5|10|12|6|5|50" hdrs="ICON|WRK|PRI|URG|CAT|SUB|GH#|AGE|TITLE"
    fi
  fi

  local -a table_rows=()
  partition_rows "$arr_name"
  local has_local=$(( ${#_local_rows[@]} > 0 ))
  local has_remote=$(( ${#_remote_ids[@]} > 0 ))
  [[ $has_local -eq 1 && $has_remote -eq 1 ]] && \
    table_rows+=("_MERGED_:[this machine: $THIS_HOST]")

  for row in "${_local_rows[@]}"; do
    # wid|pri|cat|cpu|title|urg|sub|gh|age
    IFS='|' read -r id pri cat cpu ttl urg sub gh age <<< "$row"
    if [[ "$COMPACT" == "true" ]]; then
      if [[ "$mixed" == "true" ]]; then
        table_rows+=("$emoji|$id|$pri|$cpu|$ttl")
      else
        table_rows+=("$emoji|$id|$pri|$ttl")
      fi
    else
      if [[ "$mixed" == "true" ]]; then
        table_rows+=("$emoji|$id|$pri|$urg|$cat|$sub|$gh|$age|$cpu|$ttl")
      else
        table_rows+=("$emoji|$id|$pri|$urg|$cat|$sub|$gh|$age|$ttl")
      fi
    fi
  done

  if [[ $has_remote -eq 1 ]]; then
    if [[ $has_local -eq 1 ]]; then
      table_rows+=("_MERGED_:[other machines: ${_remote_ids[*]}]")
    else
      for row in "${_remote_rows[@]}"; do
        IFS='|' read -r id pri cat cpu ttl urg sub gh age <<< "$row"
        if [[ "$COMPACT" == "true" ]]; then
          if [[ "$mixed" == "true" ]]; then
            table_rows+=("$emoji|$id|$pri|$cpu|$ttl")
          else
            table_rows+=("$emoji|$id|$pri|$ttl")
          fi
        else
          if [[ "$mixed" == "true" ]]; then
            table_rows+=("$emoji|$id|$pri|$urg|$cat|$sub|$gh|$age|$cpu|$ttl")
          else
            table_rows+=("$emoji|$id|$pri|$urg|$cat|$sub|$gh|$age|$ttl")
          fi
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
    IFS='|' read -r cid cpri csub ccpu cttl cprogress _rest <<< "$crow"
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
    IFS='|' read -r id pri sub cpu ttl reason _rest <<< "$row"
    table_rows+=("✗|$id|$sub|$reason")
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
render_ready_section   "MEDIUM — ready"                                           "\033[0m"  "·"  MED_UNBLOCKED
[[ $MED_OVERFLOW -gt 0 ]] && echo "  … and $MED_OVERFLOW more (use --limit N or --category to narrow)"

render_blocked

# ── Deferred items (not_before in the future) ─────────────────────────────
if [[ ${#DEFERRED_ITEMS[@]} -gt 0 ]]; then
  _def_widths="4|10|10|12|68" _def_hdrs="ICON|WRK|PRI|NOT BEFORE|TITLE"
  _def_rows=()
  for row in "${DEFERRED_ITEMS[@]}"; do
    IFS='|' read -r id pri sub cpu ttl nb _rest <<< "$row"
    _def_rows+=("⏳|$id|$pri|$nb|$ttl")
  done
  draw_table "DEFERRED — not before date in the future" "\033[90m" "⏳" \
    "$_def_widths" "$_def_hdrs" "${_def_rows[@]}"
fi

# ── Parallel hints ────────────────────────────────────────────────────────────
echo ""; echo "\033[1m── Parallel hints ──\033[0m"

declare -A machine_map
for row in "${HIGH_UNBLOCKED[@]}" "${NEWLY_UNBLOCKED[@]}"; do
  IFS='|' read -r id _pri _sub cpu _rest <<< "$row"
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
echo "Summary: \033[35m${_cnt_coord:-0} coordinating\033[0m · \033[36m${_cnt_work:-0} working\033[0m · \033[90m${_cnt_park:-0} parked\033[0m · \033[33m${_cnt_uncl:-0} unclaimed\033[0m · \033[32m${_cnt_high:-0} high ready\033[0m · \033[33m${_cnt_newu:-0} newly unblocked\033[0m · ${_cnt_med:-0} medium · \033[31m${_cnt_block:-0} blocked\033[0m · \033[90m${_cnt_def:-0} deferred\033[0m"
echo ""
