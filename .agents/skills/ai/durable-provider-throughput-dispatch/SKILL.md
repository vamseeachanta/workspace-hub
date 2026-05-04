---
name: durable-provider-throughput-dispatch
description: Run quota-aware but spend-forward Codex/Codex/Gemini batches when provider credits are not the bottleneck and the goal is durable plan/review/execution throughput across machines.
version: 1.0.0
tags: [quota-management, multi-provider, overnight, multi-machine, agent-dispatch]
related_skills:
  - agent-usage-optimizer
  - ace-linux-1-control-surface
  - overnight-parallel-agent-prompts
  - plan-gated-overnight-queue-partition
---

# Durable Provider Throughput Dispatch

## When to Use

Use this when the user explicitly wants to maximize AI-agent usage availability, burn weekly provider capacity, or continue useful overnight/background work even if provider credits may run out near reset.

This is the spend-forward counterpart to conservative quota routing. The goal is not merely to save credits; it is to convert available provider limits into durable artifacts that reduce future bottlenecks.

## Core Principle

When the user states that provider credits are not the bottleneck, switch from conservation mode to durable-throughput mode, but do it from fresh capacity telemetry instead of static provider rules:

- refresh provider capacity/usage roughly every 6 hours before planning the next work wave;
- spend available Codex/Codex limits on useful plan prep, adversarial review, execution-readiness, queue synthesis, and approved bounded implementation;
- treat Gemini as a lower-budget account by default: normally reserve it for cross-reviews, adversarial reviews, research/recon, and risk scans, not main implementation/execution;
- if fresh telemetry shows reliable Gemini capacity and an appropriate bounded/review/recon task, use that capacity instead of rigidly excluding it;
- tolerate high utilization or temporary end-of-cycle depletion only when the user has accepted that tradeoff;
- preserve plan gates, legal/IP/privacy gates, and GitHub mutation control.

## Required Dispatch Pattern

1. **Refresh live state first**
   - Check git status/branch/head.
   - Check active local tmux/processes/logs.
   - Check remote worker state before launching duplicate lanes.
   - Check provider CLI availability/auth where relevant.

2. **Partition work by gate state**
   - `status:plan-review` or draft issues: planning/review hardening only.
   - `status:plan-approved` plus required local markers: eligible for implementation lanes.
   - Unknown/stale state: audit-only until verified.

3. **Route by provider fit**
   - Codex: control-plane synthesis, long-context planning, adversarial review, governance-heavy work.
   - Codex: bounded implementation, tests, refactors, crisp execution-ready issues, adversarial code/readiness review.
   - Gemini: batched research, reconnaissance, standards/source scans, risk enumeration.

4. **Route by machine role**
   - Primary control surface keeps approvals, decisions, GitHub mutations, and synthesis.
   - Overflow machines run bounded worker lanes only after repo/tool/auth checks.
   - Do not let an overflow machine become a shadow control plane.

5. **Write durable artifacts**
   - Prompt packs under `docs/plans/overnight-prompts/<date-or-wave>/`.
   - Unique result file per lane under a `results/` directory.
   - Logs under a known log directory.
   - A monitor or handoff artifact that records lane names, expected outputs, and stalled-lane recovery rules.

