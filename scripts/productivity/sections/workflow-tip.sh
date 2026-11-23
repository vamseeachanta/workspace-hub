#!/usr/bin/env bash
# ABOUTME: Daily log section — picks 2 workflow tips from the catalog, avoiding recent repeats
# ABOUTME: Reads tips-catalog.yaml, checks tip-history.yaml (30-day window), outputs markdown
# Usage: bash workflow-tip.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
TIPS_DIR="$WORKSPACE_ROOT/config/workflow-tips"
CATALOG="$TIPS_DIR/tips-catalog.yaml"
HISTORY="$TIPS_DIR/tip-history.yaml"
TODAY=$(date +%Y-%m-%d)
TIPS_PER_DAY=2
COOLDOWN_DAYS=30

if [[ ! -f "$CATALOG" ]]; then
    exit 0
fi

# ── Parse catalog into parallel arrays ───────────────────────────────────────
ids=()
names=()
categories=()
oneliners=()
try_its=()
sources=()

current_id="" current_name="" current_cat="" current_one="" current_try="" current_src=""

while IFS= read -r line; do
    case "$line" in
        *"id: "*)       current_id="${line#*id: }" ;;
        *"name: "*)     current_name="${line#*name: }" ;;
        *"category: "*) current_cat="${line#*category: }"; current_cat="${current_cat%%#*}"; current_cat="${current_cat%% *}" ;;
        *"oneliner: "*) current_one="${line#*oneliner: }"; current_one="${current_one#\"}"; current_one="${current_one%\"}" ;;
        *"try_it: "*)   current_try="${line#*try_it: }"; current_try="${current_try#\"}"; current_try="${current_try%\"}" ;;
        *"source: "*)   current_src="${line#*source: }"; current_src="${current_src#\"}"; current_src="${current_src%\"}" ;;
        *"added: "*)
            if [[ -n "$current_id" ]]; then
                ids+=("$current_id")
                names+=("$current_name")
                categories+=("$current_cat")
                oneliners+=("$current_one")
                try_its+=("$current_try")
                sources+=("$current_src")
            fi
            current_id="" current_name="" current_cat="" current_one="" current_try="" current_src=""
            ;;
    esac
done < "$CATALOG"

if [[ ${#ids[@]} -eq 0 ]]; then
    exit 0
fi

# ── Collect recently shown tip IDs (within cooldown window) ──────────────────
recent_ids=""
if [[ -f "$HISTORY" ]]; then
    cutoff=$(date -d "$TODAY - $COOLDOWN_DAYS days" +%Y-%m-%d 2>/dev/null \
        || date -v-"${COOLDOWN_DAYS}d" +%Y-%m-%d 2>/dev/null)
    while IFS= read -r line; do
        if [[ "$line" =~ date:\ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
            entry_date="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ tips:\ \[(.+)\] ]]; then
            if [[ "$entry_date" > "$cutoff" || "$entry_date" == "$cutoff" ]]; then
                recent_ids="$recent_ids ${BASH_REMATCH[1]//,/ }"
            fi
        fi
    done < "$HISTORY"
fi

# ── Filter to eligible tips ──────────────────────────────────────────────────
eligible=()
for i in "${!ids[@]}"; do
    tip_id="${ids[$i]}"
    if [[ "$recent_ids" != *"$tip_id"* ]]; then
        eligible+=("$i")
    fi
done

if [[ ${#eligible[@]} -eq 0 ]]; then
    exit 0
fi

# ── Pick N tips at random ────────────────────────────────────────────────────
picked=()
pool=("${eligible[@]}")
count=$TIPS_PER_DAY
[[ $count -gt ${#pool[@]} ]] && count=${#pool[@]}

for ((n=0; n<count; n++)); do
    rand=$((RANDOM % ${#pool[@]}))
    picked+=("${pool[$rand]}")
    # Remove picked element from pool
    pool=("${pool[@]:0:$rand}" "${pool[@]:$((rand+1))}")
done

if [[ ${#picked[@]} -eq 0 ]]; then
    exit 0
fi

# ── Output markdown ──────────────────────────────────────────────────────────
echo "## Workflow Tips of the Day"
echo ""

for idx in "${picked[@]}"; do
    echo "**${names[$idx]}** (${categories[$idx]})"
    echo "${oneliners[$idx]}"
    echo "Try it: \`${try_its[$idx]}\`"
    echo "_Source: ${sources[$idx]}_"
    echo ""
done

# ── Append to history ────────────────────────────────────────────────────────
tip_list=""
for idx in "${picked[@]}"; do
    [[ -n "$tip_list" ]] && tip_list="$tip_list, "
    tip_list="$tip_list${ids[$idx]}"
done

# Ensure history file exists with proper structure
if [[ ! -f "$HISTORY" ]] || ! grep -q "^shown:" "$HISTORY"; then
    cat > "$HISTORY" <<'EOF'
# ABOUTME: Tracks which tips were shown on which dates to prevent repeats
# ABOUTME: Auto-maintained by workflow-tip.sh — 30-day no-repeat window
shown: []
EOF
fi

# Replace empty shown: [] or append to existing list
if grep -q "^shown: \[\]" "$HISTORY"; then
    sed -i "s/^shown: \[\]/shown:\n  - date: $TODAY\n    tips: [$tip_list]/" "$HISTORY"
else
    echo "  - date: $TODAY" >> "$HISTORY"
    echo "    tips: [$tip_list]" >> "$HISTORY"
fi
