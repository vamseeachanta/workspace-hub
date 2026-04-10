#!/usr/bin/env bash
# health-check.sh — Full ecosystem health report
#
# Usage:
#   bash scripts/upkeep/health-check.sh              # report only
#   bash scripts/upkeep/health-check.sh --markdown    # output as markdown
#   bash scripts/upkeep/health-check.sh --save        # also save to logs/upkeep/
#
# Checks:
#   1. Hermes gateway (alive/dead, last restart)
#   2. Cron jobs (scheduled count, ran today, failed)
#   3. Memory bridge (last run within 26h?)
#   4. Hermes memory (within char limits, fresh)
#   5. Disk filesystem (space, ~/.hermes/ growth)
#   6. Repo sync (unpushed commits across sub-repos)
#   7. Claude memory (.claude/memory/ file freshness)
#
# Exit code: 0 = all pass, 1 = warnings only, 2 = critical failures

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
TODAY="$(date +%Y-%m-%d)"
TODAY_EPOCH="$(date +%s)"
MARKDOWN_MODE=false
SAVE_MODE=false

for arg in "$@"; do
    case "$arg" in
        --markdown) MARKDOWN_MODE=true ;;
        --save) SAVE_MODE=true ;;
    esac
done

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0
CRITICAL_COUNT=0

RESULTS=()

pass() { PASS_COUNT=$((PASS_COUNT+1)); RESULTS+=("PASS|$1|$2"); }
warn() { WARN_COUNT=$((WARN_COUNT+1)); RESULTS+=("WARN|$1|$2"); }
fail() { FAIL_COUNT=$((FAIL_COUNT+1)); RESULTS+=("FAIL|$1|$2"); }
critical() { CRITICAL_COUNT=$((CRITICAL_COUNT+1)); RESULTS+=("CRIT|$1|$2"); }

# =========================================================================
# CHECK 1: Hermes Gateway
# =========================================================================
gateway_status="$(systemctl is-active hermes-gateway.service 2>/dev/null || echo 'not-found')"
if [[ "${gateway_status}" == "active" ]]; then
    last_restart="$(systemctl show hermes-gateway.service --property=ActiveEnterTimestamp 2>/dev/null | cut -d= -f2)"
    pass "Gateway (ACTIVE)" "${last_restart}"
else
    if [[ "${gateway_status}" == "not-found" ]]; then
        critical "Gateway (NOT INSTALLED)" "Service not found - cron jobs cannot fire"
    else
        critical "Gateway (DOWN)" "${gateway_status} $(systemctl status hermes-gateway.service 2>/dev/null | grep 'since' | sed 's/^[[:space:]]*//')"
    fi
fi

# =========================================================================
# CHECK 2: Cron Jobs
# =========================================================================
CRON_JSON="${HOME}/.hermes/cron/jobs.json"
if [[ -f "${CRON_JSON}" ]]; then
    job_count="$(python3 -c "import json; d=json.load(open('${CRON_JSON}')); print(len(d))" 2>/dev/null || echo 0)"
    scheduled="$(python3 -c "import json; d=json.load(open('${CRON_JSON}')); print(len([j for j in d if j.get('state')=='scheduled']))" 2>/dev/null || echo 0)"
    completed="$(python3 -c "import json; d=json.load(open('${CRON_JSON}')); print(len([j for j in d if j.get('state')=='completed']))" 2>/dev/null || echo 0)"
    pass "Cron (${job_count} jobs)" "${scheduled} scheduled (${completed} completed)"
else
    fail "Cron (no jobs.json)" "No cron configuration found"
fi

# Check if cron output has recent entries
CRON_OUTPUT="${HOME}/.hermes/cron/output"
if [[ -d "${CRON_OUTPUT}" ]]; then
    newest="$(find "${CRON_OUTPUT}" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -1)"
    mod_epoch="${newest%%.*}"
    mod_epoch="${mod_epoch:-0}"
    hours_ago=$(( (TODAY_EPOCH - mod_epoch) / 3600 ))
    if [[ ${hours_ago} -lt 26 ]]; then
        pass "Cron output" "Last modified ${hours_ago}h ago"
    else
        warn "Cron output" "Stale — last modified ${hours_ago}h ago"
    fi
elif [[ -f "${CRON_OUTPUT}" && -s "${CRON_OUTPUT}" ]]; then
    mod_epoch="$(stat -c %Y "${CRON_OUTPUT}" 2>/dev/null || echo 0)"
    hours_ago=$(( (TODAY_EPOCH - mod_epoch) / 3600 ))
    if [[ ${hours_ago} -lt 26 ]]; then
        pass "Cron output" "Last modified ${hours_ago}h ago"
    else
        warn "Cron output" "Stale — last modified ${hours_ago}h ago"
    fi
