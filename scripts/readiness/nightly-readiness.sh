#!/usr/bin/env bash
# nightly-readiness.sh — 9 ecosystem health checks for the nightly cron pipeline
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

log_pass() { echo "  OK  $1"; pass_count=$((pass_count + 1)); }
log_fail() {
  echo "  FAIL $1"
  issues+=("$1")
  fail_count=$((fail_count + 1))
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
