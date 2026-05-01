# 2026-05-01 Exit Handoff — Provider Throughput + Repo State

## Snapshot

- Snapshot time: `2026-05-01 03:58:36 CDT -0500`.
- Workspace: `/mnt/local-analysis/workspace-hub`.
- Branch: `main`.
- Local HEAD: `1aa2f6f47c64` (`docs(gtm): harden prospect demo SOP for #2346`).
- Remote `origin/main`: `dde5d0a01ba4` (`docs: close out issue 2570 plan state`).
- Divergence check at exit: local checkout reports `main...origin/main [behind 2]`.
- Important: working tree is not clean and contains unresolved conflicts; do **not** reset/clean. Salvage/reconcile first.

## User directives captured this session

1. Provider dispatch should be capacity-aware, not hard-rule based.
2. Refresh/check AI usage capacity about every 6 hours and plan the next work from fresh telemetry.
3. Claude had ~40% weekly capacity remaining with ~36 hours to reset as of `2026-04-30 18:59 CDT`; get appropriate Claude/Codex work done.
4. Gemini is a lower-budget USD $20 account and should normally be used for cross/adversarial review, recon, and risk scans; do not delegate main work to Gemini unless fresh reliable capacity and task fit justify it.
5. Continue preserving gates: no self-approval, no unapproved implementation, no contractor/prospect outreach, no destructive cleanup/reset of dirty checkouts.

## Durable memory/business-brain updates made

- Updated Business Brain memory to use fresh capacity telemetry every ~6 hours rather than rigid provider rules.
- Added capacity note: `Provider capacity note as of 2026-04-30 18:59 CDT: Claude weekly capacity had ~40% remaining with ~36 hours to reset; prioritize appropriate Claude/Codex throughput from fresh telemetry.`

## Cron / automation state

### Capacity-aware provider throughput cron

- Job ID: `a0c7a42428d9`.
- Name: `provider-capacity-aware-throughput-autofeed-20260430`.
- Schedule: `every 360m` / every 6 hours.
- Repeat: `16/30` at latest cron list.
- Last run: `2026-05-01T01:24:36.352187-05:00`, status `ok`.
- Next run: `2026-05-01T07:24:36.352187-05:00`.
- Enabled: true.
- Workdir: `/mnt/local-analysis/workspace-hub`.
- Skills: `ai/durable-provider-throughput-dispatch`, `ai/agent-usage-optimizer`, `coordination/overnight-worktree-agent-waves`, `workspace-hub/worktree-branch-sync-hygiene`.
- Policy in prompt: refresh telemetry first; reconcile active lanes by log/result path, not process count; Claude/Codex-heavy dispatch; Gemini default review/recon only; bounded small waves; preserve gates.

### Nightly jobs

- `01122d69d9a2` — `nightly-batch-1-closure-first-approved-verify-close`: repeat `2/5`, last status `ok`, next `2026-05-01T23:03:12-05:00`.
- `91252d4f37a0` — `nightly-batch-2-plan-review-rerun-hardening`: repeat `2/5`, last status `error`, next `2026-05-02T00:07:57-05:00`. Needs inspection before trusting output.
- `4a33b1712135` — `nightly-batch-3-approved-implementation-tdd`: repeat `2/5`, last status `ok`, next `2026-05-02T00:29:32-05:00`.
- `7a50251063b2` — `nightly-batch-4-gtm-artifact-factory-no-outreach`: repeat `2/5`, last status `ok`, next `2026-05-02T00:38:36-05:00`.
- `02cef7abeae6` — `nightly-batch-5-worktree-merge-hygiene-provider-throughput`: repeat `2/5`, last status `ok`, next `2026-05-02T00:59:02-05:00`.

### Other scheduled follow-ups

- `967058f7b5aa` — `acma-projects-morning-claude-sync-learning`, one-shot at `2026-05-01T07:30:00-05:00`.
- `7b73aee6e819` — `overnight-6lane-status-monitor-20260501`, every 60m x6, read-only monitor.

## Provider / usage artifact state

Latest known provider-utilization files exist and were refreshed around `2026-05-01 02:16:59 CDT`:

- `config/ai-tools/agent-quota-latest.json` — 686 bytes.
- `config/ai-tools/provider-utilization-weekly.json` — 31,228 bytes.
- `docs/reports/provider-utilization-weekly.md` — 5,076 bytes.
- `docs/reports/provider-work-queue.md` — 4,961 bytes.

Latest relevant agent log directories seen at exit:

- `/mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0004`
- `/mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0613`
- older provider-autofeed directories under `/mnt/local-analysis/agent-logs/provider-autofeed-*`

