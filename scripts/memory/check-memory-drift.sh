#!/usr/bin/env bash
# check-memory-drift.sh — Warn when Hermes memory is ahead of .claude/memory/
#
# Usage:
#   bash scripts/memory/check-memory-drift.sh           # report only
#   bash scripts/memory/check-memory-drift.sh --fix     # report + run bridge if drift found
#
# Exit codes:
#   0 — in sync (or Hermes not present)
#   1 — drift detected (new Hermes entries not in repo)
#
# Works on Linux and macOS. Safe to run from any directory inside the repo.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
AGENTS_FILE="${REPO_ROOT}/.claude/memory/agents.md"
HERMES_MEM="${HOME}/.hermes/memories/MEMORY.md"
HERMES_USER="${HOME}/.hermes/memories/USER.md"
FIX_MODE="${1:-}"

# Colours
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; NC='\033[0m'

drift_count=0
missing_entries=()

# ---------------------------------------------------------------------------
check_source() {
    local src="$1"
    local label="$2"

    [[ -f "${src}" ]] || return 0

    # Split on § delimiter; each entry is one memory fact
    while IFS= read -r entry; do
        entry="$(echo "${entry}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -z "${entry}" ]] && continue
        [[ "${entry}" == "§" ]] && continue

        # Check if any meaningful substring from this entry exists in agents.md
        # Use words 3-10 as a fingerprint (avoids leading bullets, quotes, dates)
        fingerprint="$(echo "${entry}" | tr -s ' ' | cut -d' ' -f3-10)"

        if [[ -z "${fingerprint}" ]]; then continue; fi
        if ! grep -qF "${fingerprint}" "${AGENTS_FILE}" 2>/dev/null; then
            drift_count=$((drift_count + 1))
            missing_entries+=("  [${label}] ${entry:0:120}")
        fi
    done < <(tr '§' '\n' < "${src}")
}

# ---------------------------------------------------------------------------
echo ""
echo "=== Memory Drift Check ==="
echo "  Hermes MEMORY.md : ${HERMES_MEM}"
echo "  Repo agents.md   : ${AGENTS_FILE}"
echo ""

if [[ ! -f "${AGENTS_FILE}" ]]; then
    echo -e "${RED}ERROR: ${AGENTS_FILE} not found. Run bridge script first.${NC}"
    exit 1
fi

# ── Drift staleness check (#1920) ──────────────────────────────────────────
agents_age_hours=0
if [[ -f "${AGENTS_FILE}" ]]; then
    agents_mtime=$(stat -c %Y "${AGENTS_FILE}" 2>/dev/null || echo 0)
    now=$(date +%s)
    agents_age_hours=$(( (now - agents_mtime) / 3600 ))
fi

if [[ ${agents_age_hours} -gt 48 ]]; then
    echo -e "${RED}⚠️  STALE: agents.md is ${agents_age_hours}h old (threshold: 48h)${NC}"
    echo "  Last modified: $(date -d @${agents_mtime} 2>/dev/null || date -r ${agents_mtime} 2>/dev/null || echo unknown)"
    echo "  Fix: bash scripts/memory/bridge-hermes-claude.sh --commit && git push"
    # If notify.sh exists, send alert
    if [[ -x "${REPO_ROOT}/scripts/notify.sh" ]]; then
        bash "${REPO_ROOT}/scripts/notify.sh" cron memory-drift "warn" "agents.md stale ${agents_age_hours}h" 2>/dev/null || true
    fi
    echo ""
    # Continue to drift check below — still report any content differences
fi

if [[ ! -f "${HERMES_MEM}" && ! -f "${HERMES_USER}" ]]; then
    echo -e "${YELLOW}Hermes memory not found (not on a Hermes machine). Nothing to check.${NC}"
    exit 0
fi

check_source "${HERMES_MEM}" "MEMORY"
check_source "${HERMES_USER}" "USER"

# ---------------------------------------------------------------------------
if [[ ${drift_count} -eq 0 ]]; then
    echo -e "${GREEN}✅  In sync — no drift detected.${NC}"
    echo ""
    exit 0
fi

echo -e "${YELLOW}⚠️   Drift detected: ${drift_count} Hermes entries not found in agents.md${NC}"
echo ""
echo "Missing entries:"
for entry in "${missing_entries[@]}"; do
    echo -e "  ${RED}+${NC} ${entry}"
done
echo ""
echo "Fix: bash scripts/memory/bridge-hermes-claude.sh --commit && git push"

if [[ "${FIX_MODE}" == "--fix" ]]; then
    echo ""
    echo "[drift] --fix mode: running bridge script now..."
    bash "${REPO_ROOT}/scripts/memory/bridge-hermes-claude.sh" --commit
    echo "[drift] Bridge complete. Run 'git push' to propagate."
fi

exit 1
