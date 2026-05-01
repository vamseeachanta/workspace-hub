# Archived Skill: `codex-background-burn-orchestration`

Original path: `/home/vamsee/.hermes/skills/autonomous-ai-agents/codex-background-burn-orchestration`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/autonomous-ai-agents/codex-background-burn-orchestration`
Consolidation date: 2026-04-29

---

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
   - Keep about 3-5 concurrent Codex lanes; top up periodically rather than launching too many at once.

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

Before reporting that a lane landed:
- inspect process output
- check `git -C <worktree> status --short`
- check `git -C <worktree> log --oneline -3`
- verify pushed branch or main ancestry
- verify GitHub comment/closure state

Report "running" or "blocked" rather than claiming completion when the process is only launched.
