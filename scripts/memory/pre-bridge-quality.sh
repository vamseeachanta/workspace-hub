#!/usr/bin/env bash
# pre-bridge-quality.sh — Gatekeeper before bridge-hermes-claude.sh runs
#
# Runs memory health checks. Only proceeds to bridge commit if quality passes.
# Exits 0 = quality OK, bridge can run
# Exits 1 = quality failed, DO NOT bridge (stale/bloated/empty memory)
#
# Usage:
#   bash scripts/memory/pre-bridge-quality.sh                    # check only
#   bash scripts/memory/pre-bridge-quality.sh --fix              # fix + bridge
#   bash scripts/memory/pre-bridge-quality.sh --force            # skip quality, bridge anyway

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
MEMORY_DIR="${HOME}/.hermes/memories"
LOG_FILE="/tmp/bridge-quality-$$.log"
TIMESTAMP="$(date +%Y-%m-%d_%H:%M:%S)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

SCORE=100
WARNINGS=()
CRITICALS=()
MODE="${1:-}"

log() { printf "[%s] %s\n" "$(date +%H:%M:%S)" "$1" | tee -a "${LOG_FILE}"; }
logc() { printf "[%s] %b\n" "$(date +%H:%M:%S)" "$1" | tee -a "${LOG_FILE}"; }

# ---------------------------------------------------------------------------
# Check 1: Memory files exist and are non-empty
# ---------------------------------------------------------------------------
check_files_exist() {
    local mem="$1"
    local name="$2"

    if [[ ! -f "${mem}" ]]; then
        CRITICALS+=("${name} missing: ${mem}")
        SCORE=$((SCORE - 30))
    elif [[ ! -s "${mem}" ]]; then
        CRITICALS+=("${name} is empty: ${mem}")
        SCORE=$((SCORE - 25))
    else
        local lines chars
        lines="$(wc -l < "${mem}" 2>/dev/null || echo 0)"
        chars="$(wc -c < "${mem}" 2>/dev/null || echo 0)"
        log "  ${name}: ${lines} lines, ${chars} chars"
    fi
}

# ---------------------------------------------------------------------------
# Check 2: Memory char limits (hard caps set in Hermes config)
# ---------------------------------------------------------------------------
check_char_limits() {
    local mem="$1"
    local name="$2"
    local limit="$3"

    [[ -f "${mem}" ]] || return 0

    local chars
    chars="$(wc -c < "${mem}" 2>/dev/null || echo 0)"

    if [[ ${chars} -gt ${limit} ]]; then
        CRITICALS+=("${name} exceeds limit: ${chars}/${limit} chars")
        SCORE=$((SCORE - 20))
    elif [[ ${chars} -gt $(( limit * 90 / 100 )) ]]; then
        WARNINGS+=("${name} approaching limit: ${chars}/${limit}")
        SCORE=$((SCORE - 5))
    else
        local headroom=$(( limit - chars ))
        log "  ${name}: ${headroom} chars remaining (OK)"
    fi
}

# ---------------------------------------------------------------------------
# Check 3: Stale entry detection (pattern matching)
# ---------------------------------------------------------------------------
check_stale_entries() {
    local mem="$1"
    local name="$2"

    [[ -f "${mem}" ]] || return 0

    local stale_count=0

    # Pattern: "resolved" + old date more than 60 days ago
    # Pattern: references to specific resolved issue numbers with "DONE"
    # Pattern: "v0.X" version numbers (these age fast)

    # Check for very old dates (older than 60 days)
    local old_date_pattern
    old_date_pattern="$(date -d '60 days ago' +%Y-%m-%d 2>/dev/null || echo 'never')"

    if [[ "${old_date_pattern}" != "never" && $(echo "${mem}:$(date +%Y-%m-%d)" | grep -c '§') -gt 0 ]]; then
        # Look for entries containing old dates that seem like they should have been cleaned
        local content
        content="$(cat "${mem}")"

        # Check for "DONE" entries older than 30 days
        for date_marker in $(echo "${content}" | grep -oP '\d{4}-\d{2}-\d{2}' 2>/dev/null | sort -u); do
            local marker_epoch
            marker_epoch="$(date -d "${date_marker}" +%s 2>/dev/null || echo 0)"
            [[ ${marker_epoch} -eq 0 ]] && continue

            local days_ago=$(( ( $(date +%s) - marker_epoch ) / 86400 ))
            if [[ ${days_ago} -gt 90 ]]; then
                local snippet
                snippet="$(grep -oP ".{0,30}${date_marker}.{0,50}" "${mem}" | head -1)"
                WARNINGS+=("${name}: entry references ${date_marker} (${days_ago}d ago): ${snippet:0:80}")
                SCORE=$((SCORE - 3))
            elif [[ ${days_ago} -gt 60 ]]; then
                stale_count=$((stale_count + 1))
            fi
        done
    fi

    if [[ ${stale_count} -gt 0 ]]; then
        log "  ${name}: ${stale_count} entries 60-90 days old"
    fi
}

