#!/usr/bin/env bash
# hermes-consistency-check.sh — per-machine Hermes consistency probe.
#
# WHAT: read-only audit that a machine's local Hermes runtime is consistent with
#   the canonical workspace-hub config across: harness/identity, memory, skills,
#   routing, auth, scheduled bridges, and repo sync. Prints a PASS/WARN/FAIL
#   report. Mutates NOTHING and never prints secret VALUES (only key presence).
#
# WHERE: runs on any machine (Linux or Windows Git Bash). On Windows run from
#   Git Bash:  bash scripts/readiness/hermes-consistency-check.sh
#
# WHY: #2841 (orchestrator consistency) — verify a new box (e.g. ace-win-1) before
#   it carries Hermes load. Companion to setup-cron.sh + build-soul-runtime.sh.
#
# EXIT: 0 = all PASS (warnings allowed), 1 = one or more FAIL.

set -uo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
# Resolve repo root: env override, else walk up from this script.
REPO_ROOT="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"

pass=0; warn=0; fail=0
ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$1"; pass=$((pass+1)); }
wn()   { printf '  \033[33mWARN\033[0m  %s\n' "$1"; warn=$((warn+1)); }
no()   { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; fail=$((fail+1)); }
hdr()  { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

echo "Hermes consistency check — host=$(hostname 2>/dev/null) HERMES_HOME=$HERMES_HOME"
echo "repo=$REPO_ROOT  ($(date -u +%Y-%m-%dT%H:%M:%SZ))"

# ── 0. Repo present + sync state ──────────────────────────────────────────────
hdr "Repo sync"
if [ -d "$REPO_ROOT/.git" ] || git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  ok "workspace-hub clone present at $REPO_ROOT"
  if git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
    br=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)
    git -C "$REPO_ROOT" fetch --quiet origin "$br" 2>/dev/null
    behind=$(git -C "$REPO_ROOT" rev-list --count "HEAD..origin/$br" 2>/dev/null || echo "?")
    [ "$behind" = "0" ] && ok "branch '$br' up to date with origin" \
      || wn "branch '$br' is $behind commit(s) behind origin/$br — pull to sync config"
  fi
else
  no "no workspace-hub clone at $REPO_ROOT (set WORKSPACE_HUB=...) — config comparison skipped"
fi

# ── 1. Hermes presence ────────────────────────────────────────────────────────
hdr "Hermes presence"
command -v hermes >/dev/null 2>&1 && ok "hermes CLI on PATH ($(command -v hermes))" \
  || wn "hermes CLI not on PATH (ok if launched another way)"
[ -d "$HERMES_HOME" ] && ok "HERMES_HOME exists ($HERMES_HOME)" \
  || { no "HERMES_HOME missing ($HERMES_HOME) — Hermes not installed here"; }

# ── 2. Harness / identity (SOUL runtime) ──────────────────────────────────────
hdr "Harness / identity"
SOUL_LINK="$HERMES_HOME/SOUL.md"
SOUL_CANON="$REPO_ROOT/config/agents/hermes/SOUL.runtime.md"
if [ -e "$SOUL_LINK" ]; then
  if [ -L "$SOUL_LINK" ]; then
    tgt=$(readlink "$SOUL_LINK")
    ok "~/.hermes/SOUL.md is a symlink → $tgt"
  else
    wn "~/.hermes/SOUL.md exists but is a COPY, not a symlink (drift risk — prefer install-soul-runtime.sh)"
  fi
  if [ -f "$SOUL_CANON" ]; then
    if diff -q "$SOUL_LINK" "$SOUL_CANON" >/dev/null 2>&1; then
      ok "SOUL runtime matches repo canonical (config/agents/hermes/SOUL.runtime.md)"
    else
      no "SOUL runtime DIFFERS from repo canonical — re-run scripts/agents/build-soul-runtime.sh + install-soul-runtime.sh"
    fi
  fi
else
  no "~/.hermes/SOUL.md missing — identity/gates not delivered to Hermes"
fi

# ── 3. Memory ─────────────────────────────────────────────────────────────────
hdr "Memory"
[ -f "$HERMES_HOME/memories/MEMORY.md" ] && ok "~/.hermes/memories/MEMORY.md present" \
  || wn "~/.hermes/memories/MEMORY.md absent (no read-back store yet — see #2854)"
