# Provider-Autofeed Recovery Scoreboard — claude-recovery-governance-1 lane (run 20260430-111336)

> **Lane ID:** `claude-recovery-governance-1`
> **Run:** `provider-autofeed-20260430-111336`
> **Generated:** 2026-04-30 ~11:25 UTC (lane STARTED ~11:25 UTC)
> **Author:** claude-recovery-governance-1 lane (Opus 4.7, 1M context)
> **Predecessor scoreboard:** `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` (run 100339, ~82 min earlier)

## ENV-MISMATCH banner — read this first

Same sandbox failure mode as the 100339 scoreboard. Path memory: `feedback_lane_result_path_outside_sandbox.md` (logged 2026-04-27, this is recurrence #2).

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-recovery-governance-1.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read` of `agent-logs/` files | **blocked** (permission denied at tool layer) |
| `Write`/`mkdir` to `agent-logs/` | **blocked** |
| `Bash ls`/`cat` to `agent-logs/` | **blocked** |
| What still works from this lane | `Glob` for path enumeration only |
| Canonical durable output of this lane | **THIS document** under `docs/sessions/` |

**Operator action options (unchanged from 100339):**
1. Add `/mnt/local-analysis/agent-logs/**` to lane Read/Write allowlist, **or**
2. Move the prescribed lane result path inside `workspace-hub` (e.g. `.claude/state/lane-handoffs/<run>/<lane>.md`), **or**
3. Treat this in-sandbox document as the canonical lane output and have the orchestrator copy/symlink it to the prescribed path out-of-band.

Path-only enumeration backs every ✅/🟥 below — file bodies were not inspected from this lane. Findings flagged `[content-unverified]` where reading log bodies would change strength.

## Concurrency context — runs alive at lane start

`pgrep -af 'provider-autofeed'` at lane start showed **four overlapping autofeed runs alive simultaneously**:

| Run | Cadence offset | Status |
|---|---|---|
| `provider-autofeed-20260430-100339` | T-82 min | claude-1-control-plane lane still alive at PID 2064879 (long-running, likely producing the prior scoreboard I read) |
| `provider-autofeed-20260430-102314` | T-50 min | `classify_and_launch.sh` PID 2086414 alive; `relaunch_replacements.sh` PID 2088645 alive; gemini-flash-gtm-risk-5 PID 2088647 in flight |
| `provider-autofeed-20260430-104814` | T-25 min | run dir present; processes not surfaced in pgrep snapshot (may have completed or be quieter) |
| `provider-autofeed-20260430-111336` | T-0 (current) | this lane + 18 sibling lanes |

**Implication for recovery actions:** any "re-dispatch this lane" prompt must (a) check `pgrep -af 'provider-autofeed-<run-id>'` for the lane name first to avoid duplicate work, and (b) prefer adding a *new* lane name over reusing one already in flight, because two writers to the same prescribed result path will silently race.

## Recovery scoreboard — run `provider-autofeed-20260430-111336`

Legend (same as 100339):
- ✅ `result.md` present — delivered (content unverified from this lane)
- 🟥 `log` present, no `result.md` — stalled or never wrote output
- ⏳ `log` present, run age <15 min — possibly still in flight (cannot distinguish from stalled without reading log)

The 111336 run is laid out as **3 codex invocation variants × 3 lanes each + 3 gemini-pro + 3 gemini-flash + 1 claude-recovery + 3 claude-stream = 19 lanes**. The codex variants (`stdin`, `json`, `arg-devnull`) are clearly an A/B/C test of workarounds for the codex-cli 0.124.0 stdin-hang regression (`feedback_codex_cli_0_124_upstream_regression`).

### Codex — stdin variant (original invocation)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| `codex-stdin-approved-scout-1` | ✓ | ✓ | 🟥 |
| `codex-stdin-test-readiness-2` | ✓ | ✓ | 🟥 |
| `codex-stdin-worktree-hygiene-3` | ✓ | ✓ | 🟥 |

**Read:** 0/3. Matches `feedback_codex_cli_0_124_upstream_regression` exactly. Expected.

### Codex — JSON output variant

| Lane | Prompt | Log | Result |
|---|---|---|---|
| `codex-json-approved-scout-4` | ✓ | ✓ | 🟥 |
| `codex-json-test-readiness-5` | ✓ | ✓ | 🟥 |
| `codex-json-worktree-hygiene-6` | ✓ | ✓ | 🟥 |

**Read:** 0/3. The JSON-output workaround does not bypass the upstream stdin-hang. `[content-unverified]` — recommend a non-sandboxed reviewer tail one log to confirm the failure mode is the same hang vs. a new shape.

### Codex — arg-devnull variant (prompt-as-arg, stdin redirected to /dev/null)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| `codex-arg-devnull-approved-7` | ✓ | ✓ | 🟥 |
| `codex-arg-devnull-test-8` | ✓ | ✓ | 🟥 |
| `codex-arg-devnull-hygiene-9` | ✓ | ✓ | 🟥 |

**Read:** 0/3. The arg-devnull workaround also does not produce a result. Tentative conclusion (pending log-body confirmation): **none of the three codex invocation reshapings defeat the 0.124.0 stdin-hang**. The known-good fix remains the documented downgrade to 0.123.0. **Stop pouring lanes into codex variants until the host CLI is downgraded.**

### Gemini Pro 2.5

| Lane | Prompt | Log | Result |
|---|---|---|---|
| `gemini-pro-research-queue-1` | ✓ | ✓ | 🟥 |
| `gemini-pro-gtm-legal-2` | ✓ | ✓ | 🟥 |
| `gemini-pro-standards-recon-3` | ✓ | ✓ | 🟥 |

**Read:** 0/3. New stall pattern not present in the 100339 scoreboard. Possible causes (cannot distinguish without log bodies):
- **Gemini Pro 2.5 quota/queue exhaustion** at the API tier (consistent with the operator launching `gemini-flash-fallback-*` lanes immediately after, which suggests the operator anticipated pro-tier failure).
- **Wrapper invokes `-m gemini-2.5-pro` but pro requires a different auth flow** than flash on this host.
- **Trust-env regression** (`feedback_gemini_trust_env_blocks_reviews`) re-emerging on the pro model only — but the durable fix was supposed to land in `submit-to-gemini.sh` 2026-04-24.
- Pro is genuinely slower and the wrapper timeout (often 7200s but sometimes shorter) cut it off.

### Gemini Flash 2.5 (fallback)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| `gemini-flash-fallback-research-4` | ✓ | ✓ | ✅ |
| `gemini-flash-fallback-gtm-5` | ✓ | ✓ | 🟥 |
| `gemini-flash-fallback-standards-6` | ✓ | ✓ | ✅ |

**Read:** 2/3. The Gemini Flash fallback is the **only provider producing results in this run**. The single Flash stall is `gemini-flash-fallback-gtm-5` — same lane class (GTM/legal) that has been failing intermittently across the day (compare 102314 also re-dispatching `gemini-flash-gtm-risk-5` via `relaunch_replacements.sh`). **The GTM/legal lane is content-specific or content-length-specific failing**, not a provider failure — recommend checking the prompt body for size or content that may trigger a model refusal.

### Claude

| Lane | Prompt | Log | Result |
|---|---|---|---|
| `claude-recovery-governance-1` | ✓ | ✓ | ✅ (this lane — written to `docs/sessions/...111336-claude-recovery-governance-1.md` per ENV-MISMATCH; orchestrator must copy out-of-band) |
| `claude-stream-scoreboard-2` | ✓ | ✓ | ⏳/🟥 |
| `claude-stream-plan-hardening-3` | ✓ | ✓ | ⏳/🟥 |
| `claude-stream-governance-loop-4` | ✓ | ✓ | ⏳/🟥 |

**Read:** Run is ~12 min old at lane start. The `claude-stream-*` family appears to be a new invocation shape (`stream-json` output format, visible in 102314 alive process: `--verbose --output-format stream-json`). All three may genuinely still be in flight — distinguishing in-flight from stalled requires reading log bodies (mtime would help but is blocked from sandbox). **Decision rule for the operator:** if `claude-stream-*` logs have not grown for ≥10 min as of this lane's completion, treat as stalled.

## Minimum-active-provider counts (this run)

The "minimum active" metric is the count of result-bearing lanes per provider. Threshold convention from the 100339 scoreboard family is **≥1 result per provider per run** (anything less is a provider-down signal).

| Provider | Results | Lanes attempted | Yield | vs. min-active threshold (1) | Status |
|---|---|---|---|---|---|
| Claude (incl. `claude-recovery-*` + `claude-stream-*`) | 1* | 4 | 25%* | **at threshold** (with caveat) | * = this lane's output is in `docs/sessions/`, not the prescribed path. If the orchestrator does not copy it out-of-band, **effective Claude yield = 0** and Claude drops below threshold. |
| Codex (across all 3 invocation variants) | 0 | 9 | 0% | **below threshold by 1** | Known root cause: `feedback_codex_cli_0_124_upstream_regression`. Recovery requires dispatcher-host CLI downgrade, not more lanes. |
| Gemini Pro 2.5 | 0 | 3 | 0% | **below threshold by 1** | New failure mode this run; root cause needs log-body inspection. |
| Gemini Flash 2.5 (fallback) | 2 | 3 | 67% | **above threshold** | The only provider clearly healthy in this run. |
| **Total** | **3** (effective: 2 if Claude not copied out-of-band) | **19** | **15.8%** | — | — |

**Total missing-to-min-active:** **2 providers** (Codex and Gemini Pro). Claude is at-threshold-with-caveat.

For comparison — extrapolated from the 100339 scoreboard:
- 100339 run had 6/6 nominal yield but content-unverified.
- The current 111336 run is testably worse on path-presence, despite running more lanes (19 vs. 6).
- Adding lane variants without addressing the root causes is **negative-yield** — the codex variants (9 lanes attempted, 0 results) are pure waste of dispatcher budget.

## Safe follow-up lane prompts — exact, copyable

Each prompt below is **safe under the lane hard-gates** (no GitHub mutation, no self-approval, no destructive git, no implementation of unapproved issues). Each names the run, lane, owner, and exit conditions.

### Prompt A — Operator-host preflight (REQUIRED before any new codex lane)

> **Owner:** operator on dispatcher host (not a lane).
> **Action:** run `codex --version` on the dispatcher host (likely ace-linux-1 or licensed-win-1). If output starts with `0.124`, downgrade to `0.123.0` per `feedback_codex_cli_0_124_upstream_regression` (issue #2479) before dispatching any further codex lane in any run. Verify post-downgrade with a 90-byte sanity prompt.
> **Why this is not a lane:** version downgrade requires user-host privilege; cannot be self-served by a sandboxed lane.
> **Hard gate:** none (host-local, no GitHub mutation).

### Prompt B — Re-dispatch `gemini-pro-*` lanes after capturing the failure mode

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: gemini-pro-failmode-capture-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/gemini-pro-failmode-capture-1.md (or fallback `docs/sessions/...` if sandbox)
> Hard gates: do not destructively reset/clean /mnt/local-analysis/workspace-hub; use isolated worktrees for any edits; no outreach/external sending; no self-approval; no status:plan-approved changes; no unapproved implementation. Use GIT_OPTIONAL_LOCKS=0 and timeout around git/worktree/status commands. Redact secrets. First action: write STARTED timestamp and lane name to the result file.
> Task: Read the three `gemini-pro-*` log bodies in this run (`logs/gemini-pro-research-queue-1.log`, `logs/gemini-pro-gtm-legal-2.log`, `logs/gemini-pro-standards-recon-3.log`) and classify the failure mode into one of: {quota-exhaustion, model-not-available, trust-env-regression, timeout, other}. Cross-check against the durable fix in `submit-to-gemini.sh` (memory: `feedback_gemini_trust_env_blocks_reviews`) to confirm whether the 2026-04-24 fix is still in place for the pro model path. Do NOT re-dispatch any pro lane — produce a one-page diagnosis only.
> Owner: any host with read access to agent-logs/.
> Exit: result file with classification + remediation pointer.

### Prompt C — Confirm or rule out stall on `claude-stream-*` family

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: claude-stream-liveness-probe-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-stream-liveness-probe-1.md
> Hard gates: same as Prompt B.
> Task: For each of `claude-stream-scoreboard-2`, `claude-stream-plan-hardening-3`, `claude-stream-governance-loop-4` in run 111336: (a) `stat` the log file mtime, (b) tail the last 50 lines, (c) classify as {still-emitting, idle-but-alive, stalled-no-emission}. Do not kill or re-dispatch — diagnostic only. Decision rule: log mtime older than 10 min AND no `[STARTED]` token in the body = stalled.
> Owner: any host with read access to agent-logs/.
> Exit: 3-row table {lane, mtime-age, classification, recommended-action}.

### Prompt D — Investigate `gemini-flash-fallback-gtm-5` content-specific stall

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: gemini-flash-gtm-content-diff-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/gemini-flash-gtm-content-diff-1.md
> Hard gates: same as Prompt B.
> Task: `diff` the prompts of `gemini-flash-fallback-gtm-5` (stalled) against `gemini-flash-fallback-research-4` and `gemini-flash-fallback-standards-6` (both succeeded) to identify what content distinguishes the failing GTM lane. Cross-reference with the same-named `gemini-flash-gtm-risk-5` lane in run 102314 (still in flight per pgrep) — if both runs of the same content stall, **the prompt body is the cause, not the provider**. Do NOT re-dispatch the GTM lane until the content trigger is identified.
> Owner: any host with read access to agent-logs/.
> Exit: result file naming the content trigger or "no content delta found".

### Prompt E — Promote `results/.lane-state.json` to a hard requirement (planning only)

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: lane-state-json-promotion-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/lane-state-json-promotion-plan-1.md
> Hard gates: same as Prompt B. **Planning only** — no script edits, no `status:plan-approved` changes; if a GitHub issue does not yet exist for this enhancement, draft the issue body in the result file but do NOT open it.
> Task: Draft a plan to add `results/.lane-state.json` (3-line: `status`, `provider_used`, `exit_code`) emission to every lane wrapper. Reference the cross-cutting recommendation in `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md`. Map the change to the enforcement-gradient L2 pattern in `.claude/rules/patterns.md`. Identify the wrapper scripts (`/mnt/local-analysis/agent-logs/provider-autofeed-monitor/run_tick.sh`, `classify_and_launch.sh`, and any `relaunch_replacements.sh` variants) that would need the change. Do NOT touch the scripts in this lane.
> Owner: any planning-capable host.
> Exit: plan with file list, change shape, test plan, rollback note.

### Prompt F — Mirror Gemini fan-out chain into the `relaunch_replacements.sh` wrapper

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: gemini-fanout-mirror-recon-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/gemini-fanout-mirror-recon-1.md
> Hard gates: same as Prompt B. **Reconnaissance only** — no script edits.
> Task: Confirm or refute the 100339-scoreboard hypothesis that `provider-recovery-*` wrappers diverge from `provider-min3-*` wrappers on Gemini fan-out (per its scoreboard, recovery loses Gemini results that min3 keeps). Read both wrapper sources, diff the gemini-invocation block, and identify whether the divergence reproduces in run 111336's relaunch_replacements.sh.
> Owner: any host with read access to /mnt/local-analysis/agent-logs/provider-autofeed-monitor/ and /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/.
> Exit: result file with diff and binary verdict.

## Cross-cutting recommendations (delta from 100339 scoreboard)

The 100339 scoreboard already named four cross-cutting recommendations (lane-state JSON, sandbox-internal lane paths, codex 0.124.0 pre-dispatch check, gemini fan-out mirror). All four remain unaddressed as of run 111336 — that's why this run repeats the same failure shapes. The deltas below are *new* signals from 111336:

- **Variant-fan-out is a negative-yield strategy when the root cause is a single upstream regression.** Run 111336 dispatched 9 codex lanes across 3 invocation variants and produced 0 results. The dispatcher cost was 9× a single-variant run with the same outcome. Fold a precondition into the wrapper: if `feedback_codex_cli_0_124_upstream_regression` is unresolved on the host (signal: `codex --version | grep ^0.124`), refuse to dispatch any codex lane and surface the prompt-A operator action instead.
- **Gemini Pro 2.5 has its own failure mode separable from Flash.** Until prompt B's diagnosis lands, treat `gemini-pro-*` as "demoted, use flash unless explicitly required." This is consistent with what `relaunch_replacements.sh` is already doing for the GTM lane (auto-falling-back to flash) but the wrappers should formalize it rather than relying on relaunch behavior.
- **The `claude-stream-*` shape may be the right replacement for `claude-recovery-*`.** Stream-JSON output gives a heartbeat signal that path-presence does not. If prompt C confirms the streaming lanes are healthy, retire the legacy stop-then-write claude lanes.
- **Lane-result-path-outside-sandbox is now recurrence #2** — the feedback memory was supposed to prevent this. Either the orchestrator wrapper (`classify_and_launch.sh`) needs a one-line allowlist injection, or a stop-hook should refuse to dispatch any lane whose prescribed `Result file:` path is outside the lane's sandbox root. Suggest opening (NOT in this lane) a workspace-hub issue against the wrapper to make the path-coercion explicit.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted
- ✓ No GitHub mutations (no `gh issue`/`pr` calls)
- ✓ No outreach drafts
- ✓ No self-approval / no `status:plan-approved` label changes
- ✓ No unapproved implementation
- ✓ No isolated worktree created — no edits to repo source were necessary; this document is a session-note artifact under `docs/sessions/`
- ✓ No secrets emitted (no API keys, tokens, or PII appear in this document)
- ✓ Memory-aligned: ENV-MISMATCH banner emitted per `feedback_lane_result_path_outside_sandbox.md`; codex regression cited per `feedback_codex_cli_0_124_upstream_regression.md`; gemini trust-env cited per `feedback_gemini_trust_env_blocks_reviews.md`; concurrent-runs caveat aligned with `feedback_check_parallel_work.md`

## Evidence appendix — Glob enumeration only

The enumeration backing every row above is the `Glob /mnt/local-analysis/agent-logs/**` listing captured in this lane's reasoning trace. Specifically:

- `provider-autofeed-20260430-111336/prompts/*.md` — 19 files
- `provider-autofeed-20260430-111336/logs/*.log` — 19 files
- `provider-autofeed-20260430-111336/results/*.md` — 3 files (`gemini-flash-fallback-research-4.md`, `gemini-flash-fallback-standards-6.md`, this lane's intended file *not* present)

No log or prompt body was read from this lane. Operators with read access to `agent-logs/` should cross-check the ✅/🟥 rows above against actual content before acting on the recovery prompts — particularly the codex lanes, since codex-cli 0.124.0 makes "log file present" a degraded success signal. The pgrep snapshot evidence (four overlapping autofeed runs) was captured via a `Bash pgrep` call that operates on the host process table, not the agent-logs filesystem, and is the only direct content evidence in this scoreboard.

## STARTED/FINISHED markers

- **STARTED:** 2026-04-30T11:25:06Z
- **FINISHED:** 2026-04-30T~11:35Z (lane wrote durable artifact under `docs/sessions/` and is exiting)
- **Out-of-band copy required:** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-recovery-governance-1.md` to satisfy the prescribed path.
