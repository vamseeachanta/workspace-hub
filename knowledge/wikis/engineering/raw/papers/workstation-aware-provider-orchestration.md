# Archived Skill: `workstation-aware-provider-orchestration`

Original path: `/home/vamsee/.hermes/skills/coordination/workstation-aware-provider-orchestration`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/workstation-aware-provider-orchestration`
Consolidation date: 2026-04-29

---

---
name: workstation-aware-provider-orchestration
description: Plan and operate a Hermes-led control plane that routes AI provider work across workstations using quota urgency, machine readiness, GitHub issue gates, and a dispatch ledger.
version: 1.0.0
author: Hermes Agent
tags: [hermes, provider-routing, workstation-orchestration, quota-management, dispatch-ledger, github-issues]
related_skills:
  - agent-usage-optimizer
  - gh-work-planning
  - licensed-machine-prompt-orchestration
---

# Workstation-Aware Provider Orchestration

Use this skill when the user wants Hermes to coordinate AI provider/model usage across multiple machines or workstations, especially when provider quota/credits are time-sensitive and work must still respect GitHub plan/approval gates.

## Class of task

Design or operate a central AI workflow control plane that combines provider quota urgency, GitHub issue readiness, workstation availability, and safe dispatch prompts/ledgers.

## When to use

- User asks Hermes to orchestrate Claude/Codex/Gemini or other providers across multiple machines.
- User wants one workstation to control most of the workflow while other workstations execute overflow work.
- Provider quota is expiring or underused and the user wants to burn it down safely.
- Work needs to be routed by `agent:*`, `machine:*`, `status:*`, `priority:*`, `cat:*`, or `domain:*` labels.
- Cross-workstation execution must avoid git contention and preserve plan-first governance.

## Default workspace-hub assumptions

- `ace-linux-1` is the primary Hermes/operator control-plane workstation for almost all AI workflow orchestration: provider usage decisions, queue review, prompt generation, dispatch ledger updates, GitHub state changes, and cross-workstation reconciliation.
- `ace-linux-2` is the first overflow/execution worker node, not an equal peer control plane unless failover is explicitly chosen.
- `licensed-win-1` is the first licensed engineering worker target for OrcaFlex and AQWA runs; treat it as a worker dispatched from `ace-linux-1`, not as a control plane, until repo/tool/auth readiness and remote-run smoke tests prove otherwise.
- Keep a durable machine/software inventory for every worker that records installed programs, license availability, AI-provider auth state, repo checkout roots, run/smoke-test commands, and dispatch-safe work classes. If the inventory changes, update `docs/BUSINESS_BRAIN.md` or its linked machine-readiness registry/report.
- Current provider-account assumptions can change; verify live account state before routing spend. When only one paid Codex account is confirmed, do not plan around multiple paid Codex lanes unless the user explicitly updates the account inventory.
- Claude is best preserved for orchestration, planning, synthesis, and adversarial review.
- Codex is best for bounded implementation, tests, fixes, cleanup, and mechanical execution, especially when credits are expiring.
- Gemini is best for batched research, recon, risk enumeration, and architecture review where telemetry may be directional rather than exact.

## Planning workflow

1. **Open or update a GitHub issue first**
   - Use `gh-work-planning` and `github-issues`.
   - Capture the objective, workstation priority, provider urgency, and hard gates.
   - Do not launch implementation until `status:plan-approved` is present unless the task is planning/review-only.

2. **Refresh provider telemetry**
   ```bash
   bash scripts/cron/provider-utilization-refresh.sh
   # or at minimum:
   bash scripts/ai/assessment/query-quota.sh --refresh --json
   ```
   Then inspect:
   - `docs/reports/provider-utilization-weekly.md`
   - `docs/reports/provider-routing-scorecard.md`
   - `docs/reports/provider-work-queue.md`

3. **Reconcile telemetry with user-visible state**
   - If local scripts disagree with a user-visible provider quota/expiry screen, record the conflict explicitly.
   - Do not claim exact utilization when the source is `unavailable`, `estimated`, stale, or contradictory.
   - Still use the user's expiring-credit signal to prioritize safe bounded work.

4. **Verify control-plane readiness from `ace-linux-1`**
   Check or plan checks for:
   - repo sync and branch/worktree cleanliness
   - GitHub auth
   - Hermes config/profile and provider auth
   - provider telemetry artifacts
   - VPN reachability to worker machines
   - worker machine tool readiness
   - log/report directory availability

5. **Rank issue candidates**
   Prefer:
   - `status:plan-approved`
   - explicit `agent:*` labels
   - clear provider fit from the routing scorecard
   - non-overlapping file ownership
   - bounded validation commands

6. **Map provider + workstation together**
   A dispatch decision should consider both:
   - provider urgency / fit (for example expiring Codex credit)
   - machine readiness / ownership (for example `ace-linux-1` control plane, `ace-linux-2` overflow)

7. **Emit a dispatch ledger**
   Minimum fields:
   - issue number + URL
   - provider/model
   - workstation
   - reason for routing
   - quota/urgency basis
   - approval status
   - branch/worktree/path ownership
   - launch prompt or command
   - validation command(s)
   - expected evidence artifact/comment
   - fallback/stop condition

8. **Get approval before long-running execution**
   Present the operator with the shortlist and launch plan before starting cross-machine or high-credit-burn batches.

## Immediate expiring-credit playbook

When a provider credit expires within about 24 hours:

1. Refresh telemetry and read provider work queue.
2. Reconcile telemetry with the user's visible account state.
3. Shortlist plan-approved issues matching that provider.
4. For Codex, prefer tests, implementation, repair, cleanup, and crisp execution issues.
5. Assign first to `ace-linux-1`; use `ace-linux-2` for overflow only if readiness and zero-git-contention are verified.
6. Generate self-contained prompts/commands per issue/workstation.
7. Ask for final approval before launching a long-running batch.

## Pre-delegation worker readiness gate

Before delegating work to any worker workstation, especially `ace-linux-2`, run and record a reviewable readiness probe. The worker may be repo-ready but still unsafe for AI-provider execution.

Minimum checks:

1. **Host reachability**
   ```bash
   getent hosts <host> || true
   ping -c 1 -W 2 <host> || true
   ssh -o BatchMode=yes -o ConnectTimeout=8 <host> 'hostname; uname -a; pwd'
   ```

2. **Canonical workspace root**
   - Prefer `/mnt/local-analysis/workspace-hub` for Linux workers unless evidence says otherwise.
   - Do not assume similarly named roots (for example `/home/vamsee/workspace-hub`) contain the tier-1 repo clones.

3. **Tier-1 repo readiness**
   For each target repo, capture:
   ```bash
   ssh <host> 'cd /mnt/local-analysis/workspace-hub/<repo> && \
     git branch --show-current && \
     git rev-parse --short HEAD && \
     git remote get-url origin && \
     git status --short && \
     git rev-list --left-right --count @{u}...HEAD 2>/dev/null || true && \
     test -f pyproject.toml && echo pyproject=yes || echo pyproject=no && \
     test -f uv.lock && echo uv_lock=yes || echo uv_lock=no && \
     test -d .venv && echo venv=yes || echo venv=no'
   ```
   Treat root/workspace-hub dirty state separately from child repo cleanliness; root dirt can still block workspace-hub-root work.

4. **GitHub auth readiness**
   ```bash
   ssh <host> 'gh auth status 2>&1'
   ```
   If invalid, the worker cannot safely mutate GitHub state, create PRs, or push via `gh` until re-authenticated.

5. **AI provider runtime readiness**
   Always check the worker's **login shell** as well as plain SSH. User-level installs may live in `~/.local/bin` or `~/.npm-global/bin` and be invisible in non-login SSH.
   ```bash
   ssh <host> 'for c in hermes claude codex gemini; do command -v "$c" && "$c" --version 2>&1 | head -3 || echo "$c:not-found"; done'
   ssh <host> 'bash -lc '\''for c in hermes claude codex gemini; do command -v "$c" && "$c" --version 2>&1 | head -3 || echo "$c:not-found"; done; hermes config 2>/dev/null | grep -Ei "provider|model|base_url|gpt" | head -20'\'''
   ```
   Do not route expiring provider-credit work to a worker unless the relevant CLI/auth path exists in the launch environment and is known to consume the intended account/credit. If only the login shell exposes the tools, dispatch with `ssh <host> 'bash -lc "<command>"'` or explicitly source the user's environment.

   For Codex specifically, CLI presence and `~/.codex/` files are only a weak signal. Before assigning real Codex burn work to a remote/overflow machine, run a tiny real `codex exec` smoke through the exact login-shell/tmux path you will use for the lane and confirm it does not fail with `401 Unauthorized` or `Failed to refresh token: refresh token was already used`. If that smoke fails, mark the host Codex-blocked and use it only for Claude fallback/validation until `codex login` is refreshed.

6. **Engineering software readiness**
   Check both package/command presence and a task-appropriate smoke test. Presence alone is not enough.
   Useful Linux engineering probes:
   ```bash
   ssh <host> 'command -v openfoam-selector && openfoam-selector --list || true'
   ssh <host> 'command -v gmsh && gmsh --version || true'
   ssh <host> 'command -v freecad || command -v FreeCAD || true'
   ssh <host> 'command -v blender && blender --background --version 2>&1 | head -5 || true'
   ssh <host> 'command -v pvbatch && pvbatch --version 2>&1 | head -5 || true'
   ssh <host> 'command -v ccx && ccx 2>&1 | head -5 || true'
   ssh <host> 'command -v qgis && qgis --version 2>&1 | head -3 || true'
   ssh <host> 'command -v gdalinfo && gdalinfo --version || true'
   ```
   GUI Qt tools may fail over SSH without display; prefer headless modes (`--background`, `pvbatch`) and record display/GPU caveats.

7. **GPU/display caveat**
   ```bash
   ssh <host> 'nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || true'
   ```
   Do not assign GPU or GUI-dependent work unless driver/display/headless readiness is explicitly validated.

8. **Dispatch ledger evidence**
   Store the probe result in a durable report (for example `docs/reports/YYYY-MM-DD-issue-NNN-<host>-readiness-probe.md`) and link it from the GitHub issue before delegating.

### Current learned ace-linux-2 baseline from 2026-04-27/28 probes

Use this as a starting hypothesis, not a substitute for a fresh probe:

- Reachable via SSH as `ace-linux-2` and canonical repo root was `/mnt/local-analysis/workspace-hub`.
- Tier-1 repos `digitalmodel`, `worldenergydata`, `assetutilities`, and `teamresumes` existed and were clean on `main`; `teamresumes` lacked `.venv`.
- `workspace-hub` root itself can be dirty/behind, so root-level work needs a separate dirty-state decision and implementation lanes should use fresh worktrees/clones.
- Open-source engineering tools detected included OpenFOAM ESI `openfoam2312`, Gmsh, FreeCAD, Blender, ParaView/pvbatch, CalculiX, QGIS, and GDAL/OGR.
- Proprietary/licensed tools were not detected in PATH: OrcaFlex/OrcaWave, ANSYS/AQWA, MATLAB, SALOME/Code_Aster.
- Plain non-login SSH may not expose user CLIs; login shell did expose `/home/vamsee/.local/bin/hermes`, `/home/vamsee/.npm-global/bin/claude`, `/home/vamsee/.npm-global/bin/codex`, and `/home/vamsee/.npm-global/bin/gemini`.
- `gh auth` was repaired by 2026-04-28 and reported valid on `ace-linux-2`, but keep `ace-linux-1` as the default GitHub mutation/control plane unless the lane explicitly needs remote issue comments.
- Codex CLI presence/auth files are not enough: on 2026-04-28, a real `codex exec` smoke from `/mnt/local-analysis/workspace-hub` failed with `401 Unauthorized` / `Failed to refresh token: refresh token was already used`. Treat `ace-linux-2` as Codex-blocked until `codex login` is refreshed and a same-path smoke passes.
- Claude Code smoke succeeded via login shell (`claude -p --permission-mode plan --no-session-persistence --output-format text ... </dev/null`), so ace-linux-2 overflow lanes can fall back to Claude with `--permission-mode acceptEdits` for trusted implementation work and `--permission-mode plan` for read-only review.

## Direct remote execution pattern

When the user asks to execute work on another workstation (not just prepare a prompt), use real remote process orchestration rather than `delegate_task`:

1. Copy the self-contained worker prompt to the remote host:
   ```bash
   scp local-worker-prompt.md ace-linux-2:/tmp/worker-prompt.md
   ```
2. Start a named `tmux` session over SSH from a login shell so user-level CLIs are on PATH. Prefer safe Claude Code permission modes over bypass flags:
   ```bash
   ssh ace-linux-2 "bash -lc 'mkdir -p /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports; \
     SESSION=ace2-overflow-$(date +%Y%m%d); \
     tmux has-session -t \$SESSION 2>/dev/null && { echo session exists; exit 1; }; \
     tmux new-session -d -s \$SESSION -c /mnt/local-analysis/workspace-hub \
       \"bash -lc '\''PROMPT=\\\$(< /tmp/worker-prompt.md); claude -p --permission-mode acceptEdits --no-session-persistence --output-format text \\\"\\\$PROMPT\\\" </dev/null 2>&1 | tee /mnt/local-analysis/ace2-worker-logs/\$SESSION.log'\''\"; \
     tmux list-sessions | grep \$SESSION'
   ```
   Use `--permission-mode plan` instead of `acceptEdits` for read-only review/synthesis lanes. If a Codex smoke fails on the worker but Claude smoke passes, rewrite the dispatch ledger and launch scripts to use Claude on that worker rather than leaving stale `codex exec` commands in the pack.
3. Monitor with:
   ```bash
   ssh ace-linux-2 "bash -lc 'tmux capture-pane -t ace2-overflow-YYYYMMDD -p -S -80; find /mnt/local-analysis/ace2-worker-reports -maxdepth 1 -type f -printf \"%f %s bytes\\n\"'"
   ```
4. Require the worker to write report files under a known handoff directory for the control plane to post/reconcile later.

Do **not** use shell-level `nohup ... &` wrappers through Hermes foreground `terminal`; Hermes blocks that pattern. Use Hermes `terminal(background=true)` for local tracked processes, or remote `tmux` for SSH-launched workers.

## Post-reboot / interrupted-run recovery playbook

Use this when a control-plane workstation reboots or a context handoff indicates in-flight Hermes/Claude/Codex/tmux work may have survived, stalled, or been partially landed. Work in this order:

1. **Salvage current work first**
   - Reconstruct active state from the handoff, `todo`, process tables, tmux sessions, logs, and GitHub issue labels/state.
   - Check Hermes background sessions directly by known `session_id` when available; do not assume an empty process list means the run is gone.
   - Inspect exact `ps` PIDs/PGIDs before killing anything. Avoid `pkill -f`; it can self-match and terminate the orchestrator.
   - Verify claimed completions with durable handles: issue URL/state/labels, remote commit SHA, branch, validation log, or report file.
   - Mark local todos complete only after external verification.

2. **Research/restart ongoing work second**
   - Poll local tmux panes/logs and remote worker panes/logs before relaunching.
   - For `ace-linux-2`, rerun readiness (`scripts/operations/agent-execution/ace2-readiness.sh` when available) and keep it report-only if `gh auth status` is invalid.
   - Do not duplicate Codex/Claude lanes until OS process state, worktree git state, and expected report artifacts have been checked.
   - If a worker must be restarted, use repo-owned prompt/script artifacts rather than `/tmp` prompts whenever they exist.

3. **Set off future work last**
   - Launch only plan-approved implementation lanes, or planning/review-only lanes for unapproved issues.
   - Keep ace-linux-1 as GitHub mutation/control plane and ace-linux-2 as overflow worker unless auth/readiness proves otherwise.
   - Persist reusable launch prompts and scripts inside the repo ecosystem, preferably under `docs/plans/machine-prompts/<date>/...` and `scripts/operations/agent-execution/`, then validate (`bash -n`, `--help`, dry-run) before committing.
   - Record final reconciliation with issue links, commit SHAs, validation results, remaining sessions, and blockers.

## Repo-owned agent execution scripts

For workspace-hub orchestration, prefer committed scripts over ad hoc `/tmp` launch commands when they exist:

```bash
bash scripts/operations/agent-execution/ace2-readiness.sh
bash scripts/operations/agent-execution/launch-ace1-control-plane.sh --dry-run
bash scripts/operations/agent-execution/launch-ace2-overflow-worker.sh --dry-run
bash scripts/operations/agent-execution/launch-2518-finalizer.sh --dry-run
```

These scripts encode the current safety defaults: login-shell PATH on ace-linux-2, tmux-based remote execution, repo-owned prompts, explicit logs/reports, and dry-run/help validation.

## Interactive orchestration readiness shadow session

Use this when the user wants to keep reviewing decisions in the current chat while a separate Hermes session performs read-only orchestration readiness inspection.

1. Write the handoff prompt to a durable repo path, for example:
   - `docs/plans/machine-prompts/<date>/execution/orchestration-readiness-interactive-handoff.md`
2. Start a named tmux session in the repo root:
   ```bash
   SESSION=orch-readiness-$(date +%Y%m%d)
   PROMPT=/mnt/local-analysis/workspace-hub/docs/plans/machine-prompts/$(date +%F)/execution/orchestration-readiness-interactive-handoff.md
   LOG=/mnt/local-analysis/workspace-hub/docs/plans/machine-prompts/$(date +%F)/execution/orchestration-readiness-interactive-session.log
   tmux new-session -d -s "$SESSION" -c /mnt/local-analysis/workspace-hub \
     "bash -lc 'hermes --pass-session-id 2>&1 | tee -a $LOG'"
   ```
3. Wait for the Hermes prompt before pasting the handoff; if pasted too early, it can be interpreted by the shell/tmux before Hermes is ready. Verify with `tmux capture-pane`.
4. Paste and submit the prompt:
   ```bash
   tmux load-buffer -b orch_prompt "$PROMPT"
   tmux paste-buffer -t "$SESSION" -b orch_prompt
   tmux send-keys -t "$SESSION" Enter
   ```
5. Report the tmux session name, prompt path, log path, and attach command to the user. Keep the current chat as the interactive decision/review surface.

## Bounded lane-keeper cron until provider reset

When the user asks to keep work lanes going until a reset/expiry time, update or create a Hermes cron job rather than launching uncontrolled duplicate agents.

Recommended guardrails for the cron prompt:
- State the exact stop time with timezone and tell the job to stop launching after that timestamp.
- Monitor known lanes first: OS processes, tmux sessions, worktree status, remote branches, issue labels/comments, and logs/reports.
- Classify lanes as `RUNNING`, `COMPLETED_WITH_RESULT`, `READY_FOR_REVIEW`, `STALLED_NO_OUTPUT`, or `BLOCKED`.
- Do **not** merge, close issues, force-push, hard reset/clean primary checkout, or remove `status:working` autonomously.
- Only restart a lane when it has no live process, no ahead commit/evidence, and no duplicate active branch; restrict restarts to explicitly named stalled lanes unless the prompt has a safe shortlist rule.
- If a lane completes and produces a result artifact with safe next work, let the monitor create **one bounded follow-up prompt** under the same repo-owned prompt pack (for example `docs/plans/overnight-prompts/<date-pack>/generated/`) and launch a single follow-up tmux lane. The follow-up must stay planning/review/GTM/blocker-collapse only unless live gates prove implementation eligibility.
- For ready branches, run only lightweight read-only validation and leave final merge/closure to the interactive review session.
- Keep `ace-linux-1` as control plane and avoid `ace-linux-2` GitHub mutations unless fresh auth/readiness proves safe.
- Include a final table per tick: issue/lane, PID/session, worktree, branch/HEAD when applicable, classification, action taken, generated follow-up prompt if any, and next human action.

Use `cronjob(action='update')` to retarget an existing burn/controller job when one already exists, instead of creating overlapping cron jobs. Set `enabled_toolsets` narrowly (usually `terminal,file`) and a repeat count that covers the reset window with a small buffer. If cron delivery back to the chat/control surface fails, require the job to write a durable status artifact such as `results/lane-monitor-latest.md` so the operator can inspect it manually.

### Dirty/behind remote checkout fallback

If an overflow worker repo (for example `ace-linux-2:/mnt/local-analysis/workspace-hub`) is dirty or far behind and pulling/rebasing would risk local worker artifacts, do not use git operations just to deliver an overnight prompt pack. Instead:
1. keep GitHub mutations and commits on the control plane;
2. sync only the prompt-pack directory and launch scripts to the worker with `rsync`/`scp`;
3. launch worker tmux sessions from the synced repo-owned prompt path;
4. write worker logs/reports to machine-local log/report directories; and
5. reconcile/persist any useful worker outputs later from `ace-linux-1` after manual review.

### Health signal caveat

For unattended `claude -p` lanes, zero-byte stdout logs are not sufficient evidence of failure. Check tmux/process liveness and expected result artifacts first. Treat `STALLED_NO_OUTPUT` as a classification only after the process is gone or the lane exceeds the prompt's expected runtime with no artifacts and no useful pane/log evidence.

## Pitfalls

- Treating a stale quota script as more authoritative than user-visible expiring-credit evidence.
- Dispatching implementation for issues that are not `status:plan-approved`.
- Letting `ace-linux-2` become an untracked peer control plane instead of a worker/overflow node.
- Routing by provider only and ignoring workstation readiness or git contention.
- Assuming a clean child repo means the workspace-hub root is clean enough for root-level work.
- Assuming installed engineering software is usable without a headless/tool-specific smoke test.
- Routing Codex/Claude/Gemini work to a workstation where the provider CLI is missing or unauthenticated.
- Mass-applying labels from heuristics without manual inspection.
- Losing reconciliation evidence because no dispatch ledger was written.

## Related skill overlap note

This skill intentionally overlaps with `agent-usage-optimizer` for provider quota routing, but adds the workstation/control-plane layer. Future consolidation could merge this workstation section into `agent-usage-optimizer` if external skill write access is available.
