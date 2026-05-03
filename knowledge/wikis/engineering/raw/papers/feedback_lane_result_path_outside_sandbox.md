> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_lane_result_path_outside_sandbox.md

---
name: Lane result path outside sandbox
description: Provider-autofeed lanes prescribe result paths under /mnt/local-analysis/agent-logs/ which is outside the workspace-hub sandbox; Read/Write/stat all blocked. Detect early and fall back to docs/sessions/.
type: feedback
originSessionId: 1c10e542-7eb3-4c59-b2af-3c7eadf30bfb
---
When dispatched as a provider-autofeed/min3/recovery lane, the orchestrator commonly passes a result file path under `/mnt/local-analysis/agent-logs/<run>/results/<lane>.md`. The lane sandbox is `/mnt/local-analysis/workspace-hub`, so that path is **unreachable** — `Read`, `Write`, and even `stat` via `Bash` are all denied with "may only X from the allowed working directories" errors. `Glob` against `agent-logs/**` *does* still work (path enumeration only, no file contents).

**Why:** observed 2026-04-30 in lane `claude-1-control-plane-scoreboard` of run `provider-autofeed-20260430-100339`. The lane could not write its prescribed result file. Sister monitor files (`provider-autofeed-monitor/latest.md`, `lane-state-*.md`, `snapshot-*.md`) were also unreadable. The same constraint almost certainly affects every prior provider-autofeed/min3/recovery lane run from inside the workspace-hub sandbox.

**How to apply:**
1. **Detect early.** As the first action in any lane that names an `agent-logs/...` result path, attempt a tiny `Write` to a sibling `.write-probe.tmp` and a `Read` of the prescribed result file. If either is denied with "may only ... from the allowed working directories", you are in this scenario.
2. **Fall back deterministically.** Write the canonical lane output to `docs/sessions/YYYY-MM-DD-<run>-<lane>.md` inside the workspace and put an explicit ENV-MISMATCH banner at the top so the orchestrator can locate and copy it out-of-band.
3. **Operate on path metadata only.** `Glob` enumeration of `agent-logs/**` is your only signal — use presence/absence of `results/<lane>.md` next to `logs/<lane>.log` as the stalled-vs-completed indicator, and treat `.rerun.log` / `.g25flash.log` / `.g25pro.log` / `.openrouter.log` suffixes as retry/fan-out watermarks. Flag every conclusion as `[content-unverified]`.
4. **Do not waste budget retrying.** The sandbox is enforced at the harness level, not by user permission grants. Re-attempting `Read` or asking for permission will not unblock it within the lane.
5. **Recommend the durable fix to the operator** in your output: either (a) extend the lane allowlist to include `/mnt/local-analysis/agent-logs/**`, (b) make `agent-logs/` a subtree (or symlink) of `workspace-hub`, or (c) move the prescribed result path inside the workspace.
