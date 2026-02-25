#!/usr/bin/env bash
# save-snapshot.sh — Capture file-system-observable session state before /clear
# Called by the /save skill. Writes .claude/state/session-snapshot.md
# Conversational context (Ideas/Notes) is appended by Claude, not this script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_HUB}/.claude/work-queue"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
SNAPSHOT="${STATE_DIR}/session-snapshot.md"

mkdir -p "$STATE_DIR"

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
BRANCH="$(git -C "$WORKSPACE_HUB" symbolic-ref --short HEAD 2>/dev/null || echo "detached")"

# ─── Helper: extract title from WRK file ───────────────────────────────────
extract_title() {
    local file="$1"
    # Try YAML front-matter title first
    local title
    title=$(awk '/^---/{found++; next} found==1 && /^title:/{sub(/^title:[[:space:]]*"?/,""); sub(/"?[[:space:]]*$/,""); print; exit}' "$file" 2>/dev/null)
    if [[ -z "$title" ]]; then
        # Fall back to first H1 heading
        title=$(grep -m1 '^# ' "$file" 2>/dev/null | sed 's/^# //' | sed 's/WRK-[0-9]*:[[:space:]]*//')
    fi
    echo "${title:-unknown}"
}

# ─── Helper: compute percent complete from checkboxes ──────────────────────
percent_complete() {
    local file="$1"
    local total done_count
    # Use awk — always exits 0, always prints a number
    total=$(awk '/^\s*- \[/{n++} END{print n+0}' "$file" 2>/dev/null)
    done_count=$(awk '/^\s*- \[x\]/{n++} END{print n+0}' "$file" 2>/dev/null)
    total="${total:-0}"
    done_count="${done_count:-0}"
    if [[ "$total" -eq 0 ]]; then
        echo "?%"
    else
        echo "$(( done_count * 100 / total ))%"
    fi
}

# ─── Helper: last done step (last [x] item) ────────────────────────────────
last_done_step() {
    local file="$1"
    { grep '^\s*- \[x\]' "$file" 2>/dev/null || true; } | tail -1 | sed 's/^\s*- \[x\][[:space:]]*//' | cut -c1-80
}

# ─── Helper: next step (first [ ] item) ────────────────────────────────────
next_step() {
    local file="$1"
    { grep '^\s*- \[ \]' "$file" 2>/dev/null || true; } | head -1 | sed 's/^\s*- \[ \][[:space:]]*//' | cut -c1-80
}

# ─── Collect active WRK items (working/) ───────────────────────────────────
active_section=""
if [[ -d "${QUEUE_DIR}/working" ]]; then
    while IFS= read -r wrk_file; do
        [[ ! -f "$wrk_file" ]] && continue
        wrk_id="$(basename "$wrk_file" .md)"
        title="$(extract_title "$wrk_file")"
        pct="$(percent_complete "$wrk_file")"
        last="$(last_done_step "$wrk_file")"
        next="$(next_step "$wrk_file")"

        entry="- ${wrk_id}: ${title} (${pct} complete)"
        [[ -n "$last" ]] && entry="${entry}
  - Last done: ${last}"
        [[ -n "$next" ]] && entry="${entry}
  - Next: ${next}"

        active_section="${active_section}${entry}
"
    done < <(find "${QUEUE_DIR}/working" -name "WRK-*.md" | sort)
fi

[[ -z "$active_section" ]] && active_section="_No items in working/_"

# ─── Collect recently modified WRK items (git diff) ────────────────────────
recent_section=""
while IFS= read -r rel_path; do
    wrk_file="${WORKSPACE_HUB}/${rel_path}"
    [[ ! -f "$wrk_file" ]] && continue
    wrk_id="$(basename "$wrk_file" .md)"
    title="$(extract_title "$wrk_file")"
    recent_section="${recent_section}- ${wrk_id}: ${title}
"
done < <(git -C "$WORKSPACE_HUB" diff --name-only HEAD 2>/dev/null | grep 'work-queue/.*WRK-' || true)

[[ -z "$recent_section" ]] && recent_section="_No WRK files modified since last commit_"

# ─── Write snapshot ─────────────────────────────────────────────────────────
cat > "$SNAPSHOT" <<EOF
# Session Snapshot — ${TIMESTAMP}
Branch: ${BRANCH}

## Active WRK Items
${active_section}
## Recently Modified
${recent_section}
## Ideas / Notes
_(Claude fills this section with conversational context after running this script)_
EOF

echo "Snapshot written: ${SNAPSHOT}"
echo "Branch: ${BRANCH} | Time: ${TIMESTAMP}"
