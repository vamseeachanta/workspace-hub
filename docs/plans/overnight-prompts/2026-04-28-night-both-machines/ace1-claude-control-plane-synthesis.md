# A3 — ace-linux-1 Claude control-plane synthesis lane

You are running on `ace-linux-1` from `/mnt/local-analysis/workspace-hub` in Claude Code plan/read-only mode. Do not ask the user questions.

## Mission

Act as the overnight control-plane auditor. Monitor the dispatch plan and produce a morning synthesis, but do not implement code and do not mutate GitHub issue state unless explicitly told by the operator in a later session.

## Allowed writes

Only write:

- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/control-plane-morning-runbook.md`
- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/control-plane-lane-health.md`
- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/control-plane-next-dispatch.md`

## Read-only checks

1. Re-read `master-dispatch-ledger.md` and all lane prompt files in this directory.
2. Inspect live issue state for issues: #2289, #2433, #2459, #2269, #2346, #2295, #2501, #2254, #2519, #2520, #2515, #2458, #2364, #2368, #2369, #2373, #2403, #2227.
3. Check local process/tmux state on ace-linux-1.
4. Check remote ace-linux-2 tmux/log/report state via SSH read-only commands.
5. Inspect generated result files and logs if present.

## Output requirements

### `control-plane-lane-health.md`

Table columns: lane, machine, provider, process/session, last artifact/log, classification (`RUNNING`, `READY_FOR_REVIEW`, `STALLED_NO_OUTPUT`, `BLOCKED`, `NOT_LAUNCHED`), evidence.

### `control-plane-morning-runbook.md`

Prioritized morning actions:

1. Which commits/comments to verify first.
2. Which blockers need human decisions.
3. Which issues can be closed after evidence review.
4. Which provider should receive the next batch based on observed overnight output.

### `control-plane-next-dispatch.md`

A conservative follow-up batch proposal with max 3 lanes, respecting plan gate and zero file contention. Include exact prompt-file names but do not launch them.
