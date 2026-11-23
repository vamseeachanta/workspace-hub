#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/local-analysis/workspace-hub
BASE="$ROOT/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed"
LOGDIR="$ROOT/logs/night-runs"
mkdir -p "$LOGDIR" "$BASE/results"
chmod +x "$BASE/run-claude-prompt.sh"
launch() {
  local session="$1" prompt="$2" log="$3"
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "SKIP existing $session"
    return 0
  fi
  tmux new-session -d -s "$session" "cd '$ROOT' && '$BASE/run-claude-prompt.sh' '$BASE/generated/launch-now/$prompt' '$LOGDIR/$log' acceptEdits"
  echo "STARTED $session -> $LOGDIR/$log"
}
launch nextwave-followup-2554-summaryfix-20260429-r1 nextwave-followup-plan-patch-2554-summaryfix-20260429-r1.md nextwave-followup-2554-summaryfix-20260429-r1.log
launch nextwave-followup-2555-inline-rationale-20260429-r1 nextwave-followup-plan-patch-2555-inline-rationale-20260429-r1.md nextwave-followup-2555-inline-rationale-20260429-r1.log
launch nextwave-followup-2556-outline-demo-paths-20260429-r1 nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md nextwave-followup-2556-outline-demo-paths-20260429-r1.log
launch nextwave-followup-2557-regen-spec-20260429-r1 nextwave-followup-report-spec-2557-regen-20260429-r1.md nextwave-followup-2557-regen-spec-20260429-r1.log
launch nextwave-followup-2550-2552-readiness-20260429-r1 nextwave-followup-readiness-2550-2552-20260429-r1.md nextwave-followup-2550-2552-readiness-20260429-r1.log
tmux list-sessions 2>/dev/null | grep -E 'nextwave-followup-(2554|2555|2556|2557|2550)' || true
