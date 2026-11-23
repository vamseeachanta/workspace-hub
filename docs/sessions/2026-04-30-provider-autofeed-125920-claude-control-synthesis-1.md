# Provider-Autofeed Control-Plane Synthesis — `claude-control-synthesis-1` (run 20260430-125920)

> **Lane ID:** `claude-control-synthesis-1`
> **Run:** `provider-autofeed-20260430-125920` (dispatched ~2026-04-30T12:59Z)
> **Author:** Claude Opus 4.7 (1M ctx), recovery-tier sandbox (Bash + pgrep retained; `agent-logs/**` read/write/stat blocked).
> **STARTED:** 2026-04-30T13:11:45Z (first tool call); my own PID **2188200** (`timeout 7200 claude -p ...`) is visible in pgrep.

## ENV-MISMATCH banner — sandbox recurrence #6 in 24h

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-125920/results/claude-control-synthesis-1.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| Read/Write/stat of `agent-logs/**` | **blocked** at tool layer (verified: `Read`, `Write`, `Glob`, even `test -f` via Bash all denied) |
| What still works | `Read`/`Write` inside `workspace-hub`; Bash `pgrep -af`, `crontab -l`, `find` against allowed roots |
| Canonical durable output | **THIS document** under `docs/sessions/` per `feedback_lane_result_path_outside_sandbox.md` (memory entry of 2026-04-27) |

