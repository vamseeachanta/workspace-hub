#!/usr/bin/env bash
# dispatch-pull-cron.sh — scheduled entry point for the pull-dispatch loop.
#
# WHAT: runs `scripts/operations/dispatch_pull.py` under the canonical singleton
#   runtime contract (`scripts/cron/cron_runtime.py`), so a run that is still
#   going when the next cron tick fires is REFUSED (exit 75) instead of being
#   started alongside its predecessor. Two concurrent loops on one checkout
#   would contend for the same git index, the same lease refs and the same
#   `.claude/dispatch/records` tree.
#
# WHERE: `dev-primary` (ace-linux-1) via the `dispatch-pull` task in
#   config/scheduled-tasks/schedule-tasks.yaml.
#
# ARMING: this wrapper is INERT by default — it runs the loop in dry-run, which
#   claims nothing and writes nothing. Arming is a machine-local act, not a repo
#   edit, so a checkout landing on a new box never starts dispatching by itself.
#
#   Create ~/.workspace-hub/dispatch-pull.env (mode 600, NOT in the repo) with:
#
#       DISPATCH_PULL_APPLY=1        # this wrapper passes --apply
#       DISPATCH_APPLY_ENABLED=1     # drain.py / reconcile.py write gate
#
#   BOTH are required and they are deliberately two different names. dispatch_pull
#   refuses `--apply` unless `DISPATCH_APPLY_ENABLED=1` is also set; if this
#   wrapper derived one from the other, a single variable would satisfy both
#   gates and the second gate would stop existing.
#
#   Optional in the same file: DISPATCH_PULL_MACHINE, DISPATCH_PULL_MAX_CARDS,
#   DISPATCH_PULL_DELAY. Unset means the module's own conservative defaults
#   (5 cards per run, 30 s between hand-offs).
#
# EXIT: the loop's own code (0 = nothing failed, 1 = a drain failed, 2 = refused),
#   or 75 when a previous run still holds the singleton lock.
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$WORKSPACE_ROOT/logs/dispatch-pull"
LOG_RELATIVE="logs/dispatch-pull/cron-$(date +%Y-%m-%d).log"
RUNTIME_SCRIPT="$WORKSPACE_ROOT/scripts/cron/cron_runtime.py"
SCHEDULE_FILE="$WORKSPACE_ROOT/config/scheduled-tasks/schedule-tasks.yaml"
PULL_SCRIPT="$WORKSPACE_ROOT/scripts/operations/dispatch_pull.py"
ARMING_FILE="${DISPATCH_PULL_ENV_FILE:-$HOME/.workspace-hub/dispatch-pull.env}"

mkdir -p "$LOG_DIR"

# Keep 30 days of wrapper logs. The loop's own JSONL journal lives in the same
# directory and is pruned on its own schedule — matched by name, not by glob, so
# this never eats `<date>.jsonl`.
find "$LOG_DIR" -name 'cron-*.log' -mtime +30 -delete 2>/dev/null || true

# Machine-local arming. Sourced, not exported here: this script never sets
# DISPATCH_APPLY_ENABLED itself.
if [ -f "$ARMING_FILE" ]; then
    # shellcheck disable=SC1090
    . "$ARMING_FILE"
fi

argv=(uv run --script "$PULL_SCRIPT" --repo "$WORKSPACE_ROOT")

if [ -n "${DISPATCH_PULL_MACHINE:-}" ]; then
    argv+=(--machine "$DISPATCH_PULL_MACHINE")
fi
if [ -n "${DISPATCH_PULL_MAX_CARDS:-}" ]; then
    argv+=(--max-cards "$DISPATCH_PULL_MAX_CARDS")
fi
if [ -n "${DISPATCH_PULL_DELAY:-}" ]; then
    argv+=(--delay "$DISPATCH_PULL_DELAY")
fi

if [ "${DISPATCH_PULL_APPLY:-0}" = "1" ]; then
    if [ "${DISPATCH_APPLY_ENABLED:-0}" != "1" ]; then
        # Fail here rather than let the loop refuse at gate 2. Both readings are
        # correct, but only this one names the file the operator has to fix.
        echo "dispatch-pull-cron: DISPATCH_PULL_APPLY=1 without DISPATCH_APPLY_ENABLED=1" >&2
        echo "dispatch-pull-cron: set BOTH in $ARMING_FILE — nothing claimed." >&2
        exit 2
    fi
    export DISPATCH_APPLY_ENABLED
    argv+=(--apply)
else
    echo "dispatch-pull-cron: DRY RUN (no DISPATCH_PULL_APPLY=1 in $ARMING_FILE)"
fi

exec uv run --script "$RUNTIME_SCRIPT" run \
    --schedule-file "$SCHEDULE_FILE" \
    --workspace "$WORKSPACE_ROOT" \
    --task-id dispatch-pull \
    --log "$LOG_RELATIVE" \
    -- "${argv[@]}"
