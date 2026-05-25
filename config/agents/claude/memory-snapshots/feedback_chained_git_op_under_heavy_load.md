---
name: feedback_chained_git_op_under_heavy_load
description: "Under heavy parallel-git load (kanban fleet + multi-session), chained `git add && git commit && ...` in one bash call is hazardous — one stuck step kills the entire chain; atomic per-file calls separated by `;` survive"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 62018fcb-5b01-49dd-a745-aa7eb0c440bb
---

When parallel-git load is high (active Hermes kanban fleet, multiple concurrent Claude/Codex/Gemini sessions all hammering shared FS), do NOT chain `git add && git commit && git add && git commit && ...` inside a single bash call.

**Why:** 2026-05-23 overnight Workstream A (llm-wiki standards-page batch) — a chained add+commit of 3 files hit a 19-minute stuck `git add` in kernel `D` state (PID 3108169) under 65 concurrent git processes. The `&&` short-circuit semantics meant no commits in the chain landed; the working tree was fine but `main` stayed at the first commit. Recovery: `kill -9 <pid>` + `rm .git/index.lock` + restart with atomic per-file bash calls. Total cost: ~25 min lost wall-clock, 3 commits delayed. The same pattern surfaces anytime the kanban fleet is processing (261 workers observed at peak this session).

**How to apply:**

- **Detect heavy-load condition before chaining**:
  - `pgrep -af git | wc -l` returns >20, OR
  - `pgrep -af 'hermes.*kanban task' | wc -l` returns >10, OR
  - Multiple Claude/Codex/Gemini sessions observable in `ps -ef`.
- **Under heavy load**: one bash call per `add+commit` pair, separated by `;` (not `&&`) so a stuck step doesn't kill remaining steps. Wrap each in a small shell function (e.g., `commit_one() { add; commit -- $1; }`) for readability.
- **Under any load**: prefer atomic per-file `git commit -m "..." -- <file>` pathspec form over `git commit -am` per [[feedback_multi_agent_commit_serialization]] — preserves parallel-session staged files in the index.
- **Use `GIT_OPTIONAL_LOCKS=0` on read-side commands** (`git status`, `git log`) to avoid contributing to lock contention per [[feedback_git_status_lock_storm]].
- **If a stuck git in D state for >5 min appears**: `kill -9 <pid>` + `rm .git/index.lock` is the standard recovery. Confirm only that one process holds the lock first via `lsof .git/index.lock` or `fuser .git/index.lock`. Don't blindly rm if multiple PIDs are holding it (would race).
- **Verify recovery via raw refs, not git commands**: `cat .git/HEAD && cat .git/refs/heads/main` (and `.git/packed-refs`) bypasses the index-lock dependency and works even when `git log` hangs.

**Do not apply when:** load is low (<5 concurrent git procs, no active kanban fleet) — chaining is fine and faster. The rule is heavy-load-specific.

Related: [[feedback_git_status_lock_storm]] (zombie status accumulation), [[feedback_multi_agent_commit_serialization]] (umbrella for parallel-git hazards), [[feedback_retry_loop_sweep_contamination]] (specific commit-sweep variant), [[feedback_reflog_as_ground_truth]] (recovery diagnosis).
