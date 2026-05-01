# Provider Throughput Recovery Monitor — 20260430T095017Z

## Refresh
- Repo: `/mnt/local-analysis/workspace-hub`
- HEAD: `e6104e7eb74385df70fac9b85f41497576466d92`
- origin/main: `e6104e7eb74385df70fac9b85f41497576466d92`
- `git status --short` did not complete within the later 30s retry, so this monitor did **not** commit/push the artifact. No destructive cleanup/reset was attempted.

## Provider quota snapshot

```text
Agent Credits (Thursday 2026-04-30):
  claude:  N/A (authoritative source unavailable)
  codex:   100% remaining (4/1400 msgs)
  gemini:  100% remaining (0/1000 msgs)
```

## Active provider CLI process summary
- Existing Hermes TUI sessions: 2 long-lived sessions present.
- Existing provider-recovery lanes from `/mnt/local-analysis/agent-logs/provider-recovery-20260430-0445`:
  - 2 Codex lanes alive but logs remain at `Reading additional input from stdin...`; treated as stalled/inconclusive.
  - 2 Gemini lanes alive with early Gemini agent-definition warnings; still inconclusive until result artifacts appear.
  - Claude control-plane recovery log is zero-byte and no matching live Claude recovery process was found; treated as failed/stale for this decision.
- Existing nightly lanes from `/mnt/local-analysis/agent-logs/nightly-20260430-more-lanes-0431` show prior git/worktree hang patterns.

## Logs inspected
- `/mnt/local-analysis/agent-logs/provider-recovery-20260430-0445/logs/claude-control-plane-recovery.log` — zero bytes.
- `/mnt/local-analysis/agent-logs/provider-recovery-20260430-0445/logs/codex-approved-implementation.log` — `Reading additional input from stdin...` only.
- `/mnt/local-analysis/agent-logs/provider-recovery-20260430-0445/logs/codex-worktree-recovery.log` — `Reading additional input from stdin...` only.
- `/mnt/local-analysis/agent-logs/provider-recovery-20260430-0445/logs/gemini-research-recon.log` — Gemini started; agent-definition warnings about `permissionMode`; no durable result yet observed in this pass.
- `/mnt/local-analysis/agent-logs/provider-recovery-20260430-0445/logs/gemini-gtm-risk-scan.log` — Gemini started; same warnings; no durable result yet observed in this pass.
- `/mnt/local-analysis/agent-logs/nightly-20260430-more-lanes-0431/logs/batch6.log` through `batch10.log` — prior useful reconnaissance plus git/worktree stall evidence.

## Recovery decision
Useful active lanes were below the target threshold after discounting stalled Codex stdin waits and the missing/zero-byte Claude lane. I launched 5 bounded spend-forward provider lanes under:

- Prompt/log root: `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z`

| Lane | Provider | Prompt | Log | Hermes session id | Safety scope |
|---|---|---|---|---|---|
| control-plane synthesis | Claude | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/prompts/claude-control-plane-synthesis.md` | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/logs/claude-control-plane-synthesis.log` | `proc_4fd931a05abf` | planning/review/evidence only; no GitHub mutation |
| #2564 adversarial review | Claude | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/prompts/claude-adversarial-review-2564.md` | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/logs/claude-adversarial-review-2564.log` | `proc_695cef9b913e` | review artifact only; no approval |
| approved execution scout | Codex | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/prompts/codex-approved-execution-scout.md` | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/logs/codex-approved-execution-scout.log` | `proc_5028afe08e64` | implementation only if live approved + local marker; otherwise table |
| worktree stall salvage | Codex | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/prompts/codex-worktree-stall-salvage.md` | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/logs/codex-worktree-stall-salvage.log` | `proc_3f248a373227` | classify/salvage only; no deletion |
| plan/legal risk recon | Gemini | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/prompts/gemini-plan-risk-recon.md` | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430T094906Z/logs/gemini-plan-risk-recon.log` | `proc_6338e074658b` | read-only risk matrix; no outreach |

## Immediate liveness check
- All five newly launched Hermes-tracked sessions returned `running` on initial poll.
- The two newly launched Codex sessions also showed the known `Reading additional input from stdin...` symptom; I explicitly closed their tracked stdin handles via Hermes process control after launch. They remained alive at the next poll.
- The two newly launched Claude logs were still zero-byte at the last check, which is inconclusive while the processes are alive.
- The newly launched Gemini log showed startup and the same `.gemini/agents/* permissionMode` validation warning; lane remains alive/inconclusive pending result artifact.

## Commit/push status
- Artifact path: `docs/plans/overnight-results/provider-throughput-recovery-20260430T095017Z.md`
- `git diff --check -- docs/plans/overnight-results/provider-throughput-recovery-20260430T095017Z.md` passed.
- A broad `git status --short` retry timed out after 30s and legal-scan discovery was inconclusive under current repo contention; therefore I left this narrow monitor artifact uncommitted, per instruction to commit/push only if checks pass.

## Next recovery decision
On the next cron pass:
1. Poll the five session/log paths above and check for result artifacts under `docs/plans/overnight-results/provider-autofeed-*`.
2. If Codex logs remain only `Reading additional input from stdin...`, treat them as failed stdin stalls and relaunch the missing deliverables with a stdin-pipe/EOF-hardened Codex invocation or route those tasks to Claude/Gemini.
3. Do not create/modify cron jobs.
4. Do not promote any issue to `status:plan-approved`; only report approval candidates with verified current plan/review/legal evidence.