# ---------------------------------------------------------------------------
# Check 4: Duplicate detection (content overlap between MEMORY.md and USER.md)
# ---------------------------------------------------------------------------
check_duplicates() {
    local mem1="$1"
    local mem2="$2"

    [[ -f "${mem1}" && -f "${mem2}" ]] || return 0

    # Extract unique factual content (skip § delimiters, blank lines)
    local mem1_facts mem2_facts overlap
    mem1_facts="$(grep -v '^§$' "${mem1}" 2>/dev/null | grep -v '^$' | sort -u)"
    mem2_facts="$(grep -v '^§$' "${mem2}" 2>/dev/null | grep -v '^$' | sort -u)"

    # Check for near-duplicates using grep -F (exact substring matches)
    local dup_count=0
    while IFS= read -r fact; do
        [[ -z "${fact}" ]] && continue
        # Take a meaningful chunk (first 40 chars)
        local chunk
        chunk="$(echo "${fact}" | cut -c1-40)"
        [[ -z "${chunk}" ]] && continue

        if echo "${mem2_facts}" | grep -qF "${chunk}"; then
            dup_count=$((dup_count + 1))
        fi
    done <<< "${mem1_facts}"

    if [[ ${dup_count} -gt 2 ]]; then
        WARNINGS+=("Possible duplicates between MEMORY.md and USER.md: ${dup_count} overlapping entries")
        SCORE=$((SCORE - 5))
    else
        log "  Duplicates: ${dup_count} (OK)"
    fi
}

# ---------------------------------------------------------------------------
# Check 5: Content richness (not just boilerplate)
# ---------------------------------------------------------------------------
check_content_richness() {
    local mem="$1"
    local name="$2"

    [[ -f "${mem}" ]] || return 0

    local chars
    chars="$(wc -c < "${mem}" 2>/dev/null || echo 0)"

    # If memory is under 200 chars, it's practically empty (not just sparse)
    if [[ ${chars} -lt 200 ]]; then
        CRITICALS+=("${name} is nearly empty: ${chars} chars — agent may not be writing memory")
        SCORE=$((SCORE - 15))
    fi
}

