---
name: ace-linux-1-control-surface
description: Operate ace-linux-1 as the continuous AI-agent control surface for overnight and continuous batches that keep GTM material moving toward client outreach.
triggers:
  - User wants ace-linux-1 to remain the approval/control surface while long-running lanes continue elsewhere
  - Overnight or continuous batches need tmux/log/cron inspection and lane reconciliation
  - GTM work must keep turning repo evidence and external signals into client-ready material
related_skills:
  - workstation-aware-provider-orchestration
  - hermes-memory-bridge
  - gtm-signal-to-engineering-artifact-conversion
---

# ace-linux-1 control surface

Use this when Hermes should treat `ace-linux-1` as the durable operator console for approvals, launch decisions, GitHub mutations, morning reconciliation, and GTM packaging while background lanes run on `ace-linux-1` and `ace-linux-2`.

## Durable operating model

- `ace-linux-1` is the user-facing control surface. Keep plan approvals, work approvals, queue decisions, and GitHub state changes here unless explicit failover is chosen.
- `ace-linux-2` is overflow/worker capacity. It should execute isolated work, not become a shadow control plane.
- Long-running work should leave durable evidence in three places:
  1. prompt packs under `docs/plans/overnight-prompts/`
  2. local logs such as `logs/night-runs/`
  3. repo-backed memory / GTM docs under `.claude/memory/` and `docs/gtm/`
- GTM objective: continuously convert signals, repo work, and approved engineering outputs into client-ready material while keeping the engineering-evidence boundary explicit.

## Trigger checklist

Use this skill when any of these are true:
1. A batch is already running and you need to inspect or reconcile it.
2. You are preparing an overnight prompt pack.
3. The user wants continuous GTM motion without losing approval control.
4. You need to update repo-backed memory so the control-surface pattern survives reboots and handoffs.

## Control-surface inspection commands

Run these from `/mnt/local-analysis/workspace-hub`.

### 1) Inspect active local tmux sessions
```bash
tmux list-sessions 2>/dev/null || true
tmux capture-pane -t <session> -p -S -120
```

### 2) Inspect local night-run logs
```bash
find logs/night-runs -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' 2>/dev/null | sort
```

### 3) Inspect prompt packs and result artifacts
```bash
find docs/plans/overnight-prompts -maxdepth 3 -type f \( -name '*.md' -o -name '*.sh' \) | sort | tail -200
find docs/plans/overnight-prompts/<date-pack>/results -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' 2>/dev/null | sort
```

### 4) Inspect remote ace-linux-2 worker state
```bash
ssh ace-linux-2 "bash -lc 'tmux list-sessions 2>/dev/null || true'"
ssh ace-linux-2 "bash -lc 'find /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports -maxdepth 1 -type f -printf \"%TY-%Tm-%Td %TH:%TM %s %p\\n\" 2>/dev/null | sort'"
```

### 5) Inspect cron/automation that keeps lanes moving
```bash
crontab -l | grep -Ei 'hermes|night|provider|memory|learn|cron' || true
bash scripts/upkeep/health-check.sh || true
```

### 6) Inspect workspace drift before mutating state
```bash
git status --short
git branch --show-current
git rev-parse --short HEAD
```

## Mobile / Telegram control-plane mode

When the user is operating from Telegram or another lightweight chat surface, keep orchestration terse and action-oriented:

1. Offer numbered/lettered choices for the next control-plane action, then execute the selected option immediately.
2. For recovery/status sweeps, inspect live machine state, tmux/processes/cron, GitHub auth/queue, and durable artifact paths before recommending new launches.
3. If existing provider/autofeed activity is saturated or overlapping, pause the feeder first and reconcile current lanes before starting more work.
4. Return a compact dashboard: host, workspace, repo/branch/head, git cleanliness, gateway/cron state, active-ish provider counts, key artifact paths, and the recommended next choice.
5. Avoid GitHub mutations, process kills, destructive git operations, and new long-running fan-out during reconciliation unless the user explicitly approves that action.

## Multi-machine Telegram/Hermes MVP

When the user asks whether Telegram + Hermes can connect to all available machines, do not collapse connectivity into execution. Use a staged MVP:

1. GitHub issues remain the authoritative queue and audit trail.
2. Labels route work to hosts, for example `machine:ace-linux-1`, `machine:ace-linux-2`, and `agent:<provider>`.
3. Each host runs its own local cron/scheduler worker and only claims approved work assigned to that host.
4. Workers post progress, artifacts, failures, and completion evidence back to GitHub comments.
5. Telegram/Hermes is the control/status/notification surface until direct Telegram-to-machine dispatch has separately approved auth, target-selection, locking, audit, rollback, and cost controls.
6. Implement the shared queue/claim/lock contract before host-specific worker behavior.

Reference: `references/github-label-cron-telegram-mvp.md`.

## Lane routing policy

1. **Keep approvals on ace-linux-1**
   - User decisions
   - plan approvals / work approvals
   - GitHub comments, labels, close/reopen decisions
   - dispatch ledger updates
2. **Use ace-linux-1 for orchestration-heavy lanes**
   - provider routing
   - queue triage
   - planning / synthesis / adversarial review
   - GTM packaging and morning runbooks
3. **Use ace-linux-2 only for bounded overflow**
   - isolated implementation or review worktrees
   - only after readiness checks and zero-contention path ownership
   - avoid GitHub mutation there unless auth/readiness is freshly proven safe
4. **Route by evidence type**
   - planning/research => Claude/Gemini
   - bounded implementation/repair => Codex or Claude worker
   - outreach packaging => ace-linux-1 synthesis lane using repo-backed GTM docs

## Approval gates

Before launching or restarting any long-running lane:
1. Confirm whether the issue is implementation-approved or planning-only.
2. Verify file-ownership / worktree isolation.
3. Confirm the provider is authenticated on the exact launch path.
4. Ensure the lane writes to a bounded artifact location.
5. If the action changes GitHub state or starts a costly long-running batch, keep the final go/no-go on `ace-linux-1`.

## GTM push loop

Use this loop to keep material moving toward outreach:

1. **Collect signals**
   - `docs/gtm/`
   - job scanner outputs
   - approved issue outputs
   - external topic signals (conference pages, posts, inbound requests)
2. **Convert to engineering artifact or evidence**
   - demo report
   - methodology note
   - capability page
   - benchmark note
   - outreach template tied to a real asset
3. **Package for client readiness**
   - update `docs/gtm/*.md`
   - draft or refine outreach copy
   - attach proof paths and engineering caveats
4. **Queue the next ask**
   - technical call
   - demo send
   - targeted outreach email
   - follow-up research issue
5. **Persist memory**
   - update `.claude/memory/` when the operating model changes
   - keep facts concise and durable; never store credentials

## Verification checklist

A control-surface update is complete when:
- repo-backed memory states that `ace-linux-1` is the approval/reconciliation surface
- the current prompt pack / lane logs are discoverable from the repo
- at least one skill documents tmux/log/cron inspection plus routing and approval gates
- GTM docs still reflect the engineering-evidence boundary
- `git diff --stat` shows only intended files before commit

## Pitfalls

- Letting `ace-linux-2` silently become a second control plane.
- Storing only temporary session notes instead of repo-backed memory.
- Launching new lanes before checking existing tmux sessions, logs, and result artifacts.
- Turning conference/social signals directly into client claims without engineering proof.
- Committing telemetry, session-signals, or secrets with the control-surface update.
- Editing generated memory files without updating the template/source that should own the fact.
