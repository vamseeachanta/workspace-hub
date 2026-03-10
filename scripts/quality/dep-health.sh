#!/usr/bin/env bash
# dep-health.sh — Dependency health checks across 5 tier-1 Python repos (WRK-1090)
# Checks: uv.lock freshness, outdated packages, CVE advisories via pip-audit.
# Usage: dep-health.sh [--repo <name>] [--help]
# Exit: 0 = healthy, 1 = CVE HIGH/CRITICAL found or stale lock

set -uo pipefail

REPO_ROOT="${QUALITY_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
# Allow tests to override the scripts dir (for mock next-id.sh)
SCRIPTS_ROOT="${SCRIPTS_OVERRIDE:-$REPO_ROOT}"

declare -A REPO_MAP=(
    [assetutilities]="assetutilities"
    [digitalmodel]="digitalmodel"
    [worldenergydata]="worldenergydata"
    [assethold]="assethold"
    [ogmanufacturing]="OGManufacturing"
)
REPO_ORDER=(assetutilities digitalmodel worldenergydata assethold ogmanufacturing)

OPT_REPO=""

usage() {
    cat << 'EOF'
Usage: dep-health.sh [OPTIONS]

Check dependency health across 5 tier-1 Python repos.

Options:
  --repo <name>   Run only this repo (lowercase)
  --help          Show this help

Exit code: 0 if healthy, 1 if CVE HIGH/CRITICAL found or lock stale.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)  OPT_REPO="${2:?--repo requires a value}"; shift 2 ;;
        --help|-h) usage; exit 0 ;;
        *) echo "ERROR: Unknown flag: $1" >&2; usage >&2; exit 1 ;;
    esac
done

pad_label() { printf "%-18s" "[$1]"; }

EXIT_CODE=0

declare -A FRESHNESS_RESULTS
declare -A OUTDATED_RESULTS
declare -A CVE_RESULTS

# ---------------------------------------------------------------------------
# YAML report setup
# ---------------------------------------------------------------------------
LOG_DIR="$REPO_ROOT/logs/quality"
mkdir -p "$LOG_DIR"
REPORT="$LOG_DIR/dep-health-$(date +%Y-%m-%dT%H%M).yaml"

{
    echo "run_at: \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    echo "repos:"
} > "$REPORT"

# ---------------------------------------------------------------------------
# Per-repo checks
# ---------------------------------------------------------------------------
CVE_BLOCKING_REPOS=()

