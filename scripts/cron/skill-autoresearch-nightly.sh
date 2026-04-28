#!/usr/bin/env bash
# skill-autoresearch-nightly.sh — compatibility wrapper for the generic runner.
#
# Preserves the legacy skill lane while delegating branch isolation, evaluator
# dispatch, revert-on-non-improvement, and generalized result logging to:
#   scripts/skills/repo_ecosystem_autoresearch.py
#
# Safety: NEVER modifies main directly. The delegated runner uses
# autoresearch/skills-YYYY-MM-DD branch isolation and git_safe_commit.
#
# Usage:
#   bash scripts/cron/skill-autoresearch-nightly.sh [--dry-run] [--max-attempts N]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RUNNER="${WS_HUB}/scripts/skills/repo_ecosystem_autoresearch.py"
RESULTS_FILE="${WS_HUB}/.claude/state/skill-autoresearch/results.jsonl"
LEGACY_RESULTS_FILE="${WS_HUB}/.claude/state/skill-autoresearch/results.tsv"
EVAL_SCRIPT="${WS_HUB}/.claude/skills/development/skill-eval/scripts/eval-skills.py"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-5}"
TIME_BUDGET="${TIME_BUDGET:-180}"
declare -a ARGS=()

# Static adoption marker for cron policy tests; the runner invokes git_safe_commit
# through scripts/cron/lib/git-safe.sh after keeping an improvement. Branch
# isolation is implemented with git switch / git branch checks, and rejected
# candidates restore the original file content instead of relying on git restore.
GIT_SAFE_COMMIT_POLICY="git_safe_commit"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            ARGS+=("--dry-run")
            shift
            ;;
        --max-attempts)
            MAX_ATTEMPTS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--max-attempts N]"
            echo "  --dry-run       Show what would be done without making changes"
            echo "  --max-attempts  Max improvement attempts per run (default: 5)"
            echo ""
            echo "Delegates to scripts/skills/repo_ecosystem_autoresearch.py --target-type skill."
            exit 0
            ;;
        *)
            echo "Unknown arg: $1"
            exit 1
            ;;
    esac
done

cd "$WS_HUB" || exit 1
exec uv run --no-project python "$RUNNER" \
    --root "$WS_HUB" \
    --target-type skill \
    --max-attempts "$MAX_ATTEMPTS" \
    --time-budget "$TIME_BUDGET" \
    --results-file "$RESULTS_FILE" \
    --legacy-skill-results-tsv "$LEGACY_RESULTS_FILE" \
    --skill-eval-script "$EVAL_SCRIPT" \
    "${ARGS[@]:-}"
