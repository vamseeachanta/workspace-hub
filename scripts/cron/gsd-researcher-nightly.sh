#!/usr/bin/env bash
# ABOUTME: Nightly GSD researcher — rotates domains by day-of-week, writes to .planning/research/
# ABOUTME: Pipes PROJECT.md + ROADMAP.md as context to claude CLI
# Issue: #1434
#
# Domain rotation:
#   Mon = standards (offshore/subsea)
#   Tue = python-ecosystem
#   Wed = ai-tooling (Claude, GSD, MCP)
#   Thu = competitor/market (Sesam, SACS, OrcaFlex, etc.)
#   Fri = synthesis (week review + action table)
#   Sat = skill-design (agent skill authoring patterns, low-cost haiku)
#   Sun = off (no API cost)
#
# Usage: bash scripts/cron/gsd-researcher-nightly.sh [--dry-run]

set -uo pipefail
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
DAY_NUM=$(date +%u)  # 1=Mon, 7=Sun
TIME_BUDGET=300
DRY_RUN=false
LOG_DIR="${WS_HUB}/logs/research"
OUTPUT_DIR="${WS_HUB}/.planning/research"
MAX_CONTEXT_CHARS=120000

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR" "$OUTPUT_DIR"
LOG_FILE="${LOG_DIR}/${DATE}.log"

log() { echo "[gsd-researcher] $(date -u +%H:%M:%S) $*" >> "$LOG_FILE"; }

# ── Hostname guard (reads from workstation registry) ─────────────────────────
source "${WS_HUB}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

# ── Git helpers (shared library) ─────────────────────────────────────────────
# All cron scripts use the same lock + heal + retry-push library (#1548)
GIT_SAFE_LOG_PREFIX="[gsd-researcher]"
source "${WS_HUB}/scripts/cron/lib/git-safe.sh"
git_safe_init "$WS_HUB" 2>>"$LOG_FILE"

# ── Git pull ─────────────────────────────────────────────────────────────────
log "Starting nightly research"
cd "$WS_HUB" || { log "ERROR: cannot cd to $WS_HUB"; exit 1; }
git_safe_pull 2>>"$LOG_FILE" || {
    log "WARNING: git pull failed — continuing with local state"
}

# ── Domain selection ─────────────────────────────────────────────────────────
case "$DAY_NUM" in
    1) DOMAIN="standards" ;;
    2) DOMAIN="python-ecosystem" ;;
    3) DOMAIN="ai-tooling" ;;
    4) DOMAIN="competitor-market" ;;
    5) DOMAIN="synthesis" ;;
    6) DOMAIN="skill-design" ;;
    7)
        log "SKIP: Sunday (day=${DAY_NUM})"
        exit 0
        ;;
esac

# Model selection: Haiku for daily scans, Sonnet for synthesis (D-11)
if [[ "$DOMAIN" == "synthesis" ]]; then
    MODEL="sonnet"
    BUDGET="2.00"
else
    MODEL="haiku"
    BUDGET="0.50"
fi

log "Domain: ${DOMAIN} (day=${DAY_NUM}), model: ${MODEL}, budget: \$${BUDGET}"

# ── Context assembly ─────────────────────────────────────────────────────────
CONTEXT=""
for f in .planning/PROJECT.md .planning/ROADMAP.md; do
    if [[ -f "$f" ]]; then
        CONTEXT+="--- $(basename "$f") ---"$'\n'
        CONTEXT+="$(cat "$f")"$'\n\n'
    fi
done