Exit process snapshot found no active provider processes matching `claude -p|codex exec|gemini|hermes chat --provider|provider-capacity|provider-min3|provider-autofeed` at `2026-05-01 03:58:36 CDT`.

## Git / repository hazards at exit

The working tree is dirty and conflicted. Do not run destructive cleanup. Notable conflict markers/status from `git status --short --branch`:

- Earlier broad status showed `UU docs/plans/README.md`; a later path-scoped check showed `M  docs/plans/README.md`. Treat it as a conflict-adjacent modified planning file and inspect before any merge/push.
- `AA docs/plans/2026-05-01-issue-2570-b1528-sirocco-yaw-moment-report.md`
- Local branch is behind `origin/main` by 2 commits:
  - `dde5d0a01 docs: close out issue 2570 plan state`
  - `52c1cf09a docs: close out issue 2570 plan state`
- Many staged/modified `.claude/skills`, `.claude/state`, provider reports, session logs, knowledge wiki raw papers, and docs/session artifacts are present from automation/skills/memory bridge/overnight lanes.
- Current checkout also has untracked files including:
  - `.claude/state/corrections/session_20260501.jsonl`
  - `.planning/you-are-claude-1-control-luminous-balloon.md`
  - `.planning/you-are-claude-3-marker-readiness-eager-wand.md`
  - `docs/sessions/2026-05-01-acma-projects-sparse-checkout-b1528.md`

Because of the `UU`/`AA` conflicts and broad staged/untracked state, this exit handoff was intentionally written but not committed/pushed.

## Recent landed/local commit context

Local recent commits at exit:

```text
1aa2f6f47 docs(gtm): harden prospect demo SOP for #2346
1380739ed fix(state): wire session-signal size guards for issue 2070
db4d6f383 chore(planning): record approved marker for issue 2070
84d5787e2 complete issue 2569 B1528 source pack: docs/plans/README.md
f12d3ee14 complete issue 2569 B1528 source pack: docs/plans/2026-05-01-issue-2569-b1528-sirocco-source-pack.md
315bfbaac complete issue 2569 B1528 source pack: scripts/review/results/2026-05-01-implementation-2569-hermes.md
5a25c9797 complete issue 2569 B1528 source pack: knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md
3c8e45292 complete issue 2569 B1528 source pack: scripts/validation/validate_b1528_source_pack.py
```

However, latest `git status` says local branch is behind `origin/main` by two commits. Reconcile before any push.

## Safe next-session priorities

1. **Salvage current dirty/conflicted work first** per user preference.
   - Do not reset/clean.
   - Inspect `docs/plans/README.md` and `docs/plans/2026-05-01-issue-2570-b1528-sirocco-yaw-moment-report.md` conflicts.
   - Fetch and compare `HEAD...origin/main`.
   - Decide whether to preserve local changes, accept remote closeout, or create a narrow reconciliation commit.
2. **Inspect nightly-batch-2 error** (`91252d4f37a0`) before relying on plan-review hardening output.
3. **Review provider-capacity cron output** from `/mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-0613` and the next run after `07:24 CDT`.
4. **Use Claude/Codex capacity appropriately**: with Claude 40% remaining at prior snapshot, prefer Claude for governance/plan review/synthesis and Codex for bounded implementation/tests. Keep Gemini on review/recon unless telemetry says otherwise.
5. **Only after conflict salvage**, consider committing this handoff artifact and any narrow reconciliation docs.

## Fresh-session copy/paste prompt

```text
Resume from /mnt/local-analysis/workspace-hub.
Read docs/session-handoffs/2026-05-01-exit-provider-throughput-and-repo-state.md first.
Priority order:
1. Salvage current dirty/conflicted work first. Do not reset/clean. Inspect `git status --short --branch`, `git log --oneline --decorate --left-right HEAD...origin/main`, `docs/plans/README.md`, and `docs/plans/2026-05-01-issue-2570-b1528-sirocco-yaw-moment-report.md`.
2. Reconcile local `main` vs `origin/main` (local HEAD 1aa2f6f47c64, origin/main dde5d0a01ba4 at exit) without losing local staged/untracked artifacts.
3. Inspect cron job `91252d4f37a0` last error and provider capacity cron `a0c7a42428d9` outputs/log dirs.
4. Continue capacity-aware provider work: check usage telemetry about every 6h; Claude had ~40% weekly capacity left with ~36h to reset as of 2026-04-30 18:59 CDT; use Claude/Codex appropriately; Gemini mostly review/recon unless reliable capacity is available.
Preserve gates: no self-approval, no unapproved implementation, no contractor/prospect outreach, no destructive cleanup/reset, no secret leakage.
```