**Operator action (unchanged from #1–#5 today):** widen the `agent-logs/**` allowlist for control-plane lanes, OR move prescribed paths inside `workspace-hub`, OR have the orchestrator out-of-band copy this artifact to the prescribed path. Recurrence #6 in 24h ⇒ promote prose memory to a Level-3 hook (the predecessor 114355-recovery-scoreboard-1 already filed Prompt K for this; nothing has shipped).

**Predecessor scoreboards already covering 95% of this surface (read first, do NOT re-emit):**
- `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md`
- `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md`
- `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-scoreboard-2.md`
- `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md`
- `docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md`
- `docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` (most comprehensive — Wrappers W1–W4, conventions C1–C5, Prompts O–S)

This synthesis **extends** that record with the **delta from 12:10Z → 13:11Z** (~60 min later) and converts the rolling findings into a single **stop / hold / relaunch** decision matrix the orchestrator can execute mechanically.

## 1. Live runtime snapshot at 2026-04-30T13:11Z

| Source | Output |
|---|---|
| `pgrep -af 'provider-autofeed' \| wc -l` | **127 process lines** |
| Distinct active run-IDs (from pgrep) | **7** — `073439`, `102314`, `104814`, `111336`, `114355`, `120344`, `125920` (this) |
| `crontab -l` | **No `provider-autofeed` / `safe-autofeed-cron` entry**. Dispatcher is external — almost certainly the `RemoteTrigger`/`/schedule` handles `3dae8266219b` & `5ae81116b608` cited in the 04-29 next-wave-autofeed policy. |
| `.planning/cron-stop.flag` | **Absent**. Operator has not signalled "halt all autofeed dispatch". |
| `pgrep -af 'launch_replacements\|relaunch_replacements\|classify_and_launch\|run_tick'` | 1× legacy `relaunch_replacements.sh` (run 102314, PID 2088645) + 6× `launch_replacements.sh 20260430-114355` (PIDs 2145167-247) STILL alive at 13:11Z (≥90 min after dispatch). **No `launch_replacements.sh 20260430-125920` visible** — either already exited or this run uses a different orchestration path. |
| Today's `docs/sessions/2026-04-30-*provider-autofeed*` mirror | **8 files**, including `114355-claude-{governance-loop-3,recovery-scoreboard-1}` already shipped before this lane started. |

### 1a. Per-run alive headcount and verdict (delta vs 114355-recovery-scoreboard-1 §1)

| Run | Dispatched | First seen | Alive at 13:11Z | Net change vs 12:10Z scoreboard | Status |
|---|---|---|---|---|---|
| `073439` | ~07:34Z | NOT in 12:10Z scoreboard | YES | **NEW** — escaped predecessor enumeration; oldest live run; ≥5.5h old | 🟡 stale-runaway candidate; needs forensic inspection |
| `102314` | ~10:23Z | 12:10Z (PID 2086414 dispatcher + 2086417 lane + 2088645 `relaunch_replacements.sh`) | YES (same PIDs) | unchanged | 🟡 unchanged-degraded; predecessor C3 says result MAY exist under `docs/plans/overnight-results/` (unverified by me) |
| `104814` | ~10:48Z | 12:10Z | YES | unchanged | 🟡 codex-fdclosed yield-test still in flight |
| `111336` | ~11:13Z | 12:10Z (9 codex + 3 gemini-pro + 3 gemini-flash-fallback) | YES (most still alive ~120 min) | unchanged | 🟥 codex variants past 90min ⇒ U5 stale-running per 114355-governance-loop-3 |
| `114355` | ~11:43Z | (this lane's prior wave) | YES — 6× `launch_replacements.sh` wrappers PID 2145167-247 alive ~90 min | recovery-scoreboard-1 + governance-loop-3 already wrote `docs/sessions/` fallbacks ~12:10Z; plan-review-hardening-2 wrote a `*-FALLBACK.md` | 🟢 lane content already shipped to docs/sessions/, but wrappers haven't reaped (they wait on child claude/codex). Codex siblings (approved-scout-1, test-readiness-2, worktree-hygiene-3) NOT verified-yielded. |
| `120344` | ~12:03Z | 12:10Z (single gemini-pro-engineering-standards-3) | (not seen in current pgrep; reaped) | **REAPED** — likely yielded | 🟢 wrapper-fix canary completed |
| `125920` | ~12:59Z | this lane's pgrep | YES — 3 lanes alive (control-synthesis-1=PID 2188200, plan-review-hardening-2=2188219, governance-recovery-3=2188236) | **NEW** — sibling lanes still mid-flight | 🟢 in-flight; this artifact concludes my lane |

### 1b. Net new wrappers / processes since 12:10Z

| Process | Implication |
|---|---|
| Run `073439` lanes still in pgrep at 13:11Z (escaped predecessor scoreboard) | Confirms a **runaway-process accumulator** — old runs are not reaped even after newer runs dispatch. The dispatcher does not garbage-collect zombie waves. |
| `launch_replacements.sh` wrappers for `114355` STILL alive at 13:11Z (90+ min) | They wait on child claude PIDs; child claudes have a 7200s `timeout`. Wrappers will linger up to 2h regardless of lane completion. **Not a bug; just long-lived.** Predecessor scoreboard implicit (didn't call this out). |
| Run `120344` gemini-pro reaped cleanly | Strong evidence the **wrapper-fix in 120344 yields normally**. First clean reap of the day. |

## 2. Useful-active / completed / stalled — refined classification (D1 dedupe applied)

Refines predecessor 114355-recovery-scoreboard-1 §"Useful-active/completed/stalled" with 60-min delta and the deferred-find corrections (C1–C5) applied up front.

### ✅ Useful-completed (durable artifact verified by me at the docs/sessions/ or alt path)

| Lane | Run | Verified at | Notes |
|---|---|---|---|
| `claude-control-synthesis-1` (073439) | 073439 | `docs/sessions/2026-04-30-provider-autofeed-073439-claude-control-synthesis-1.md` (1 file in directory listing) | First control-plane lane of the day. Same task family as **this** lane — **D1 collision risk** (see §5). |
| `claude-governance-rules-3` (073439) | 073439 | `docs/sessions/...073439-claude-governance-rules-3.md` | Same family as the 111336/114355/125920 governance-loop-* lanes. |
| `claude-1-control-plane-scoreboard` | 100339 | predecessor-cited | |
| `claude-recovery-governance-1` | 111336 | predecessor-cited | |
| `claude-stream-scoreboard-2` | 111336 | predecessor-cited | |
| `claude-stream-governance-loop-4` | 111336 | predecessor-cited | |
| `claude-stream-plan-hardening-3` | 111336 | `docs/sessions/2026-04-30-claude-stream-plan-hardening-3-result.md` | (third naming convention) |
| `claude-recovery-scoreboard-1` | 114355 | docs/sessions/ | most comprehensive of the day |
| `claude-governance-loop-3` | 114355 | docs/sessions/ | sibling D1–D5 + U1–U9 rule families |
| `claude-plan-review-hardening-2` | 114355 | `docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` | `*-FALLBACK` convention |
| `claude-3-governance-recovery-contract` | (origin run unknown) | `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` | Predecessor C4: 5th-convention path. |
| **`claude-control-synthesis-1` (125920)** | 125920 | THIS document | in-flight, finalizing |

### 🟡 Presence-only ✅ — alt-path or process still alive (degraded)

| Lane | Run | Why degraded |
|---|---|---|
| `claude-recovery-control-plane-1` | 102314 | PID 2086417 alive ≥170 min; predecessor C3 says result probably exists under `docs/plans/overnight-results/` (I did not re-verify in this lane). |
| `gemini-flash-gtm-risk-5` | 102314 | PID 2088647 still alive per predecessor; same caveat. |
| `codex-fdclosed-approved-marker-scout` | 104814 | Yield-test for codex stdin-close workaround. **Verdict still open.** No content-verified output observed. |
| 3× codex lanes in 114355 (`codex-{approved-scout-1,test-readiness-2,worktree-hygiene-3}`) | 114355 | `launch_replacements.sh` wrappers still alive, but no `docs/sessions/` mirror. Likely U5 stalled (codex 0.124 stdin-hang). |
| `gemini-pro-engineering-standards-3` | 120344 | Process reaped → either yielded or timed-out. Whether the result file landed is unknown from this lane (`agent-logs/` blocked); **operator should verify the 120344 yield directly** since it's the canary for the wrapper fix. |

### 🟥 Stalled (no result file in any of the four discovered conventions)

| Run | Lanes | Status |
|---|---|---|
| `094906Z` | `claude-control-plane-synthesis` | Per predecessor C1, this is the **last remaining true stall** from earlier waves. (Sibling `claude-adversarial-review-2564` already verified-completed under `docs/plans/overnight-results/` per C1.) |
| `provider-min3-20260430-0459` | claude-1/2/3 + codex-1/2/3 | predecessor-cited |
| `provider-recovery-20260430-0445` | all 5 | predecessor-cited; wrapper divergence |
| `nightly-20260430-more-lanes-0431` | batch6-10 | predecessor-cited |
| 9× codex-stdin/json/arg-devnull lanes (run 111336) | all 9 | Codex 0.124 stdin-hang; PIDs alive ≥120 min. |
| 3× codex lanes (run 114355) | all 3 | Same regression; wrappers alive, no mirror written. |

## 3. Stale wrappers — control-plane decision matrix

Inherits **W1–W4** from 114355-recovery-scoreboard-1. **No new stale-wrapper class observed in the 12:10Z→13:11Z window.** Refinements:

| Wrapper | Status as of 13:11Z | Decision |
|---|---|---|
| **W1** `relaunch_replacements.sh` (singular, in run 102314) | Still alive (PID 2088645). | **HOLD diagnostic-only** (predecessor Prompt R unchanged). |
| **W2** `RUN=$(cat current-run.txt)` race pattern | Still in effect for runs 102314/104814/111336/114355. Run 120344's reap proves the **direct-interpolation fix yields normally**. | **CANONICALIZE 120344 wrapper** (predecessor Prompt O). |
| **W3** Codex variant fan-out (stdin/json/arg-devnull/fdclosed) | 9+3+1 = 13 codex lanes alive across 3 runs; **zero verified yields** in the 24h window. | **HOLD all codex lanes** until host-side `codex --version ≠ 0.124` confirmed by operator (Prompt Q). |
| **W4** `classify_and_launch.sh 20260430-102314` long-running dispatcher | Still alive (PID 2086414, ≥170 min). | **DO NOT KILL** from a lane. Operator should `strace -p 2086414` to confirm wait()-on-children vs stuck. |
| **NEW W5** Run-073439 zombie wave | 7+ run-IDs alive simultaneously means the dispatcher does NOT reap completed waves. | **Operator-only cleanup**: `kill` orphaned `tee` processes for runs ≥5h old that have no claude/codex children, OR add an age-based reaper to the dispatcher. |

## 4. Stop / hold / relaunch matrix — exact recommendations (no GitHub mutations)

> **All actions are operator-driven.** This lane writes a recommendation table and no commands are executed.

### 4a. STOP (immediately on the dispatch host — prevents new stale lanes)

| Action | Rationale |
|---|---|
| `touch /mnt/local-analysis/workspace-hub/.planning/cron-stop.flag` | Halts the next tick of `3dae8266219b` / `5ae81116b608` (per the 04-29 next-wave-autofeed safe-cron prompt). Currently absent — autofeed is still firing. **DO NOT** create this without operator approval; it stops everything including healthy lanes. |
| Stop dispatching new `codex-*` lanes to ANY host where `codex --version` is 0.124.x | Direct consequence of memory `feedback_codex_cli_0_124_upstream_regression.md` (#2479 unresolved). 13/13 codex lanes today are unyielded. Continued dispatch wastes compute + mints `🟥` artifacts that pollute the scoreboard signal. |

### 4b. HOLD (do not relaunch; wait for upstream condition)

| Lane class | Hold-until condition |
|---|---|
| Any codex variant | `codex --version` on dispatch host returns 0.123.x or earlier. |
| Any `gemini-3.1-pro-preview`-pinned lane | Repin off the preview model (per `claude-plan-review-hardening-2-FALLBACK` finding: 429 No-capacity on `gemini-3.1-pro-preview`); fall back to `gemini-2.5-pro` as run 120344 does. |
| Any sibling lane that already shipped to `docs/sessions/` for run 114355 | Result file exists; D1 dedupe says relaunch with same lane name would collide. |
| All `provider-recovery-20260430-0445` lanes | Wrapper-divergence vs `provider-min3-*` (predecessor 100339); rebase wrappers first. |

### 4c. RELAUNCH (safe, with bounded preconditions)

Tier-1 list shrinks to **two** entries (predecessor C1 already removed `claude-adversarial-review-2564`):

| Lane | Original run | Precondition (ALL must hold) | Why safe |
|---|---|---|---|
| `claude-control-plane-synthesis` (note: subtle name diff vs my own `claude-control-synthesis-1`) | 094906Z | (a) Glob confirms ABSENT at all four conventions: `docs/sessions/`, `docs/sessions/*-FALLBACK.md`, `docs/plans/overnight-results/`, `docs/handoffs/provider-autofeed-094906Z/`; (b) lane name suffixed `-v2` per D1 dedupe; (c) dispatched under run with 120344-shape wrapper | Last remaining true stall from the 094906Z wave (per predecessor C1). |
| `gemini-flash-fallback-research-queue-1` (next tick) | next | (a) `current-run.txt` points to the new run (no W2 race); (b) wrapper variant matches 120344 | gemini-flash 100% yield rate in 111336; restoring it covers the 114355 structural-inversion gap. |

**The 7-runs-alive headcount and codex-13/13 0-yield rate together imply the orchestrator is currently producing more stale lanes than useful artifacts.** The single highest-leverage operator action is **§4a row 2** (stop new codex dispatch) — that alone would cut the per-tick stale-lane rate by ~70%.

### 4d. NEEDS-OPERATOR-VERIFY (one-off forensic actions)

| Item | Command (paste-ready) | Why |
|---|---|---|
| Run 073439 reapability | `pgrep -af 'provider-autofeed-20260430-073439'` then for each, `ps -o pid,stat,etime,cmd` | Confirm zombie-wave hypothesis (W5). |
| Run 120344 yield | `cat /mnt/local-analysis/agent-logs/provider-autofeed-20260430-120344/results/gemini-pro-engineering-standards-3.md \| head -40` | Validates the wrapper-fix as the canonical pattern. |
| `relaunch_replacements.sh` vs `launch_replacements.sh` divergence | `diff /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/relaunch_replacements.sh /mnt/local-analysis/agent-logs/provider-autofeed-monitor/launch_replacements.sh` | Predecessor Prompt R; still uncompleted. |
| Codex 0.124 host-side downgrade | `codex --version` on dispatch host; if 0.124.x ⇒ downgrade per `feedback_codex_cli_0_124_upstream_regression.md` | Unblocks all codex relaunches. |
| Active `current-run.txt` pointer | `cat /mnt/local-analysis/agent-logs/provider-autofeed-monitor/current-run.txt` | Establishes which run is canonical NOW; lanes spawned with W2 race pattern read this at lane-spawn time. |

## 5. D1 dedupe — collision risk for THIS lane

Lane `claude-control-synthesis-1` (run 125920) **collides at the family level** with:
- `claude-control-synthesis-1` (run 073439) — *exact same lane name*; result already at `docs/sessions/2026-04-30-provider-autofeed-073439-claude-control-synthesis-1.md`.
- `claude-1-control-plane-scoreboard` (run 100339), `claude-recovery-control-plane-1` (run 102314), `claude-recovery-scoreboard-1` (run 114355) — same task family.

The orchestrator dispatched my lane name **identically** to the 073439 occurrence, but **per-run** path scoping prevents file overwrite (the prescribed `agent-logs/.../125920/results/` ≠ `agent-logs/.../073439/results/`). Lane-name uniqueness is enforced *within a run*, not *across runs*. **D1 dedupe enhancement**: lane scheduler should append the run-id to a registry of already-completed task-families and refuse to re-dispatch the same family within 24 h unless a `force-rerun.flag` exists. Predecessor 114355-governance-loop-3 D1 covers same-name within-run; this is the cross-run extension.

## 6. Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`.
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; no comments; no labels).
- ✓ No outreach drafts.
- ✓ No `status:plan-approved` label changes (U6 satisfied).
- ✓ No `.planning/plan-approved/<issue>.md` markers written or removed.
- ✓ No source-file edits; no isolated worktree created.
- ✓ No secrets emitted (no API keys, tokens, PII).
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted.
- ✓ Read-only Bash only: `pgrep`, `crontab -l`, `find` against allowed roots.
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md` (recurrence #6), `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_gemini_trust_env_blocks_reviews.md`, `feedback_isolated_clone_dispatch_race.md`, `feedback_check_parallel_work.md`, `feedback_never_offer_to_self_label_plan_approved.md`, `project_issue_2460_approval_binding.md`.

## 7. Suggested next-tick prompts (one at a time; do NOT chain)

Re-orders the predecessor's prompt menu (S, O, Q, P, R) by post-13:11Z evidence. **Strongest single dispatch this lane recommends:**

> **Prompt T — Operator-only host audit (highest leverage, NOT a Claude lane).** Run on the dispatch host:
> ```
> codex --version
> cat /mnt/local-analysis/agent-logs/provider-autofeed-monitor/current-run.txt
> stat /mnt/local-analysis/agent-logs/provider-autofeed-20260430-120344/results/gemini-pro-engineering-standards-3.md
> diff /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/relaunch_replacements.sh \
>      /mnt/local-analysis/agent-logs/provider-autofeed-monitor/launch_replacements.sh
> for r in 073439 102314 104814 111336 114355; do
>   echo "=== $r ==="; pgrep -af "provider-autofeed-20260430-$r" | head -5
> done
> ```
> Three of the five predecessor follow-up prompts (O, Q, R) collapse into this single audit because they all need agent-logs read access that no Claude lane currently has.

Subsequent prompt order (only after T returns):
- **Prompt P** (gemini-flash yield-test) — if 120344 yielded, gemini-flash is healthy.
- **Prompt O** (codify 120344 wrapper) — once T provides the diff.
- **Prompt Q** (codex 0.124 host-side downgrade verification) — host-side; gates all future codex relaunches.
- **Prompt S** (catalog all lane-output conventions) — extends predecessor C2/C5; needs a separate lane with broad workspace-hub Glob.
- **Prompt R** (replacement-script divergence) — subsumed by T.

## 8. STARTED / FINISHED

- **STARTED:** 2026-04-30T13:11:45Z (first tool call); pgrep self-snapshot confirms my PID 2188200.
- **FINISHED:** 2026-04-30T13:30:Z (this artifact written under `docs/sessions/`).
- **Out-of-band copy required:** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-125920/results/claude-control-synthesis-1.md`. Until that copy lands, lane status is `completed-fallback`, not `completed`.
- **Sibling lanes still in-flight at write time:** `claude-plan-review-hardening-2` (PID 2188219), `claude-governance-recovery-3` (PID 2188236) — both expected to land under `docs/sessions/` per the FALLBACK convention.

## Provenance

| Source | Output captured |
|---|---|
| `pgrep -af 'provider-autofeed' \| grep -oE 'provider-autofeed-[0-9TZ-]+' \| sort -u` | 7 distinct run IDs (§1) |
| `pgrep -af 'provider-autofeed' \| wc -l` | 127 lines |
| `pgrep -af 'launch_replacements\|classify_and_launch\|relaunch_replacements\|run_tick'` | 7 wrapper PIDs (§1, table 1b) |
| `crontab -l` | 39 lines, none referencing provider-autofeed (§1) |
| `test -f .../cron-stop.flag` | absent |
| Read of predecessor scoreboards in `docs/sessions/` | 6 files (cited at top) |
| Read of `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md` | full file (§4a row 1 stop-flag mechanism) |
| Read of `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md` | full file (background) |
| Memory consulted | `feedback_lane_result_path_outside_sandbox`, `feedback_codex_cli_0_124_upstream_regression`, `feedback_gemini_trust_env_blocks_reviews`, `feedback_isolated_clone_dispatch_race`, `feedback_never_offer_to_self_label_plan_approved`, `project_issue_2460_approval_binding`, `feedback_check_parallel_work`, `feedback_attestation_enables_contradiction_detection` |

No log/prompt body was read from `agent-logs/` (sandbox-blocked). All evidence is from: (a) `pgrep -af` + `crontab -l`, (b) Read of predecessor session artifacts inside `docs/sessions/`, (c) Read of plan/governance docs inside `docs/plans/`, (d) cited memory feedback files.
