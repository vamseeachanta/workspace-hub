---
name: codex-background-burn-orchestration
description: Run quota-aware Codex usage-burn waves as useful background issue-execution lanes, including Hermes stdin-close and sandbox recovery patterns.
version: 1.0.0
author: Hermes Agent
category: autonomous-ai-agents
tags: [codex, quota-burn, background-processes, github-issues, worktrees, provider-utilization]
related_skills:
  - codex
  - agent-usage-optimizer
  - parallel-approved-issue-worktrees
---

# Codex Background Burn Orchestration

## Trigger / when to use

Use this when the user asks to deliberately spend/burn Codex capacity over a short window, or to keep Codex productively occupied on approved work, especially phrases like:
- "burn X% of Codex usage"
- "use up Codex capacity over the next 24 hours"
- "keep Codex lanes running"
- "route underused Codex quota to approved issues"

Class of task: quota-aware Codex lane orchestration that converts available Codex capacity into bounded, approved GitHub issue execution rather than synthetic token waste.

## Operating pattern

1. Refresh telemetry first
   - Run the provider utilization refresh if available:
     ```bash
     bash scripts/cron/provider-utilization-refresh.sh
     ```
   - Inspect:
     - `config/ai-tools/agent-quota-latest.json`
     - `config/ai-tools/provider-routing-scorecard.json`
     - `config/ai-tools/provider-work-queue.json`
   - Convert the target into a rough message budget. Example: if Codex shows `week_messages=5`, `weekly_limit=1400`, and the user asks for 50% remaining in 24h, target about `(1400-5)*0.5 ≈ 700` messages.

2. Select useful lanes, not synthetic burn
   - Prefer `provider-work-queue.json -> provider_queues.codex.top_issues`.
   - Favor open issues with `status:plan-approved` and bounded implementation/test/refactor/documentation scope.
   - Respect existing `agent:*` labels and avoid issues already `status:working` unless recovering a known stalled lane.
   - When the user asks for ecosystem-aware or ambition-aware burn planning, combine the generated queue with live per-repo issue scans and recent-session/history signals; use `references/workspace-ecosystem-lane-selection.md` for the lane-selection checklist and avoid-list.
   - For repeated judge/checklist prompts after terminal-but-incomplete runs, use `references/checklist-crosswalk-generator-pattern.md` to write fresh crosswalk evidence instead of relaunching or only restating blockers.
   - Keep about 3-5 concurrent Codex lanes; top up periodically rather than launching too many at once.
   - For short burn windows where the goal is high useful throughput, bundle 2-4 tightly related approved issues from the same repo into one Codex lane/worktree only when they share validation setup and can land as separate commits or clearly scoped blocker notes; see `references/multi-issue-bundle-closeout.md`.
   - Before launching an overnight/12-hour burn, produce a compact launch manifest, per-lane PID/session/log paths, exit-code/status artifacts, and autonomous-vs-human-in-loop exclusions; use `references/autonomous-burn-launch-closeout.md` for the launch, closeout, checklist-grade continuation audit, supplemental-audit, and evidence-redaction shape. Treat missing PID/exit/status launch evidence as unrecoverable later rather than backfilling guesses.
   - When all requested Codex bundles are terminal but the operation is not successful, write a judge-ready incomplete closeout instead of implying success; use `references/judge-ready-incomplete-closeout.md` for terminal-vs-success classification, blocked-partial bundles, refined secret scans, hashes, and concise user-facing closeout.

3. Isolate each lane
   - Create one worktree or clone per issue under a run directory, e.g.:
     ```bash
     git worktree add -b codex/burn-YYYYMMDD-issue-NNNN /mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN origin/main
     ```
   - If `git worktree add` is slow or leaves corrupt metadata, use a shared clone fallback:
     ```bash
     git clone --shared --branch main /mnt/local-analysis/workspace-hub /mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN
     git -C /mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN checkout -B codex/burn-YYYYMMDD-issue-NNNN
     ```
   - Never run dangerous Codex modes in a dirty shared checkout.