for key in "${REPO_ORDER[@]}"; do
    [[ -n "$OPT_REPO" && "$OPT_REPO" != "$key" ]] && continue
    repo_rel="${REPO_MAP[$key]}"
    repo_path="$REPO_ROOT/$repo_rel"

    if [[ ! -d "$repo_path" ]]; then
        echo "$(pad_label "$key") SKIP (not found)"
        FRESHNESS_RESULTS[$key]="skip"
        OUTDATED_RESULTS[$key]="skip"
        CVE_RESULTS[$key]="skip"
        continue
    fi

    # ── Freshness ────────────────────────────────────────────────────────────
    freshness_out=$(cd "$repo_path" && uv lock --check --offline 2>&1) && fresh_rc=0 || fresh_rc=$?
    if [[ $fresh_rc -ne 0 ]]; then
        echo "$(pad_label "$key") freshness: STALE"
        FRESHNESS_RESULTS[$key]="stale"
        EXIT_CODE=1
    else
        FRESHNESS_RESULTS[$key]="ok"
    fi

    # ── Outdated ─────────────────────────────────────────────────────────────
    outdated_json=$(cd "$repo_path" && uv run pip list --outdated --format=json 2>/dev/null) || outdated_json="[]"
    pkg_count=$(echo "$outdated_json" | uv run --no-project python -c \
        "import json,sys; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
    if [[ "$pkg_count" -gt 0 ]]; then
        echo "$(pad_label "$key") outdated: WARN ($pkg_count package(s))"
        OUTDATED_RESULTS[$key]="warn:$pkg_count"
    else
        OUTDATED_RESULTS[$key]="ok"
    fi

    # ── CVE scan ─────────────────────────────────────────────────────────────
    req_txt=$(uv export --no-hashes --format requirements-txt --directory "$repo_path" 2>/dev/null || echo "")
    if [[ -z "$req_txt" ]]; then
        CVE_RESULTS[$key]="skip:no-requirements"
    else
        # Capture both stdout and exit code; pip-audit exits 1 when vulns found
        cve_json=$(echo "$req_txt" | uvx pip-audit --format=json --stdin 2>/dev/null || true)
        [[ -z "$cve_json" ]] && cve_json="[]"
        blocking=$(echo "$cve_json" | uv run --no-project python -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = []
count = 0
for pkg in data:
    for v in pkg.get('vulns', []):
        sev = str(v.get('severity', '')).upper()
        if sev in ('HIGH', 'CRITICAL'):
            count += 1
print(count)
" 2>/dev/null || echo "0")
        warn_count=$(echo "$cve_json" | uv run --no-project python -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = []
count = 0
for pkg in data:
    for v in pkg.get('vulns', []):
        sev = str(v.get('severity', '')).upper()
        if sev in ('MEDIUM', 'LOW'):
            count += 1
print(count)
" 2>/dev/null || echo "0")
        if [[ "$blocking" -gt 0 ]]; then
            echo "$(pad_label "$key") CVE: HIGH/CRITICAL ($blocking blocking)"
            CVE_RESULTS[$key]="blocking:$blocking"
            CVE_BLOCKING_REPOS+=("$key")
            EXIT_CODE=1
        elif [[ "$warn_count" -gt 0 ]]; then
            echo "$(pad_label "$key") CVE: WARN ($warn_count medium/low)"
            CVE_RESULTS[$key]="warn:$warn_count"
        else
            CVE_RESULTS[$key]="ok"
        fi
    fi

    # ── YAML report entry ────────────────────────────────────────────────────
    {
        echo "  $key:"
        echo "    freshness: \"${FRESHNESS_RESULTS[$key]}\""
        echo "    outdated: \"${OUTDATED_RESULTS[$key]}\""
        echo "    cves: \"${CVE_RESULTS[$key]}\""
        if [[ "${CVE_RESULTS[$key]}" == blocking* ]]; then
            echo "    status: \"blocking\""
        elif [[ "${FRESHNESS_RESULTS[$key]}" == "stale" ]]; then
            echo "    status: \"stale\""
        else
            echo "    status: \"ok\""
        fi
    } >> "$REPORT"
done

# ---------------------------------------------------------------------------
# Auto-WRK on blocking CVEs
# ---------------------------------------------------------------------------
if [[ ${#CVE_BLOCKING_REPOS[@]} -gt 0 ]]; then
    REPOS_STR="${CVE_BLOCKING_REPOS[*]}"
    LOCKFILE="$REPO_ROOT/.claude/work-queue/state.yaml.lock"
    (
        flock --timeout 10 200 || { echo "WARN: flock timeout — skipping auto-WRK capture"; exit 0; }
        NEXT_ID=$(bash "$SCRIPTS_ROOT/scripts/work-queue/next-id.sh" 2>/dev/null || echo "WRK-AUTO")
        PENDING_DIR="$REPO_ROOT/.claude/work-queue/pending"
        mkdir -p "$PENDING_DIR"
        TMPFILE=$(mktemp)
        cat > "$TMPFILE" << EOF
---
id: ${NEXT_ID}
title: "CVE remediation — HIGH/CRITICAL advisories in: ${REPOS_STR}"
status: pending
priority: high
complexity: simple
created_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
target_repos: [${REPOS_STR// /, }]
computer: ace-linux-1
execution_workstations: [ace-linux-1]
plan_workstations: [ace-linux-1]
category: harness
subcategory: security
auto_captured: true
source: dep-health.sh
---
## Mission

Remediate HIGH/CRITICAL CVEs detected by dep-health.sh in: ${REPOS_STR}

## What

Review dep-health report at: ${REPORT}
Update affected packages to patched versions.
Re-run dep-health.sh to confirm clean scan.

## Acceptance Criteria

- [ ] All blocking CVEs resolved (dep-health.sh exits 0)
- [ ] uv.lock files updated and committed
EOF
        mv "$TMPFILE" "$PENDING_DIR/${NEXT_ID}.md"
        echo "Auto-captured: $PENDING_DIR/${NEXT_ID}.md"
    ) 200>"$LOCKFILE"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
stale_count=$(for k in "${!FRESHNESS_RESULTS[@]}"; do echo "${FRESHNESS_RESULTS[$k]}"; done | grep -c "stale" || true)
outdated_count=$(for k in "${!OUTDATED_RESULTS[@]}"; do echo "${OUTDATED_RESULTS[$k]}"; done | grep -c "^warn" || true)
cve_count=$(for k in "${!CVE_RESULTS[@]}"; do echo "${CVE_RESULTS[$k]}"; done | grep -c "^blocking" || true)
checked=$(echo "${REPO_ORDER[@]}" | wc -w)
[[ -n "$OPT_REPO" ]] && checked=1

echo ""
echo "DEP-HEALTH SUMMARY: ${checked} repos checked, ${stale_count} stale, ${outdated_count} outdated, ${cve_count} blocking CVEs"
echo "Report: $REPORT"

exit "$EXIT_CODE"
