#!/usr/bin/env bash
# ABOUTME: Cross-platform "sync every repo in the ecosystem" driver (Linux/macOS + Windows Git Bash).
# ABOUTME: Auto-detects sibling vs nested layout; modes full|pull|status. Skill-invokable; no hardcoded paths.
#
# Why this exists alongside scripts/repository_sync:
#   repository_sync hardcodes WORKSPACE_ROOT to workspace-hub and expects each repo at
#   workspace-hub/<repo>. On hosts where the repos are independent clones SIBLING to
#   workspace-hub (e.g. the Windows host ace-win-2 where they live under the workspace-hub
#   parent dir), that assumption finds nothing. This driver resolves the ecosystem root by
#   detection so the same command works on both layouts and both OSes.
#
# Usage:
#   scripts/sync/sync-ecosystem.sh [--mode full|pull|status] [--root <dir>] [-m "<msg>"] [--dry-run]
#
# Modes:
#   full   (default) per repo: git add -u -> commit if staged -> fetch --prune -> pull --ff-only -> push
#   pull             per repo: fetch --prune -> pull --ff-only            (no commit, no push)
#   status           per repo: fetch --prune -> report branch/ahead/behind/dirty (read-only)
#
# Root resolution order: --root  >  $WS_ECOSYSTEM_ROOT  >  auto-detect (sibling vs nested).
#
# Exit: 0 if no repo reported a hard failure (push/commit failures count; ff-pull divergence is a warning).

set -uo pipefail

MODE="full"
ROOT=""
MSG=""
DRY_RUN="false"

usage() { sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --mode)        MODE="${2:?--mode needs a value}"; shift 2 ;;
    --mode=*)      MODE="${1#*=}"; shift ;;
    --root)        ROOT="${2:?--root needs a value}"; shift 2 ;;
    --root=*)      ROOT="${1#*=}"; shift ;;
    -m|--message)  MSG="${2:?--message needs a value}"; shift 2 ;;
    --dry-run)     DRY_RUN="true"; shift ;;
    -h|--help)     usage; exit 0 ;;
    *) echo "sync-ecosystem: unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$MODE" in full|pull|status) ;; *) echo "sync-ecosystem: bad --mode '$MODE' (full|pull|status)" >&2; exit 2 ;; esac
[ -n "$MSG" ] || MSG="chore(sync): auto-sync $(date +%F)"

# Count immediate child dirs that are git repos.
_count_git_children() {
  local base="$1" n=0 d
  [ -d "$base" ] || { echo 0; return; }
  for d in "$base"/*/; do [ -e "${d}.git" ] && n=$((n+1)); done
  echo "$n"
}

# Resolve ecosystem root by detection when not given explicitly.
_resolve_root() {
  [ -n "$ROOT" ] && { (cd "$ROOT" && pwd); return; }
  [ -n "${WS_ECOSYSTEM_ROOT:-}" ] && { (cd "$WS_ECOSYSTEM_ROOT" && pwd); return; }
  local hub parent sib nes
  hub="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"   # this script lives in <hub>/scripts/sync
  parent="$(cd "$hub/.." && pwd)"
  sib="$(_count_git_children "$parent")"                       # sibling layout: hub + siblings under parent
  nes="$(_count_git_children "$hub")"                          # nested layout: repos inside hub
  if [ "$sib" -ge 2 ]; then echo "$parent"
  elif [ "$nes" -ge 1 ]; then echo "$hub"
  else echo "$parent"; fi
}

ROOT="$(_resolve_root)"
[ -d "$ROOT" ] || { echo "sync-ecosystem: ecosystem root not found: $ROOT" >&2; exit 1; }

echo "===================================================="
echo "sync-ecosystem  | os=$(uname -s) | mode=$MODE | root=$ROOT"
[ "$DRY_RUN" = "true" ] && echo "(dry-run: no mutations)"
echo "===================================================="

n_ok=0; n_warn=0; n_fail=0

for d in "$ROOT"/*/; do
  [ -e "${d}.git" ] || continue
  repo="$(basename "$d")"
  echo "=== $repo ==="
  branch="$(git -C "$d" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"

  if [ "$MODE" = "status" ]; then
    git -C "$d" fetch --prune origin >/dev/null 2>&1 || true
    dirty="clean"; [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ] && dirty="dirty"
    ahead="$(git -C "$d" rev-list --count '@{u}..HEAD' 2>/dev/null || echo '?')"
    behind="$(git -C "$d" rev-list --count 'HEAD..@{u}' 2>/dev/null || echo '?')"
    echo "  $branch  ahead=$ahead behind=$behind  $dirty"
    n_ok=$((n_ok+1))
    continue
  fi

  if [ "$DRY_RUN" = "true" ]; then
    echo "  [dry-run] would: ${MODE} on branch $branch"
    n_ok=$((n_ok+1))
    continue
  fi

  result="ok"
  if [ "$MODE" = "full" ]; then
    git -C "$d" add -u 2>/dev/null || true
    if ! git -C "$d" diff --cached --quiet 2>/dev/null; then
      if ! git -C "$d" commit -m "$MSG" >/dev/null 2>&1; then result="commit-failed"; fi
    fi
  fi

  git -C "$d" fetch --prune origin >/dev/null 2>&1 || true
  if ! git -C "$d" pull --ff-only >/dev/null 2>&1; then
    echo "  pull skipped (diverged/no-ff)"
    [ "$result" = "ok" ] && result="warn-pull"
  fi

  if [ "$MODE" = "full" ]; then
    push_out=""
    if push_out="$(git -C "$d" push 2>&1)"; then
      :
    elif echo "$push_out" | grep -Eiq "archived|read[- ]only|everything up-to-date"; then
      :
    else
      echo "  push skipped/failed"
      result="push-failed"
    fi
  fi

  case "$result" in
    ok)         n_ok=$((n_ok+1)) ;;
    warn-*)     n_warn=$((n_warn+1)) ;;
    *)          n_fail=$((n_fail+1)) ;;
  esac
done

echo "----------------------------------------------------"
echo "Done. ok=$n_ok warn=$n_warn fail=$n_fail"
[ "$n_fail" -eq 0 ]
