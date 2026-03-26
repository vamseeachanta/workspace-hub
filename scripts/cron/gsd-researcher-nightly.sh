#!/usr/bin/env bash
# ABOUTME: Nightly GSD researcher — rotates domains by day-of-week, writes to .planning/research/
# ABOUTME: Pipes PROJECT.md + ROADMAP.md as context to claude CLI
# Issue: #1434
#
# Domain rotation:
#   Mon/Thu = standards (offshore/subsea)
#   Tue/Fri = python-ecosystem
#   Wed/Sat = ai-tooling (Claude, GSD, MCP)
#   Sun     = synthesis (week review)
#
# Usage: bash scripts/cron/gsd-researcher-nightly.sh [--dry-run]

set -uo pipefail
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
DAY_NUM=$(date +%u)  # 1=Mon, 7=Sun
TIME_BUDGET=180
DRY_RUN=false
LOG_DIR="${WS_HUB}/logs/research"
OUTPUT_DIR="${WS_HUB}/.planning/research"

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR" "$OUTPUT_DIR"
LOG_FILE="${LOG_DIR}/${DATE}.log"

log() { echo "[gsd-researcher] $(date -u +%H:%M:%S) $*" | tee -a "$LOG_FILE"; }

# ── Hostname guard (reads from workstation registry) ─────────────────────────
source "${WS_HUB}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

# ── Git pull ─────────────────────────────────────────────────────────────────
log "Starting nightly research"
cd "$WS_HUB" || { log "ERROR: cannot cd to $WS_HUB"; exit 1; }
git pull --rebase --quiet 2>>"$LOG_FILE" || {
    log "WARNING: git pull failed — continuing with local state"
}

# ── Domain selection ─────────────────────────────────────────────────────────
case "$DAY_NUM" in
    1|4) DOMAIN="standards" ;;
    2|5) DOMAIN="python-ecosystem" ;;
    3|6) DOMAIN="ai-tooling" ;;
    7)   DOMAIN="synthesis" ;;
    *)   DOMAIN="standards" ;;
esac

log "Domain: ${DOMAIN} (day=${DAY_NUM})"

# ── Context assembly ─────────────────────────────────────────────────────────
CONTEXT=""
for f in .planning/PROJECT.md .planning/ROADMAP.md; do
    if [[ -f "$f" ]]; then
        CONTEXT+="--- $(basename "$f") ---"$'\n'
        CONTEXT+="$(cat "$f")"$'\n\n'
    fi
done

# ── Domain prompts ───────────────────────────────────────────────────────────
OUTPUT_FORMAT='Use this exact output format:

# Research: __DOMAIN__ — __DATE__

## Key Findings
- Finding with source/reference (one bullet per finding, 3-5 findings)

## Relevance to Project
- How each finding affects a specific package or workflow in this project

## Recommended Actions
- [ ] Actionable item (one of: promote to PROJECT.md, create GitHub issue, or ignore with reason)'

case "$DOMAIN" in
    standards)
        PROMPT="You are a research assistant for an offshore/subsea engineering team. Given the project context below, search your knowledge for recent developments in engineering standards relevant to this project. Focus on:
- API (American Petroleum Institute) standards updates
- DNV (Det Norske Veritas) recommended practices and rules
- ABS (American Bureau of Shipping) guides
- ISO standards for offshore/marine structures
- Any regulatory changes affecting cathodic protection, VIV, fitness-for-service, or structural analysis

Report only findings from the past 6 months that are relevant to the packages and domains described in the project context.

${OUTPUT_FORMAT}"
        ;;
    python-ecosystem)
        PROMPT="You are a research assistant tracking the Python packaging ecosystem. Given the project context below, search your knowledge for recent developments relevant to this project. Focus on:
- uv package manager changes, new features, or breaking changes
- Dependencies used by tier-1 packages (numpy, pandas, pyyaml, etc.) — new versions, deprecations, security advisories
- Python packaging standards (PEP updates, pyproject.toml changes)
- Testing ecosystem changes (pytest, coverage tools)
- Any CVEs or security advisories affecting common scientific Python packages

Report only findings from the past 3 months that are relevant to the packages described in the project context.

${OUTPUT_FORMAT}"
        ;;
    ai-tooling)
        PROMPT="You are a research assistant tracking AI developer tooling. Given the project context below, search your knowledge for recent developments relevant to this project. Focus on:
- Claude Code CLI updates, new features, or behavior changes
- GSD framework (get-shit-done) updates and new patterns
- Codex CLI and Gemini CLI changes
- MCP (Model Context Protocol) ecosystem updates — new servers, protocol changes
- Agent SDK developments (Anthropic, OpenAI)
- Multi-agent orchestration patterns

Report only findings from the past 3 months that are relevant to the AI tooling stack described in the project context.

${OUTPUT_FORMAT}"
        ;;
    synthesis)
        # For synthesis, add this week's research files as context
        WEEK_FILES=""
        for f in "${OUTPUT_DIR}/${DATE%%-*}"*.md; do
            [[ -f "$f" ]] || continue
            file_date=$(basename "$f" | grep -oP '^\d{4}-\d{2}-\d{2}' || echo "")
            if [[ -n "$file_date" ]]; then
                days_old=$(( ($(date -d "$DATE" +%s) - $(date -d "$file_date" +%s)) / 86400 )) 2>/dev/null || days_old=99
                if [[ "$days_old" -le 7 ]]; then
                    WEEK_FILES+="--- $(basename "$f") ---"$'\n'
                    WEEK_FILES+="$(cat "$f")"$'\n\n'
                fi
            fi
        done
        CONTEXT+="${WEEK_FILES}"

        PROMPT="You are synthesizing this week's research findings for an engineering team. Review all research reports from this week (provided below) and produce a weekly synthesis. Focus on:
- Rank findings by impact to the project (high/medium/low)
- Identify cross-domain connections (e.g., a Python CVE affecting an engineering package)
- Flag the top 3 insights that should be promoted to PROJECT.md
- Note any findings that warrant a GitHub issue

Output format:

# Weekly Research Synthesis — __DATE__

## Top 3 Insights for PROJECT.md
1. Insight with rationale for promotion
2. ...
3. ...

## Cross-Domain Connections
- Connection between domains

## Action Items
- [ ] Promote: specific insight → PROJECT.md section
- [ ] Issue: specific finding → GitHub issue title
- [ ] Monitor: finding to watch next week"
        ;;
esac

# ── Replace placeholders in prompts ──────────────────────────────────────────
PROMPT="${PROMPT//__DOMAIN__/$DOMAIN}"
PROMPT="${PROMPT//__DATE__/$DATE}"

OUTPUT_FILE="${OUTPUT_DIR}/${DATE}-${DOMAIN}.md"

# ── Dry run ──────────────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == true ]]; then
    log "DRY RUN — would call claude with domain=${DOMAIN}"
    log "Context length: ${#CONTEXT} chars"
    log "Output would go to: ${OUTPUT_FILE}"
    exit 0
fi

# ── Research call ────────────────────────────────────────────────────────────
if ! command -v claude >/dev/null 2>&1; then
    log "ERROR: claude CLI not found in PATH"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "claude CLI not found" || true
    exit 1
fi

log "Calling claude (timeout=${TIME_BUDGET}s)..."
RESULT=$(echo "$CONTEXT" | timeout "$TIME_BUDGET" claude -p "$PROMPT" 2>>"$LOG_FILE") || {
    log "ERROR: claude call failed or timed out"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "claude timeout or error" || true
    exit 1
}

# ── Write output ─────────────────────────────────────────────────────────────
if [[ -z "$RESULT" ]]; then
    log "ERROR: claude returned empty result"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "empty result for domain=${DOMAIN}" || true
    exit 1
fi
echo "$RESULT" > "$OUTPUT_FILE"
log "Research written to: ${OUTPUT_FILE} ($(wc -l < "$OUTPUT_FILE") lines)"

# ── Git commit (best-effort) ─────────────────────────────────────────────────
git add "$OUTPUT_FILE" 2>>"$LOG_FILE" || true
if ! git diff --staged --quiet 2>/dev/null; then
    git commit -m "docs(research): ${DOMAIN} research ${DATE}" --quiet 2>>"$LOG_FILE" || {
        log "WARNING: git commit failed"
    }
    git push --quiet 2>>"$LOG_FILE" || {
        log "WARNING: git push failed — will sync on next repo-sync"
    }
fi

# ── Notify ───────────────────────────────────────────────────────────────────
bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher pass "domain=${DOMAIN}" || true
log "Done"