else
    warn "Cron output" "No output file — cron jobs may not be executing"
fi

# =========================================================================
# CHECK 3: Memory Bridge Freshness
# =========================================================================
# Check if bridge ran recently (last commit to .claude/memory/ within 26h)
last_bridge="$(git -C "${REPO_ROOT}" log -1 --format=%ct -- .claude/memory/ 2>/dev/null || echo 0)"
if [[ ${last_bridge} -gt 0 ]]; then
    bridge_hours=$(( (TODAY_EPOCH - last_bridge) / 3600 ))
    if [[ ${bridge_hours} -lt 26 ]]; then
        pass "Memory bridge" "Ran ${bridge_hours}h ago"
    else
        warn "Memory bridge" "Stale — last ran ${bridge_hours}h ago (should be <26h)"
    fi
else
    warn "Memory bridge" "No git commits to .claude/memory/"
fi

# Check drift
drift_script="${REPO_ROOT}/scripts/memory/check-memory-drift.sh"
if [[ -x "${drift_script}" ]]; then
    if bash "${drift_script}" > /tmp/drift-check-$$ 2>&1; then
        pass "Memory drift" "In sync"
    else
        drift_count="$(grep -c "Missing entries:" /tmp/drift-check-$$ 2>/dev/null || echo 0)"
        warn "Memory drift" "Hermes memory has new entries not in repo"
    fi
    rm -f /tmp/drift-check-$$
fi

# =========================================================================
# CHECK 4: Hermes Memory Health
# =========================================================================
for mem_file in MEMORY.md USER.md; do
    mem_path="${HOME}/.hermes/memories/${mem_file}"
    if [[ -f "${mem_path}" ]]; then
        chars="$(wc -c < "${mem_path}")"
        if [[ "${mem_file}" == "MEMORY.md" ]]; then
            limit=2200
        else
            limit=1375
        fi
        if [[ ${chars} -gt ${limit} ]]; then
            fail "Memory ${mem_file}" "Exceeds limit: ${chars}/${limit}"
        elif [[ ${chars} -gt $((limit * 90 / 100)) ]]; then
            warn "Memory ${mem_file}" "Approaching limit: ${chars}/${limit}"
        else
            pass "Memory ${mem_file}" "OK: ${chars}/${limit}"
        fi
    else
        fail "Memory ${mem_file}" "File not found"
    fi
done

# =========================================================================
# CHECK 5: Disk / Filesystem
# =========================================================================
disk_usage="$(df -h / 2>/dev/null | tail -1 | awk '{print $5 " used (" $3 " of " $2 ")" }' || echo "unknown")"
disk_pct="$(df / 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%' || echo 0)"
if [[ ${disk_pct} -gt 90 ]]; then
    fail "Disk space" "Critical: ${disk_usage}"
elif [[ ${disk_pct} -gt 80 ]]; then
    warn "Disk space" "High: ${disk_usage}"
else
    pass "Disk space" "OK: ${disk_usage}"
fi

hermes_size="$(du -sh ~/.hermes 2>/dev/null | awk '{print $1}' || echo "unknown")"
pass "Hermes directory" "${hermes_size}"

claude_size="$(du -sh ~/.claude 2>/dev/null | awk '{print $1}' || echo "unknown")"
pass "Claude directory" "${claude_size}"

# =========================================================================
# CHECK 6: Repo Sync
# =========================================================================
unpushed="$(git -C "${REPO_ROOT}" log --oneline origin/main..main 2>/dev/null | wc -l)"
if [[ ${unpushed} -gt 5 ]]; then
    warn "Repo unpushed" "${unpushed} commits ahead of origin"
elif [[ ${unpushed} -gt 0 ]]; then
    pass "Repo unpushed" "${unpushed} commit(s) to push"
else
    pass "Repo unpushed" "Up to date"
fi

# Check sub-repos
for sub_repo in digitalmodel aceengineer-strategy worldenergydata; do
    sub_path="${REPO_ROOT}/${sub_repo}"
    if [[ -d "${sub_path}/.git" ]]; then
        sub_unpushed="$(git -C "${sub_path}" log --oneline origin/main..main 2>/dev/null | wc -l)"
        if [[ ${sub_unpushed} -gt 0 ]]; then
            warn "${sub_repo} sync" "${sub_unpushed} unpushed commits"
        else
            pass "${sub_repo} sync" "Up to date"
        fi
    fi
done

# =========================================================================
# CHECK 7: Claude Memory Freshness
# =========================================================================
topic_count="$(find "${REPO_ROOT}/.claude/memory/topics" -name '*.md' 2>/dev/null | wc -l)"
if [[ ${topic_count} -gt 0 ]]; then
    pass "Claude topics" "${topic_count} topic files mirrored"
