#!/usr/bin/env bash
# bridge-commit.sh — the extracted, testable commit path of bridge-hermes-claude.sh (#3384).
#
# Function: bridge_commit_and_push <repo_root> <slice_owner:true|false> <timestamp>
#
# Fixes three defects that left the memory-bridge silently non-committing for ~6 weeks:
#   1. Self-stash bug — the old code ran `git stash push` AFTER `git add` but BEFORE `git commit`, so
#      it stashed the very staged content it was about to commit → "nothing to commit" every run.
#      Fix: commit FIRST; the manual pre-commit stash is deleted (redundant with `pull --rebase
#      --autostash`, which handles the rebase).
#   2. No liveness signal — context.md + the read-back slices are deterministic/byte-invariant, so
#      their git-commit clock never advances on a quiet day. Fix: write a daily, MACHINE-INDEPENDENT
#      heartbeat (date-only content) so an owner run always produces exactly one commit/day; the
#      identical blob makes concurrent/double-scheduled owners self-serialize (first commits, rest
#      no-op). `audit_memory_freshness.py` clocks this heartbeat for freshness.
#   3. Silent non-FF push — `git push` had no retry. Fix: bounded pull-rebase-then-push retry.
#
# Params (no script globals — unit-testable in isolation, r1/r2 review Finding):
#   repo_root    repo to commit in
#   slice_owner  "true" only on the designated owner box; anything else ⇒ dry-run (no commit)
#   timestamp    label for the commit message

bridge_commit_and_push() {
    local repo_root="$1" slice_owner="$2" timestamp="$3"
    cd "$repo_root" || return 1

    # Whole commit is owner-only — avoids cross-machine thrash on the shared snapshot (r2 Finding 1).
    if [[ "$slice_owner" != "true" ]]; then
        echo "[bridge] not slice owner — dry-run only (no commit)"
        return 0
    fi

    # Daily, MACHINE-INDEPENDENT heartbeat: date-only ⇒ every owner/run yields the identical blob ⇒
    # whoever commits first wins, others see no diff and no-op (self-serializing, double-schedule-safe).
    local hb=".claude/state/memory-bridge-heartbeat.json"
    mkdir -p "$(dirname "$hb")"
    printf '{"last_bridge_commit_utc":"%s","schema_version":1}\n' "$(date -u +%Y-%m-%d)" > "$hb"

    git add .claude/memory/ config/agents/codex/MEMORY.runtime.md \
            config/agents/gemini/MEMORY.runtime.md "$hb" 2>/dev/null

    if git diff --cached --quiet; then
        echo "[bridge] nothing to commit — memory + heartbeat already up to date"
        return 0
    fi

    # Pathspec-scoped commit (multi-agent-commit-serialization) — NEVER a bare `git add -A` sweep.
    # Commit BEFORE any stash/pull so the staged content actually lands (the old self-stash bug).
    git commit -q -m "chore(memory): bridge refresh + heartbeat (${timestamp})" -- \
        .claude/memory/ config/agents/codex/MEMORY.runtime.md \
        config/agents/gemini/MEMORY.runtime.md "$hb" || return 1

    # Bounded non-FF retry. --autostash handles any unrelated tracked dirt for the rebase; a failed
    # `git push` on the left of the `if` is errexit-exempt, so the loop continues to the next attempt.
    local attempt
    for attempt in 1 2 3; do
        if ! git pull --rebase --autostash --quiet; then
            echo "[bridge] rebase conflict during pull — resolve manually, then git push" >&2
            return 1
        fi
        if git push --quiet; then
            return 0
        fi
        echo "[bridge] push rejected (non-FF); retry ${attempt}/3" >&2
    done
    echo "[bridge] push still failing after 3 attempts — commit is local (reflog intact); next run pushes" >&2
    return 1
}
