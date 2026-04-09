#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/mnt/local-analysis/workspace-hub"
cd "$REPO_ROOT"
mkdir -p logs

run_prompt() {
  local name="$1"
  local prompt_file="$2"
  local mode="$3"
  local budget="$4"
  local log_file="logs/${name}-$(date +%Y%m%d-%H%M%S).log"
  local prompt
  prompt=$(< "$prompt_file")

  echo "Launching $name"
  echo "  prompt: $prompt_file"
  echo "  mode:   $mode"
  echo "  log:    $log_file"

  if [[ "$mode" == "acceptEdits" ]]; then
    claude -p \
      --permission-mode acceptEdits \
      --no-session-persistence \
      --output-format text \
      --max-budget-usd "$budget" \
      "$prompt" </dev/null | tee "$log_file"
  else
    claude -p \
      --permission-mode "$mode" \
      --no-session-persistence \
      --output-format text \
      "$prompt" </dev/null | tee "$log_file"
  fi
}

case "${1:-}" in
  t2)
    run_prompt "claude-terminal-2-rerun" "docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md" "acceptEdits" 20
    ;;
  t4)
    run_prompt "claude-terminal-4-rerun" "docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md" "acceptEdits" 20
    ;;
  t1-audit)
    run_prompt "claude-terminal-1-audit" "docs/plans/overnight-prompts/2026-04-09-4claude/terminal-1-subseaiq-benchmarks.md" "plan" 0
    ;;
  t3-audit)
    run_prompt "claude-terminal-3-audit" "docs/plans/overnight-prompts/2026-04-09-4claude/terminal-3-naval-arch-vessel-integration.md" "plan" 0
    ;;
  all-main)
    run_prompt "claude-terminal-2-rerun" "docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md" "acceptEdits" 20
    run_prompt "claude-terminal-4-rerun" "docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md" "acceptEdits" 20
    ;;
  *)
    cat <<'EOF'
Usage:
  bash scripts/claude-rerun-second-pass.sh t2
  bash scripts/claude-rerun-second-pass.sh t4
  bash scripts/claude-rerun-second-pass.sh t1-audit
  bash scripts/claude-rerun-second-pass.sh t3-audit
  bash scripts/claude-rerun-second-pass.sh all-main
EOF
    exit 1
    ;;
esac
