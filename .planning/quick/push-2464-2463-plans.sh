#!/usr/bin/env bash
# Worker-4 plans-only push helper for issues #2464 and #2463.
# Uses the pre-push hook's documented GIT_PRE_PUSH_SKIP soft-bypass because
# scripts/quality/check_config_drift.py is missing a pyyaml dependency
# declaration (PEP 723 inline metadata OR `uv run --with pyyaml`). Fixing
# that is outside this worker's write boundaries (plans + review artifacts only).
#
# The bypass is audited by the hook to logs/hooks/pre-push-bypass.jsonl.
set -euo pipefail
export GIT_PRE_PUSH_SKIP=1
export GIT_PRE_PUSH_SKIP_REASON="worker-4 plans-only push (#2463 #2464); check_config_drift.py missing pyyaml dep is outside plan write boundaries — documented in .planning/quick/push-2464-2463-plans.sh"
git -C /mnt/local-analysis/workspace-hub/.claude/worktrees/ws-2460-2465-w4 \
    push origin HEAD:refs/heads/nightly/2460-2465-planwave
