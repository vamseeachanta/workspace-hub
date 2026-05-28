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
# Colors only on an interactive TTY and when NO_COLOR is unset — otherwise ANSI
# escapes garble CI logs, redirected output, and some Windows terminals.
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_G='\033[32m'; C_Y='\033[33m'; C_R='\033[31m'; C_B='\033[1m'; C_0='\033[0m'
else
  C_G=''; C_Y=''; C_R=''; C_B=''; C_0=''
fi
ok()   { printf '  %bPASS%b  %s\n' "$C_G" "$C_0" "$1"; pass=$((pass+1)); }
wn()   { printf '  %bWARN%b  %s\n' "$C_Y" "$C_0" "$1"; warn=$((warn+1)); }
no()   { printf '  %bFAIL%b  %s\n' "$C_R" "$C_0" "$1"; fail=$((fail+1)); }
hdr()  { printf '\n%b== %s ==%b\n' "$C_B" "$1" "$C_0"; }

# Hostname: `hostname` is absent on some minimal Git Bash installs — fall back to
# the Windows %COMPUTERNAME%, then "unknown".
host=$(hostname 2>/dev/null); host=${host:-${COMPUTERNAME:-unknown}}
echo "Hermes consistency check — host=$host HERMES_HOME=$HERMES_HOME"
echo "repo=$REPO_ROOT  ($(date -u +%Y-%m-%dT%H:%M:%SZ))"

# ── 0. Repo present + sync state ──────────────────────────────────────────────
hdr "Repo sync"
if [ -d "$REPO_ROOT/.git" ] || git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  ok "workspace-hub clone present at $REPO_ROOT"
  if git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
    br=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)
    # Only fetch+compare when this branch exists on origin. A local-only branch
    # (or an unreachable origin) otherwise yields a bogus "? commits behind" WARN.
    if git -C "$REPO_ROOT" ls-remote --exit-code --heads origin "$br" >/dev/null 2>&1; then
      git -C "$REPO_ROOT" fetch --quiet origin "$br" 2>/dev/null
      behind=$(git -C "$REPO_ROOT" rev-list --count "HEAD..origin/$br" 2>/dev/null || echo "?")
      if [ "$behind" = "0" ]; then
        ok "branch '$br' up to date with origin"
      elif [ "$behind" = "?" ]; then
        wn "branch '$br' sync state undetermined (origin/$br ref unavailable locally)"
      else
        wn "branch '$br' is $behind commit(s) behind origin/$br — pull to sync config"
      fi
    else
      wn "branch '$br' not found on origin (local-only branch or origin unreachable) — sync check skipped"
    fi
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
    # Compare CRLF-insensitively: on Windows a core.autocrlf checkout can give one
    # side CRLF and the other LF, which would otherwise report a false DIFFERS.
    if diff -q <(tr -d '\r' < "$SOUL_LINK") <(tr -d '\r' < "$SOUL_CANON") >/dev/null 2>&1; then
      ok "SOUL runtime matches repo canonical (config/agents/hermes/SOUL.runtime.md)"
    else
      no "SOUL runtime DIFFERS from repo canonical — re-run scripts/agents/build-soul-runtime.sh + install-soul-runtime.sh"
    fi
  else
    wn "canonical SOUL not found at $SOUL_CANON — cannot compare (check sparse-checkout / branch)"
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
    # Confirm BOTH the Linux-cron id and its Windows task-scheduler "-win" variant
    # are present, rather than asserting the -win variant without checking it.
    base_ok=0; win_ok=0
    # Anchor to the YAML list-item form ("- id: <name>") from line start so a
    # commented "# id: ..." or a longer key like "grid:" can't produce a match.
    grep -qE "^[[:space:]]*-?[[:space:]]*id:[[:space:]]*${id}([[:space:]]|\$)" "$SCHED" && base_ok=1
    grep -qE "^[[:space:]]*-?[[:space:]]*id:[[:space:]]*${id}-win([[:space:]]|\$)" "$SCHED" && win_ok=1
    if [ "$base_ok" = 1 ] && [ "$win_ok" = 1 ]; then
      ok "declared in schedule-tasks.yaml: $id + ${id}-win"
    elif [ "$base_ok" = 1 ]; then
      wn "declared: $id but MISSING Windows variant ${id}-win"
    else
      wn "not declared: $id"
    fi
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
