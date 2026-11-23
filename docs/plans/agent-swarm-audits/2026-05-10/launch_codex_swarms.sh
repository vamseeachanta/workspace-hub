#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/agent-swarm-audits/2026-05-10"
LOGS="$BASE/logs"
mkdir -p "$LOGS"
: > "$LOGS/codex-swarm-pids.txt"
for spec in \
  "1 live-state-gate-audit" \
  "2 capability-gap-map" \
  "3 plan-review-drift" \
  "4 execution-readiness-partition" \
  "5 learning-transfer"; do
  set -- $spec
  i=$1
  name=$2
  prompt_file="$BASE/prompt-swarm-$i-$name.md"
  jsonl="$LOGS/swarm-$i-codex.jsonl"
  last="$LOGS/swarm-$i-last-message.txt"
  # Run as a detached subshell; prompt is supplied on stdin via `-`.
  # This avoids Codex 0.130.0 hanging on Hermes' open stdin and avoids
  # command-line prompt parsing issues for multi-line /goal text.
  (
    cd "$ROOT"
    codex exec --cd "$ROOT" --sandbox workspace-write --json --output-last-message "$last" - < "$prompt_file" > "$jsonl" 2>&1
  ) &
  pid=$!
  echo "swarm-$i $pid $jsonl $last" | tee -a "$LOGS/codex-swarm-pids.txt"
done
