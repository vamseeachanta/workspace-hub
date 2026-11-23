#!/usr/bin/env bash
# check-memory-index-size.sh — wh#3366
# Guard the Claude Code auto-memory INDEX (MEMORY.md) against the harness's
# BYTE-size load cap. The harness loads MEMORY.md into context up to ~24.4KB
# and SILENTLY DROPS everything past that — long-tail memories stop being
# recalled with no error. The existing scripts/memory/compact-memory.py
# triggers on LINE count (MEMORY_MD_LIMIT=180), which a small number of very
# long lines sails past while the byte size blows the load cap. This check
# closes that gap: it measures bytes, not lines.
#
# Usage:
#   scripts/enforcement/check-memory-index-size.sh [--warn-kib=<N>] [--hard-kib=<N>] [<file>...]
#
# With no positional args, scans the auto-memory indices at
#   ~/.claude/projects/*/memory/MEMORY.md
# (per-project, machine-local; not repo-tracked). With positional args,
# checks exactly those files (used by tests).
#
# Thresholds (KiB, defaults chosen from the harness reminders):
#   --warn-kib  17   over the compaction target — compact soon (exit 0 + warn)
#   --hard-kib  24   at/over the load cap — content is being DROPPED (exit 1)
#
# Exit codes: 0 = ok or warn-only; 1 = one or more indices at/over the hard cap.
# Bypass: ALLOW_MEMORY_INDEX_OVERSIZE=1 (logs to stderr).

set -euo pipefail

WARN_KIB=17
HARD_KIB=24
declare -a POSITIONAL=()

while (( $# > 0 )); do
  case "$1" in
    --warn-kib=*) WARN_KIB="${1#*=}"; shift ;;
    --warn-kib)   WARN_KIB="${2:?--warn-kib requires a value}"; shift 2 ;;
    --hard-kib=*) HARD_KIB="${1#*=}"; shift ;;
    --hard-kib)   HARD_KIB="${2:?--hard-kib requires a value}"; shift 2 ;;
    --)           shift; POSITIONAL+=("$@"); break ;;
    -*)           echo "check-memory-index-size: unknown flag: $1" >&2; exit 2 ;;
    *)            POSITIONAL+=("$1"); shift ;;
  esac
done

warn_bytes=$(( WARN_KIB * 1024 ))
hard_bytes=$(( HARD_KIB * 1024 ))

declare -a TARGETS=()
if (( ${#POSITIONAL[@]} == 0 )); then
  # Glob may not expand; guard with nullglob.
  shopt -s nullglob
  for f in "$HOME"/.claude/projects/*/memory/MEMORY.md; do
    TARGETS+=("$f")
  done
  shopt -u nullglob
  if (( ${#TARGETS[@]} == 0 )); then
    # No auto-memory indices on this machine — nothing to guard.
    exit 0
  fi
else
  for arg in "${POSITIONAL[@]}"; do
    [[ -f "$arg" ]] || { echo "check-memory-index-size: not a file: $arg" >&2; exit 2; }
    TARGETS+=("$arg")
  done
fi

file_bytes() {
  # Portable byte count (Linux `stat -c`, BSD/macOS `stat -f`, wc fallback).
  stat -c%s "$1" 2>/dev/null || stat -f%z "$1" 2>/dev/null || wc -c < "$1"
}

declare -a OVER_HARD=()
declare -a OVER_WARN=()
for f in "${TARGETS[@]}"; do
  bytes="$(file_bytes "$f")"
  kib=$(( bytes / 1024 ))
  if (( bytes >= hard_bytes )); then
    OVER_HARD+=("$f")
    printf '%s: %d KiB (>= %d KiB load cap — content is being DROPPED on load)\n' "$f" "$kib" "$HARD_KIB" >&2
  elif (( bytes >= warn_bytes )); then
    OVER_WARN+=("$f")
    printf '%s: %d KiB (>= %d KiB target — compact soon)\n' "$f" "$kib" "$WARN_KIB" >&2
  fi
done

if (( ${#OVER_WARN[@]} > 0 && ${#OVER_HARD[@]} == 0 )); then
  echo "check-memory-index-size: ${#OVER_WARN[@]} index(es) over the ${WARN_KIB} KiB target (still loading in full)." >&2
  echo "  Compact via scripts/memory/compact-memory.py or trim MEMORY.md hooks." >&2
fi

if (( ${#OVER_HARD[@]} > 0 )); then
  if [[ "${ALLOW_MEMORY_INDEX_OVERSIZE:-0}" == "1" ]]; then
    echo "check-memory-index-size: ${#OVER_HARD[@]} oversize index(es); ALLOW_MEMORY_INDEX_OVERSIZE=1 bypass in effect" >&2
    exit 0
  fi
  echo "" >&2
  echo "check-memory-index-size: ${#OVER_HARD[@]} auto-memory index(es) at/over the ${HARD_KIB} KiB load cap." >&2
  echo "  Everything past the cap is silently dropped from recall. Compact to under ${WARN_KIB} KiB:" >&2
  echo "  keep one line per entry, move detail into the topic file, drop/merge stale entries (detail survives in the topic .md files)." >&2
  echo "  One-shot bypass (logged): ALLOW_MEMORY_INDEX_OVERSIZE=1 ..." >&2
  exit 1
fi
exit 0
