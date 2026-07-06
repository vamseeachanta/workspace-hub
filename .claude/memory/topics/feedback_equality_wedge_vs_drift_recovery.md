> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_equality_wedge_vs_drift_recovery.md

---
name: feedback_equality_wedge_vs_drift_recovery
description: "When the auto-sync loop is WEDGED (non-FF deadlock), self-healing can't recover — reset local main to origin/main then run equality-matrix-cron.sh"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4acd88b0-1acd-4909-803f-a9a0d2187f13
---

The "cron re-greens, never manual reset to chase green" rule ([[feedback_dev_primary_equality_green_is_self_healing]]) has ONE exception: a **wedge**, not drift.

**Signature of a wedge:** local `main` is simultaneously *ahead* (N unpushed `chore(sync): auto-sync` commits) AND *behind* origin/main. The auto-sync push is rejected non-fast-forward every tick, so the loop can never converge on its own. Downstream: the equality matrix fail-closed logic grades every dev-primary cell STALE-CHECKOUT because the machine's evidence never reaches origin/main. Observed 2026-07-05 on ace-linux-1 (dev-primary): 23 unpushed + 72 behind, wedged since ~Jun 29.

**Why:** self-healing assumes the push can land. A non-FF deadlock breaks that assumption — the cron re-greens drift, it cannot un-wedge itself.

**How to apply (this is a destructive control-plane decision — get the user's OK, per the memory guard):**
1. **Prove regenerability before reset.** `git log origin/main..HEAD --format='%s' | sort -u` should be all `auto-sync`. Then `comm -23 <(git ls-tree -r --name-only HEAD|sort) <(git ls-tree -r --name-only origin/main|sort)` filtered against regenerable patterns must be empty. Flagged `scripts/`/`skills/` paths are a false alarm if `git diff origin/main HEAD -- <f>` shows pure *deletions* (local snapshot is older; origin is strictly ahead on hand-authored content — reset GAINS those lines).
2. **Backup tag first:** `git tag backup/main-prewedge-<sha> HEAD` (reset is recoverable; stashes + untracked files survive `reset --hard` untouched).
3. `git reset --hard origin/main` on local main.
4. **Re-green with the canonical entrypoint** (NOT manual git surgery): `bash scripts/readiness/equality-matrix-cron.sh` — it runs collect-equality.sh (fresh self-report showing dirty:false/behind:0/ahead:0) → build-equality-matrix.py → publish-equality.sh --rebuild (publishes via a disposable sparse worktree off origin/main; fast-forward by construction, allowlist-guarded — cannot re-wedge). A landing FF push (`git push` shows `<old>..<new> HEAD -> main`) is the proof the wedge is gone.

Companion: [[feedback_always_update_equality_matrix]] (agent CAN run publish-equality.sh), [[feedback_autosync_clobbers_subagent_worktree_commits]].
