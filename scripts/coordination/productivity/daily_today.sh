#!/usr/bin/env bash
# ABOUTME: Daily productivity review — orchestrates section scripts into a daily log
# ABOUTME: Each section lives in scripts/productivity/sections/
# Usage: ./daily_today.sh [--week] [--interactive]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECTIONS_DIR="$SCRIPT_DIR/sections"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DAILY_LOG_DIR="$WORKSPACE_ROOT/logs/daily"
WEEKLY_LOG_DIR="$WORKSPACE_ROOT/logs/weekly"
TODAY=$(date +%Y-%m-%d)
WEEK_NUM=$(date +%Y-W%V)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

[[ -t 1 ]] && GREEN='\033[0;32m' YELLOW='\033[1;33m' NC='\033[0m' || GREEN='' YELLOW='' NC=''
log()  { echo -e "${GREEN}[today]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }

mkdir -p "$DAILY_LOG_DIR" "$WEEKLY_LOG_DIR"

MODE="daily"
INTERACTIVE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --week|-w)      MODE="weekly";      shift ;;
        --interactive|-i) INTERACTIVE=true; shift ;;
        --help|-h) echo "Usage: $0 [--week] [--interactive]"; exit 0 ;;
        *) shift ;;
    esac
done

# ── section runner — calls a section script, falls back gracefully ────────────
run_section() {
    local script="$SECTIONS_DIR/$1"; shift
    if [[ -x "$script" ]]; then
        bash "$script" "$@"
    else
        warn "Section not found: $script"
    fi
    echo ""
}

# ── generate daily log ────────────────────────────────────────────────────────
generate_daily() {
    local out="$DAILY_LOG_DIR/${TODAY}.md"
    log "Generating daily summary for $TODAY"

    {
        printf -- "---\ndate: %s\ngenerated: %s\nreviewed: false\n---\n\n" \
            "$TODAY" "$(date -Iseconds)"
        echo "# Daily Log - $TODAY"
        echo ""

        run_section ai-usage-summary.sh   "$WORKSPACE_ROOT"
        run_section wrk-health.sh         "$WORKSPACE_ROOT"

        echo "## Summary"
        echo ""
        run_section git-summary.sh        "$WORKSPACE_ROOT" "$YESTERDAY"
        run_section branch-status.sh      "$WORKSPACE_ROOT"
        run_section suggestions.sh        "$WORKSPACE_ROOT" "$DAILY_LOG_DIR"

        echo "## Today's Priorities"
        echo ""
        printf "1. [ ] \n2. [ ] \n3. [ ] \n"
        echo ""
        echo "## Notes"
        echo ""
        echo "_Add notes throughout the day_"
        echo ""
        echo "## End of Day Review"
        echo ""
        printf -- "- [ ] Priorities completed\n- [ ] Blockers logged\n- [ ] Tomorrow's focus identified\n"

    } > "$out"

    log "Daily log saved to: $out"
    echo ""
    cat "$out"
}

# ── generate weekly log ───────────────────────────────────────────────────────
generate_weekly() {
    local out="$WEEKLY_LOG_DIR/${WEEK_NUM}.md"
    local week_start; week_start=$(date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-monday +%Y-%m-%d)
    log "Generating weekly summary for $WEEK_NUM"

    {
        printf -- "---\nweek: %s\ngenerated: %s\nreviewed: false\n---\n\n" \
            "$WEEK_NUM" "$(date -Iseconds)"
        echo "# Weekly Summary - $WEEK_NUM"
        echo ""

        run_section git-summary.sh   "$WORKSPACE_ROOT" "$week_start"
        run_section wrk-health.sh    "$WORKSPACE_ROOT"

        echo "### Daily Logs This Week"
        echo ""
        find "$DAILY_LOG_DIR" -name "*.md" -mtime -7 2>/dev/null \
            | sort | while read -r f; do echo "- $(basename "$f" .md)"; done
        echo ""

        run_section suggestions.sh   "$WORKSPACE_ROOT" "$DAILY_LOG_DIR"

        echo "## Next Week Focus"
        echo ""
        printf "1. [ ] \n2. [ ] \n3. [ ] \n"
        echo ""
        echo "## Retrospective"
        echo ""
        printf "### What went well\n\n### What could improve\n\n### Action items\n"

    } > "$out"

    log "Weekly summary saved to: $out"
    echo ""
    cat "$out"
}

# ── main ──────────────────────────────────────────────────────────────────────
log "Starting daily productivity review"
log "Workspace: $WORKSPACE_ROOT"
log "Mode: $MODE"
echo ""

[[ "$MODE" == "weekly" ]] && generate_weekly || generate_daily

if [[ "$INTERACTIVE" == true ]]; then
    command -v claude &>/dev/null \
        && claude --resume "Review today's productivity summary and suggest improvements" \
        || warn "Claude Code CLI not found"
fi

log "Done!"
