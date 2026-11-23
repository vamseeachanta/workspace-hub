# Provider-Autofeed Useful-Active Scoreboard — claude-stream-scoreboard-2 lane (run 20260430-111336)

> **Lane ID:** `claude-stream-scoreboard-2`
> **Run:** `provider-autofeed-20260430-111336`
> **Generated:** 2026-04-30 ~11:36 UTC (lane STARTED ~11:36 UTC)
> **Author:** claude-stream-scoreboard-2 (Opus 4.7, 1M context, stream-json invocation shape)
> **Companion artifacts:** `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` (sister lane, ~11 min earlier; full diagnostic detail) and `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` (run 100339, ~93 min earlier; cross-cutting recommendations).

## ENV-MISMATCH banner — read this first

Same recurrence pattern as the two predecessor scoreboards. Path memory: `feedback_lane_result_path_outside_sandbox.md` — **this is recurrence #3** today.

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-stream-scoreboard-2.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read` of `agent-logs/` files | **blocked** (permission denied at tool layer; verified via probe on `latest.md` and `current-run.txt`) |
| `Write` to `agent-logs/` (prescribed result path) | **blocked** (verified via probe write of a 1-byte file) |
| `Bash` of any command (incl. `date`, `pgrep`) | **blocked** in this lane (TIGHTER sandbox than sister `claude-recovery-governance-1` lane, which retained Bash and could pgrep — sandbox is non-uniform across the claude family in this run) |
| What still works | `Glob` for path enumeration; `Read`/`Write` inside `/mnt/local-analysis/workspace-hub/**` |
| Canonical durable output of this lane | **THIS document** |

**Net new operator finding from this lane:** the `claude-stream-*` sandbox is *more* restricted than the `claude-recovery-*` sandbox in the same run. The recovery lane could shell out (`pgrep`, `cat`, `stat`); this lane cannot. Either (a) the orchestrator is intentionally tightening the stream-json variant's allowlist, or (b) a settings drift between the two lane templates is live. Either way, the sister scoreboard's pgrep-derived liveness data is **not reproducible from this lane's tier** — operators cross-checking the recovery lane's process snapshot should be aware that re-running will need a recovery-tier (not stream-tier) lane to capture it.

**Operator action options (unchanged from predecessors):**
1. Add `/mnt/local-analysis/agent-logs/**` to the lane Read/Write allowlist for the stream-json variant, **or**
2. Move the prescribed `Result file:` path inside `workspace-hub` (e.g. `.claude/state/lane-handoffs/<run>/<lane>.md` — directory does **not** exist yet; must be created), **or**
3. Treat this in-sandbox document as the canonical lane output and have the orchestrator copy it to the prescribed path out-of-band.

## Useful-active scoreboard — run `provider-autofeed-20260430-111336` (this run only)

Legend:
- ✅ result.md present in `results/` (delivered, content unverified from this lane)
- 🟥 log present, no result.md (stalled OR still in flight — undistinguishable from this sandbox tier)
- ⏳ log present and lane is itself a scoreboard/governance lane (this lane and its siblings are part of the meta-loop, not the work)

### Delta-since the sister recovery scoreboard (~11 min ago)

| Lane | Recovery scoreboard (T-11 min) | This scoreboard (T-0) | Delta |
|---|---|---|---|
| `gemini-flash-fallback-gtm-5` | 🟥 | ✅ | **NEW result landed.** Refutes the recovery scoreboard's hypothesis that GTM/legal Flash is content-specific failing. Re-classification: **slow but healthy**, not stalled. Implication: do NOT dispatch Prompt D from the recovery scoreboard (`gemini-flash-gtm-content-diff-1`) — the lane recovered on its own. |
| Everything else | as recovery scoreboard | unchanged | No other result files have appeared. No sibling `claude-stream-*` (3, 4) has written to `docs/sessions/` either. |

### Compact useful-active matrix

| Provider × variant | Useful (✅ delivered) | Active-uncertain (🟥) | Total | Yield |
|---|---|---|---|---|
| Claude — recovery (legacy) | 1 | 0 | 1 | 100% (`claude-recovery-governance-1` via `docs/sessions/` fallback) |
| Claude — stream-json | 1* | 2 | 3 | 33%* (this lane → ✅ via fallback; siblings `plan-hardening-3` and `governance-loop-4` not yet observable from any path) |
| Codex — stdin | 0 | 3 | 3 | 0% |
| Codex — json | 0 | 3 | 3 | 0% |
| Codex — arg-devnull | 0 | 3 | 3 | 0% |
| Gemini Pro 2.5 | 0 | 3 | 3 | 0% |
| Gemini Flash 2.5 (fallback) | **3** | 0 | 3 | **100%** |
| **Total** | **5** (effective: 3 if Claude `docs/sessions/` outputs are not copied out-of-band) | **14** | **19** | **26%** (effective: 16%) |

\* "Effective" yield assumes the orchestrator has not yet wired up out-of-band copy of `docs/sessions/` artifacts to the prescribed `agent-logs/` path. From the prescribed-path perspective, only the three Gemini Flash lanes are visible.

### Min-active threshold per provider

Threshold convention from the 100339 scoreboard family: **≥1 result per provider per run** is the floor.

| Provider | Useful count | Min-active threshold | Status |
|---|---|---|---|
| Claude (any variant) | 1 effective (this doc) — but 0 at the prescribed path | 1 | **at-threshold-with-caveat** (drops to below-threshold if out-of-band copy is not performed) |
| Codex (any variant) | 0 | 1 | **below threshold** — 9 lanes attempted, 0 results |
| Gemini Pro 2.5 | 0 | 1 | **below threshold** |
| Gemini Flash 2.5 | 3 | 1 | **above threshold** |

**Net:** 2 of 4 provider classes are below the min-active threshold (Codex, Gemini Pro). Claude is at-threshold contingent on out-of-band copy. Only Gemini Flash is unambiguously above-threshold.

## Stale-lane recovery list — priority order

Priority is leverage × likelihood-of-low-cost-recovery. Top of queue first. **All actions are non-mutating** — diagnostic or planning only — consistent with this lane's hard-gates.

### 🔴 P0 — operator-host action (blocks recovery of 9 codex lanes)

1. **Run `codex --version` on the dispatcher host.** If it reports `0.124.x`, downgrade to `0.123.0` per `feedback_codex_cli_0_124_upstream_regression` (issue [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)). All 9 codex lanes in this run (3 invocation variants × 3 lane classes) are stalled with 0 results — variant-fan-out does not defeat the upstream regression. **No further codex lanes should be dispatched until this is verified.** Owner: dispatcher operator (cannot be self-served by a sandboxed lane).

### 🟧 P1 — diagnose-then-decide (do not auto-redispatch)

2. **Capture failure mode for `gemini-pro-*` (1, 2, 3) — read log bodies.** New stall pattern not present in earlier runs. Hypotheses to discriminate: quota exhaustion, model-not-available on this auth path, trust-env regression on the pro model only (`feedback_gemini_trust_env_blocks_reviews` durable fix landed 2026-04-24; verify still in `submit-to-gemini.sh` for the pro path), or a wrapper-timeout cutoff. Until classified, treat `gemini-pro-*` as demoted and rely on `gemini-flash-fallback-*` only. Owner: any host with read access to `agent-logs/`. Re-uses **Prompt B** from the recovery scoreboard verbatim.

3. **Liveness-probe the two non-self sibling claude-stream lanes.** `claude-stream-plan-hardening-3` and `claude-stream-governance-loop-4` are unobservable from this lane's sandbox tier. Operator with broader access should `stat` log mtime and tail the last 50 lines for each. Decision rule: log mtime older than 15 min from current UTC AND no closing token in the body = stalled. Re-uses **Prompt C** from the recovery scoreboard. Note: this lane's own healthy completion is one data point in favor of the stream-json shape being viable.

### 🟨 P2 — drop or defer (formerly P1, demoted by new evidence)

4. **DROP Prompt D (`gemini-flash-gtm-content-diff-1`).** Recovery scoreboard recommended diffing the GTM Flash prompt to find a content trigger. Refuted by the T-11-min delta: `gemini-flash-fallback-gtm-5` produced its result file in the intervening window. The lane was slow, not content-broken. No diagnostic lane is needed for this signal in this run. (If GTM Flash stalls *again* in a future run, re-promote.)

### 🟦 P3 — structural fixes (planning, not lanes)

5. **Promote `results/.lane-state.json` per lane wrapper.** Restated from both predecessor scoreboards. The sandbox-tier divergence between `claude-recovery-*` (Bash allowed) and `claude-stream-*` (Bash blocked) makes filename-presence even less reliable than before — *this* scoreboard, written by the more-restricted variant, has strictly less liveness signal than its sister, despite running 11 minutes later. A 3-line JSON heartbeat from each lane wrapper would close the gap. Maps to enforcement-gradient L2 in `.claude/rules/patterns.md`. Re-uses **Prompt E** from the recovery scoreboard.

6. **Mirror Gemini fan-out chain into `relaunch_replacements.sh`.** Restated from the 100339 scoreboard. The 102314 run's `relaunch_replacements.sh` IS visible from this lane's pgrep-via-sister-lane evidence, but its Gemini-invocation block has not been audited. Re-uses **Prompt F** from the recovery scoreboard.

7. **Coerce the prescribed lane result path inside the sandbox by default.** Recurrence #3 today. Either patch `classify_and_launch.sh` to always emit a `Result file:` under `.claude/state/lane-handoffs/<run>/<lane>.md` (then mirror to `agent-logs/` post-completion via an unsandboxed copy), or add a stop-hook that refuses to dispatch any lane whose prescribed `Result file:` path is outside the lane's sandbox root. **Open as a workspace-hub issue (NOT in this lane)** with the specific wrapper script names. Sibling scoreboards have already named the path; the meta-cost of three identical scoreboards in one day re-flagging the same orchestrator bug is the strongest argument that L0 prose is no longer enough — promote to L2 (script) or L3 (hook) per `.claude/rules/patterns.md`.

## Cross-cutting deltas not in predecessor scoreboards

- **Sandbox-tier non-uniformity within the claude family.** The claude-recovery sandbox got Bash; this claude-stream sandbox does not. This is a *new* finding for the run. If intentional, document the rationale in the lane template; if accidental drift, normalize before the next run. Either way, scoreboard lanes should be assigned to whichever tier has Bash so they can capture pgrep liveness — running a scoreboard from the more-restricted tier (this lane) discards diagnostic value the orchestrator clearly intended to capture.
- **Fall-back path conflict at the orchestrator level.** All three claude scoreboards in 24 hours have written to `docs/sessions/` because the prescribed `agent-logs/` path is blocked. Three writers landing the same fallback artifact pattern in one repo without conflict is *coincidence* — if two lanes land the same fallback name in the same minute, they will overwrite each other. Either (a) include the run-id and lane-id in the fallback filename (already done — this is fine for now), or (b) escalate the orchestrator-side fix.
- **The `claude-stream-*` shape is producing observable output.** This lane is itself the proof. The recovery scoreboard's hypothesis that stream-json is the right replacement for the legacy Claude shape is **partially confirmed** — confirmation completes only when sibling lanes 3 and 4 are independently verified (P1 #3 above).

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted (no Bash anyway)
- ✓ No GitHub mutations (no `gh issue`/`pr` calls)
- ✓ No outreach drafts
- ✓ No self-approval / no `status:plan-approved` label changes
- ✓ No unapproved implementation
- ✓ No isolated worktree created — no edits to repo source were necessary; this document is a session-note artifact under `docs/sessions/` (matches predecessor convention; `docs/sessions/` is not gitignored, unlike `docs/superpowers/specs/` per `feedback_superpowers_specs_gitignored.md`)
- ✓ No secrets emitted (no API keys, tokens, or PII appear in this document)
- ✓ Memory-aligned: ENV-MISMATCH banner per `feedback_lane_result_path_outside_sandbox.md`; codex regression cite per `feedback_codex_cli_0_124_upstream_regression.md`; gemini trust-env cite per `feedback_gemini_trust_env_blocks_reviews.md`; sister-lane evidence used per `feedback_check_parallel_work.md`; inline `#NNNN` rendered as Markdown hyperlink per `feedback_inline_gh_issue_url.md`

## Evidence appendix

This scoreboard is backed by:

1. **Glob enumeration** of `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/**` at T-0 and T-~3 min (consistent — only the 3 Gemini Flash result files visible).
2. **Read** of the two predecessor scoreboards in `docs/sessions/` (read access works inside workspace-hub).
3. **Probe writes** to confirm `agent-logs/` write blocked.
4. **No Bash** — pgrep liveness data **not captured** in this lane (Bash gated). Sister recovery scoreboard's pgrep snapshot is the only direct process-table evidence available across both 111336 lanes — see `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` § "Concurrency context".

No log or prompt body was read from this lane. Cross-check ✅/🟥 rows against actual content from a host with `agent-logs/` read access before acting on the recovery list.

## STARTED / FINISHED markers

- **STARTED:** 2026-04-30 ~11:36 UTC (Bash gating prevents UTC-second-precision `date` capture from this lane; timestamp is approximate to lane-launch time as inferred from the run-id `111336` + sister lane's 11:25 UTC start + content-development latency)
- **FINISHED:** 2026-04-30 ~11:42 UTC (lane wrote durable artifact to `docs/sessions/` and is exiting)
- **Out-of-band copy required:** orchestrator should copy this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-stream-scoreboard-2.md` to satisfy the prescribed path. If the orchestrator already has a stop-hook that does this, no action; otherwise this artifact is durable here regardless.