6. **Monitor, reconcile, then feed lanes**
   - Use scheduled/local monitors for long runs.
   - Treat zero-byte Codex logs as inconclusive while the process is alive; prefer process liveness and expected output artifacts.
   - If a lane stalls, salvage useful log content and relaunch only the missing bounded deliverable.
   - When the user reports provider credits sitting idle, verify useful provider activity rather than process liveness alone: compare log sizes/mtimes across snapshots, inspect child provider processes, and look for durable output artifacts. Wrappers running with unchanged logs are not enough.
   - Replan provider routing from fresh capacity telemetry about every 6 hours; see `references/capacity-aware-provider-routing.md` for the current capacity-aware Codex/Codex/Gemini policy.
   - When the machine is already saturated or an autofeed cron is launching overlapping waves, **pause the recurring feeder first**, then reconcile run directories before any replacement launches. Useful provider throughput requires completed artifacts, not raw process count.
   - Watch for known non-consuming stall signatures: Codex logs stuck at `Reading additional input from stdin...`, Codex sandbox startup failures such as `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, Gemini startup validation errors from repo-local `.gemini/agents`, Gemini capacity failures (`429 RESOURCE_EXHAUSTED` / `No capacity available`), Codex `stream-json requires --verbose`, and Hermes/worker lanes exiting `143` after worktree-command timeouts. See `references/provider-stall-recovery-autofeed.md`.
   - Do not let monitors stop at passive reporting when the user's goal is continuous throughput. After primary lanes complete, run a safe auto-feed decision: `draft -> adversarial review`, `review MAJOR -> plan patch lane`, `review APPROVE/MINOR -> status:plan-review command/comment pack`, `blocked -> blocker-prep packet`, `approval candidates -> synthesis table`. Keep unsafe transitions gated: no `status:plan-approved`, no outreach, and no unapproved implementation without explicit user approval.
   - Limit each auto-feed tick to a small bounded number of new lanes (for example 1-2), require unique prompt/log/result paths, and write the generated follow-up prompt under the same repo-owned prompt pack (`generated/`) before launching it.
   - For anti-idle recovery, create both immediate direct provider lanes and a recurring autofeed monitor (for example every 30 minutes for the current work window) so completed/stalled lanes are replaced without a multi-hour gap. For over-saturation recovery, keep the monitor paused until stale/orphan lanes are classified and launcher rules are patched/dry-run verified.
   - After patching an over-saturated autofeed monitor, do **not** resume recurring cron immediately. Run exactly one controlled live tick while the cron remains paused, then inspect log/result mtimes, result sizes, failure signatures, and child-process duplication. If the live tick produces zero durable useful outputs or only provider-capacity/sandbox/no-output signatures, clean up that tick and switch to provider-health probes instead of restarting the feeder. See `references/provider-autofeed-health-recovery.md`.
   - If the workspace is dirty and capacity should be used immediately, prefer a **read-only Codex plan-mode scout wave** with absolute prompt/output paths before creating write-enabled worktrees. Background launches may not honor relative paths as expected, and interrupted `git worktree add` can leave broken `.git/worktrees/*` metadata. See `references/dirty-workspace-plan-mode-scout-wave.md`.

## Safety Gates That Do Not Relax

Even in spend-forward mode:

- Do not implement issues before plan approval.
- Do not mutate GitHub labels/comments/closures from worker lanes unless explicitly authorized.
- Do not publish or promote raw/client/standards/GTM artifacts without source, provenance, license, privacy, and IP checks.
- Do not preserve or output secrets; redact credentials.
- Do not count an issue as approval-ready unless current plan/review/legal artifacts support that claim.

## Good Deliverables

A strong overnight spend-forward batch produces one or more of:

- approval-readiness package with issue numbers, live labels, plan paths, review paths, legal gate status, blockers, and exact operator commands;
- adversarial review reports from independent providers;
- execution scout report listing already-approved, low-contention issues;
- follow-up prompt pack for the next wave;
- monitor/handoff artifact with lane status and recovery instructions.

## Pitfalls

- Conserving credits after the user has explicitly prioritized throughput.
- Burning credits on non-durable chat output instead of repo-tracked artifacts.
- Launching duplicate lanes without checking existing sessions/logs/results.
- Treating `status:plan-review` as approval-ready without artifact verification.
- Letting provider enthusiasm bypass legal or plan-gate controls.
- Resuming an autofeed cron just because the classifier script was patched; a patched classifier can still reveal that provider launch health is zero. Prove at least one durable provider output in a controlled live tick or minimal health probe before recurring dispatch.
- Counting child provider processes as separate lanes. Deduplicate by result/log path so wrapper, `timeout`, `node`, binary, and `tee` processes do not inflate useful-active counts.
- Letting result-file freshness override explicit failure signatures; capacity/sandbox/stdin/stream-json signatures must classify stale even when a result stub exists.
