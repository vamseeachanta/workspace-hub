#!/usr/bin/env bash
# review-skills-graph.sh — Score skill domains by demand vs depth
#
# Reads:
#   - .claude/skills/        (directory tree of SKILL.md files)
#   - .claude/work-queue/{pending,working,blocked}/*.md
#   - git log (single call for recent 30-day activity)
#
# Outputs:
#   - Priority list   (high demand + activity, low data)
#   - Archival candidates  (zero demand + activity)
#   - Gap candidates  (WRK demand, no skill exists)
#   - Appends one JSON record to .claude/state/skills-graph-review-log.jsonl
#
# Usage:
#   scripts/skills/review-skills-graph.sh [--json] [--top N]
#   --json    Print machine-readable JSON summary to stdout
#   --top N   Number of priority skills to surface (default: 10)
#
# Exit codes: 0=ok, 1=error

set -uo pipefail

# ── Resolve workspace root ────────────────────────────────────────────────────
resolve_root() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidate
    candidate="$(cd "$script_dir/../.." && pwd)"
    if [[ -d "$candidate/.claude" ]]; then echo "$candidate"; return; fi
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        [[ -d "$dir/.claude" ]] && echo "$dir" && return
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

ROOT="$(resolve_root)"
STATE_DIR="$ROOT/.claude/state"
SKILLS_DIR="$ROOT/.claude/skills"
WQ_DIR="$ROOT/.claude/work-queue"
LOG_FILE="$STATE_DIR/skills-graph-review-log.jsonl"

OUTPUT_JSON=false
TOP_N=10

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) OUTPUT_JSON=true ;;
        --top)  shift; TOP_N="${1:-10}" ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
    shift
done

run_date="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ── 1. Collect skill names ────────────────────────────────────────────────────
mapfile -t skills < <(
    find "$SKILLS_DIR" -name "SKILL.md" -print0 2>/dev/null \
      | xargs -0 -I{} dirname {} \
      | xargs -I{} basename {} \
      | sort -u
)

# ── 2. WRK text (all active queues) ──────────────────────────────────────────
wrk_text=""
for status in pending working blocked; do
    local_dir="$WQ_DIR/$status"
    [[ -d "$local_dir" ]] || continue
    while IFS= read -r -d '' f; do
        wrk_text+="$(cat "$f" 2>/dev/null) "
    done < <(find "$local_dir" -name "WRK-*.md" -print0 2>/dev/null)
done

# ── 3. Single git log call → store changed filenames in variable ──────────────
git_activity_text=""
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_activity_text="$(
        git -C "$ROOT" log --since="30 days ago" --name-only --pretty=format: 2>/dev/null \
          | tr '/' '\n' \
          | grep -v '^$'
    )"
fi

# ── 4. Depth: count lines in each SKILL.md ───────────────────────────────────
declare -A depth_map
while IFS= read -r -d '' skill_file; do
    skill_name="$(basename "$(dirname "$skill_file")")"
    lines="$(wc -l < "$skill_file" | tr -d ' ')"
    depth_map["$skill_name"]="${lines:-0}"
done < <(find "$SKILLS_DIR" -name "SKILL.md" -print0 2>/dev/null)

# ── 5. Score each skill ───────────────────────────────────────────────────────
depth_norm() {
    local d="${1:-0}"
    if   [[ "$d" -ge 200 ]]; then echo 3
    elif [[ "$d" -ge 100 ]]; then echo 2
    else echo 1
    fi
}

declare -A demand_map activity_map score_map

for skill in "${skills[@]}"; do
    # demand: case-insensitive count in WRK text
    d=$(echo "$wrk_text" | grep -oi "$skill" 2>/dev/null | wc -l | tr -d ' ')
    demand_map["$skill"]="${d:-0}"

    # activity: count of path segments containing skill name in git log
    a=$(echo "$git_activity_text" | grep -ic "$skill" 2>/dev/null || echo 0)
    activity_map["$skill"]="${a:-0}"

    # priority score
    dn=$(depth_norm "${depth_map[$skill]:-0}")
    score_map["$skill"]=$(( d * 3 + a * 2 - dn ))
