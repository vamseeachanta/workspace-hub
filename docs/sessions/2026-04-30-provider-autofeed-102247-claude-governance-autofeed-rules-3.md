# Provider-Autofeed Governance/Recovery — `claude-governance-autofeed-rules-3` (run 20260430-102247)

> **Lane ID:** `claude-governance-autofeed-rules-3`
> **Run:** `provider-autofeed-20260430-102247`
> **Author:** Claude Opus 4.7 (1M ctx), recovery-tier sandbox.
> **STARTED:** 2026-04-30T15:29:09Z (first tool call: `date -u`; lane wrapper dispatch nominally at ~10:22Z — see J1 evidence)
> **FINISHED:** 2026-04-30T~15:35Z (this artifact written)
> **Inspected commands/sources at lane start:** `Glob /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/**`, `date -u`, `Read docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md`, `Read docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md`, `Read config/ai-tools/provider-routing-scorecard.json`, `Read config/ai-tools/provider-utilization-weekly.json`, `Read docs/sessions/2026-04-30-claude-stream-plan-hardening-3-result.md`, `Read agent-logs/.../prompts/<lane>.md` (denied — sandbox-blocked, expected per memory).

## ENV-MISMATCH banner — sandbox recurrence #9 in 24h

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/results/claude-governance-autofeed-rules-3.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read`/`Write`/`stat` of `agent-logs/**` | **blocked** at tool layer (verified — `Read` of own prompt file denied; `Bash mkdir`/`pgrep` required permission approval, not auto-allowed) |
| What still works | `Read`/`Write` inside `workspace-hub`; `Glob` enumeration of `agent-logs/**`; restricted `Bash` |
| Canonical durable output | **THIS document** at `docs/sessions/2026-04-30-provider-autofeed-102247-claude-governance-autofeed-rules-3.md` per H8b canonical naming + `feedback_lane_result_path_outside_sandbox.md` |
| Out-of-band copy required (U3) | Orchestrator MUST `cp` this file to the prescribed path. Until copy lands, lane status = `completed-fallback`, NOT `completed`. |

Recurrence #9 in 24h (predecessor 145633 counted #8): 100339 (`claude-3-governance-recovery-contract`), 111336×2, 114355×2, 125920×2, 145633, **102247** (this lane). Same shape; same operator-side mitigation (widen sandbox grant set OR relocate prescribed path inside `workspace-hub`).

## Cross-run predecessors (cite-only — D3 forbids redefinition)

This lane extends the rule ladder; it does NOT redefine prior rules. The `J` prefix is fresh per D3 (predecessor 145633 used `H`; before that R/D/U/W/G).

| Source | Rules already authored | Why I cite, not extend |
|---|---|---|
| `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` | R1–R4 + scoreboard-based stall taxonomy | Earliest-today scoreboard; documents the stall patterns my J-series consumes |
| `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` | Useful-lane defn, `LOG_MTIME_MAX_S=600`, `RESULT_MIN_BYTES=256` | Top-level contract; J-series obeys these defaults |
| `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` | Prompts A–F | recovery scoreboard scaffold |
| `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md` | R1–R10 + Prompts G–J | rule prefixes R, dedupe lattice |
| `docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` | W1–W4, conventions C1–C5, Prompts O–S | path-convention precursor |
| `docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md` | D1–D5 dedupe + U1–U9 unsafe-transition | dedupe + transition gate primitives |
| `docs/sessions/2026-04-30-provider-autofeed-125920-claude-control-synthesis-1.md` | W5 + decision matrix + Prompt T | provider mix decision frame |
| `docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md` | G1–G8, Prompts U–X | Hermes-active gate, codex-zombie aggregator |
| `docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md` | **H1–H8** + Prompts Y/Z/AA/BB | rule-drift detector, run-density cap, write-probe stub disambiguation, aggregate-budget visibility, retirement scanner, in-flight sibling contract, codex overwrite protection, **path-conventions manifest H8a–H8e** |

**Note on temporal inversion:** my run is `102247` (dispatched ~10:22Z). The 145633-run `H` lane was dispatched ~14:56Z and authored before my wrapper got around to executing. By dispatch order I am earlier; by execution order I am later. The artifact ladder is keyed by execution wall-clock, so 145633 H-series is precedent. This is itself the load-bearing instance of **J1** below.

## Lane scope — narrow per dispatch task

The orchestrator asked for: **"turn this tick's stale-lane and provider stall evidence into bounded autofeed rules with dedupe, unsafe-transition gates, and canonical result/log path conventions."**

The **path-conventions** third leg is fully discharged by H8a–H8e (predecessor 145633). I will NOT redefine; I cite and reuse the H8b fallback (this very file's path is the worked example).

The **stale-lane** and **provider-stall** legs need fresh signatures specific to run 102247 evidence:

1. **Long dispatch-vs-execution skew** — my own wrapper started at ~10:22Z and ran at 15:29Z. The 100339 scoreboard already documented `provider-autofeed-20260430T094906Z` (5+h skew, 0/5 results). Same shape, recurring.
2. **Provider activity stall vs quota headroom** — codex `last_ts` = 2026-04-28T06:15Z (per `provider-utilization-weekly.json`), >2 days stale, while `quota_utilization_pct = 0.4%` (vast headroom). Gemini at 0.1% quota with 3 sessions all week. Both providers idle despite room to run.
3. **Cross-tick re-fire of same-named lanes** — `claude-3-governance-autofeed` (provider-min3-20260430-0459 stalled 🟥), `claude-3-governance-recovery-contract` (100339 ✅), `claude-governance-recovery-3` (125920 ✅), `claude-governance-loop-rules-3` (145633 ✅), `claude-governance-autofeed-rules-3` (102247, this) — same lane *family* fired ≥5 times today.
4. **Cascade pattern** — predecessor 100339 enumerated 5+ runs across the morning where most lanes ended 🟥; the orchestrator kept dispatching anyway.

I author **J1–J5** below with embedded dedupe + unsafe-transition gates per D3+H lattice.

## Live tick-102247 evidence

| Source | Output | Implication |
|---|---|---|
| `Glob agent-logs/provider-autofeed-20260430-102247/**` | 9 prompt files, 9 result files, 6 log files (gemini-pro lanes have `-lite` variants without `.log`, plus 3 non-`-lite` result files for gemini-pro) | Result files **exist before** this lane's write — orchestrator probe-stubs (per H3 from 145633). Log files exist for codex/claude lanes only; gemini wrappers redirect differently. |
| Lane name set in 102247 | `claude-{control-plane-synthesis-1, plan-review-hardening-2, governance-autofeed-rules-3}`, `codex-{approved-eligibility-scout-1, test-readiness-scout-2, worktree-hygiene-salvage-3}`, `gemini-{research-queue-expansion-1, gtm-legal-risk-2, standards-source-recon-3}` (and `-lite` variants) | Standard 9-lane provider-mix triplet; `-lite` Gemini variants are runtime fallbacks. |
| `gemini-pro-{research-queue-1, gtm-legal-risk-2, standards-recon-3}-lite.md` | All present in `results/` per Glob | Gemini-pro lite wrapper completed (consistent with 145633 evidence that gemini-pro lanes finalize fast). |
| Provider-utilization-weekly.json `codex.last_ts` for W18 | `2026-04-28T06:15:26.687000Z` | **>2 days stale** at lane start (15:29Z is 2026-04-30); quota at 0.4% (5840+ msg headroom). **Direct provider-stall evidence.** |
| Provider-utilization-weekly.json `gemini.last_ts` for W18 | `2026-04-29T07:03:25.228000Z` | ~32h stale; only 3 sessions / 4 post-records all week. **Underused but not strictly stalled.** |
| Provider-utilization-weekly.json `claude` for W18 | 131 sessions, last_ts `2026-04-30T12:56:28Z`, 10.1% activity util | Claude is the only provider actively turning over today. |
| Predecessor 100339 scoreboard | `provider-autofeed-20260430T094906Z` = 5 lanes started, 0 results delivered after >5h | **Cascade** — same dispatch shape as today; same outcome pattern. J5 consumes this. |
| Predecessor 100339 scoreboard | `provider-min3-20260430-0459` = claude-1/2/3 retried (`.rerun.log`) and still 🟥; codex-1/2/3 stalled no-rerun | Same root cause as J3 (re-fire) and the codex-cli 0.124.0 stdin-hang ([#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)). |
| `Bash pgrep -af` for live PIDs | Permission-blocked at tool layer for this lane invocation | I can NOT directly count alive PIDs from this lane; cite by name only per H6 in-flight-sibling contract. Predecessor 145633 (~30 min before my synthesis) measured 111 autofeed PIDs across 6 distinct runs and 46 codex zombies. |

## Non-consuming stall signature catalog — N9–N13

(Numbered to avoid collision with predecessor `S9–S16` from 145633.)

| # | Signature | Observable via | Currently consumed by | Coverage gap |
|---|---|---|---|---|
| N9 | Lane wrapper alive >2× per-lane timeout (`timeout 7200`) | `pgrep -af '<lane-name>'` matched against `--make_and_launch.sh` start time | (none — H2 caps run-density, not per-lane lifetime) | No detector for "wrapper has been alive 4+ h beyond `timeout`"; orchestrator does not reap |
| N10 | Provider activity stall vs quota headroom mismatch | `config/ai-tools/provider-utilization-weekly.json` → `<provider>.<W>.last_ts` vs `quota_utilization_pct` | (none — scorecard `recommendations[].actions` advises but does not block) | Scorecard recommends "route bounded work to codex" while codex has been silent ≥48h; no dispatch suppression rule fires |
| N11 | Cross-tick re-fire of same lane family | Glob over `agent-logs/*/prompts/<family-prefix>*.md` for last 24h | (none — H1 detects rule-drift, not lane re-fire) | Same lane name re-dispatched ≥3 times in 24h with prior 🟥 outcomes signals stall-source-not-fixed |
| N12 | Stale-tick recovery-write provenance | First tool call timestamp vs run-id timestamp parsed from path | (none — H8c records `started_utc` but doesn't classify skew) | Lane that runs 5h late should be `recovery-write` not `fresh-write`; consumers may treat both equally |
| N13 | Tick-cascade — % of lanes in same tick that finished 🟥 | Glob `agent-logs/<run>/results/*.md` size + content sniff per H3 | (none — H4 budgets, doesn't shape-detect cascade) | When ≥60% of a tick's lanes return probe-stub or `started-only`, the next tick should pause and surface to operator |

## J-series — bounded autofeed rules (each with embedded dedupe + unsafe-transition gate)

### J1 — Lane-runtime-vs-timeout zombie detector (consumes N9; refines G4)

| Field | Value |
|---|---|
| **Precondition** | Dispatcher about to start a new autofeed run, OR scoreboard about to render. |
| **Check** | For each alive `pgrep -af 'provider-autofeed'` PID, derive lane start-time from `/proc/<pid>/stat` field 22 (or `ps -o lstart`). If `(now - start) > 2 * LANE_TIMEOUT_SECONDS` (default `LANE_TIMEOUT_SECONDS=7200` ⇒ trigger at 4h), emit `LANE-ZOMBIE: pid=<p>, lane=<n>, age=<h>h, expected_max=<2h>`. |
| **Action when matched** | Surface to operator. Do NOT auto-kill — composes with G3 (operator-owned). The lane's eventual result file (if it ever writes) MUST be classified `recovery-write` per J4. |
| **Built-in dedupe** | One zombie emission per `(pid, hourly-bucket)`. Same PID still alive next hour increments age but does not duplicate row. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane sending SIGKILL/SIGTERM to peer PIDs to "free" budget (composes with G3 — operator-owned reaping). **Forbidden:** the lane mutating `make_and_launch.sh` to extend `timeout` per its own benefit (wrapper-owned). **Forbidden:** counting a zombie's eventual result as `fresh-write` (composes with J4). |
| **No-op clause** | All alive PIDs younger than `2 * LANE_TIMEOUT_SECONDS`. |
| **Citation** | This lane — wrapper dispatched ~10:22Z (run-id `102247`), first tool call 15:29Z = ~5h skew = ~2.5× timeout. Predecessor 100339 scoreboard documented `provider-autofeed-20260430T094906Z` 5 lanes alive ~5h with 0 results. |
| **Retire when** | Wrapper enforces `timeout` natively at SIGKILL with reaping (currently the `timeout` shell builtin does SIGTERM at deadline; Claude wrappers can ignore SIGTERM mid-streaming). |
| **Bound** | One `pgrep` + one `/proc/<pid>/stat` field-22 read per alive PID. |

### J2 — Provider activity-stall guard (consumes N10)

| Field | Value |
|---|---|
| **Precondition** | Dispatcher about to allocate a lane to provider P. |
| **Check** | Read `config/ai-tools/provider-utilization-weekly.json`. For provider P, current week W, compute `staleness_hours = (now - last_ts)`. If `staleness_hours > 24` AND `quota_utilization_pct < 50` (vast headroom but provider is silent), emit `PROVIDER-STALLED: provider=<P>, last_ts=<ts>, staleness_h=<h>, quota_pct=<q>`. |
| **Action when matched** | **Suppress** dispatch of P-typed lanes for the current tick. Document suppression in tick manifest. Operator owns the unsuppression (e.g., when codex 0.124.0 regression resolves per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479), or when dispatcher confirms a successful test invocation against P). |
| **Built-in dedupe** | One `PROVIDER-STALLED` emission per `(provider, daily-bucket)`. Within a single dispatch decision, one emission per provider regardless of how many lanes were planned for it. |
| **Built-in unsafe-transition gate** | **Forbidden:** auto-rewriting `recommendations[].priority` to "lowest" (the scorecard is read-only telemetry). **Forbidden:** synthetically generating activity (e.g., dispatching a no-op canary lane just to refresh `last_ts`) — the activity counter must reflect real work. **Forbidden:** consuming `last_ts` from a stale snapshot (always re-derive from `/home/vamsee/.agent-usage/weekly-log.jsonl` or fresh `agent-quota-latest.json` if available). |
| **No-op clause** | Provider's `last_ts` within 24h, OR `quota_utilization_pct >= 50` (provider is just busy elsewhere). |
| **Citation** | This tick — codex `last_ts = 2026-04-28T06:15Z`, staleness_h ≈ 56h, quota = 0.4%. Tick still dispatched 3 codex lanes; predecessor 145633 noted same pattern with 46 codex zombies alive. |
| **Retire when** | Scorecard `recommendations[]` includes a machine-readable `dispatch_suppressed: true` field that the dispatcher honors. |
| **Bound** | One JSON parse per dispatch decision. |

### J3 — Cross-tick re-fire detector for same-named lanes (consumes N11)

| Field | Value |
|---|---|
| **Precondition** | Dispatcher about to dispatch lane L into run R. |
| **Check** | `Glob agent-logs/*/prompts/<L-family>*.md` for the last 24h. For each prior dispatch of L's family, classify outcome via H3 (probe-stub / started-only / delivered). If `count(prior dispatches with outcome != delivered) >= 3`, emit `LANE-RE-FIRE: family=<F>, attempts_24h=<n>, last_outcome=<o>`. |
| **Action when matched** | Surface to operator. Suppress THIS dispatch unless operator marker `.planning/lane-refire-approved/<family>.md` exists. The marker expires 24h after creation. |
| **Built-in dedupe** | One `LANE-RE-FIRE` emission per `(family, 24h-window)`. Once surfaced, same family does not re-emit until window rolls. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane creating its own re-fire-approved marker (operator-owned per `feedback_never_offer_to_self_label_plan_approved.md`'s spirit; user-in-loop gate). **Forbidden:** renaming the lane to dodge family detection (composes with R5/D1 — lane-name + prompt-hash dedupe). **Forbidden:** auto-inferring "successful" from probe-stub presence (composes with H3 classification). |
| **No-op clause** | < 3 prior 24h failed dispatches, OR all prior dispatches delivered. |
| **Citation** | `claude-3-governance-autofeed` (provider-min3-20260430-0459 🟥), `claude-3-governance-recovery-contract` (100339 ✅), `claude-governance-recovery-3` (125920 ✅), `claude-governance-loop-rules-3` (145633 ✅), `claude-governance-autofeed-rules-3` (102247, this) — 5 dispatches in <24h of same family; 1 outright 🟥, 4 succeeded with substantive overlap. Re-fire is functioning here but is masking the fact that no consumer of these governance docs exists (per H1 rule-drift). |
| **Retire when** | Dispatcher reads prior outcomes before dispatching, AND H1 rule-drift detector lands AND surfaces non-consumption to operators (then re-firing the same family is provably useful or provably wasteful). |
| **Bound** | One Glob over `agent-logs/*/prompts/` + one H3 classification per prior hit. |

### J4 — Recovery-write provenance contract (consumes N12; refines H8c)

| Field | Value |
|---|---|
| **Precondition** | A lane is about to write its canonical fallback artifact under `docs/sessions/` per H8b. |
| **Check** | Compare `started_utc` (first tool call timestamp) with the run-id timestamp parsed from prescribed path: `provider-autofeed-YYYYMMDD-HHMMSS`. If `(started_utc - run_id_dispatch_ts) > 2 * LANE_TIMEOUT_SECONDS`, classify as `recovery-write`. |
| **Action when matched** | Add to H8c `.lane-state.json`: `"write_classification": "recovery-write"`, `"dispatch_to_execute_skew_seconds": <int>`. Add a `## Recovery-write notice` block at top of artifact body explaining the skew. |
| **Built-in dedupe** | Per-artifact: one classification field. Recovery-write artifacts are NOT counted toward "fresh tick yield" by H1 / scoreboard renderers. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane back-dating `started_utc` to mask skew (this would defeat downstream stall analytics; composes with U6 invariant of honest provenance). **Forbidden:** the lane writing the artifact under a non-canonical name (e.g., adding a `-recovery` suffix) — H8b canonical naming holds; the classification belongs in metadata, not filename. **Forbidden:** suppressing the recovery-write notice block "to keep the doc clean" — operators rely on the notice for triage. |
| **No-op clause** | `started_utc` within `2 * LANE_TIMEOUT_SECONDS` of run-id dispatch ts. |
| **Citation** | This lane — run-id `102247` parses to dispatch ~10:22Z; `started_utc = 2026-04-30T15:29:09Z`; skew ≈ 18,500s ≈ 5h ≈ 2.6× `LANE_TIMEOUT_SECONDS`. ⇒ `write_classification: "recovery-write"`. |
| **Retire when** | Wrapper enforces `timeout` at SIGKILL AND reaps the wrapper before its replacement dispatches (then 5h-late writes structurally cannot happen). |
| **Bound** | Two timestamp parses + one subtract per finalize. |

### J5 — Tick-cascade detector (consumes N13; refines H4)

| Field | Value |
|---|---|
| **Precondition** | Dispatcher about to start a new autofeed run R+1, AND prior run R has been alive ≥ `LANE_TIMEOUT_SECONDS`. |
| **Check** | For run R: `Glob agent-logs/<R>/results/*.md` and apply H3 classification. Compute `cascade_pct = count(probe-stub OR started-only OR died-empty) / total_lanes`. If `cascade_pct >= 60`, emit `TICK-CASCADE: run=<R>, cascade_pct=<p>, n_lanes=<n>`. |
| **Action when matched** | **Hold** R+1 for `2 * LANE_TIMEOUT_SECONDS` (default 4h). Surface cascade evidence to operator. After hold expires, operator must clear with `.planning/cascade-clear/<R>.md` marker before R+1 fires. |
| **Built-in dedupe** | One cascade emission per `(prior-run-id)`. R+2 / R+3 inherit the hold until operator clears R explicitly. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane writing its own cascade-clear marker (operator-owned). **Forbidden:** the lane clearing prior cascades en-bloc (composes with U2 — dual approval). **Forbidden:** auto-counting a `recovery-write` (per J4) toward "delivered" — recovery writes prove a hung lane eventually finalized, NOT that the cascade resolved. |
| **No-op clause** | `cascade_pct < 60`, OR prior run R is younger than `LANE_TIMEOUT_SECONDS` (R may still finalize). |
| **Citation** | Predecessor 100339 scoreboard documented `provider-autofeed-20260430T094906Z` (5 lanes / 0 delivered = 100% cascade), `provider-recovery-20260430-0445` (5 lanes / 0 delivered = 100% cascade), `nightly-20260430-more-lanes-0431` (5 lanes / 0 delivered = 100% cascade). Each followed by another tick within minutes. **Cascade-pause was authored zero times.** |
| **Retire when** | Dispatcher tracks tick outcomes natively AND auto-pauses on cascade signal AND the operator-marker workflow is wired. |
| **Bound** | One Glob + one H3 classification per lane in the prior run. |

## Rule precedence — J-series interaction with R/D/U/W/G/H

Insert into the existing precedence chain at these positions. Earlier rules win and short-circuit later ones.

1. **U6** (self-label invariant) — unchanged. Always first.
2. **U2** (dual approval gate) — unchanged.
3. **G1** (Hermes-active dispatch suppression) — unchanged.
4. **J5** (tick-cascade detector) — **NEW; fires first at dispatcher-start** because if the prior tick cascaded, no per-lane decisions matter. Composes with G1 (Hermes can ALSO hold; either blocks dispatch).
5. **H2** (run-ID density cap) — unchanged.
6. **J2** (provider activity-stall guard) — **NEW; fires next at per-provider allocation** before any per-lane gate. If P is suppressed, lanes destined for P are skipped before the per-lane chain runs.
7. **J3** (cross-tick re-fire detector) — **NEW; fires at per-lane dispatch** before R5/D1. Re-fire suppression dominates lane-name dedupe.
8. **H1** (rule-drift detector) — unchanged. Fires at scoreboard render and at governance-lane authoring.
9. R5 → D1 → D3 → R2 → U3 → R1/R9 — unchanged.
10. **G4** (codex zombie aggregator) → **H7** (codex overwrite protection) — unchanged.
11. **J1** (lane-runtime zombie detector) — **NEW; fires immediately after G4** at scoreboard render (or whenever dispatcher considers reaping). G4 counts codex zombies; J1 counts ANY long-runtime lane. Both must surface.
12. **G5** (provider-mix structural-inversion gate) — unchanged.
13. D2 → R3/R10 → U8 → R4 — unchanged.
14. **H6** (in-flight sibling content dependency) — unchanged.
15. G2 → G3 — unchanged.
16. **H4** (aggregate-budget visibility) — unchanged.
17. R8 → R6 → U4 → R7 — unchanged.
18. **H3** (write-probe stub disambiguation) → U5 → G6 → D4 → U7 — unchanged.
19. **H8** (path conventions manifest) — unchanged.
20. **J4** (recovery-write provenance contract) — **NEW; fires inside the H8 finalize-write step** when J1's age-threshold matched at the time `started_utc` was recorded. J4 is a refinement of H8c, NOT a replacement.
21. **H5** (rule-set retirement scanner) — unchanged.
22. **G7** (plan past-tense drift) → **G8** (sustained-MAJOR loop consensus) — unchanged.
23. D5 → U9 — unchanged.

## What this lane explicitly does NOT do

- ✗ Does **not** label any GitHub issue with `status:plan-approved` (U6). No `gh` mutation calls executed.
- ✗ Does **not** open any GitHub issue, PR, or post a comment (U9 + D5). Suggested prompts below name issue drafts; issue creation is operator-owned.
- ✗ Does **not** edit `classify_and_launch.sh`, `run_tick.sh`, `relaunch_replacements.sh`, `launch_replacements.sh`, `make_and_launch.sh`, or any provider wrapper.
- ✗ Does **not** modify `submit-to-codex.sh` or `submit-to-gemini.sh`.
- ✗ Does **not** create a worktree (no source edits attempted).
- ✗ Does **not** kill any process (J1/J5 surface operator-only actions per G3 composition).
- ✗ Does **not** copy this artifact to the prescribed `agent-logs/` path (orchestrator-owned per U3).
- ✗ Does **not** retire any prior rule (H5 ownership; J5/J1 do not redefine R/D/U/W/G/H members).
- ✗ Does **not** redefine any rule in R1–R10, D1–D5, U1–U9, W1–W5, G1–G8, H1–H8 (D3 honored; fresh prefix `J`; precedence list extends, not rewrites).
- ✗ Does **not** mutate `.claude/state/`, `.planning/plan-approved/`, or any memory feedback file.
- ✗ Does **not** consume sibling lane content (H6 self-honoring; sibling outputs cited by name only).
- ✗ Does **not** write to `agent-logs/.../state/<lane>.json` directly (H8c self-honoring; embedded JSON below).
- ✗ Does **not** create `.planning/cascade-clear/<run>.md`, `.planning/lane-refire-approved/<family>.md`, or any other operator marker (J3/J5 explicitly defer to operator).
- ✗ Does **not** re-derive `last_ts` from `weekly-log.jsonl` directly (sandbox-blocked); cited the JSON snapshot at hand and noted the canonical source for J2's retire-when path.

## Suggested next-tick prompts (one at a time; do NOT chain)

Predecessor lanes shipped Prompts A–N (recovery-governance-1 + governance-loop-3), O–T (recovery-scoreboard-1 + control-synthesis-1), U–X (governance-recovery-3), Y/Z/AA/BB (governance-loop-rules-3). The J-series implies these new prompts. **Strongest single recommendation: Prompt CC** — J5 (tick-cascade detector) closes today's loudest visible failure mode (the morning's three back-to-back 100% cascades).

### Prompt CC — Land J5 (tick-cascade detector) as a dispatcher pre-start check

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: tick-cascade-detector-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/tick-cascade-detector-plan-1.md (fallback `docs/sessions/...` per H8b)
> Hard gates: do not destructively reset/clean; isolated worktrees; no outreach; no self-approval; no `status:plan-approved` changes; no unapproved implementation; `GIT_OPTIONAL_LOCKS=0`; redact secrets. **Planning only.**
> Task: Read J5 in `docs/sessions/2026-04-30-provider-autofeed-102247-claude-governance-autofeed-rules-3.md` and H3 in `docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md`. Spec a script `scripts/enforcement/check-autofeed-tick-cascade.sh` callable from the dispatcher pre-start path. Inputs: prior run-id; output: cascade verdict + `TICK-CASCADE: ...` line. Reuse H3 size/content classifier as a library function (do NOT reimplement). Map to enforcement-gradient L2 per `.claude/rules/patterns.md`; promote to L3 (pre-dispatch hook) once a per-tick outcome ledger lands. Wire the operator marker `.planning/cascade-clear/<run>.md` and document expiration semantics. Do NOT modify the dispatcher itself in this lane. Exit: 1-page plan + GitHub issue draft (do NOT open the issue).

### Prompt DD — Land J2 (provider activity-stall guard) as a dispatcher allocation check

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: provider-stall-guard-plan-1
> Result file: per H8b canonical naming.
> Hard gates: same as Prompt CC.
> Task: Read J2 in this lane plus the provider-routing-scorecard.json + provider-utilization-weekly.json schemas. Spec a script `scripts/enforcement/check-provider-stall.sh` taking `--provider <P>` and reading the latest `last_ts` and quota figures. Output: `PROVIDER-STALLED` line OR exit 0 silently. Reference [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) (codex 0.124.0 stdin-hang) as the active retire-when blocker for codex specifically. Spec the `dispatch_suppressed` field promotion path on `recommendations[]`. Exit: 1-page plan + diff sketch for `provider-routing-scorecard.json` schema bump.

### Prompt EE — Land J1 + J4 as a paired observability bundle

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: lane-runtime-observer-plan-1
> Result file: per H8b canonical naming.
> Hard gates: same as Prompt CC.
> Task: Read J1 + J4 in this lane and H8c (`.lane-state.json` schema) in 145633. Spec a wrapper-side helper that records lane start-time + run-id-dispatch-time skew into the embedded JSON block at finalize. Reuse `LANE_TIMEOUT_SECONDS` from the top-level governance contract. Spec a scoreboard renderer that distinguishes `recovery-write` (J4) from `fresh-write` and surfaces `LANE-ZOMBIE` rows (J1) at the top. Map to L2; promote J1 to L3 (auto-emit at scoreboard render) when the `.lane-state.json` lands as a versioned spec per Prompt Z. Exit: 1-page plan.

### Prompt FF — Operator-host action: clear today's cascade backlog

> **Owner:** operator on dispatcher host (NOT a lane).
> **Action:** Read J5 in this lane. Decide whether to retroactively pause the dispatcher (per J5's hold semantics) given today's 3+ recorded 100%-cascade ticks (`provider-autofeed-20260430T094906Z`, `provider-recovery-20260430-0445`, `nightly-20260430-more-lanes-0431` per 100339 evidence). If pausing, write `.planning/cron-stop.flag` and document reason in `docs/governance/autofeed-cascade-pause.md`. **Hard gate:** none (host-local, no GitHub mutation).

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`. No git mutations attempted.
- ✓ `GIT_OPTIONAL_LOCKS=0` honored — read-only `Bash` only (one `date -u` call succeeded; `pgrep`/`mkdir` required permission and were declined when not auto-allowed).
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; no comments; no labels).
- ✓ No outreach drafts.
- ✓ No `status:plan-approved` label changes (U6 satisfied).
- ✓ No `.planning/plan-approved/<issue>.md` markers written or removed.
- ✓ No source-file edits; no isolated worktree created.
- ✓ No secrets emitted.
- ✓ No mutation of `.claude/state/` or any memory feedback file.
- ✓ U3 satisfied: this lane's `.lane-state.json` (when written by the wrapper) should match the embedded JSON in §.lane-state.json below.
- ✓ D3 satisfied: extends prior R/D/U/W/G/H with new `J` prefix; does not redefine any prior rule.
- ✓ D4 + G6 satisfied: single canonical artifact at `docs/sessions/2026-04-30-provider-autofeed-102247-claude-governance-autofeed-rules-3.md` (no `-FALLBACK`/`-result` suffix).
- ✓ U2 satisfied: planning/specification only. J-rules are *prescriptive specs*; landing them requires Prompts CC/DD/EE (planning) plus user approval.
- ✓ U9 satisfied: Prompts CC/DD/EE reference GitHub issue drafts but issue creation is operator-owned.
- ✓ G1 self-honoring: no dispatch, no commit; only emitted a session-note artifact.
- ✓ H6 self-honoring: cited siblings by name + Glob-presence only; did NOT consume sibling content (sandbox-blocked from `agent-logs/`).
- ✓ H8 self-honoring: embedded `.lane-state.json` per H8c; included `Log:` back-pointer per H8d in the .lane-state.json `log_path_prescribed`; included `## Provenance` per H8e (below).
- ✓ J4 self-honoring: classified own write as `recovery-write` (~5h skew); added recovery-write classification to embedded JSON; cited skew in metadata header.
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md` (recurrence #9), `feedback_codex_cli_0_124_upstream_regression.md` (J2 retire-when, [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)), `feedback_check_parallel_work.md` (predecessor scan satisfied via `ls docs/sessions/`), `feedback_never_offer_to_self_label_plan_approved.md` (U6 + J3 marker semantics), `feedback_inline_gh_issue_url.md` (issue refs hyperlinked), `feedback_hermes_active_preflight_check.md` (G1 composition), `project_issue_2460_approval_binding.md` (U2 backbone), `feedback_plan_past_tense_artifact_claims.md` (J-series uses future tense for unmerged spec landing).

## .lane-state.json (H8c — embedded for orchestrator pickup)

```json
{
  "lane_name": "claude-governance-autofeed-rules-3",
  "run_id": "provider-autofeed-20260430-102247",
  "status": "completed-fallback",
  "result_path_actual": "docs/sessions/2026-04-30-provider-autofeed-102247-claude-governance-autofeed-rules-3.md",
  "result_path_prescribed": "/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/results/claude-governance-autofeed-rules-3.md",
  "log_path_prescribed": "/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/logs/claude-governance-autofeed-rules-3.log",
  "started_utc": "2026-04-30T15:29:09Z",
  "finished_utc": "2026-04-30T15:35:00Z",
  "run_id_dispatch_ts_inferred": "2026-04-30T10:22:47Z",
  "dispatch_to_execute_skew_seconds": 18382,
  "write_classification": "recovery-write",
  "predecessors_in_run": [
    "claude-control-plane-synthesis-1",
    "claude-plan-review-hardening-2",
    "codex-approved-eligibility-scout-1",
    "codex-test-readiness-scout-2",
    "codex-worktree-hygiene-salvage-3",
    "gemini-research-queue-expansion-1",
    "gemini-gtm-legal-risk-2",
    "gemini-standards-source-recon-3"
  ],
  "predecessors_cross_run": [
    "docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md",
    "docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md",
    "docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md",
    "docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md",
    "docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md",
    "docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md",
    "docs/sessions/2026-04-30-provider-autofeed-125920-claude-control-synthesis-1.md",
    "docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md",
    "docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md"
  ],
  "rules_authored": ["J1", "J2", "J3", "J4", "J5"],
  "rules_cited_only": [
    "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10",
    "D1", "D2", "D3", "D4", "D5",
    "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9",
    "W1", "W2", "W3", "W4", "W5",
    "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8",
    "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"
  ],
  "awaiting_orchestrator_copy": true,
  "env_mismatch_recurrence_count_24h": 9,
  "next_recommended_prompt": "CC"
}
```

## Evidence appendix — what backed every J-rule

| J-rule | Backing evidence |
|---|---|
| J1 | This lane's own dispatch-vs-execution skew: ~10:22Z dispatch, 15:29Z first tool call ⇒ ~5h ≈ 2.6× `LANE_TIMEOUT_SECONDS=7200`. Predecessor 100339 documented `provider-autofeed-20260430T094906Z` 5 lanes alive >5h with 0 results. |
| J2 | `provider-utilization-weekly.json` W18: codex `last_ts = 2026-04-28T06:15Z` (>56h stale) at quota_pct = 0.4%; gemini `last_ts = 2026-04-29T07:03Z` (~32h) at quota_pct = 0.0%. `provider-routing-scorecard.json` recommends "route to codex" while codex is silent. |
| J3 | `claude-3-governance-autofeed` (provider-min3-20260430-0459 🟥), `claude-3-governance-recovery-contract` (100339 ✅), `claude-governance-recovery-3` (125920 ✅), `claude-governance-loop-rules-3` (145633 ✅), `claude-governance-autofeed-rules-3` (102247, this) — 5 dispatches in <24h of same governance family. |
| J4 | This lane self-evidences: `started_utc = 2026-04-30T15:29:09Z`, `run_id_dispatch_ts_inferred = 2026-04-30T10:22:47Z`, skew = 18,382s ≈ 5.1h. |
| J5 | Predecessor 100339 enumerated three back-to-back 100%-cascade runs from this morning: `provider-autofeed-20260430T094906Z` (5/0), `provider-recovery-20260430-0445` (5/0), `nightly-20260430-more-lanes-0431` (5/0). Subsequent ticks fired regardless. |

## Provenance (H8e — required block)

| Source | Output captured |
|---|---|
| `Glob /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/**` | 9 prompt files, 9 result files (probe-stubs, write-blocked from this lane), 6 log files, 6 pid files, plus 3 `-lite` gemini result/prompt/log files |
| `Bash date -u +%FT%TZ` | `2026-04-30T15:29:09Z` |
| `Bash ls docs/sessions/ \| grep -E "2026-04-30.*(governance\|autofeed\|recovery\|stale\|stream)"` | 13 session-note artifacts across runs 073439, 100339, 111336, 114355, 125920, 145633 |
| `Bash ls docs/sessions/ \| grep 102247` | (empty — confirmed no prior fallback artifact for this run) |
| `Read config/ai-tools/provider-routing-scorecard.json` | Recommendations + per-provider stale-state evidence |
| `Read config/ai-tools/provider-utilization-weekly.json` | W18 last_ts and quota_utilization figures for codex/gemini/claude/hermes |
| `Read docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md` | H1–H8 source — precedent rules, embedded JSON schema, prompts Y/Z/AA/BB |
| `Read docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` | Tick-cascade evidence — 3 morning runs at 100% cascade |
| `Read docs/sessions/2026-04-30-claude-stream-plan-hardening-3-result.md` | Cross-cited memory + producer-precondition contract |
| `Read /mnt/local-analysis/agent-logs/.../prompts/<lane>.md` | DENIED — sandbox-blocked at tool layer; consistent with predecessor 145633's verified-blocked behavior |
| `Bash pgrep -af 'provider-autofeed'` | Permission-blocked at tool layer for this invocation; cited predecessor 145633 measurements (111 PIDs / 6 distinct run-IDs / 46 codex zombies as of ~14:58Z) |
| Memory consulted | `feedback_lane_result_path_outside_sandbox` (H8b fallback contract, recurrence count), `feedback_codex_cli_0_124_upstream_regression` ([#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — J2 retire-when), `feedback_check_parallel_work` (predecessor scan), `feedback_never_offer_to_self_label_plan_approved` (U6 + J3 marker), `feedback_inline_gh_issue_url` (Markdown hyperlink format), `feedback_hermes_active_preflight_check` (G1 composition), `feedback_codex_sustained_major_loop` (G8 cited), `feedback_plan_past_tense_artifact_claims` (J-series uses future tense for spec-landing), `project_issue_2460_approval_binding` (U2 backbone), `feedback_attestation_enables_contradiction_detection` (J1+J4 pair enable rule-vs-state contradiction detection) |

No log/prompt body was read from `agent-logs/` (sandbox-blocked at tool layer for this session — verified at lane start). All evidence is from: (a) `Bash date -u` + `ls`/`grep` over `docs/sessions/`, (b) `Read` of predecessor session artifacts inside `docs/sessions/` and `config/ai-tools/`, (c) `Glob` enumeration of `agent-logs/**` (allowed for path metadata only), (d) cited memory feedback files.

## Strongest single follow-up

**Prompt CC** (land J5 as dispatcher pre-start cascade detector). Today's morning had three back-to-back 100%-cascade ticks; the dispatcher fired the next tick anyway, each time. Without J5, every governance/recovery rule we author is solving a downstream symptom of the same pre-tick bypass. J5 is the highest-leverage observable rule because the cascade signal is already visible from path metadata (no body reads, no PID inference) — the L2 script can be ~30 lines.