4. Coordinate GitHub
   - Add labels when safe:
     ```bash
     gh issue edit NNNN --add-label agent:codex,status:working
     ```
   - Post an execution-start comment naming the branch/worktree and validation intent.

5. Prompt each Codex lane
   Include:
   - issue URL and number
   - branch/worktree path
   - approved plan artifact paths
   - hard gates: verify issue open + `status:plan-approved`, TDD, validation, adversarial self-review
   - commit/push/comment requirements
   - explicit forbidden paths and no force-push
   - close only if landed/allowed by policy

## Hermes/Codex background launch gotchas

### Stdin close is mandatory in Hermes background mode

Codex may print `Reading additional input from stdin...` and hang indefinitely even when the command uses `< /dev/null` or an empty pipe.

Reliable Hermes pattern:
```python
# 1. Launch background process
terminal(
  command='codex exec -c model_reasoning_effort="high" --dangerously-bypass-approvals-and-sandbox --cd /abs/worktree "$(cat /abs/prompt.md)"',
  background=True,
  notify_on_complete=True,
  workdir='/abs/worktree',
)

# 2. Immediately close stdin on the returned session_id
process(action='close', session_id='<session_id>')

# 3. Then monitor
process(action='poll', session_id='<session_id>')
```

If a run is stuck at only `Reading additional input from stdin...`:
1. `process(action='close', session_id='...')`
2. wait briefly
3. if still stuck, kill and relaunch with the explicit close pattern

### Prefer Codex `--cd` over terminal workdir alone

Codex may report an unexpected banner `workdir` when relying only on the terminal tool's `workdir`. Pass both:
```bash
codex exec --cd /abs/worktree "$(cat /abs/prompt.md)"
```

### Sandbox loopback failure recovery

In some environments, `--full-auto` / sandboxed Codex runs cannot execute shell commands and emit:
```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

For implementation lanes that are already isolated to a dedicated worktree/clone, relaunch with:
```bash
codex exec \
  -c model_reasoning_effort="high" \
  --dangerously-bypass-approvals-and-sandbox \
  --cd /abs/worktree \
  "$(cat /abs/prompt.md)"
```

Safety requirements for this fallback:
- only in an isolated issue worktree/clone
- prompt must narrowly constrain owned paths and issue scope
- no force-push
- verify diffs before landing

## Periodic controller pattern

For a multi-hour burn target, create a scheduled controller every 1-2 hours that:
1. refreshes quota/routing artifacts
2. counts active Codex processes/lanes
3. inspects completed lane outputs and worktree status
4. avoids duplicate issues
5. launches new lanes only until the target concurrency is restored
6. reports issue URLs, branches, process IDs, quota snapshot, and blockers

Do not let the controller recursively schedule more cron jobs.

## Verification before claiming success

Before reporting that a lane landed or a burn wave is complete/incomplete:
- inspect process output and capture Codex-reported token usage when available
- check `git -C <worktree> status --short`
- check `git -C <worktree> log --oneline -3`
- verify pushed branch or main ancestry
- verify GitHub comment/closure state
- remove any temporary `status:working` label from closed or explicitly blocked issues that are no longer actively running
- when the user supplies a judge/checklist-style continuation, use `references/autonomous-burn-launch-closeout.md` to emit evidence artifacts and a checklist crosswalk instead of self-marking boxes or merely restating blockers; if the checklist says “work on unchecked items” but provides no new bundle IDs or override decisions, refresh live/process/git/GitHub evidence, write `checklist-crosswalk-evidence-*` artifacts, set `new_launches_this_turn=0`, and stop on explicit user/governance input rather than inventing a continuation lane

Report "running" or "blocked" rather than claiming completion when the process is only launched. For partial bundles, close only issues with landed/verified scope and leave blockers open with an evidence comment naming the missing prerequisite or approval gap.