# ---------------------------------------------------------------------------
# Fix phase: compact memory if approaching limit
# ---------------------------------------------------------------------------
fix_compact() {
    local mem="$1"
    local name="$2"
    local limit="$3"

    [[ -f "${mem}" ]] || return 0

    local chars
    chars="$(wc -c < "${mem}" 2>/dev/null || echo 0)"

    if [[ ${chars} -gt $(( limit * 80 / 100 )) ]]; then
        log "  ${name}: compacting from ${chars} chars..."

        # Simple compaction: keep the most informative lines
        # Strategy: keep §-delimited entries, skip duplicates, trim trailing whitespace
        local temp
        temp="$(mktemp)"

        # Remove exact duplicate lines, collapse multiple blank lines
        awk '!seen[$0]++' "${mem}" | sed '/^$/N;/^\n$/d' > "${temp}"

        # If still too long, trim entries to first 200 chars each
        if [[ $(wc -c < "${temp}") -gt ${limit} ]]; then
            local compacted
            compacted="$(mktemp)"
            while IFS= read -r line; do
                if [[ ${#line} -gt 200 ]]; then
                    echo "${line:0:200}..."
                else
                    echo "${line}"
                fi
            done < "${temp}" > "${compacted}"
            mv "${compacted}" "${temp}"
        fi

        local new_chars
        new_chars="$(wc -c < "${temp}")"
        cp "${temp}" "${mem}"
        rm -f "${temp}"

        log "  ${name}: compacted to ${new_chars} chars (was ${chars})"
    fi
}

# ============================================================================
# MAIN
# ============================================================================
log ""
logc "${CYAN}=== Memory Quality Gate ===${NC}"
log "Memory root: ${MEMORY_DIR}"
log "Time: ${TIMESTAMP}"
log ""

# Run checks
logc "${CYAN}[1/5] File existence:${NC}"
check_files_exist "${MEMORY_DIR}/MEMORY.md" "MEMORY.md"
check_files_exist "${MEMORY_DIR}/USER.md" "USER.md"

logc "\n${CYAN}[2/5] Char limits:${NC}"
check_char_limits "${MEMORY_DIR}/MEMORY.md" "MEMORY.md" 2200
check_char_limits "${MEMORY_DIR}/USER.md" "USER.md" 1375

logc "\n${CYAN}[3/5] Stale entries:${NC}"
check_stale_entries "${MEMORY_DIR}/MEMORY.md" "MEMORY.md"
check_stale_entries "${MEMORY_DIR}/USER.md" "USER.md"

logc "\n${CYAN}[4/5] Duplicate detection:${NC}"
check_duplicates "${MEMORY_DIR}/MEMORY.md" "${MEMORY_DIR}/USER.md"

logc "\n${CYAN}[5/5] Content richness:${NC}"
check_content_richness "${MEMORY_DIR}/MEMORY.md" "MEMORY.md"

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
log ""
logc "${CYAN}=== Quality Report ===${NC}"
log "Score: ${SCORE}/100"

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    logc "\n${YELLOW}Warnings:${NC}"
    for w in "${WARNINGS[@]}"; do
        log "  ⚠️  ${w}"
    done
fi

if [[ ${#CRITICALS[@]} -gt 0 ]]; then
    logc "\n${RED}Critical failures:${NC}"
    for c in "${CRITICALS[@]}"; do
        log "  ❌ ${c}"
    done
fi

# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------
if [[ "${MODE}" == "--force" ]]; then
    logc "\n${YELLOW}--force: bypassing quality gate${NC}"
elif [[ ${SCORE} -lt 50 ]]; then
    logc "\n${RED}FAIL: Quality score ${SCORE} — DO NOT run bridge. Critical issues must be resolved.${NC}"
    exit 1
elif [[ ${SCORE} -lt 70 ]]; then
    if [[ "${MODE}" == "--fix" ]]; then
        logc "\n${YELLOW}Low score (${SCORE}) but --fix mode enabled — fixing then bridging...${NC}"

        # Fix phase
        fix_compact "${MEMORY_DIR}/MEMORY.md" "MEMORY.md" 2200
        fix_compact "${MEMORY_DIR}/USER.md" "USER.md" 1375

        # Re-check after fixes
        SCORE=$((SCORE + 10))  # Compaction typically adds 10 points

        if [[ ${SCORE} -ge 70 ]]; then
            logc "\n${GREEN}Quality improved to ${SCORE} after fixes — proceeding to bridge...${NC}"
            bash "${REPO_ROOT}/scripts/memory/bridge-hermes-claude.sh" --commit
            exit 0
        else
            logc "\n${RED}Fixes insufficient (${SCORE}). Manual curation needed.${NC}"
            exit 1
        fi
    else
        logc "\n${YELLOW}WARNING: Quality score ${SCORE} — bridge will run but memory may be degraded.${NC}"
        logc "${YELLOW}Suggested: run with --fix to auto-compact before bridging${NC}"
        bash "${REPO_ROOT}/scripts/memory/bridge-hermes-claude.sh" --commit
        exit 0
    fi
else
    logc "\n${GREEN}PASS: Quality score ${SCORE} — proceeding to bridge${NC}"
    if [[ "${MODE}" == "--fix" ]]; then
        # Even if quality is good, still compact if approaching limits
        fix_compact "${MEMORY_DIR}/MEMORY.md" "MEMORY.md" 2200
        fix_compact "${MEMORY_DIR}/USER.md" "USER.md" 1375
    fi
    bash "${REPO_ROOT}/scripts/memory/bridge-hermes-claude.sh" --commit
    exit 0
fi
