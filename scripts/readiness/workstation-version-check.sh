#!/usr/bin/env bash
# workstation-version-check.sh — ANSYS + OrcaFlex version checks for daily readiness
# Runs on Windows workstation via Git Bash / MINGW64.
# Appends a ## Readiness section to logs/daily/YYYY-MM-DD.md.
# Exit codes: 0 = all pass, 1 = one or more checks failed.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
TODAY=$(date +%Y-%m-%d)
DAILY_LOG="${WORKSPACE_HUB}/logs/daily/${TODAY}.md"

pass_count=0
fail_count=0
rows=()

log_pass() { echo "  OK   $1"; pass_count=$((pass_count + 1)); rows+=("| pass | $1 |"); }
log_warn() { echo "  WARN $1"; rows+=("| warn | $1 |"); }
log_fail() { echo "  FAIL $1"; fail_count=$((fail_count + 1)); rows+=("| fail | $1 |"); }

echo "=== Workstation Version Check: ${TODAY} ==="

# ─────────────────────────────────────────────────────────────────────────────
# R-ANSYS: Detect installed ANSYS versions; flag latest expected version
# Expected: v252 (R25.2). Warn if not present; list all found versions.
# ─────────────────────────────────────────────────────────────────────────────
check_ansys() {
  local ansys_root="/c/Program Files/ANSYS Inc"
  local expected_ver="v252"
  if [[ ! -d "$ansys_root" ]]; then
    log_fail "R-ANSYS: ANSYS not found at '$ansys_root'"
    return
  fi
  local versions
  versions=$(ls "$ansys_root" 2>/dev/null | grep -E '^v[0-9]+$' | sort -V | tr '\n' ' ' | sed 's/ $//')
  if [[ -z "$versions" ]]; then
    log_fail "R-ANSYS: no version directories found under '$ansys_root'"
    return
  fi
  local latest
  latest=$(echo "$versions" | tr ' ' '\n' | tail -1)
  if [[ "$latest" == "$expected_ver" ]]; then
    local build=""
    local build_file="${ansys_root}/${latest}/builddate.txt"
    [[ -f "$build_file" ]] && build=$(head -1 "$build_file" 2>/dev/null | tr -d '\r')
    log_pass "R-ANSYS: latest=${latest} (${build}) — installed: ${versions}"
  else
    log_warn "R-ANSYS: latest installed=${latest}, expected ${expected_ver} — installed: ${versions}"
  fi
}
check_ansys || true

# ─────────────────────────────────────────────────────────────────────────────
# R-ORCAFLEX: Detect installed OrcaFlex versions; flag latest expected version
# Expected: 11.6. Warn if not present; confirm OrcaFlex64.exe reachable.
# ─────────────────────────────────────────────────────────────────────────────
check_orcaflex() {
  local orcaflex_root="/c/Program Files (x86)/Orcina/OrcaFlex"
  local expected_ver="11.6"
  if [[ ! -d "$orcaflex_root" ]]; then
    log_fail "R-ORCAFLEX: OrcaFlex not found at '$orcaflex_root'"
    return
  fi
  local versions
  versions=$(ls "$orcaflex_root" 2>/dev/null | grep -E '^[0-9]+\.' | sort -V | tr '\n' ' ' | sed 's/ $//')
  if [[ -z "$versions" ]]; then
    log_fail "R-ORCAFLEX: no version directories under '$orcaflex_root'"
    return
  fi
  local latest
  latest=$(echo "$versions" | tr ' ' '\n' | tail -1)
  local exe="${orcaflex_root}/${latest}/OrcaFlex64.exe"
  if [[ "$latest" == "$expected_ver" && -f "$exe" ]]; then
    log_pass "R-ORCAFLEX: version=${latest}, OrcaFlex64.exe present"
  elif [[ "$latest" == "$expected_ver" ]]; then
    log_warn "R-ORCAFLEX: version=${latest} found but OrcaFlex64.exe missing at '${exe}'"
  else
    log_warn "R-ORCAFLEX: latest installed=${latest}, expected ${expected_ver} — installed: ${versions}"
  fi
}
check_orcaflex || true

# ─────────────────────────────────────────────────────────────────────────────
# Append Readiness section to today's daily log
# ─────────────────────────────────────────────────────────────────────────────
mkdir -p "$(dirname "$DAILY_LOG")"

# Remove any existing Readiness section before re-appending (idempotent)
if [[ -f "$DAILY_LOG" ]]; then
  # Strip from '## Readiness' to end of file if already present
  sed -i '/^## Readiness$/,$ { /^## Readiness$/d; /^.*$/d }' "$DAILY_LOG" 2>/dev/null || true
fi

{
  echo ""
  echo "## Readiness"
  echo ""
  echo "Workstation check: $(date +%Y-%m-%dT%H:%M:%S) — ${fail_count} failed, ${pass_count} passed"
  echo ""
  echo "| Status | Check |"
  echo "|--------|-------|"
  for row in "${rows[@]}"; do
    echo "$row"
  done
  echo ""
} >> "$DAILY_LOG"

echo ""
if [[ "$fail_count" -gt 0 ]]; then
  echo "=== ${fail_count}/$((pass_count + fail_count)) checks failed — see ${DAILY_LOG} ==="
  exit 1
else
  echo "=== All ${pass_count} checks passed — appended to ${DAILY_LOG} ==="
fi
