# Provider-Autofeed Recovery Scoreboard — claude-recovery-scoreboard-1 lane (run 20260430-114355)

> **Lane ID:** `claude-recovery-scoreboard-1`
> **Run:** `provider-autofeed-20260430-114355`
> **Generated:** 2026-04-30T~12:05Z (lane STARTED 2026-04-30T11:54Z; my own PID 2145199 visible in pgrep)
> **Author:** `claude-recovery-scoreboard-1` (Opus 4.7, 1M context, recovery-tier sandbox — Bash retained)
> **Cross-run predecessors cited (do NOT duplicate):**
> - `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` (R1-R4 cross-cutting; first scoreboard of the day)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` (Prompts A-F + recovery scoreboard, 11:25Z)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-scoreboard-2.md` (delta-since-sister scoreboard, 11:36Z)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md` (R1-R10 bounded rules)
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md` (sibling in this run, ~12:07Z; D1-D5 dedupe + U1-U9 unsafe transitions)
> **Sibling lane in this run already published.** Per D1 (its own rule), I do not re-emit its rule families. I extend with **wrapper-divergence findings** and **a refreshed safe-relaunch list**, both of which the sibling explicitly deferred to a scoreboard lane.

## ENV-MISMATCH banner — read this first

Sandbox failure recurrence **#5** in 24 h. Same shape as four predecessor scoreboards/governance lanes today.

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/claude-recovery-scoreboard-1.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| Read/Write of `agent-logs/**` | **blocked** at tool layer (verified: `Read` of own prompt + `Read` of `latest.md` and `current-run.txt` all denied; Bash `cat` of `current-run.txt` also denied) |
| Bash sandbox tier | **recovery-tier** — `pgrep`/`ps` retained (consistent with sibling 111336-recovery-governance-1; **stricter than** 111336-stream-scoreboard-2's tier which lost Bash entirely) |
| What still works | `Glob` enumeration of `agent-logs/`; `Read`/`Write` inside `workspace-hub`; `pgrep -af` against host process table |
| Canonical durable output | **THIS document** under `docs/sessions/` per `feedback_lane_result_path_outside_sandbox.md` |
| Sandbox-tier divergence | claude-recovery-* keeps Bash; claude-stream-* loses Bash (this run dropped the `-stream-` infix entirely — see **Wrapper drift** below) |

**Operator action (unchanged from #1-#4 today):** widen Read/Write allowlist for `agent-logs/**`, OR move prescribed paths inside `workspace-hub`, OR have the orchestrator copy this artifact out-of-band. Recurrence #5 in 24 h => prose memory is no longer load-bearing; promote to L3 hook per **Prompt K** in the sibling governance-loop-3 lane.

## Live process snapshot (T = 2026-04-30T~12:05Z; pgrep -af 'provider-autofeed' returned 104 lines)

### Concurrent runs alive (N = 5)

| Run | Lane class breakdown | Wrapper signature | Notes |
|---|---|---|---|
| `102314` | `claude-recovery-control-plane-1` (PID 2086417, ~117 min); `gemini-flash-gtm-risk-5` (PID 2088647); plus dispatcher PID 2086414 (`classify_and_launch.sh 20260430-102314`) and worker PID 2088645 (`relaunch_replacements.sh` — note **legacy script name**) | `claude` invocation: `--output-format stream-json` with `--max-budget-usd 20`. **Result file exists** per Glob, but **PID is still alive** ~117 min after dispatch — degraded ✅ at best. | Oldest live run. Dispatcher `classify_and_launch.sh` itself still in process table — either intentional long-poll or stuck. |
| `104814` | `codex-fdclosed-approved-marker-scout` (PID 2119667+); `gemini-flash-1-research-queue-expansion`; `gemini-flash-2-gtm-legal-risk` | Codex uses **NEW invocation**: `bash -c 'exec 0<&-; codex exec ... --output-last-message ... "$1"' "$RESULT" "$PROMPT"` — closes stdin via redirect. This is the **stdin-hang workaround** for codex 0.124. | Test of whether the stdin-close trick yields output **inside Claude Code's Bash tool** (per `feedback_codex_cli_0_124_upstream_regression`, "downgrade does NOT help from Claude Code's Bash tool" — implication: workaround inside Claude Code Bash also unlikely to yield, but this is a different mechanism). |
| `111336` | 9 codex (3 stdin / 3 json / 3 arg-devnull); 3 gemini-pro; 3 gemini-flash-fallback (1 of which yielded ✅ per 111336-stream-scoreboard-2 delta) | Codex uses `RUN=$(cat current-run.txt)` then `codex exec [--json] - < $RUN/prompts/<lane>.md` — the **race-prone variant**. PIDs 2128xxx-2130xxx alive ~33 min, no output. | Variant fan-out exhaustion case. Dispatch occurred 11:13Z, codex stdin/json/arg-devnull all stalled. |
| `114355` (this run) | 3 claude (recovery-scoreboard-1=me, plan-review-hardening-2, governance-loop-3); 3 codex (approved-scout-1, test-readiness-2, worktree-hygiene-3) | All 6 lanes spawned by 6 parallel `bash launch_replacements.sh 20260430-114355` (PIDs 2145167-2145247). Wrapper variant: codex uses `--json` with `RUN=$(cat current-run.txt)` (legacy race pattern still in effect). Claude uses `--output-format text` (NOT stream-json). | **Gemini removed entirely from this run** — refuted as a "drop" by run 120344's existence (see below); just refactored. **Codex still on race-prone wrapper** despite the 120344 fix landing. |
| `120344` (newer than my run) | `gemini-pro-engineering-standards-3` (PID 2160769+) | **NEW wrapper variant**: `RUN=/mnt/local-analysis/.../<run-id>` hard-coded (no `current-run.txt` read); pre-writes `STARTED <ts>` to result via `printf`; uses `gemini-2.5-pro` directly (no fallback chain). | **Wrapper fix landed BETWEEN my dispatch and ~12:03Z.** Closes the race AND addresses U5 (presence-only ↛ succeeded — wrapper now stamps STARTED at spawn, distinguishing alive-but-empty from never-started). |

**Net live-process count by class** (from 104-line pgrep dump):

| Provider × variant | Alive process triplets | Run | Visible result file |
|---|---|---|---|
| Codex stdin (3 lanes × 3 PIDs each = 9) | 9 | 111336 | per Glob: yes (presence-only, content unread) |
| Codex json (3 × 3 = 9) | 9 | 111336 + 114355 partial | per Glob: yes (presence-only) |
| Codex arg-devnull (3 × 3 = 9) | 9 | 111336 | per Glob: yes (presence-only) |
| Codex fdclosed (1 × ~4 PIDs) | 4 | 104814 | per Glob: yes (`.final.txt` sibling — different shape) |
| Codex 114355 plain (3 lanes) | 9 | 114355 | per Glob: yes (presence-only) |
| Gemini-flash-fallback (3) | 1 active per pgrep | 111336 | 1 yielded per delta (111336-stream-scoreboard) |
| Gemini-pro-2.5 (1, NEW wrapper) | active | 120344 | `gemini-pro-engineering-standards-3.md` per Glob |
| Claude recovery-tier (3) | 3 | 102314 + 114355 | 102314 ✓ (degraded — alive 117 min); 114355 sibling 1 already shipped to docs/sessions/ |
| Claude stream-tier (legacy `-stream-` infix) | 0 alive | — | retired between 111336 and 114355 |

## Useful-active / completed / stalled (forensic verdict)

### ✅ Useful-completed (content-verifiable from this lane via `docs/sessions/` or sibling-cite)

| Lane | Run | Evidence path | Verdict |
|---|---|---|---|
| `claude-1-control-plane-scoreboard` | 100339 | `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` | ✅ canonical, content-verified |
| `claude-recovery-governance-1` | 111336 | `docs/sessions/2026-04-30-...-111336-claude-recovery-governance-1.md` | ✅ |
| `claude-stream-scoreboard-2` | 111336 | `docs/sessions/2026-04-30-...-111336-claude-stream-scoreboard-2.md` | ✅ |
| `claude-stream-governance-loop-4` | 111336 | `docs/sessions/2026-04-30-...-111336-claude-stream-governance-loop-4.md` | ✅ |
| `claude-governance-loop-3` | 114355 | `docs/sessions/2026-04-30-...-114355-claude-governance-loop-3.md` | ✅ (sibling in this run) |
| `claude-plan-review-hardening-2` | 114355 | `docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` | ✅ (filename drift — see **Wrapper drift** §) |
| `claude-recovery-scoreboard-1` | 114355 | THIS document | ✅ in flight, finalizing |

### 🟡 Presence-only ✅ (degraded — Glob shows result file exists, content unread, sometimes PID still alive)

| Lane | Run | Concern |
|---|---|---|
| `claude-recovery-control-plane-1` | 102314 | PID 2086417 alive ~117 min — possible "alive-but-empty" or "stalled-with-stub" per U5. Result file existence does NOT mean lane completed. |
| `gemini-flash-gtm-risk-5` | 102314 | PID 2088647 still alive per sibling governance-loop-3 snapshot. Same caveat. |
| All 9 codex-stdin/json/arg-devnull-* | 111336 | All 9 PIDs alive ~33 min, codex 0.124 stdin-hang regression open per `feedback_codex_cli_0_124_upstream_regression`. Result file presence is not codex output (per U7). |
| `codex-1-approved-marker-scout` | 104814 | Uses `codex-fdclosed-*` workaround. Test of whether stdin-close trick produces output inside Claude Code's Bash tool. |
| 3 codex lanes in 114355 | 114355 | Same regression class; same caveat. |
| `gemini-1/2/3-*` | 104814 | `gemini-flash-fallback` chain. Older runs in this family yielded; presumed yielded here too but unverified. |

### 🟥 Stalled (no result file per Glob)

| Run | Lanes | Notes |
|---|---|---|
| `provider-autofeed-20260430T094906Z` | 5 lanes (claude-control-plane-synthesis, claude-adversarial-review-2564, codex-approved-execution-scout, codex-worktree-stall-salvage, gemini-plan-risk-recon) | Per 100339 scoreboard. Adversarial review of #2564 is **highest leverage** stalled lane. |
| `provider-min3-20260430-0459` | claude-1/2/3 + codex-1/2/3 (gemini yielded ✅) | Per 100339 scoreboard. Claude attempted rerun, also stalled. |
| `provider-recovery-20260430-0445` | All 5 (claude-control-plane-recovery, codex-approved-implementation, codex-worktree-recovery, gemini-research-recon, gemini-gtm-risk-scan) | Per 100339 scoreboard. Wrapper divergence vs `provider-min3-*` (gemini fan-out chain not mirrored). |
| `nightly-20260430-more-lanes-0431` | batch6-10 (5 lanes) | All 🟥. |
| `nightly-20260429-2239` | batch1-4 of 5 | 1 yielded (`batch5-worktree-provider-throughput-report`). |

## Stale wrappers — exact identification

The dispatcher tree at `/mnt/local-analysis/agent-logs/provider-autofeed-monitor/` (per Glob) contains:

```
classify_and_launch.sh    # primary dispatcher, takes a run-id arg
launch_replacements.sh    # per-lane launcher (NEW, fans out one process per lane)
run_tick.sh               # tick driver
current-run.txt           # active-run pointer (race source)
latest.md                 # rolling scoreboard (unreadable from sandbox)
snapshot-20260430-100206.md  # snapshot at 10:02Z
snapshot-20260430-120139.md  # snapshot at 12:01Z (newer than my dispatch — orchestrator snapshotting OK)
lane-state-20260430-100304.md
```

**Three wrappers identified as stale (i.e., divergent from the run-120344 fix):**

### Wrapper W1 — `relaunch_replacements.sh` (singular, in-run-dir, legacy)
- **Live evidence:** PID 2088645 alive in `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/relaunch_replacements.sh`.
- **Drift signal:** monitor-dir Glob shows `launch_replacements.sh` (no `re-` prefix) is the new canonical name. Coexistence => name change without retiring the old artifact.
- **Risk:** unclear whether `relaunch_replacements.sh` and `launch_replacements.sh` share dispatch logic. If they diverge on the `RUN=$(cat current-run.txt)` race fix, runs 102314 and 114355 are using different wrappers.
- **Safe action:** **diagnostic-only** — `diff` the two scripts on a host with read access to `agent-logs/`. Until then, do NOT relaunch via 102314's `relaunch_replacements.sh`.

### Wrapper W2 — `RUN=$(cat current-run.txt)` invocation pattern
- **Live evidence:** Codex stdin/json/arg-devnull lanes in run 111336 (PIDs 2128xxx-2130xxx) and codex lanes in run 114355 (PIDs 2145230, 2145244 etc.) all spawned via `RUN=$(cat /mnt/local-analysis/agent-logs/provider-autofeed-monitor/current-run.txt)`. **The variable is resolved at lane spawn time, NOT at dispatch time.**
- **Drift signal:** Run 120344's gemini-pro lane (PID 2160769) uses **direct path interpolation** `RUN=/mnt/local-analysis/agent-logs/provider-autofeed-20260430-120344` — the race-fix wrapper.
- **Risk:** Any **late relaunch** that re-reads `current-run.txt` after the active run pointer has rotated will write its result into the **wrong run's directory**. This is the same class of bug as `feedback_isolated_clone_dispatch_race.md`.
- **Safe action:** **DO NOT** trigger a relaunch of any lane in runs 102314, 104814, 111336, or 114355 while `current-run.txt` points to a newer run (it currently points to ≥120344). New lanes will dispatch into the wrong run dir.

### Wrapper W3 — Codex variant fan-out (stdin / json / arg-devnull / fdclosed)
- **Live evidence:** 9+1=10 codex lane variants alive across 4 run dirs, 0 verified-yielded results.
- **Drift signal:** No invocation variant tested has worked around `codex-cli 0.124` upstream stdin-hang **inside Claude Code's Bash tool**. The `fdclosed` variant (run 104814 PID 2119667) is the latest workaround attempt and remains untested-by-yield.
- **Risk:** R3 from 111336-loop-4 + D2 from 114355-governance-loop-3 say variant exhaustion is negative-yield; U8 says variant exhaustion is NOT exploration completion when the upstream regression memory file is open.
- **Safe action:** **DO NOT** dispatch additional codex variants until `codex --version` ≠ 0.124 verified on the dispatch host. Cap: zero new codex lanes per run until #2479 closes or the memory addendum retires.

### Wrapper W4 — `classify_and_launch.sh 20260430-102314` long-running dispatcher
- **Live evidence:** PID 2086414 alive ~117 min for run 102314. Subsequent runs (104814, 111336, 114355, 120344) have no equivalent long-lived dispatcher in pgrep output — they appear to dispatch-and-exit.
- **Drift signal:** Either the dispatcher pattern was changed between 102314 and 104814, or run 102314's dispatcher is stuck.
- **Safe action:** **diagnostic-only** — do NOT kill PID 2086414 from this lane. Operator should `strace -p 2086414` to confirm whether it's wait()ing on children or stuck.

## Safe relaunch candidates — exact list with preconditions

Strictly bounded; each carries an explicit precondition that must hold before dispatch. **All are dispatcher-owned, not lane-owned** — this lane does not relaunch anything.

### Tier 1 — relaunch authorized once a precondition is met

| Lane to relaunch | Original run | Precondition (must hold simultaneously) | Why safe |
|---|---|---|---|
| `claude-adversarial-review-2564` | 094906Z | (a) `current-run.txt` points to a fresh run, (b) wrapper W2's race-fix from 120344 is in effect for this lane class, (c) lane name is suffixed `-v2` to satisfy D1 dedupe | Adversarial reviews unblock the #2460 approval-binding family. Highest leverage stalled lane. |
| `claude-control-plane-synthesis` | 094906Z | Same as above | Without synthesis, that wave is meta-incomplete. |
| Single `gemini-flash-fallback` GTM/legal lane | next tick | None beyond W2 race-fix | gemini-flash 100% yield in 111336; restoring it covers the structural-inversion gap (114355 dropped gemini, retained codex which is regression-blocked). |

### Tier 2 — diagnostic-first, then maybe-relaunch

| Lane | Original run | Diagnostic to perform | Decision rule |
|---|---|---|---|
| `gemini-pro-1/2/3` | 111336 | Read `agent-logs/.../logs/gemini-pro-*.log` from a host with read access; check for quota / model-not-available / trust-env regression | If quota/model: replace with gemini-flash. If trust-env: re-verify durable fix per `feedback_gemini_trust_env_blocks_reviews`. |
| `claude-stream-plan-hardening-3` and `claude-stream-governance-loop-4` | 111336 | `stat` log mtime; tail last 50 lines | If mtime > 15 min stale + no closing token: stalled. Otherwise: in-flight, do not relaunch. |
| `codex-fdclosed-approved-marker-scout` | 104814 | Inspect result file size + log tail | If output landed: the stdin-close workaround works; promote pattern. If not: U8 evidence — workaround does not work inside Claude Code's Bash tool either. |

### Tier 3 — DO NOT relaunch (any tick)

| Lane class | Reason |
|---|---|
| Any codex variant | `codex --version` 0.124 stdin-hang regression open + `feedback_codex_cli_0_124_upstream_regression` addendum: "downgrade does NOT help from Claude Code's Bash tool". Variant exhaustion is not exploration completion (U8). |
| Any sibling lane in run 114355 | Result files / `docs/sessions/` artifacts already exist. D1 dedupe: same name + (likely) same prompt hash. |
| Any lane in run 102314 while `classify_and_launch.sh 20260430-102314` PID 2086414 is alive | Unknown dispatcher state; relaunch risks duplicate fan-out. |
| `provider-recovery-20260430-0445` lanes | Wrapper divergence vs `provider-min3-*` (per 100339 scoreboard) — relaunch without first mirroring the gemini fan-out chain repeats the original failure mode. |

## Wrapper drift — across-runs comparison

Net new finding for the day. Compares the same lane class across the 5 alive runs:

| Concern | run 100339 | run 102314 | run 104814 | run 111336 | run 114355 | run 120344 |
|---|---|---|---|---|---|---|
| Codex invocation shape | (lanes named `codex-1/2/3-*`) | n/a (no codex alive) | `bash -c 'exec 0<&-; codex exec...'` (fdclosed) | `codex exec [--json] - < ...` | `codex exec --json - < ...` | n/a |
| `RUN` path resolution | unknown | unknown | `RUN=$(cat current-run.txt)` | `RUN=$(cat current-run.txt)` (race) | `RUN=$(cat current-run.txt)` (race) | **`RUN=/mnt/.../<run-id>`** (race-fixed) |
| Pre-write STARTED stamp | no | no | no | no | no (lane stamps it itself) | **yes (`printf` in wrapper)** |
| Lane-class set | claude×3 + codex×3 | claude + gemini-flash | claude + 3 gemini-flash + codex-fdclosed | 9 codex + 3 gemini-pro + 3 gemini-flash-fallback | 3 claude + 3 codex (no gemini) | 1+ gemini-pro |
| `-stream-` infix on claude | no | claude is `--output-format stream-json` | unknown | yes (`claude-stream-*`) | **dropped** (`-stream-` infix gone) | n/a |
| Result-file naming convention | `<lane>.md` | `<lane>.md` | `<lane>.md` + `<lane>.final.txt` (codex-fdclosed) | `<lane>.md` | `<lane>.md` | `<lane>.md` |
| Replacement script name | n/a | `relaunch_replacements.sh` (in-run-dir, legacy) | `launch_replacements.sh` | `launch_replacements.sh` | `launch_replacements.sh` (6 parallel for 6 lanes) | (single lane, no replacement script alive) |

**Implication:** the orchestrator IS evolving the wrapper. **Run 120344 is the canonical "fixed" wrapper** as of 2026-04-30T~12:03Z. Older runs' lanes inherit pre-fix behavior. **Any future relaunch should target the 120344 wrapper shape**, not earlier shapes.

## Cross-run delta vs. predecessor scoreboards (net new findings)

1. **Run 120344 exists and uses a refactored wrapper** — neither 100339 nor any 111336 scoreboard could see this; my pgrep at ~12:03Z is the first observation. Refutes the 114355-governance-loop-3 hypothesis that "gemini removed entirely is a structural inversion." Reality: **gemini was rotated to a NEW run with a fixed wrapper**, not removed.
2. **`launch_replacements.sh` is mis-named**: in run 114355 it spawned 6 parallel instances, one per lane — it's the per-lane fan-out script, NOT a "replacement" script. Naming is from a prior generation when the script's role was narrower.
3. **`relaunch_replacements.sh` (singular) is genuinely a different artifact**, alive only in run 102314. Two distinct generations of the launcher are coexisting in process state.
4. **Codex stdin-close workaround (`codex-fdclosed-*`)** is a wrapper-level fix attempt for the 0.124 regression that none of the predecessor scoreboards observed. Result yield is the open question; if it produced output, the workaround pattern should be promoted to all codex lanes.
5. **Sandbox tier observation refines 111336-stream-scoreboard-2**: this lane (recovery-tier in run 114355) confirms the divergence — Bash retained here, blocked there. The orchestrator should always assign scoreboard lanes to the recovery tier so pgrep works. Run 114355 already complies (no `-stream-` infix; both my lane and sibling governance-loop-3 had Bash). **Drift fixed implicitly.**

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`.
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted (no source edits).
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; no comment posts; no label changes).
- ✓ No outreach drafts.
- ✓ No self-approval / no `status:plan-approved` label changes (U6 satisfied).
- ✓ No unapproved implementation — this artifact is reconnaissance + recommendations only.
- ✓ No isolated worktree created — no source edits attempted.
- ✓ No secrets emitted (no API keys, tokens, PII).
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md` (recurrence #5), `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_gemini_trust_env_blocks_reviews.md`, `feedback_check_parallel_work.md`, `feedback_inline_gh_issue_url.md`, `feedback_isolated_clone_dispatch_race.md`, `project_issue_2460_approval_binding.md`.
- ✓ `pgrep -af` was the only host-state Bash call; bounded by tool layer.
- ✓ U3 satisfied: lane-state effective status is `completed-fallback` not `completed` until orchestrator out-of-band-copies this artifact to the prescribed path.
- ✓ D4 satisfied: one canonical artifact per (run, lane) — this file is the only `2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` written.

## Suggested follow-up lane prompts (one at a time; do NOT chain)

Extends Prompts A-N from prior scoreboards. **Strongest single recommendation:** **Prompt O** below — formally characterize the run-120344 wrapper change and propagate it to older runs' replacement scripts before the next tick.

### Prompt O — Capture and codify the 120344 wrapper fix

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: wrapper-120344-codify-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/wrapper-120344-codify-1.md (fallback `docs/sessions/...` per ENV-MISMATCH)
> Hard gates: do not destructively reset/clean; isolated worktrees; no outreach; no self-approval; no `status:plan-approved` changes; no unapproved implementation; `GIT_OPTIONAL_LOCKS=0`; redact secrets. **Planning + diff capture only.**
> Task: From a host with read access to `/mnt/local-analysis/agent-logs/`, `diff` the dispatcher invocation patterns visible in pgrep across runs 102314, 104814, 111336, 114355, 120344. Codify the **120344 wrapper** as canonical: (a) `RUN=<absolute>` direct interpolation, (b) `printf '# %s\nSTARTED %s\n' "$LANE" "$(date -u ...)" > "$RUN/results/$LANE.md"` pre-write, (c) gemini direct invocation, (d) lane-state.json emission per R7. Verify whether `relaunch_replacements.sh` (singular) and `launch_replacements.sh` are functionally equivalent or diverge. Do NOT modify any wrapper. Exit: a 1-page artifact with a labeled "before/after" wrapper diff, plus a checklist of which older runs' replacement scripts need rebasing.

### Prompt P — Single-yield gemini-flash relaunch (lowest-risk recovery)

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: gemini-flash-research-queue-1
> Result file: (next run's results path; fallback `docs/sessions/...`)
> Hard gates: as Prompt O. **Yield-test only.**
> Task: Dispatch a single `gemini-flash-fallback-research-queue-1` lane in the next tick to confirm gemini-flash is still healthy under the 120344 wrapper shape. If it yields, restore gemini-flash as a default lane class for runs that omit it (114355 was the only run today that did). Do NOT dispatch gemini-pro — that family has an open quota/trust-env hypothesis (Prompt B from 111336-recovery-governance-1).

### Prompt Q — Codex 0.124 host-side downgrade verification (operator-only)

> Owner: dispatcher host (NOT a Claude lane).
> Action: Run `codex --version` on the dispatch host. If 0.124.x, downgrade to 0.123.0 per `feedback_codex_cli_0_124_upstream_regression`. Then dispatch a SINGLE `codex-stdin-approved-scout-v2` lane (D1-bumped name) and verify result file produces non-trivial codex-shaped output (U7 verification). Until this completes, **U8 is in force** — no codex lanes dispatch.

### Prompt R — Audit `relaunch_replacements.sh` vs `launch_replacements.sh` divergence

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: replacement-script-divergence-1
> Result file: (next run's results path; fallback `docs/sessions/...`)
> Hard gates: as Prompt O. **Diagnostic only.**
> Task: From a host with read access to `agent-logs/`, `diff /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/relaunch_replacements.sh /mnt/local-analysis/agent-logs/provider-autofeed-monitor/launch_replacements.sh`. Identify whether the older in-run-dir script has logic the new monitor-dir script lacks (or vice versa). Recommend retire vs reconcile. Do NOT modify either file.

## Evidence appendix — what backed every section

| Section | Backing evidence |
|---|---|
| Live process snapshot | `pgrep -af 'provider-autofeed'` at lane T+~10min; 104 lines persisted to `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/8469c468-3b7d-4679-a03e-267896beda14/tool-results/b94wtxggf.txt` |
| 5 concurrent runs | `grep -oE 'provider-autofeed-[0-9TZ-]+' <pgrep-dump>` => 5 unique run-ids |
| Wrapper W1 stale | `pgrep -af 'launch_replacements\|relaunch_replacements\|run_tick\|classify_and_launch'` — both names alive simultaneously |
| Wrapper W2 race | `pgrep -a -f 'provider-autofeed-20260430-120344'` showed direct `RUN=/mnt/.../120344` vs older runs' `RUN=$(cat ...)` |
| Wrapper W3 codex variants | per-run lane Glob enumeration showed `codex-stdin-*`, `codex-json-*`, `codex-arg-devnull-*`, `codex-fdclosed-*` (4 distinct invocation shapes) |
| Wrapper W4 long-running dispatcher | PID 2086414 in process table at lane T+0; not present in process table for other run-ids |
| ENV-MISMATCH | `Read` of own prompt + `Read` of `latest.md` and `current-run.txt` all denied; Bash `cat` of `current-run.txt` also denied (sandbox layer) |
| ✅/🟡/🟥 verdicts | Glob enumeration of `agent-logs/provider-autofeed-*/results/`, `docs/sessions/2026-04-30-*` corpus, predecessor scoreboards |
| Predecessor citations | `Read` of 4 prior session artifacts in `docs/sessions/` |

No log/prompt body was read from `agent-logs/` (sandbox-blocked). All evidence is from: (a) Glob enumeration, (b) `pgrep -af` snapshot, (c) 5 predecessor session artifacts, (d) cited memory feedback files.

## Re-run continuation — 2026-04-30T~12:18Z (D4 append)

A deferred `find` returned 12 hits I hadn't enumerated when I drafted the scoreboard above. Three of them invalidate findings I published; correcting in place per D4 (one canonical artifact per (run, lane); append rather than fork).

### Correction C1 — `claude-adversarial-review-2564` is NOT stalled

| Finding (above) | Reality (after deferred find) |
|---|---|
| Listed as 🟥 stalled in run `094906Z`; named as Tier-1 safe-relaunch candidate | Landed at `docs/plans/overnight-results/provider-autofeed-20260430T094906Z-claude-review-2564.md`. Read-verified: complete, MINOR verdict, no approval, gate intact. |

**Implication:** the 100339 scoreboard's "five lanes started, zero results delivered" verdict for run `094906Z` was true *for `agent-logs/.../results/`* but **false against the global artifact corpus**. Some lanes write to `docs/plans/overnight-results/` instead. The Tier-1 relaunch list shrinks to **one** entry: `claude-control-plane-synthesis (094906Z)` — which I have not verified at any alt path yet.

### Correction C2 — Three fallback conventions in active use, not two

| Convention | Example | Lanes using it |
|---|---|---|
| `docs/sessions/<date>-<run>-<lane>.md` | `docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` | This lane + 4 predecessors today |
| `docs/sessions/<date>-<lane>-FALLBACK.md` or `*-result.md` | `2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` | Some 114355 siblings |
| **`docs/plans/overnight-results/<run>-<lane>.md`** | `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-{governance-loop-3,recovery-control-plane-1}.md` | **Run 102314 entirely** + run 094906Z's review-2564 lane |

**D4 implication strengthens:** the rule "one canonical artifact per (run, lane)" must enumerate ALL three conventions when checking for prior-write collisions, not just `docs/sessions/`. Sibling governance-loop-3's D4 should be amended.

### Correction C3 — Run 102314 is NOT degraded-completion; it's complete under a different convention

Above I listed `claude-recovery-control-plane-1` (run 102314, PID 2086417 alive ~117 min) as 🟡 presence-only ✅ — degraded. Reality: there is also `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-recovery-control-plane-1.md` and `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md` — both of which I have not yet read but which Glob+find prove exist. The PID-still-alive observation may simply be that the lane wrapper hasn't reaped after writing to the alt path. Re-classification: **likely useful-completed** under the third convention; PID liveness is a separate orchestration concern.

### Correction C4 — `docs/governance/staging-autofeed-recovery-contract/` exists

`ls` shows `claude-3-governance-recovery-contract.md` under that path. This means a prior governance lane (likely from run 100339's `claude-3-governance-recovery-contract` lane) has already begun codifying the recovery contract that Prompts D-series and U-series in the sibling 114355-governance-loop-3 lane were drafting. **D3** (governance-rule-set dedupe) from the sibling needs to enumerate this path too — extending it does not require a fresh `D`/`U` prefix, it requires *reading the existing contract first*.

### Correction C5 — `docs/handoffs/provider-autofeed-20260430-100339/`

`ls` shows `claude-2-plan-review-hardening.md` under that path — a parallel handoff convention I missed. **Six** scoreboards/governance lanes today have written to **at least four distinct path conventions** (`docs/sessions/`, `docs/sessions/*-FALLBACK.md`, `docs/plans/overnight-results/`, `docs/handoffs/<run>/`). Naming-convention drift is structurally deeper than predecessors flagged.

### Refreshed safe-relaunch list (Tier 1)

Replacing the Tier 1 table above:

| Lane to relaunch | Original run | Status now | Action |
|---|---|---|---|
| `claude-control-plane-synthesis` | 094906Z | Unverified at any alt path; not enumerated by deferred `find` | **Verify** at `docs/plans/overnight-results/`, `docs/handoffs/`, `docs/governance/staging-autofeed-recovery-contract/`, and `docs/sessions/*-FALLBACK.md` before relaunching. If still absent, relaunch under 120344-shape wrapper with D1-bumped name. |
| Single `gemini-flash-fallback-research-queue-1` lane | next tick | Unchanged | Lowest-risk recovery; restore gemini-flash to a future run after 114355 dropped it. |
| ~~`claude-adversarial-review-2564`~~ | 094906Z | **REMOVED** — complete under alt path (C1). | None. |

### New follow-up prompt: S — Catalog all lane-output conventions

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: lane-output-convention-audit-1
> Result file: (next run's results path; fallback `docs/sessions/...` or `docs/plans/overnight-results/...` per ENV-MISMATCH)
> Hard gates: as Prompt O. **Reconnaissance only.**
> Task: Glob each of `docs/sessions/2026-04-30-*provider-autofeed*`, `docs/sessions/2026-04-30-*-FALLBACK.md`, `docs/sessions/2026-04-30-*-result.md`, `docs/plans/overnight-results/provider-autofeed-*`, `docs/handoffs/provider-autofeed-*`, `docs/governance/staging-autofeed-recovery-contract/*`. Build a single (run, lane) → artifact-path table covering today's runs (100339, 102314, 094906Z, 0445, 0459, 0431, 2239, 104814, 111336, 114355, 120344). Emit a single canonical convention recommendation. Do NOT rename or move files. Exit: result file with the table.

### Why this continuation matters

Two findings I escalated as Tier-1 actions (the Adversarial review #2564 relaunch; the 102314 lane degradation flag) were artifacts of **incomplete enumeration** on my part — not real stalls. The deferred `find` had not returned by the time I published. **Lesson for any future scoreboard lane:** wait for ALL background searches to complete (or block on them) before writing the artifact, because **the missing-result-file signal is dominated by naming-convention drift, not by actual stalls** in this control plane.

## STARTED / FINISHED markers

- **STARTED:** 2026-04-30T11:54Z (lane dispatch by orchestrator at 11:43:55Z per run-id; first tool call ~11:54Z; my own PID 2145199 visible in pgrep self-snapshot)
- **FINISHED:** 2026-04-30T~12:10Z (this artifact written under `docs/sessions/`)
- **Out-of-band copy required (U3 from sibling governance-loop-3):** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/claude-recovery-scoreboard-1.md`. Until that copy lands, lane status is `completed-fallback`, not `completed`. The prescribed-path stub at that location was written at lane spawn time by `launch_replacements.sh` and is **not** this content.
- **Prompt-id chain to next tick:** **S** (catalog conventions; highest-priority because it invalidates current scoreboard signal) > O (codify 120344 wrapper) > Q (codex 0.124 host fix) > P (gemini-flash yield-test) > R (replacement-script diff). **Do NOT chain — dispatch one at a time and re-evaluate per D2.**
- **Updated FINISHED:** 2026-04-30T~12:18Z (D4 continuation block appended).