done

# ── 6. Sort and build output lists ───────────────────────────────────────────
mapfile -t sorted_skills < <(
    for skill in "${!score_map[@]}"; do
        echo "${score_map[$skill]} $skill"
    done | sort -rn | awk '{print $2}'
)

priority_list=()
archival_candidates=()
count=0

for skill in "${sorted_skills[@]}"; do
    d="${demand_map[$skill]:-0}"
    a="${activity_map[$skill]:-0}"
    dp="${depth_map[$skill]:-0}"

    if [[ $count -lt $TOP_N && ( "$d" -gt 0 || "$a" -gt 0 ) ]]; then
        priority_list+=("$skill")
        (( count++ )) || true
    fi

    if [[ "$d" -eq 0 && "$a" -eq 0 && "$dp" -gt 20 ]]; then
        archival_candidates+=("$skill")
    fi
done

# Gap candidates: hyphenated tokens in WRK text with no matching skill
skill_set=" ${skills[*]} "
gap_candidates=()
mapfile -t wrk_domains < <(
    echo "$wrk_text" | grep -oE '[a-z]+-[a-z]+(-[a-z]+)?' | sort -u | head -50
)
for domain in "${wrk_domains[@]}"; do
    if [[ "$skill_set" != *" $domain "* ]]; then
        d=$(echo "$wrk_text" | grep -oi "$domain" | wc -l | tr -d ' ')
        [[ "$d" -ge 2 ]] && gap_candidates+=("$domain")
    fi
done

# ── 7. Human-readable output ──────────────────────────────────────────────────
if [[ "$OUTPUT_JSON" == false ]]; then
    echo "=== Skills Graph Review — $run_date ==="
    echo ""
    echo "PRIORITY LIST (top $TOP_N · demand × 3 + activity × 2 − depth):"
    if [[ ${#priority_list[@]} -eq 0 ]]; then
        echo "  (none with non-zero demand or activity)"
    fi
    for s in "${priority_list[@]}"; do
        printf "  %-42s demand=%-3s activity=%-3s depth=%-4s score=%s\n" \
            "$s" "${demand_map[$s]:-0}" "${activity_map[$s]:-0}" \
            "${depth_map[$s]:-0}" "${score_map[$s]:-0}"
    done
    echo ""
    echo "ARCHIVAL CANDIDATES (zero demand, zero activity):"
    if [[ ${#archival_candidates[@]} -eq 0 ]]; then echo "  (none)"
    else for s in "${archival_candidates[@]}"; do echo "  $s"; done; fi
    echo ""
    echo "GAP CANDIDATES (WRK demand, no skill exists):"
    if [[ ${#gap_candidates[@]} -eq 0 ]]; then echo "  (none)"
    else for s in "${gap_candidates[@]}"; do echo "  $s"; done; fi
fi

# ── 8. Build JSON log entry ───────────────────────────────────────────────────
json_arr() {
    local arr=("$@")
    local out='[' first=true
    for item in "${arr[@]}"; do
        $first || out+=','
        out+="\"$item\""
        first=false
    done
    out+=']'
    echo "$out"
}

wrk_count=$(echo "$wrk_text" | grep -c "^# " 2>/dev/null || echo 0)
log_entry=$(printf \
    '{"date":"%s","skills_scanned":%d,"wrk_items_scanned":%d,"priority_list":%s,"archival_candidates":%s,"gap_candidates":%s}' \
    "$run_date" "${#skills[@]}" "$wrk_count" \
    "$(json_arr "${priority_list[@]}")" \
    "$(json_arr "${archival_candidates[@]}")" \
    "$(json_arr "${gap_candidates[@]}")"
)

mkdir -p "$STATE_DIR"
echo "$log_entry" >> "$LOG_FILE"

[[ "$OUTPUT_JSON" == true ]] && echo "$log_entry"

echo ""
echo "Log appended → $LOG_FILE"
echo "Scanned: ${#skills[@]} skills | Priority: ${#priority_list[@]} | Archival: ${#archival_candidates[@]} | Gaps: ${#gap_candidates[@]}"
