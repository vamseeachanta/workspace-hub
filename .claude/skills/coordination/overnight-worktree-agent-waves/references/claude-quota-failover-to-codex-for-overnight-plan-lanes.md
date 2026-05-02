# Archived Skill: `claude-quota-failover-to-codex-for-overnight-plan-lanes`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/claude-quota-failover-to-codex-for-overnight-plan-lanes`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/claude-quota-failover-to-codex-for-overnight-plan-lanes`
Consolidation date: 2026-04-29

---

---
name: claude-quota-failover-to-codex-for-overnight-plan-lanes
description: Recover an overnight multi-worktree planning wave when some Claude lanes hit quota by relaunching only the failed lanes with Codex in the same isolated worktrees and prompt files.
version: 1.0.0
author: Hermes Agent
---

# Claude quota failover to Codex for overnight plan lanes

Use when:
- you launched a large overnight planning-only wave with `claude -p`
- some lanes fail with `You've hit your limit · resets ...`
- other lanes are still healthy and should not be restarted
- each lane already has its own isolated worktree and committed prompt file

## Why this exists

In the 2026-04-23 10-agent pre-plan-review wave, several Claude workers exited due to quota exhaustion while other workers were still making progress. Restarting the entire batch would have wasted work and increased git contention risk. The reliable recovery was lane-by-lane failover to Codex, reusing the exact same worktree and prompt file.

## Preconditions

- each issue has its own isolated worktree
- each worktree already contains a self-contained worker prompt file
- the lane is planning-only or otherwise safe to rerun without user interaction
- Codex CLI is installed and authenticated

Verify:
- `which codex`
- `codex --version`
- the failed Claude lane's prompt file still exists
- the failed lane's worktree path is correct

## Recovery pattern

1. Detect quota-hit lanes from process output.
   Typical signal:
   - `You've hit your limit · resets 2pm (America/Chicago)`

2. Do **not** stop the healthy Claude lanes.
   Keep all still-running lanes alive.

3. Relaunch only the failed lane with Codex in the same worktree using the same prompt file.

Canonical command:

```bash
PROMPT=$(< /mnt/local-analysis/worktrees/ws-<issue>-planwave10/docs/plans/overnight-prompts/<wave-id>/worker.md)
codex exec \
  --sandbox workspace-write \
  -C /mnt/local-analysis/worktrees/ws-<issue>-planwave10 \
  --skip-git-repo-check \
  --output-last-message /mnt/local-analysis/worktrees/ws-<issue>-planwave10/logs/overnight-plan-wave/worker-codex-last.txt \
  "$PROMPT" </dev/null | tee /mnt/local-analysis/worktrees/ws-<issue>-planwave10/logs/overnight-plan-wave/worker-codex.log
```

4. Record the new process/session id and continue monitoring both the surviving Claude lanes and the Codex recovery lanes.

5. When reporting status, distinguish:
- healthy original Claude lanes
- failed Claude lanes
- Codex backfill lanes now running in recovery

## Why this works

- preserves zero git contention because the worktree ownership does not change
- preserves auditability because the prompt file does not change
- avoids redoing successful Claude work
- keeps the overnight batch moving despite provider-specific quota exhaustion

## Operational notes

- use this as lane-level failover, not as a reason to switch the entire batch provider midstream
- prefer Codex only for the failed lanes; avoid introducing unnecessary provider churn in healthy lanes
- store Codex output in separate `worker-codex.log` and `worker-codex-last.txt` files so provenance remains clear
- if a lane had already partially advanced GitHub state before Claude failed, verify the live issue labels/comments before relaunching to avoid duplicate label flips or duplicate summary comments

## Best fit

Best for:
- 6-10 lane overnight planning waves
- plan-gated repos like workspace-hub
- issue-by-issue isolated worktree orchestration

Less useful for:
- single-lane work
- waves where prompts are not yet written to disk
- non-isolated shared-worktree batches

## Example affected issues from the originating run

Recovered this way during the 2026-04-23 waves:
- #2454
- #2447
- #2439
- #2445
- #2446
- #2440
- #2449
- #2452

These were backfilled with Codex while other Claude planning lanes continued running.

## Additional lessons from the same run

- The failover can be repeated lane-by-lane many times in the same wave; you do not need to wait for all Claude lanes to fail before switching the affected subset.
- Process notifications from background workers are enough to trigger the failover loop; you can read the quota-hit message from the completed process output and relaunch immediately.
- Keep the same per-lane log convention when switching providers:
  - `logs/overnight-plan-wave/worker.log` for the original Claude lane
  - `logs/overnight-plan-wave/worker-codex.log` and `worker-codex-last.txt` for the Codex recovery lane
- When running a larger replacement wave (for example 10 isolated worktrees after a smaller 4-lane wave), pause any older continuation cron that targets overlapping pre-plan-review queues before creating the new continuation cron. This avoids duplicate relaunches and conflicting orchestration.
- The practical pattern becomes:
  1. launch the batch with Claude in isolated worktrees
  2. watch for quota-hit completions
  3. relaunch only the failed lanes with `codex exec` in the same worktrees
  4. keep all healthy lanes untouched
  5. continue overnight monitoring with a wave-specific cron job

## New lesson: Codex failover is not guaranteed to be healthy

The 2026-04-23 10-agent wave showed that Claude→Codex failover can itself degrade under sandbox/runtime constraints.

Observed failure signals on Codex recovery lanes:
- `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`
- `js_repl kernel exited unexpectedly`
- MCP GitHub fetch/search failures after the sandbox/runtime error
- final lane summaries that explicitly say no plan file, no review artifacts, no GitHub mutation succeeded

Practical rule:
- do not assume that a Codex recovery lane made useful progress just because the process is still running or exits `0`
- inspect the lane log/output for concrete success markers before counting it as recovered:
  - canonical `docs/plans/YYYY-MM-DD-issue-NNN-*.md` path actually created
  - `scripts/review/results/*plan-NNN-*` artifacts actually created
  - GitHub label/comment mutation actually succeeded
- if the lane reports environment-blocked outcomes (no writes, no review dispatch, no GitHub mutation), classify it as **blocked by environment**, not as a planning success and not as an approval-ready item

## Triage rule after failed Codex fallback

When Codex fallback shows the sandbox/runtime failure signals above:
1. mark the lane as environment-blocked in the live status summary
2. do not keep blindly relaunching the same provider in the same environment
3. separate issues into:
   - recovered successfully via Codex
   - still running and unknown
   - blocked by environment after Codex fallback
4. continue the rest of the overnight wave, but be explicit that throughput is now constrained by the environment rather than by prompt quality or issue decomposition

This matters because overnight orchestration can otherwise overstate progress: the right outcome is often "GitHub/planning mutation did not happen; rerun later in a working session," not "lane completed with caveats."