else
    warn "Claude topics" "No topic files — bridge may not have run"
fi

claude_auto="${REPO_ROOT}/.claude/memory/claude-auto-memory.md"
if [[ -f "${claude_auto}" ]]; then
    last_mod="$(stat -c %Y "${claude_auto}" 2>/dev/null || echo 0)"
    snapshot_hours=$(( (TODAY_EPOCH - last_mod) / 3600 ))
    if [[ ${snapshot_hours} -lt 26 ]]; then
        pass "Claude auto snapshot" "Fresh (${snapshot_hours}h ago)"
    else
        warn "Claude auto snapshot" "Stale (${snapshot_hours}h ago)"
    fi
else
    warn "Claude auto snapshot" "No snapshot file"
fi

# =========================================================================
# REPORT
# =========================================================================
TOTAL=$((PASS_COUNT+WARN_COUNT+FAIL_COUNT+CRITICAL_COUNT))

if [[ "${MARKDOWN_MODE}" = true ]] || [[ "${SAVE_MODE}" = true ]]; then
    {
        echo "# Ecosystem Health Report — ${TODAY}"
        echo ""
        echo "| # | Check | Status | Detail |"
        echo "|---|-------|--------|--------|"
        for i in "${!RESULTS[@]}"; do
            IFS='|' read -r sev check detail <<< "${RESULTS[$i]}"
            case "${sev}" in
                PASS) icon="✅" ;;
                WARN) icon="⚠️" ;;
                FAIL) icon="❌" ;;
                CRIT) icon="🔴" ;;
            esac
            echo "| $((i+1)) | ${check} | ${icon} ${sev} | ${detail} |"
        done
        echo ""
        echo "## Summary"
        echo "Total: ${TOTAL} checks · ✅ ${PASS_COUNT} pass · ⚠️ ${WARN_COUNT} warn · ❌ ${FAIL_COUNT} fail · 🔴 ${CRITICAL_COUNT} critical"
        echo ""
        if [[ ${CRITICAL_COUNT} -gt 0 ]]; then
            echo "**Critical issues need immediate attention.**"
            echo ""
            for r in "${RESULTS[@]}"; do
                IFS='|' read -r sev check detail <<< "${r}"
                [[ "${sev}" == "CRIT" ]] && echo "- ${check}: ${detail}"
            done
        fi
    } > /tmp/health-report-$$

    if [[ "${MARKDOWN_MODE}" = true ]]; then
        cat /tmp/health-report-$$
    fi

    if [[ "${SAVE_MODE}" = true ]]; then
        mkdir -p "${REPO_ROOT}/logs/upkeep"
        cp /tmp/health-report-$$ "${REPO_ROOT}/logs/upkeep/${TODAY}-health.md"
        echo "Saved to ${REPO_ROOT}/logs/upkeep/${TODAY}-health.md"
    fi

    rm -f /tmp/health-report-$$
else
    # Terminal output (compact table)
    echo ""
    echo "============================================"
    echo "  Ecosystem Health — ${TODAY}"
    echo "============================================"
    printf "| %-4s | %-20s | %-6s | %s\n" "#" "Check" "Status" "Detail"
    echo "|------|----------------------|--------|-------"
    for i in "${!RESULTS[@]}"; do
        IFS='|' read -r sev check detail <<< "${RESULTS[$i]}"
        case "${sev}" in
            PASS) icon="✅" ;;
            WARN) icon="⚠️" ;;
            FAIL) icon="❌" ;;
            CRIT) icon="🔴" ;;
        esac
        printf "| %-4s | %-20s | %-6s | %s\n" "$((i+1))" "${check}" "${icon}" "${detail}"
    done
    echo "|------|----------------------|--------|-------"
    echo "Total: ${TOTAL} | ✅ ${PASS_COUNT} | ⚠️ ${WARN_COUNT} | ❌ ${FAIL_COUNT} | 🔴 ${CRITICAL_COUNT}"
    echo ""
    if [[ ${CRITICAL_COUNT} -gt 0 ]]; then
        echo "  🔴 CRITICAL ISSUES:"
        for r in "${RESULTS[@]}"; do
            IFS='|' read -r sev check detail <<< "${r}"
            [[ "${sev}" == "CRIT" ]] && echo "    - ${check}: ${detail}"
        done
        echo ""
    fi
fi

# Exit code: 2 if critical, 1 if warnings, 0 if all pass
if [[ ${CRITICAL_COUNT} -gt 0 ]] || [[ ${FAIL_COUNT} -gt 0 ]]; then
    exit 2
elif [[ ${WARN_COUNT} -gt 0 ]]; then
    exit 1
else
    exit 0
fi
