#!/usr/bin/env bash
# nightly-readiness.sh — 11 ecosystem health checks for the nightly cron pipeline
# Called from comprehensive-learning-nightly.sh Step 5 (WRK-308)
# Each check is best-effort: failures are logged but never abort the pipeline.
# Issues append to .claude/state/readiness-issues.md for Phase 6 to surface.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
ISSUES_FILE="${STATE_DIR}/readiness-issues.md"
RUN_TS=$(date +%Y-%m-%dT%H:%M:%S)

mkdir -p "$STATE_DIR"

# Accumulate issues in memory; write once at end
issues=()
pass_count=0
fail_count=0
declare -A check_results=()
declare -A check_details=()

log_pass() {
  echo "  OK  $1"
  pass_count=$((pass_count + 1))
  local cid="${1%%:*}"
  check_results["$cid"]="pass"
  check_details["$cid"]="${1#*: }"
}
log_fail() {
  echo "  FAIL $1"
  issues+=("$1")
  fail_count=$((fail_count + 1))
  local cid="${1%%:*}"
  check_results["$cid"]="fail"
  check_details["$cid"]="${1#*: }"
}

echo "--- Readiness: ${RUN_TS} ---"

# ─────────────────────────────────────────────────────────────────────────────
# R1: Memory files ≤ 200 lines
# ─────────────────────────────────────────────────────────────────────────────
check_r1() {
  local mem_dir="${WORKSPACE_HUB}/.claude/memory"
  [[ -d "$mem_dir" ]] || { log_pass "R1: memory/ absent — skip"; return; }
  local over=()
  while IFS= read -r -d '' f; do
    local lc
    lc=$(wc -l < "$f" 2>/dev/null || echo 0)
    [[ "$lc" -gt 200 ]] && over+=("$(basename "$f"):${lc}L")
  done < <(find "$mem_dir" -name "*.md" -print0 2>/dev/null)
  if [[ ${#over[@]} -eq 0 ]]; then
    log_pass "R1: memory files ≤ 200 lines"
  else
    log_fail "R1: memory files over 200 lines: ${over[*]}"
  fi
} ; check_r1 || true

# ─────────────────────────────────────────────────────────────────────────────
# R5: Context budget — key context files ≤ 16KB total
# Budget: Global 2KB + Workspace 4KB + Project 8KB + Local 2KB = 16KB
# ─────────────────────────────────────────────────────────────────────────────
check_r5() {
  local total=0
  local candidates=(
    "${WORKSPACE_HUB}/CLAUDE.md"
    "${WORKSPACE_HUB}/.claude/rules/coding-style.md"
    "${WORKSPACE_HUB}/.claude/rules/git-workflow.md"
    "${WORKSPACE_HUB}/.claude/rules/legal-compliance.md"
    "${WORKSPACE_HUB}/.claude/rules/patterns.md"
    "${WORKSPACE_HUB}/.claude/rules/security.md"
    "${WORKSPACE_HUB}/.claude/rules/testing.md"
  )
  for f in "${candidates[@]}"; do
    [[ -f "$f" ]] || continue
    local sz
    sz=$(wc -c < "$f" 2>/dev/null || echo 0)
    total=$((total + sz))
  done
  local kb=$(( total / 1024 ))
  if [[ "$total" -le 16384 ]]; then
    log_pass "R5: context budget ${kb}KB / 16KB"
  else
    log_fail "R5: context budget ${kb}KB exceeds 16KB — trim rules or CLAUDE.md"
  fi
} ; check_r5 || true

# ─────────────────────────────────────────────────────────────────────────────
# R6: Submodules on tracking branches, ≤5 commits behind
# ─────────────────────────────────────────────────────────────────────────────
check_r6() {
  command -v git &>/dev/null || { log_pass "R6: git absent — skip"; return; }
  local behind=()
  local detached=()
  while IFS= read -r sub_path; do
    [[ -z "$sub_path" ]] && continue
    local full_path="${WORKSPACE_HUB}/${sub_path}"
    [[ -d "$full_path/.git" || -f "$full_path/.git" ]] || continue
    local branch
    branch=$(git -C "$full_path" symbolic-ref --short HEAD 2>/dev/null || echo "")
    if [[ -z "$branch" ]]; then
      detached+=("$sub_path")
      continue
    fi
    local count
    count=$(git -C "$full_path" rev-list --count \
      "HEAD..origin/${branch}" 2>/dev/null || echo "0")
    [[ "$count" -gt 5 ]] && behind+=("${sub_path}:${count}")
  done < <(git -C "$WORKSPACE_HUB" submodule --quiet foreach \
    'echo "$displaypath"' 2>/dev/null)

  local msgs=()
  [[ ${#detached[@]} -gt 0 ]] && msgs+=("detached: ${detached[*]}")
  [[ ${#behind[@]} -gt 0 ]] && msgs+=("behind: ${behind[*]}")
  if [[ ${#msgs[@]} -eq 0 ]]; then
    log_pass "R6: submodules on tracking branches, within 5 commits"
  else
    log_fail "R6: submodule issues — ${msgs[*]}"
  fi
} ; check_r6 || true

# ─────────────────────────────────────────────────────────────────────────────
# R-CODEX: CODEX.md MAX_TEAMMATES matches .claude/settings.json
# ─────────────────────────────────────────────────────────────────────────────
check_r_codex() {
  local codex="${WORKSPACE_HUB}/.codex/CODEX.md"
  local settings="${WORKSPACE_HUB}/.claude/settings.json"
  [[ -f "$codex" ]] || { log_pass "R-CODEX: CODEX.md absent — skip"; return; }
  [[ -f "$settings" ]] || { log_pass "R-CODEX: settings.json absent — skip"; return; }
  command -v jq &>/dev/null || { log_pass "R-CODEX: jq absent — skip"; return; }
  local codex_val settings_val
  codex_val=$(grep -oP 'MAX_TEAMMATES[=:]\s*\K[0-9]+' "$codex" 2>/dev/null | head -1 || echo "")
  settings_val=$(jq -r '.maxTeammates // empty' "$settings" 2>/dev/null || echo "")
  if [[ -z "$codex_val" && -z "$settings_val" ]]; then
    log_pass "R-CODEX: MAX_TEAMMATES not configured — skip"
  elif [[ "$codex_val" == "$settings_val" ]]; then
    log_pass "R-CODEX: MAX_TEAMMATES=${codex_val} matches settings.json"
  else
    log_fail "R-CODEX: MAX_TEAMMATES mismatch — CODEX.md=${codex_val} settings.json=${settings_val}"
  fi
} ; check_r_codex || true

# ─────────────────────────────────────────────────────────────────────────────
# R-MODEL: No stale model IDs in scripts/ (weekly guard)
# ─────────────────────────────────────────────────────────────────────────────
check_r_model() {
  local scripts_dir="${WORKSPACE_HUB}/scripts"
  [[ -d "$scripts_dir" ]] || { log_pass "R-MODEL: scripts/ absent — skip"; return; }
  # Stale model patterns (pre-Claude 3 naming)
  local stale_patterns=(
    'claude-2\b'
    'claude-instant'
    'claude-v1'
    'claude-1\.'
  )
  local hits=()
  for pat in "${stale_patterns[@]}"; do
    while IFS= read -r match; do
      [[ -n "$match" ]] && hits+=("$match")
    done < <(grep -rlo --include="*.sh" --include="*.py" --include="*.yaml" \
      --include="*.yml" -E "$pat" "$scripts_dir" 2>/dev/null || true)
  done
  # Deduplicate
  local unique_hits
  unique_hits=$(printf '%s\n' "${hits[@]+"${hits[@]}"}" | sort -u | head -5)
  if [[ -z "$unique_hits" ]]; then
    log_pass "R-MODEL: no stale model IDs in scripts/"
  else
    log_fail "R-MODEL: stale model IDs found in scripts/: $(echo "$unique_hits" | tr '\n' ' ')"
  fi
} ; check_r_model || true

# ─────────────────────────────────────────────────────────────────────────────
# R-REGISTRY: model-registry.yaml ≤ 14 days old (weekly guard)
# ─────────────────────────────────────────────────────────────────────────────
check_r_registry() {
  local reg="${WORKSPACE_HUB}/config/agents/model-registry.yaml"
  [[ -f "$reg" ]] || { log_fail "R-REGISTRY: model-registry.yaml absent"; return; }
  local now_epoch reg_epoch age_days
  now_epoch=$(date +%s 2>/dev/null || echo "0")
  reg_epoch=$(date -r "$reg" +%s 2>/dev/null || \
    stat -c %Y "$reg" 2>/dev/null || echo "0")
  age_days=$(( (now_epoch - reg_epoch) / 86400 ))
  if [[ "$age_days" -le 14 ]]; then
    log_pass "R-REGISTRY: model-registry.yaml ${age_days}d old (≤14)"
  else
    log_fail "R-REGISTRY: model-registry.yaml ${age_days}d old — run update-model-ids.sh"
  fi
} ; check_r_registry || true

# ─────────────────────────────────────────────────────────────────────────────
# R-XPROV: CODEX.md + GEMINI.md contain legal + TDD mandates
# ─────────────────────────────────────────────────────────────────────────────
check_r_xprov() {
  local xprov_ok=1
  local missing=()
  local -A xprov_map=(
    ["CODEX.md"]="${WORKSPACE_HUB}/.codex/CODEX.md"
    ["GEMINI.md"]="${WORKSPACE_HUB}/.gemini/GEMINI.md"
  )
  for fname in CODEX.md GEMINI.md; do
    local fpath="${xprov_map[$fname]}"
    [[ -f "$fpath" ]] || continue  # absent files are skipped, not failed
    grep -qi "legal\|legal-compliance\|legal_compliance" "$fpath" 2>/dev/null \
      || { missing+=("${fname}:legal"); xprov_ok=0; }
    grep -qi "TDD\|test.driven\|testing" "$fpath" 2>/dev/null \
      || { missing+=("${fname}:TDD"); xprov_ok=0; }
  done
  if [[ "$xprov_ok" -eq 1 ]]; then
    log_pass "R-XPROV: CODEX.md/GEMINI.md contain legal+TDD mandates"
  else
    log_fail "R-XPROV: missing mandates: ${missing[*]}"
  fi
} ; check_r_xprov || true

# ─────────────────────────────────────────────────────────────────────────────
# R-SKILLS: session-signals/ fresh + skills committed in last 7 days
# ─────────────────────────────────────────────────────────────────────────────
check_r_skills() {
  local signals_dir="${STATE_DIR}/session-signals"
  local skills_dir="${WORKSPACE_HUB}/.claude/skills"
  local issues_local=()

  # Check session-signals freshness (any file modified in last 7 days)
  if [[ -d "$signals_dir" ]]; then
    local recent
    recent=$(find "$signals_dir" -name "*.jsonl" -mtime -7 2>/dev/null | head -1 || true)
    [[ -z "$recent" ]] && issues_local+=("no session-signals updated in 7 days")
  else
    issues_local+=("session-signals/ directory absent")
  fi

  # Check skills committed in last 7 days
  if command -v git &>/dev/null && [[ -d "$skills_dir" ]]; then
    local skills_commit
    skills_commit=$(git -C "$WORKSPACE_HUB" log --oneline --since="7 days ago" \
      -- ".claude/skills/" 2>/dev/null | head -1 || echo "")
    [[ -z "$skills_commit" ]] && issues_local+=("no skills committed in 7 days")
  fi

  if [[ ${#issues_local[@]} -eq 0 ]]; then
    log_pass "R-SKILLS: session-signals fresh, skills committed recently"
  else
    log_fail "R-SKILLS: ${issues_local[*]}"
  fi
} ; check_r_skills || true

# ─────────────────────────────────────────────────────────────────────────────
# R-HARNESS: agent harness files ≤ 25 lines each (rule: ≤20; grace: 25)
# Covers: CLAUDE.md, MEMORY.md, AGENTS.md, .codex/CODEX.md, .gemini/GEMINI.md
# ─────────────────────────────────────────────────────────────────────────────
check_r_harness() {
  local -A harness_map=(
    ["CLAUDE.md"]="${WORKSPACE_HUB}/CLAUDE.md"
    ["MEMORY.md"]="${WORKSPACE_HUB}/MEMORY.md"
    ["AGENTS.md"]="${WORKSPACE_HUB}/AGENTS.md"
    ["CODEX.md"]="${WORKSPACE_HUB}/.codex/CODEX.md"
    ["GEMINI.md"]="${WORKSPACE_HUB}/.gemini/GEMINI.md"
  )
  local over=()
  for fname in CLAUDE.md MEMORY.md AGENTS.md CODEX.md GEMINI.md; do
    local fpath="${harness_map[$fname]}"
    [[ -f "$fpath" ]] || continue
    local lc
    lc=$(wc -l < "$fpath" 2>/dev/null || echo 0)
    [[ "$lc" -gt 25 ]] && over+=("${fname}:${lc}L")
  done
  if [[ ${#over[@]} -eq 0 ]]; then
    log_pass "R-HARNESS: agent harness files ≤ 25 lines"
  else
    log_fail "R-HARNESS: harness files over 25 lines: ${over[*]}"
  fi
} ; check_r_harness || true


# ─────────────────────────────────────────────────────────────────────────────
# R-ANSYS: Installed ANSYS versions include expected latest (v252 = R25.2)
# Windows-workstation check; silently skips on non-Windows machines.
# ─────────────────────────────────────────────────────────────────────────────
check_r_ansys() {
  local ansys_root="/c/Program Files/ANSYS Inc"
  [[ -d "$ansys_root" ]] || { log_pass "R-ANSYS: ANSYS root absent — skip (non-Windows)"; return; }
  local expected_ver="v252"
  local versions latest
  versions=$(ls "$ansys_root" 2>/dev/null | grep -E '^v[0-9]+$' | sort -V | tr '\n' ' ' | sed 's/ $//')
  if [[ -z "$versions" ]]; then
    log_fail "R-ANSYS: no version dirs under '$ansys_root'"
    return
  fi
  latest=$(echo "$versions" | tr ' ' '\n' | tail -1)
  if [[ "$latest" == "$expected_ver" ]]; then
    log_pass "R-ANSYS: latest=${latest}, installed: ${versions}"
  else
    log_fail "R-ANSYS: latest installed=${latest}, expected ${expected_ver} — installed: ${versions}"
  fi
} ; check_r_ansys || true

# ─────────────────────────────────────────────────────────────────────────────
# R-ORCAFLEX: OrcaFlex 11.6 installed and OrcaFlex64.exe present
# Windows-workstation check; silently skips on non-Windows machines.
# ─────────────────────────────────────────────────────────────────────────────
check_r_orcaflex() {
  local orcaflex_root="/c/Program Files (x86)/Orcina/OrcaFlex"
  [[ -d "$orcaflex_root" ]] || { log_pass "R-ORCAFLEX: OrcaFlex root absent — skip (non-Windows)"; return; }
  local expected_ver="11.6"
  local versions latest
  versions=$(ls "$orcaflex_root" 2>/dev/null | grep -E '^[0-9]+\.' | sort -V | tr '\n' ' ' | sed 's/ $//')
  if [[ -z "$versions" ]]; then
    log_fail "R-ORCAFLEX: no version dirs under '$orcaflex_root'"
    return
  fi
  latest=$(echo "$versions" | tr ' ' '\n' | tail -1)
  local exe="${orcaflex_root}/${latest}/OrcaFlex64.exe"
  if [[ "$latest" == "$expected_ver" && -f "$exe" ]]; then
    log_pass "R-ORCAFLEX: version=${latest}, OrcaFlex64.exe present"
  elif [[ "$latest" == "$expected_ver" ]]; then
    log_fail "R-ORCAFLEX: version=${latest} but OrcaFlex64.exe missing"
  else
    log_fail "R-ORCAFLEX: latest installed=${latest}, expected ${expected_ver}"
  fi
} ; check_r_orcaflex || true

# ─────────────────────────────────────────────────────────────────────────────
# R-AI-CLI: AI agent CLIs present and at or above minimum version
# Delegates to ai-agent-readiness.sh; reads JSONL to count warn/error rows.
# ─────────────────────────────────────────────────────────────────────────────
check_r_ai_cli() {
  local readiness_script="${SCRIPT_DIR}/ai-agent-readiness.sh"
  [[ -f "$readiness_script" ]] || { log_pass "R-AI-CLI: ai-agent-readiness.sh absent — skip"; return; }

  bash "$readiness_script" >/dev/null 2>&1 || true

  local jsonl="${STATE_DIR}/session-signals/ai-readiness.jsonl"
  [[ -f "$jsonl" ]] || { log_pass "R-AI-CLI: no ai-readiness.jsonl yet — skip"; return; }

  # Only examine the latest run: take the last 20 rows (> 3 agents + quota rows per run)
  # This avoids a growing warn count from historical appended rows.
  local warn_count
  warn_count=$(tail -20 "$jsonl" | grep -c '"status":"warn"' 2>/dev/null || echo 0)
  local agents_with_warn
  agents_with_warn=$(tail -20 "$jsonl" | grep '"status":"warn"' 2>/dev/null \
    | grep -oP '"agent":"\K[^"]*' | sort -u | tr '\n' ' ' || true)

  if [[ "$warn_count" -eq 0 ]]; then
    log_pass "R-AI-CLI: all AI agents present and at minimum version"
  else
    log_fail "R-AI-CLI: ${warn_count} agent warning(s) — ${agents_with_warn}see ai-readiness.jsonl"
  fi
} ; check_r_ai_cli || true

# ─────────────────────────────────────────────────────────────────────────────
# R-AI-QUOTA: providers < 80% weekly usage
# ─────────────────────────────────────────────────────────────────────────────
check_r_ai_quota() {
  local quota_file="${WORKSPACE_HUB}/config/ai-tools/agent-quota-latest.json"
  [[ -f "$quota_file" ]] || { log_pass "R-AI-QUOTA: agent-quota-latest.json absent — skip"; return; }
  command -v jq &>/dev/null || { log_pass "R-AI-QUOTA: jq absent — skip"; return; }

  local high_providers=()
  while IFS= read -r entry; do
    local provider week_pct
    provider=$(echo "$entry" | jq -r '.provider // "unknown"')
    week_pct=$(echo "$entry" | jq -r '.week_pct // 0')
    [[ "$week_pct" == "null" ]] && week_pct=0
    local is_high
    is_high=$(awk -v p="$week_pct" 'BEGIN { print (p >= 80) ? "yes" : "no" }')
    [[ "$is_high" == "yes" ]] && high_providers+=("${provider}:${week_pct}%")
  done < <(jq -c '.agents[]' "$quota_file" 2>/dev/null || true)

  if [[ ${#high_providers[@]} -eq 0 ]]; then
    log_pass "R-AI-QUOTA: all providers below 80% weekly usage"
  else
    log_fail "R-AI-QUOTA: providers at ≥80% weekly quota: ${high_providers[*]}"
  fi
} ; check_r_ai_quota || true

# ─────────────────────────────────────────────────────────────────────────────
# R-UX: Cross-machine terminal UX consistency (WRK-228)
# Checks: keybindings.json, CLAUDE_SCREENSHOT_DIR, Chrome Claude extension.
# Delegates to check-ux-consistency.sh; reads exit code + stdout.
# ─────────────────────────────────────────────────────────────────────────────
check_r_ux() {
  local ux_script="${SCRIPT_DIR}/check-ux-consistency.sh"
  [[ -f "$ux_script" ]] || { log_pass "R-UX: check-ux-consistency.sh absent — skip"; return; }

  local ux_output fail_count warn_count
  ux_output=$(bash "$ux_script" 2>&1 || true)

  # Count FAIL and WARN lines from the UX script output.
  # grep -c exits 1 when count is 0 under pipefail; use awk to avoid that.
  fail_count=$(printf '%s\n' "$ux_output" | awk '/^\s*FAIL/{n++} END{print n+0}')
  warn_count=$(printf '%s\n' "$ux_output" | awk '/^\s*WARN/{n++} END{print n+0}')

  if [[ "$fail_count" -eq 0 && "$warn_count" -eq 0 ]]; then
    log_pass "R-UX: keybindings, screenshot dir, Chrome extension all consistent"
  elif [[ "$fail_count" -gt 0 ]]; then
    local fail_details
    fail_details=$(printf '%s\n' "$ux_output" | grep '^\s*FAIL' | sed 's/^\s*//' \
      | tr '\n' '; ' | sed 's/; $//')
    log_fail "R-UX: ${fail_count} UX gap(s) — ${fail_details}"
  else
    local warn_details
    warn_details=$(printf '%s\n' "$ux_output" | grep '^\s*WARN' | sed 's/^\s*//' \
      | tr '\n' '; ' | sed 's/; $//')
    log_fail "R-UX: ${warn_count} UX inconsistency/ies — ${warn_details}"
  fi
} ; check_r_ux || true

# ─────────────────────────────────────────────────────────────────────────────
# WRK-1047: harness readiness checks (R-JQ, R-PLUGINS, R-HOOKS, R-HOOK-STATIC,
#           R-SETTINGS, R-UV, R-PRECOMMIT; extended R-HARNESS tier-1; R-SKILLS sync)
# ─────────────────────────────────────────────────────────────────────────────
HARNESS_CONFIG="${HARNESS_CONFIG:-${SCRIPT_DIR}/harness-config.yaml}"

# Read a scalar from harness-config.yaml without PyYAML (strips inline comments)
_hc_scalar() {
  grep -E "^${1}:" "${HARNESS_CONFIG}" 2>/dev/null | head -1 \
    | sed 's/^[^:]*:[[:space:]]*//' | sed 's/[[:space:]]*#.*//' | tr -d '"' | tr -d "'"
}
# Read a YAML list (one item per line under a key, indented with "  - ")
# Strips surrounding single/double quotes to support multi-word values like 'git commit'
_hc_list() {
  awk "/^${1}:/{found=1;next} \
       found && /^  - /{sub(/^[[:space:]]*-[[:space:]]*/,\"\"); print; next} \
       found && /^[^ ]/{exit}" \
    "${HARNESS_CONFIG}" 2>/dev/null | tr -d "'\""
}

# ─────────────────────────────────────────────────────────────────────────────
# R-JQ: jq available (prerequisite for JSON checks)
# ─────────────────────────────────────────────────────────────────────────────
check_r_jq() {
  if command -v jq &>/dev/null; then
    log_pass "R-JQ: jq available ($(jq --version 2>/dev/null || echo 'unknown version'))"
  else
    log_fail "R-JQ: jq not found — install with: sudo apt-get install jq"
  fi
} ; check_r_jq || true

# ─────────────────────────────────────────────────────────────────────────────
# R-PLUGINS: required plugins installed (required-set from harness-config.yaml)
# ─────────────────────────────────────────────────────────────────────────────
check_r_plugins() {
  [[ -f "${HARNESS_CONFIG}" ]] || { log_pass "R-PLUGINS: harness-config.yaml absent — skip"; return; }
  command -v claude &>/dev/null || { log_fail "R-PLUGINS: claude CLI not found"; return; }

  local plugin_list missing=()
  plugin_list=$(timeout 15 claude plugin list 2>/dev/null || true)

  while IFS= read -r plugin; do
    [[ -z "$plugin" ]] && continue
    # Match exact plugin name: "  > plugin-name@..." or "  plugin-name" lines
    if ! echo "$plugin_list" | grep -qE "(>|^)[[:space:]]*${plugin}(@|[[:space:]]|$)"; then
      missing+=("$plugin")
    fi
  done < <(_hc_list "required_plugins")

  if [[ ${#missing[@]} -eq 0 ]]; then
    log_pass "R-PLUGINS: all required plugins present"
  else
    log_fail "R-PLUGINS: missing required plugins: ${missing[*]}"
  fi
} ; check_r_plugins || true

# ─────────────────────────────────────────────────────────────────────────────
# R-HOOKS: all hook paths in settings.json exist on disk
# ─────────────────────────────────────────────────────────────────────────────
check_r_hooks() {
  local settings="${WORKSPACE_HUB}/.claude/settings.json"
  [[ -f "$settings" ]] || { log_pass "R-HOOKS: settings.json absent — skip"; return; }
  command -v jq &>/dev/null || { log_pass "R-HOOKS: jq absent — skip"; return; }

  local missing=()
  # Extract literal script paths from hook commands (skip variable-expanded paths)
  while IFS= read -r hook_path; do
    [[ -z "$hook_path" ]] && continue
    # Skip paths containing shell variable expansions — cannot resolve statically
    [[ "$hook_path" == *'${'* ]] && continue
    [[ "$hook_path" == *'$('* ]] && continue
    local abs_path="${hook_path}"
    [[ "${hook_path}" != /* ]] && abs_path="${WORKSPACE_HUB}/${hook_path}"
    [[ -f "$abs_path" ]] || missing+=("$hook_path")
  done < <(jq -r '.. | strings | select(test("bash ")) | split("bash ")[1]
                   | split(" ")[0] | select(length > 0)
                   | select(startswith("-") | not)
                   | select(contains("/") or test("\\.sh$"))' \
             "$settings" 2>/dev/null | sort -u || true)

  if [[ ${#missing[@]} -eq 0 ]]; then
    log_pass "R-HOOKS: all hook scripts present on disk"
  else
    log_fail "R-HOOKS: hook scripts missing from disk: ${missing[*]}"
  fi
} ; check_r_hooks || true

# ─────────────────────────────────────────────────────────────────────────────
# R-HOOK-STATIC: hook files ≤200 lines and no blocking patterns
# ─────────────────────────────────────────────────────────────────────────────
check_r_hook_static() {
  local hooks_dir="${WORKSPACE_HUB}/.claude/hooks"
  [[ -d "$hooks_dir" ]] || { log_pass "R-HOOK-STATIC: no hooks/ dir — skip"; return; }

  local max_lines
  max_lines=$(_hc_scalar "hook_static_max_lines")
  max_lines=${max_lines:-200}

  local violations=()
  while IFS= read -r -d '' hook_file; do
    local lc
    lc=$(wc -l < "$hook_file" 2>/dev/null || echo 0)
    if [[ "$lc" -gt "$max_lines" ]]; then
      violations+=("$(basename "$hook_file"):${lc}L>max${max_lines}")
    fi
    # Check blocking patterns from harness-config.yaml (exclude comment lines)
    local config_patterns=()
    mapfile -t config_patterns < <(_hc_list "hook_blocking_patterns" 2>/dev/null || true)
    if [[ ${#config_patterns[@]} -eq 0 ]]; then
      config_patterns=('git commit' 'git push' '\bcurl\b' '\bwget\b' 'http://' 'https://')
    fi
    for pat in "${config_patterns[@]}"; do
      if grep -vE '^\s*#' "$hook_file" 2>/dev/null | grep -qE "$pat"; then
        violations+=("$(basename "$hook_file"):blocking-pattern:'${pat}'")
      fi
    done
  done < <(find "$hooks_dir" -name "*.sh" -print0 2>/dev/null)

  if [[ ${#violations[@]} -eq 0 ]]; then
    log_pass "R-HOOK-STATIC: all hooks ≤${max_lines} lines, no blocking patterns"
  else
    log_fail "R-HOOK-STATIC: hook violations: ${violations[*]}"
  fi
} ; check_r_hook_static || true

# ─────────────────────────────────────────────────────────────────────────────
# R-SETTINGS: settings.json is valid JSON
# ─────────────────────────────────────────────────────────────────────────────
check_r_settings() {
  local settings="${WORKSPACE_HUB}/.claude/settings.json"
  [[ -f "$settings" ]] || { log_pass "R-SETTINGS: settings.json absent — skip"; return; }
  command -v jq &>/dev/null || { log_pass "R-SETTINGS: jq absent — skip"; return; }

  if jq empty "$settings" 2>/dev/null; then
    log_pass "R-SETTINGS: .claude/settings.json is valid JSON"
  else
    log_fail "R-SETTINGS: .claude/settings.json is not valid JSON — run: jq . .claude/settings.json"
  fi
} ; check_r_settings || true

# ─────────────────────────────────────────────────────────────────────────────
# R-UV: uv ≥ 0.5.0 available
# ─────────────────────────────────────────────────────────────────────────────
check_r_uv() {
  if ! command -v uv &>/dev/null; then
    log_fail "R-UV: uv not found — install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    return
  fi
  local raw_ver parsed_ver
  raw_ver=$(uv --version 2>/dev/null | head -1 || echo "")
  parsed_ver=$(printf '%s' "$raw_ver" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "")
  if [[ -z "$parsed_ver" ]]; then
    log_fail "R-UV: uv installed but version unreadable"
    return
  fi
  local min="0.5.0"
  local lo
  lo=$(printf '%s\n%s\n' "$parsed_ver" "$min" | sort -V | head -1)
  if [[ "$lo" == "$min" ]]; then
    log_pass "R-UV: uv ${parsed_ver} ≥ ${min}"
  else
    log_fail "R-UV: uv ${parsed_ver} below minimum ${min} — run: uv self update"
  fi
} ; check_r_uv || true

# ─────────────────────────────────────────────────────────────────────────────
# R-PRECOMMIT: .pre-commit-config.yaml present + legal-sanity-scan.sh entry
#              in each tier-1 repo; file must be executable
# ─────────────────────────────────────────────────────────────────────────────
check_r_precommit() {
  [[ -f "${HARNESS_CONFIG}" ]] || { log_pass "R-PRECOMMIT: harness-config.yaml absent — skip"; return; }
  local issues_local=()
  while IFS= read -r repo; do
    [[ -z "$repo" ]] && continue
    local repo_dir="${WORKSPACE_HUB}/../${repo}"
    [[ -d "$repo_dir" ]] || continue
    local pc="${repo_dir}/.pre-commit-config.yaml"
    if [[ ! -f "$pc" ]]; then
      issues_local+=("${repo}:.pre-commit-config.yaml missing")
      continue
    fi
    if ! grep -q "legal-sanity-scan" "$pc" 2>/dev/null; then
      issues_local+=("${repo}:legal-sanity-scan.sh entry missing")
    fi
  done < <(_hc_list "tier1_repos")

  if [[ ${#issues_local[@]} -eq 0 ]]; then
    log_pass "R-PRECOMMIT: all tier-1 repos have .pre-commit-config.yaml with legal scan"
  else
    log_fail "R-PRECOMMIT: ${issues_local[*]}"
  fi
} ; check_r_precommit || true

# ─────────────────────────────────────────────────────────────────────────────
# R-HARNESS (extended): hub + tier-1 repos — CLAUDE.md/AGENTS.md ≤ 20 lines
# ─────────────────────────────────────────────────────────────────────────────
check_r_harness_extended() {
  local over=()
  # Hub harness files (already checked by existing R-HARNESS; this adds tier-1 repos)
  while IFS= read -r repo; do
    [[ -z "$repo" ]] && continue
    local repo_dir="${WORKSPACE_HUB}/../${repo}"
    [[ -d "$repo_dir" ]] || continue
    for fname in CLAUDE.md AGENTS.md CODEX.md GEMINI.md; do
      local fpath="${repo_dir}/${fname}"
      [[ -f "$fpath" ]] || continue
      local lc
      lc=$(wc -l < "$fpath" 2>/dev/null || echo 0)
      [[ "$lc" -gt 20 ]] && over+=("${repo}/${fname}:${lc}L")
    done
  done < <(_hc_list "tier1_repos")

  if [[ ${#over[@]} -eq 0 ]]; then
    log_pass "R-HARNESS-TIER1: tier-1 repo harness files all ≤ 20 lines"
  else
    log_fail "R-HARNESS-TIER1: tier-1 harness files over 20 lines: ${over[*]}"
  fi
} ; check_r_harness_extended || true

# ─────────────────────────────────────────────────────────────────────────────
# R-SKILLS (extended): sync dry-run + SKILL.md count ≥ baseline + command count
# ─────────────────────────────────────────────────────────────────────────────
check_r_skills_extended() {
  [[ -f "${HARNESS_CONFIG}" ]] || { log_pass "R-SKILLS-SYNC: harness-config.yaml absent — skip"; return; }
  local issues_local=()

  # 1. sync-knowledge-work-plugins.sh --dry-run
  local sync_script="${WORKSPACE_HUB}/scripts/skills/sync-knowledge-work-plugins.sh"
  if [[ -f "$sync_script" ]]; then
    if ! bash "$sync_script" --dry-run &>/dev/null; then
      issues_local+=("sync-knowledge-work-plugins.sh --dry-run failed (stale skills)")
    fi
  fi

  # 2. No _diverged/ or incoming/ leftovers
  local skills_dir="${WORKSPACE_HUB}/.claude/skills"
  for leftover_dir in "_diverged" "incoming"; do
    local ldir="${skills_dir}/${leftover_dir}"
    if [[ -d "$ldir" ]] && [[ -n "$(ls -A "$ldir" 2>/dev/null)" ]]; then
      issues_local+=("${leftover_dir}/ has unresolved files — run skill curation")
    fi
  done

  # 3. SKILL.md count ≥ baseline (skip if baseline=0)
  local skill_baseline
  skill_baseline=$(_hc_scalar "skill_count_baseline")
  skill_baseline=${skill_baseline:-0}
  if [[ "$skill_baseline" -gt 0 ]]; then
    local skill_count
    skill_count=$(find "${skills_dir}" -name "SKILL.md" 2>/dev/null | wc -l || echo 0)
    [[ "$skill_count" -lt "$skill_baseline" ]] && \
      issues_local+=("SKILL.md count=${skill_count} below baseline=${skill_baseline} — run --update-baseline after curation")
  fi

  # 4. command count ≥ baseline (skip if baseline=0)
  local cmd_baseline
  cmd_baseline=$(_hc_scalar "command_count_baseline")
  cmd_baseline=${cmd_baseline:-0}
  if [[ "$cmd_baseline" -gt 0 ]]; then
    local cmd_count
    cmd_count=$(find "${WORKSPACE_HUB}/.claude/commands" -name "*.md" 2>/dev/null | wc -l || echo 0)
    [[ "$cmd_count" -lt "$cmd_baseline" ]] && \
      issues_local+=("command count=${cmd_count} below baseline=${cmd_baseline} — run --update-baseline after curation")
  fi

  if [[ ${#issues_local[@]} -eq 0 ]]; then
    log_pass "R-SKILLS-SYNC: plugin sync clean, no leftovers, counts within baseline"
  else
    log_fail "R-SKILLS-SYNC: ${issues_local[*]}"
  fi
} ; check_r_skills_extended || true

# ─────────────────────────────────────────────────────────────────────────────
# Phase B: emit harness-readiness-report.yaml (host-qualified, structured)
# ─────────────────────────────────────────────────────────────────────────────
_emit_harness_report() {
  local hostname_short
  hostname_short=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
  local report_path="${STATE_DIR}/harness-readiness-${hostname_short}.yaml"
  local overall="pass"
  [[ "$fail_count" -gt 0 ]] && overall="fail"
  {
    echo "schema_version: 1"
    echo "host: ${hostname_short}"
    echo "generated_at: \"${RUN_TS}\""
    echo "overall: ${overall}"
    echo "pass_count: ${pass_count}"
    echo "fail_count: ${fail_count}"
    echo "checks:"
    for cid in $(echo "${!check_results[@]}" | tr ' ' '\n' | sort); do
      local status="${check_results[$cid]}"
      local detail
      detail=$(printf '%s' "${check_details[$cid]}" | sed "s/'/\\''/g")
      echo "  ${cid}:"
      echo "    status: ${status}"
      echo "    detail: '${detail}'"
    done
  } > "$report_path"
} ; _emit_harness_report || true

# ─────────────────────────────────────────────────────────────────────────────
# --update-baseline: set skill/command count baselines in harness-config.yaml
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--update-baseline" ]]; then
  skill_count=$(find "${WORKSPACE_HUB}/.claude/skills" -name "SKILL.md" 2>/dev/null | wc -l || echo 0)
  cmd_count=$(find "${WORKSPACE_HUB}/.claude/commands" -name "*.md" 2>/dev/null | wc -l || echo 0)
  sed -i "s/^skill_count_baseline: .*/skill_count_baseline: ${skill_count}/" "${HARNESS_CONFIG}" 2>/dev/null || true
  sed -i "s/^command_count_baseline: .*/command_count_baseline: ${cmd_count}/" "${HARNESS_CONFIG}" 2>/dev/null || true
  echo "--- Baseline updated: skills=${skill_count}, commands=${cmd_count} ---"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Write issues to readiness-issues.md for Phase 6 to surface
# ─────────────────────────────────────────────────────────────────────────────
if [[ ${#issues[@]} -gt 0 ]]; then
  {
    echo "# Readiness Issues — ${RUN_TS}"
    echo ""
    echo "Nightly readiness: ${fail_count} failed, ${pass_count} passed"
    echo ""
    echo "## Warnings"
    for issue in "${issues[@]}"; do
      echo "- ${issue}"
    done
    echo ""
  } > "$ISSUES_FILE"
  echo "--- Readiness: ${fail_count}/$((pass_count + fail_count)) checks failed — see ${ISSUES_FILE} ---"
else
  echo "# Readiness Issues — ${RUN_TS}" > "$ISSUES_FILE"
  echo "" >> "$ISSUES_FILE"
  echo "All ${pass_count} checks passed." >> "$ISSUES_FILE"
  echo "--- Readiness: all ${pass_count} checks passed ---"
fi