CFG="$HERMES_HOME/config.yaml"
if [ -f "$CFG" ]; then
  grep -qiE '^\s*memory_enabled:\s*true' "$CFG" && ok "memory_enabled: true" \
    || wn "memory_enabled not true in config.yaml"
else
  wn "~/.hermes/config.yaml not found — cannot verify memory/routing settings"
fi

# ── 4. Routing (gpt-5.5 / openai-codex, NO OpenRouter, NO provider:auto) ──────
hdr "Routing policy (per feedback_hermes_no_openrouter_always_gpt55)"
if [ -f "$CFG" ]; then
  # Strip comment lines first so a "# openrouter removed" note doesn't false-FAIL.
  CFG_ACTIVE=$(grep -vE '^\s*#' "$CFG")
  if printf '%s' "$CFG_ACTIVE" | grep -qiE 'openrouter'; then
    no "OpenRouter reference in active config.yaml — must be removed (2026-05-25 directive)"
  else ok "no OpenRouter reference (active lines)"; fi
  if printf '%s' "$CFG_ACTIVE" | grep -qiE 'provider:\s*auto'; then
    no "'provider: auto' in active config.yaml — must be pinned (gpt-5.5/openai-codex)"
  else ok "no 'provider: auto' (active lines)"; fi
  printf '%s' "$CFG_ACTIVE" | grep -qiE 'gpt-5\.5|openai-codex' && ok "pinned provider (gpt-5.5/openai-codex) referenced" \
    || wn "no explicit gpt-5.5/openai-codex pin found — verify default routing"
fi

# ── 5. Skills ─────────────────────────────────────────────────────────────────
hdr "Skills"
if [ -f "$CFG" ] && grep -qiE '^\s*skills:' "$CFG"; then
  ok "skills: block present in config.yaml"
else
  wn "no skills: block in config.yaml — Hermes may not resolve workspace skills"
fi
[ -d "$REPO_ROOT/.claude/skills" ] && ok "repo .claude/skills present ($(find "$REPO_ROOT/.claude/skills" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ') SKILL.md)" \
  || wn "repo .claude/skills not found in this clone"

# ── 6. Auth (presence only — never print values) ─────────────────────────────
hdr "Auth"
ENVF="$HERMES_HOME/.env"
if [ -f "$ENVF" ]; then
  ok "~/.hermes/.env present"
  # check key NAMES exist, not values
  for k in OPENAI_API_KEY ANTHROPIC_API_KEY; do
    grep -qE "^\s*${k}=" "$ENVF" 2>/dev/null && ok "  $k defined" || wn "  $k not defined in .env"
  done
  grep -qiE '^\s*OPENROUTER_API_KEY=' "$ENVF" 2>/dev/null \
    && no "  OPENROUTER_API_KEY present in .env — should be removed" \
    || ok "  no OPENROUTER_API_KEY (correct)"
else
  wn "~/.hermes/.env absent — auth may be configured elsewhere"
fi

# ── 7. Scheduled memory bridges (#2846) ───────────────────────────────────────
hdr "Scheduled bridges (#2846)"
SCHED="$REPO_ROOT/config/scheduled-tasks/schedule-tasks.yaml"
if [ -f "$SCHED" ]; then
  for id in provider-dream-bridge hermes-claude-bridge; do
    grep -qE "id:\s*${id}\b" "$SCHED" && ok "declared in schedule-tasks.yaml: $id (+ -win variant)" \
      || wn "not declared: $id"
  done
  echo "  (On Windows, confirm the windows-task-scheduler tasks are actually registered:"
  echo "   PowerShell:  Get-ScheduledTask | Where-Object {\$_.TaskName -like '*dream*' -or \$_.TaskName -like '*hermes*'} )"
else
  wn "schedule-tasks.yaml not found — cannot verify bridge declarations"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
hdr "Summary"
printf '  PASS=%d  WARN=%d  FAIL=%d\n' "$pass" "$warn" "$fail"
if [ "$fail" -gt 0 ]; then
  echo "  => INCONSISTENT — resolve FAIL items before ace-win-1 carries Hermes load."
  exit 1
fi
echo "  => consistent (warnings are advisory)."
exit 0