# Prior research context — last 7 days of all domains (D-10)
for f in "${OUTPUT_DIR}"/*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename "$f")" == "README.md" ]] && continue
    file_date=$(basename "$f" | grep -oP '^\d{4}-\d{2}-\d{2}' || echo "")
    if [[ -n "$file_date" ]]; then
        days_old=$(( ($(date -d "$DATE" +%s) - $(date -d "$file_date" +%s)) / 86400 )) 2>/dev/null || days_old=99
        if [[ "$days_old" -le 7 && "$days_old" -ge 0 ]]; then
            CONTEXT+="--- prior-research: $(basename "$f") ---"$'\n'
            CONTEXT+="$(cat "$f")"$'\n\n'
        fi
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
    competitor-market)
        PROMPT="You are a research assistant tracking the competitive landscape for offshore/subsea engineering software. Given the project context below, search for recent developments in competing tools. Focus on:
- Sesam (Wood Group) — structural analysis updates, new modules, pricing changes
- SACS (Bentley) — offshore structural analysis, version updates, cloud offerings
- OrcaFlex (Orcina) — dynamic analysis, new cable/riser models, licensing changes
- Flexcom (Wood Group) — flexible pipe/riser analysis, new capabilities
- ANSYS (Ansys Inc) — mechanical/structural updates relevant to offshore, API changes
- Any new entrants in offshore/subsea engineering software
- Open-source alternatives gaining traction (OpenFAST, Blue Kenue, etc.)

Report pricing changes, new capabilities, deprecated features, and any shifts that create opportunities or threats for aceengineer.com's calculator and consulting positioning.

${OUTPUT_FORMAT}"
        ;;
    skill-design)
        PROMPT="You are a research assistant tracking agent skill design and authoring patterns. Given the project context below, search your knowledge for recent developments relevant to this project's skill system. Focus on:
- Latest Anthropic Claude skill authoring patterns (CLAUDE.md, AGENTS.md)
- Community best practices for AGENTS.md and CLAUDE.md in production repos
- Agent skill specification updates or emerging standards across vendors
- Progressive disclosure patterns for agent instructions (directory scoping, context-aware loading)
- Skill testing and evaluation approaches (canary tasks, regression testing, metrics)
- Multi-agent skill coordination (delegation boundaries, skill registries, inheritance)

Report only findings from the past 3 months that are relevant to the skill architecture described in the project context.

${OUTPUT_FORMAT}"
        ;;
    synthesis)
        PROMPT="You are synthesizing this week's research findings for an engineering team. Review all research reports from this week (provided below) and produce a weekly synthesis.

Output format:

# Weekly Research Synthesis — __DATE__

## Action Table
| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| [finding] | High/Medium/Low | Promote to PROJECT.md / Create GitHub issue / Monitor / Ignore | Pending |

## Top 3 Insights for PROJECT.md
1. Insight with rationale for promotion
2. ...
3. ...

## Cross-Domain Connections
- Connection between domains

## Detailed Action Items
- [ ] Promote: specific insight -> PROJECT.md section
- [ ] Issue: specific finding -> GitHub issue title
- [ ] Monitor: finding to watch next week"
        ;;
esac

# ── Replace placeholders in prompts ──────────────────────────────────────────
PROMPT="${PROMPT//__DOMAIN__/$DOMAIN}"
PROMPT="${PROMPT//__DATE__/$DATE}"

OUTPUT_FILE="${OUTPUT_DIR}/${DATE}-${DOMAIN}.md"

# ── Dry run ──────────────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == true ]]; then
    log "DRY RUN — domain=${DOMAIN}, model=${MODEL}, budget=\$${BUDGET}"
    log "Tools: Read,WebSearch | Context length: ${#CONTEXT} chars"
    log "Output would go to: ${OUTPUT_FILE}"
    echo "[DRY RUN] domain=${DOMAIN} model=${MODEL} budget=\$${BUDGET} tools=Read,WebSearch context=${#CONTEXT}chars output=${OUTPUT_FILE}"
    exit 0
fi

# ── Output validation (D-12) ─────────────────────────────────────────────────
trim_to_heading() {
    local file="$1"
    local tmp
    tmp=$(mktemp)
    awk '
        /^# Research: / || /^# Weekly Research Synthesis / {seen=1}
        seen {print}
    ' "$file" > "$tmp"
    if [[ -s "$tmp" ]]; then
        mv "$tmp" "$file"
    else
        rm -f "$tmp"
    fi
}

validate_output() {
    local file="$1"
    local domain="$2"
    local missing=()

    if [[ "$domain" == "synthesis" ]]; then
        grep -qi "action table" "$file"              || missing+=("Action Table")
        grep -qi "top 3 insights" "$file"            || missing+=("Top 3 Insights")
        grep -qi "cross-domain connections" "$file"  || missing+=("Cross-Domain Connections")
        grep -qi "detailed action items" "$file"     || missing+=("Detailed Action Items")
    else
        grep -qi "key findings" "$file"          || missing+=("Key Findings")
        # BUG FIX I-3: "relevance" is too loose — matches any occurrence of the word.
        # Match the actual heading "## Relevance to Project" to avoid false positives.
        grep -qiP "^#+\s.*relevance" "$file"   || missing+=("Relevance to Project")
        grep -qi "recommended actions" "$file"  || missing+=("Recommended Actions")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "${missing[*]}"
        return 1
    fi
    return 0
}

run_claude() {
    local context="$1"
    echo "$context" | timeout "$TIME_BUDGET" claude -p "$PROMPT" \
        --model "$MODEL" \
        --tools "Read,WebSearch" \
        --allowedTools "Read WebSearch" \
        --max-budget-usd "$BUDGET" \
        --no-session-persistence \
        2>>"$LOG_FILE"
}

build_reduced_context() {
    local base_context="$1"
    if [[ ${#base_context} -le $MAX_CONTEXT_CHARS ]]; then
        printf '%s' "$base_context"
    else
        printf '%s' "${base_context:0:$MAX_CONTEXT_CHARS}"
    fi
}

# ── Research call ────────────────────────────────────────────────────────────
if ! command -v claude >/dev/null 2>&1; then
    log "ERROR: claude CLI not found in PATH"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "claude CLI not found" || true
    exit 1
fi

log "Calling claude (timeout=${TIME_BUDGET}s, model=${MODEL}, budget=\$${BUDGET})..."
RESULT=$(run_claude "$CONTEXT") || RESULT=""
if [[ -z "$RESULT" ]]; then
    log "WARNING: primary claude call failed or timed out — retrying once with reduced context"
    REDUCED_CONTEXT=$(build_reduced_context "$CONTEXT")
    RESULT=$(run_claude "$REDUCED_CONTEXT") || RESULT=""
    if [[ -z "$RESULT" ]]; then
        log "ERROR: claude call failed or timed out after retry"
        bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "claude timeout or error after retry" || true
        exit 1
    fi
fi

# ── Write output ─────────────────────────────────────────────────────────────
if [[ -z "$RESULT" ]]; then
    log "ERROR: claude returned empty result"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "empty result for domain=${DOMAIN}" || true
    exit 1
fi
echo "$RESULT" > "$OUTPUT_FILE"
trim_to_heading "$OUTPUT_FILE"

# Validate output structure (D-12)
MISSING=$(validate_output "$OUTPUT_FILE" "$DOMAIN") || {
    log "WARNING: output missing sections: ${MISSING} — retrying with explicit section guidance"
    # BUG FIX I-4: Don't send identical prompt on retry — add explicit guidance
    # about which sections were missing so the retry is more likely to succeed.
    REDUCED_CONTEXT=$(build_reduced_context "$CONTEXT")
    ORIG_PROMPT="$PROMPT"
    PROMPT="IMPORTANT: Your previous response was missing these required sections: ${MISSING}. Make sure to include ALL of them this time.

${PROMPT}"
    RESULT=$(run_claude "$REDUCED_CONTEXT") || RESULT=""
    PROMPT="$ORIG_PROMPT"  # restore original prompt
    if [[ -z "$RESULT" ]]; then
        log "ERROR: retry claude call failed"
        bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "retry failed for domain=${DOMAIN}" || true
        exit 1
    fi
    echo "$RESULT" > "$OUTPUT_FILE"
    trim_to_heading "$OUTPUT_FILE"
    MISSING=$(validate_output "$OUTPUT_FILE" "$DOMAIN") || {
        log "WARNING: retry still missing sections: ${MISSING} — accepting output anyway"
    }
}
log "Research written to: ${OUTPUT_FILE} ($(wc -l < "$OUTPUT_FILE") lines)"

# ── Git commit + push (best-effort, via shared library) ──────────────────────
cd "$WS_HUB"
git_safe_commit "docs(research): ${DOMAIN} research ${DATE}" "$OUTPUT_FILE" 2>>"$LOG_FILE" || {
    log "WARNING: git commit failed"
}
git_safe_push 2>>"$LOG_FILE" || {
    log "WARNING: git push failed — will sync on next repo-sync cycle"
}

# ── Prune old research artifacts: 90 days for daily, 365 days for synthesis (D-08) ──
log "Pruning old research artifacts..."
PRUNED_DAILY=$(find "$OUTPUT_DIR" -name "????-??-??-*.md" ! -name "*-synthesis.md" -mtime +90 -delete -print 2>/dev/null | wc -l)
PRUNED_SYNTH=$(find "$OUTPUT_DIR" -name "*-synthesis.md" -mtime +365 -delete -print 2>/dev/null | wc -l)
log "Pruned: ${PRUNED_DAILY} daily, ${PRUNED_SYNTH} synthesis artifacts"

# ── Notify ───────────────────────────────────────────────────────────────────
bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher pass "domain=${DOMAIN}" || true
log "Done"
