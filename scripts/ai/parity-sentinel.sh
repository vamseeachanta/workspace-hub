#!/usr/bin/env bash
# parity-sentinel.sh — measure live Opus behavior vs the Fable baseline and alert on regression.
#
# Part of continuous parity instrumentation (#3061, harden-ecosystem epic #3058).
# Samples recent Claude Code transcripts that used the current primary model,
# digests them (no client content leaves the box), computes behavioral metrics,
# and compares to analysis/parity-baseline.json (the Fable corpus baseline, #3056).
#
# Usage: parity-sentinel.sh [--model claude-opus-4-8] [--days 14]
# Env: EQUIV_ALERT_ISSUE=<n> to post regressions to an issue.
# Exit: 0 = within bounds, 1 = regression detected.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$ROOT" || exit 1
MODEL="claude-opus-4-8"; DAYS=14   # model-id-ok (CLI default)
while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift ;;
    --days) DAYS="$2"; shift ;;
  esac; shift
done

PROJ="$HOME/.claude/projects"
[ -d "$PROJ" ] || { echo "no transcripts at $PROJ"; exit 0; }
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT

# recent transcripts that actually used $MODEL (model-tagged per assistant turn)
mapfile -t files < <(find "$PROJ" -name '*.jsonl' -mtime "-${DAYS}" 2>/dev/null \
  | xargs grep -l "\"model\":\"${MODEL}\"" 2>/dev/null)
if [ "${#files[@]}" -eq 0 ]; then
  echo "no $MODEL transcripts in last ${DAYS}d — nothing to measure"; exit 0
fi

# digest locally (PII stays in the tmp dir; only aggregate metrics persist)
uv run --no-project python scripts/ai/transcript-digest.py "$(hostname)" "$work/digests" "${files[@]}" >/dev/null 2>&1

stamp="$(date -u +%Y-%m-%d)"
mkdir -p "$ROOT/.claude/state/parity"
report="$ROOT/.claude/state/parity/parity-live-${stamp}.json"
PYTHONPATH=scripts/ai uv run --no-project python scripts/ai/parity_metrics.py \
  "$work/digests" --model "$MODEL" --baseline analysis/parity-baseline.json --json | tee "$report"
rc="${PIPESTATUS[0]}"   # python's exit (1 = regression), not tee's

if [ "$rc" = "1" ]; then
  echo "PARITY REGRESSION vs Fable baseline ($MODEL, last ${DAYS}d) — see $report" >&2
  if [ -n "${EQUIV_ALERT_ISSUE:-}" ] && command -v gh >/dev/null 2>&1; then
    gh issue comment "$EQUIV_ALERT_ISSUE" --body-file - < "$report" 2>/dev/null \
      && echo "[alert] posted to #$EQUIV_ALERT_ISSUE" >&2
  fi
fi
exit "$rc"
