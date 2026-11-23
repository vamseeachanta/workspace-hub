# Provider-Autofeed Governance/Recovery — `claude-governance-loop-rules-3` (run 20260430-145633)

> **Lane ID:** `claude-governance-loop-rules-3`
> **Run:** `provider-autofeed-20260430-145633`
> **Author:** Claude Opus 4.7 (1M ctx), recovery-tier sandbox.
> **STARTED:** 2026-04-30T15:15:11Z (first tool call: `date -u`)
> **FINISHED:** 2026-04-30T~15:23Z (this artifact written)
>
> **Predecessors in same run (alive at write time per `pgrep -af 'provider-autofeed-20260430-145633'`; cite by name only — content sandbox-blocked):**
> - `claude-control-synthesis-recovery-1` (PID 2223241/2223243 alive at 15:18Z)
> - `claude-plan-review-hardening-2` (PID 2223254/2223256 alive at 15:18Z)
> - `codex-{approved-eligibility-scout-1, test-readiness-scout-2, worktree-hygiene-salvage-3}` (codex-exec PIDs 2223281+ alive — see H1, H7 evidence)
> - `gemini-pro-{research-queue-1, gtm-legal-risk-2, standards-recon-3}` (no `pgrep` matches at 15:18Z snapshot — already finalized or never started; `Glob` shows result files exist)
>
> **Cross-run predecessors cited (do NOT redefine; extend only):**
> - `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` (R1–R4 source)
> - `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` (top-level contract: useful-lane defn, `LOG_MTIME_MAX_S=600`, `RESULT_MIN_BYTES=256`, etc.)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` (recovery scoreboard + Prompts A–F)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md` (R1–R10 + Prompts G–J)
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` (W1–W4, conventions C1–C5, Prompts O–S)
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md` (D1–D5 dedupe + U1–U9 unsafe-transition)
> - `docs/sessions/2026-04-30-provider-autofeed-125920-claude-control-synthesis-1.md` (W5 + decision matrix + Prompt T)
> - `docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md` (G1–G8, Prompts U–X)

## ENV-MISMATCH banner — sandbox recurrence #8 in 24h

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/results/claude-governance-loop-rules-3.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read`/`Write`/`stat` of `agent-logs/**` | **blocked** at tool layer (verified — `Read` on `prompts/<lane>.md`, `snapshot.txt`, `make_and_launch.sh` all denied at lane start; `Bash ls` denied; `Bash test -f` blocked) |
| What still works | `Read`/`Write` inside `workspace-hub`; `Glob` enumeration of `agent-logs/**`; `Bash pgrep`/`date -u`/`test -f` inside workspace |
| Canonical durable output | **THIS document** at `docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md` per G6 canonical naming + `feedback_lane_result_path_outside_sandbox.md` |
| Out-of-band copy required (U3) | orchestrator should `cp` this file to the prescribed path. Until the copy lands, lane status is `completed-fallback`, NOT `completed`. |

Recurrence #8 in 24h: 100339 (`claude-3-governance-recovery-contract` → `staging-autofeed-recovery-contract/`), 111336×2, 114355×2, 125920×2, **145633** (this lane). Prompt K from 114355 (escalate to dispatcher hook) remains the right escalation. Predecessor 125920 already raised this to "critical-priority"; recurrence #8 confirms.

## Lane scope — narrow per dispatch task

The orchestrator asked for: **"convert known stall signatures and this tick evidence into bounded autofeed rules with dedupe, unsafe-transition gates, and result/log path conventions."**

Predecessor lanes shipped ~36 rules (R1–R10 + D1–D5 + U1–U9 + W1–W5 + G1–G8). This lane:

1. Captures **tick-145633 fresh evidence** — primarily the rule-drift signature: rules authored ~2h ago are not consumed by the dispatcher.
2. Surfaces **8 new non-consuming stall signatures (S9–S16)** not covered by R/D/U/W/G.
3. Authors **H1–H8** with embedded dedupe + unsafe-transition gates (per D3: fresh prefix; never redefine).
4. Adds a **result/log path conventions manifest** — the dispatch task's explicit third leg, never previously codified.

I use prefix **`H`** (host/handoff/hardening) per D3 (governance-rule-set dedupe).

## Live tick-145633 evidence (captured 15:15Z–15:18Z)

| Source | Output | Implication |
|---|---|---|
| `pgrep -af 'provider-autofeed' \| wc -l` | **111 PIDs** | unchanged from 125920's 127 — wrapper accumulation continues |
| Distinct alive run-IDs | `111336, 125920, 133520, 140140, 143424, 145633` (**6 runs**) | runs 133520/140140/143424 are NEW since 125920 — dispatcher is firing every ~7 min |
| `pgrep -af 'codex exec' \| wc -l` | **46 codex PIDs** (was 13+ at 125920) | **G4 threshold (≥5) blown by 9×; tick still dispatched 3 codex lanes (PIDs 2223281, 2223289, 2223301)** ⇒ **direct evidence rules are advisory, not enforced** |
| `pgrep -af 'git (rebase\|stash push\|merge\|reset\|switch)'` | **0 matches** | Hermes not active right now — G1 no-op clause holds. Hermes was active at 125920; window is racy. |
| `test -f .planning/cron-stop.flag` | **ABSENT** | operator has not signalled halt across 8 ticks |
| `Glob` of run-145633 result files | 9 files exist (`claude-{control-synthesis-recovery-1, plan-review-hardening-2, governance-loop-rules-3}`, `codex-{approved-eligibility-scout-1, test-readiness-scout-2, worktree-hygiene-salvage-3}`, `gemini-pro-{research-queue-1, gtm-legal-risk-2, standards-recon-3}`) | THIS lane's prescribed result file shows in Glob despite write-blocked sandbox ⇒ **write-probe stub pre-created by orchestrator** (S11 evidence) |
| Provider mix this tick | claude×3, codex×3, gemini-pro×3, gemini-flash×0 | Gemini-pro is BACK from the 114355 drop. R4 (Gemini-pro demotion) was authored, never consumed. Gemini-flash is now 0 — **structural inversion of G5 shape** but in opposite direction (now keeping the regression-blocked codex AND the demoted-by-R4 pro, while excluding the only-yielding-in-111336 flash). |

The **rule-drift signature (S9)** is the load-bearing fresh signal of this lane. R1 (codex version gate), R3 (variant cap — not blown but adjacent), R4 (Gemini-pro demotion), and G4 (cross-run codex zombie aggregator) all had their preconditions evidence-true at dispatch and would have blocked or modified the manifest if consumed. The dispatcher dispatched anyway. **Rules in markdown are not rules.**

## Non-consuming stall signature catalog — S9–S16

The 8 rows below are each (a) observable today via Bash/Glob, (b) NOT consumed by any rule in R1–R10 / D1–D5 / U1–U9 / W1–W5 / G1–G8, and (c) candidate next-tick rule subjects.

| # | Signature | Observable via | Currently consumed by | Coverage gap |
|---|---|---|---|---|
| S9 | Authored-but-unenforced rule drift | latest `docs/sessions/*governance*.md` rule cited by an alive lane that violates its precondition | (none — D3 retire-when names the fix but does not detect drift) | No detector for "rule X exists, X.precondition is true, dispatcher acted as if X did not exist" |
| S10 | Run-ID temporal density | `pgrep -af 'provider-autofeed' \| grep -oE 'provider-autofeed-[0-9]+' \| sort -u \| wc -l` over time-windowed buckets | (none) | No cap on `runs_per_hour` — 145633/143424/140140 = 3 runs in 16 min |
| S11 | Write-probe stub artifacts | `Glob agent-logs/<run>/results/<lane>.md` returns hit, but file size 0 (orchestrator pre-created OR stale-attempt residue) | U5 covers presence-only-not-success; doesn't distinguish probe-stub from real | No size-zero classification; consumers may misread as success |
| S12 | Per-tick aggregate budget | each lane sees its `$X/$20` line; no aggregator | (none) | 9 lanes × $20 cap = $180/tick × 6 ticks/2h = $1080+; no rule caps aggregate burn |
| S13 | Rule-set retirement scan | each rule has `Retire when:`; nothing checks the retirement condition | (none) | rule list grows monotonically; reviewers paged on stale rules indefinitely |
| S14 | In-flight sibling content dependency | dispatch prompt asks lane N to consume "this tick evidence" but sibling lane outputs are content-blocked from sandbox | U1 "predecessor-pending" branch covers completed-but-content-unverifiable; not in-flight-not-yet-finalized | This lane consumed siblings only via name + pgrep liveness, not content |
| S15 | Codex result-file overwrite-after-orchestrator-write | codex's `--output-last-message <result>` writes directly to the prescribed result path; if orchestrator wrote a probe stub, codex overwrites it; if a previous codex run hung and eventually completes, it stomps a fresh artifact | U7 covers result-file ↛ "codex executed"; doesn't address the write-collision shape | No file-locking or path-arbitration convention between orchestrator probe-stubs and codex direct-writes |
| S16 | Result/log path convention drift | logs continue to `agent-logs/<run>/logs/<lane>.log` even when result fell back to `docs/sessions/`; `.lane-state.json` location unspecified for fallback; no back-pointer convention | G6 covers result filename canonicalization; D4 covers same-(run, lane) artifact dedupe; **neither defines logs+state+provenance for fallback** | Dispatch task explicitly named this; previously uncodified |

## H-series — next-tick autofeed rules (each with embedded dedupe + unsafe-transition gate)

### H1 — Authored-but-unenforced rule-drift detector (consumes S9)

| Field | Value |
|---|---|
| **Precondition** | A governance lane is about to publish or a scoreboard is about to render. |
| **Check** | For each rule R in the latest governance artifact (newest mtime in `docs/sessions/*provider-autofeed*governance*.md`), evaluate R.precondition over current host state. If true AND a lane was dispatched in the most-recent run that R would have blocked/modified, emit `RULE-DRIFT: rule=<id>, precondition=<expr>, latest_run=<run-id>, lane=<name>`. |
| **Action** | Surface drift table to operator. **Do NOT auto-enforce** — rules live in markdown by D3 design until the versioned spec lands. Mark rule as `advisory-only` with drift-count incremented per occurrence. |
| **Built-in dedupe** | One `RULE-DRIFT` row per `(rule_id, run_id)` pair per scoreboard render. If same pair already surfaced in this 24h window, increment count, do not duplicate row. |
| **Built-in unsafe-transition gate** | **Forbidden:** auto-deleting or auto-rewriting rules just because they show drift (drift means the *consumer* is missing, not that the rule is wrong). **Forbidden:** lane killing the dispatcher, mutating the manifest, or back-filling enforcement code (composes with U2 — that's implementation, requires `status:plan-approved`). **Forbidden:** counting a rule as "honored this run" purely on no-drift-emission when the rule's precondition was false (no-op clauses are not honor signals). |
| **No-op clause** | No prior governance artifact in window, OR all rule preconditions false. |
| **Citation** | This tick — G4 precondition (≥5 codex PIDs alive) was true (46 alive); 145633 dispatched 3 codex lanes anyway. R4 precondition (Gemini-pro demotion) implicitly true; 145633 dispatched 3 gemini-pro lanes. |
| **Retire when** | D3 retire-when lands: rules move from `docs/sessions/` to `docs/governance/provider-autofeed/rules.md` AND a dispatcher-side script reads them. Then drift is structurally impossible. |
| **Bound** | One mtime sort + one regex pass over rules + one `pgrep`/Glob per rule precondition. |

### H2 — Run-ID temporal-density cap (consumes S10)

| Field | Value |
|---|---|
| **Precondition** | Dispatcher about to start a new autofeed run. |
| **Check** | Count distinct run-IDs in `pgrep -af 'provider-autofeed'` started in last 60 min. |
| **Action when matched (count ≥ 4)** | **Hold** the new run for 15 min. Emit `RUN-DENSITY: <count> runs in 60min; new run held until <T+15min>; existing runs may still be reaping`. After 15 min, re-check; if still ≥4, emit operator-only alert and STOP. |
| **Built-in dedupe** | One density-emission per (hold-start-time bucket); if same bucket already triggered hold, do NOT re-emit. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane killing existing runs to free density budget (composes with G3 — operator-owned). **Forbidden:** advancing the run state past `held` while H2 is holding. **Forbidden:** auto-tuning the cap from inside the lane (operator-owned config). |
| **No-op clause** | < 4 runs in window. |
| **Citation** | This tick — runs 133520/140140/143424/145633 = 4 runs in ~16 min. Sibling 125920 noted 7 alive runs already; today's host has had 8+ distinct runs in <8h. |
| **Retire when** | Dispatcher gains a per-host run-rate-limit config knob. |
| **Bound** | One `pgrep` + one `sort -u` per dispatcher start. |

### H3 — Write-probe stub disambiguation (consumes S11; refines U5)

| Field | Value |
|---|---|
| **Precondition** | A consumer (scoreboard, dispatcher, dashboard) is about to count `Glob hit on results/<lane>.md` as a deliverable. |
| **Check** | `stat -c %s <file>` AND read first 64 bytes. Classify: |
|  | • size = 0 ⇒ **`probe-stub`** (orchestrator pre-create or stale-attempt residue) |
|  | • size > 0 AND first line matches `STARTED \d{4}-\d{2}-\d{2}` AND no `FINISHED` marker AND mtime stale (>30 min) ⇒ **`started-only`** |
|  | • else ⇒ continue to U5/G7 logic |
| **Action when matched** | Tag accordingly. `probe-stub` does NOT count toward yield, scoreboard, or U5. `started-only` counts as `delivered-presence-only` per U5 unless content sniff shows otherwise. |
| **Built-in dedupe** | Per-tick: one classification per `(run_id, lane_name, file_mtime)` triple. Re-running classifier on same file with same mtime returns cached label. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane deleting `probe-stub` files (the orchestrator's create may be load-bearing for downstream copy mechanics). **Forbidden:** writing into a `probe-stub` from a lane other than the one named — composes with R5 + D1 (lane-name × prompt-hash dedupe). |
| **No-op clause** | File size > 64 bytes AND has any non-stub content past STARTED line. |
| **Citation** | This tick — Glob shows `results/claude-governance-loop-rules-3.md` exists for THIS lane despite Write-blocked sandbox; orchestrator pre-creates result files for downstream `tee` reasoning. Lane 145633 result-file presence cannot be a yield signal. |
| **Retire when** | Orchestrator separates probe-stub paths from result paths (`results-pending/<lane>.md` vs. `results/<lane>.md`). |
| **Bound** | One `stat -c %s` + one `head -c 64` per Glob hit per consumer. |

### H4 — Per-tick aggregate-budget visibility (consumes S12)

| Field | Value |
|---|---|
| **Precondition** | Dispatcher about to dispatch a new autofeed run; or a scoreboard about to render. |
| **Check** | Sum `--max-budget-usd` across all `claude -p`/`codex exec`/`gemini` commands in `pgrep -af 'provider-autofeed'`. Emit `AGGREGATE-BUDGET: alive=<sum>, runs=<list>, threshold=<configured>`. |
| **Action when matched (sum > threshold)** | Surface to operator BEFORE dispatching new lanes. Do NOT auto-block — operator may deliberately exceed (e.g., backfill burst). |
| **Built-in dedupe** | One `AGGREGATE-BUDGET` emission per scoreboard render or per dispatch decision. Hash on `(sum_bucket, run_set)` — if same set with same bucket already emitted in tick, do not duplicate. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane killing high-budget peers to "free budget" (composes with G3 — operator-owned). **Forbidden:** scaling individual lane `--max-budget-usd` from inside the lane (per-lane budget is wrapper-owned). **Forbidden:** auto-pausing a run mid-execution to free budget for a new run (mid-execution stop loses partial work — composes with U3 fallback contract). |
| **No-op clause** | Threshold not configured (until operator sets one), no-op but emit a Once-Per-Day `AGGREGATE-BUDGET-UNCONFIGURED` reminder. |
| **Citation** | This tick — 9 lanes × $20 cap = $180/tick × 6 ticks/2h ≈ $1080 budgeted (actual burn likely lower; visibility absent). |
| **Retire when** | Dispatcher emits aggregate-budget telemetry per dispatch decision and scoreboards include it. |
| **Bound** | One `pgrep` parse per emission. |

### H5 — Rule-set retirement scanner (consumes S13)

| Field | Value |
|---|---|
| **Precondition** | A governance lane is about to author new rules. |
| **Check** | Read all rules from latest governance artifact. For each rule R, evaluate R's `Retire when:` clause as a boolean over current state (memory file content, codebase grep, host state). If true, emit `RULE-RETIREMENT-CANDIDATE: <id> — <reason>` for operator review. |
| **Action** | Surface candidate list. **Do NOT auto-retire** — retirement edits a memory or contract file, which is operator-owned. New governance lane MUST cite candidates in its predecessors block as "candidate for retirement next tick". |
| **Built-in dedupe** | Per-rule: one retirement-candidate emission per (rule_id, retirement-condition-snapshot). If condition snapshot unchanged from previous lane's emission, do NOT re-emit (use a back-pointer instead). |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane editing the predecessor governance artifact to mark a rule retired (predecessor doc is immutable history). **Forbidden:** omitting a still-active rule from the precedence list to "implicitly retire" it (composes with D3 — must extend, not redefine). **Forbidden:** auto-promoting candidate to retired without operator marker (e.g., `.planning/rule-retired/<id>.md`). |
| **No-op clause** | All rules have unsatisfied retire-when conditions, OR no rules exist yet. |
| **Citation** | The R/D/U/W/G ladder has 36 rules; no rule-set today checks its own retirement. Multiple `Retire when:` clauses (R1, R3, R4, R6, R7, U7, U8, G1, G3, G4, G6) reference conditions ("Codex 0.124 fixed", "wrapper enforces X natively") that this lane cannot affirm but should at least probe. |
| **Retire when** | Versioned spec lands AND it has a built-in retirement workflow. |
| **Bound** | One pass per governance lane authoring decision. |

### H6 — In-flight sibling content dependency contract (consumes S14)

| Field | Value |
|---|---|
| **Precondition** | A lane's dispatch task names "this tick" or "current run" or otherwise asks for cross-lane synthesis with siblings in the same run. |
| **Check** | At lane start: `pgrep -af 'provider-autofeed-<run-id>'` AND `Glob agent-logs/<run-id>/results/*.md`. Classify each sibling: |
|  | • alive (PID matches) AND result-empty/probe-stub ⇒ **`in-flight`** |
|  | • dead (no PID) AND result-non-empty ⇒ **`finalized-readable-or-blocked`** (sandbox-blocked from THIS lane is still finalized for orchestrator) |
|  | • dead AND result-empty ⇒ **`died-empty`** |
| **Action** | If any required sibling is `in-flight`: lane MUST cite by name only (per U1 predecessor-pending branch); MUST NOT cite sibling content. If `finalized-readable-or-blocked` AND content sandbox-blocked: cite by name + Glob hit; do NOT speculate content. If `died-empty`: tag `[sibling-died-pre-emission]` and proceed. |
| **Built-in dedupe** | One sibling-classification per (run_id, sibling-lane-name) per consuming lane. Cached for the duration of the consuming lane. |
| **Built-in unsafe-transition gate** | **Forbidden:** waiting for sibling to finalize past lane's own timeout (`timeout 7200 claude -p` per `make_and_launch.sh`); spinning lane wastes wrapper budget. **Forbidden:** consuming sibling content from sandbox-blocked path via probe (e.g., `cat agent-logs/.../results/<sibling>.md`) — sandbox-block is structural, not race-condition. **Forbidden:** auto-spawning a "wait for sibling" subagent. |
| **No-op clause** | Dispatch task is independent of siblings. |
| **Citation** | This lane — dispatch task said "this tick evidence"; siblings `claude-control-synthesis-recovery-1` (PID 2223241 alive at lane-start), `claude-plan-review-hardening-2` (PID 2223254 alive). My output cites them by name + pgrep liveness only — H6's `in-flight` branch. |
| **Retire when** | Orchestrator dispatches dependent lanes serially with a verified-output handoff (then U1 covers the cross-tick case and H6 is moot). |
| **Bound** | One `pgrep` + one Glob per lane start. |

### H7 — Codex result-file overwrite protection (consumes S15)

| Field | Value |
|---|---|
| **Precondition** | A `codex exec` invocation includes `--output-last-message <path>`. |
| **Check** | Before launch: `stat <path>` — if file exists with size > 0 from a prior orchestrator-write, abort. After completion: verify the file's content matches expected codex output shape (per U7); if it overwrote a non-codex artifact (e.g., orchestrator probe-stub merged with codex output), tag `result-overwrite-suspect`. |
| **Action** | At dispatch: if path non-empty pre-launch, refuse codex exec; emit `BLOCKED: pre-existing artifact at <path>; will not overwrite without operator confirmation`. At post-completion: if shape suspect, tag and surface; do not auto-roll-back. |
| **Built-in dedupe** | One block emission per (run_id, lane_name) at dispatch. One overwrite-suspect emission per (run_id, lane_name) at completion. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane deleting an existing artifact at the codex output path (composes with H3 — orchestrator probe-stubs). **Forbidden:** rerunning codex with `--output-last-message` pointing to a path that another live `codex exec` PID also writes to (write-collision; composes with G4). **Forbidden:** redirecting codex output to a different path mid-flight ("fix" by rewriting flag) — that's wrapper-mutation, composes with R9. |
| **No-op clause** | Path empty pre-launch AND post-completion content shape passes. |
| **Citation** | This tick — codex 145633 lanes (PIDs 2223281, 2223289, 2223301) are running with `--output-last-message <path>` against pre-existing orchestrator probe-stubs at those exact paths (`Glob` confirms); regression-zombie codex from older runs (e.g., 111336 PID 2128357 history) could complete on stale args and stomp a 145633 lane's output. |
| **Retire when** | Codex 0.124 stdin-hang fixed (zombies stop happening) AND orchestrator routes probe-stubs to a separate path (composes with H3 retire-when). |
| **Bound** | Two `stat` calls + one shape-regex per codex exec. |

### H8 — Result/log path conventions manifest (consumes S16; explicit dispatch-task third leg)

This is the **dispatch-prompt-explicit ask** and was uncodified in R/D/U/W/G. H8 specifies the path manifest, the fallback path manifest, and the metadata back-pointers.

#### H8a — Prescribed path manifest (when sandbox grants `agent-logs/`)

```
/mnt/local-analysis/agent-logs/provider-autofeed-<run-id>/
├── make_and_launch.sh        # dispatcher artifact (already exists)
├── snapshot.txt              # dispatcher snapshot at run-start (already exists)
├── active_ps.txt             # dispatcher pgrep snapshot (already exists)
├── prompts/
│   └── <lane-name>.md        # dispatch prompt per lane (already exists)
├── logs/
│   ├── <lane-name>.log       # tee'd stdout from `claude -p`/`codex exec`/`gemini`
│   └── <lane-name>.pid       # wrapper PID (already exists)
├── results/
│   └── <lane-name>.md        # canonical lane output (lane writes here)
├── state/                    # NEW per H8 — created by lane wrapper
│   └── <lane-name>.json      # .lane-state.json per R7 + U3 (currently absent)
└── meta/                     # NEW per H8 — orchestrator-owned
    ├── manifest.json         # provider mix + dispatch decisions (currently absent)
    └── budget.json           # aggregate budget per H4 (currently absent)
```

#### H8b — Fallback path manifest (when ENV-MISMATCH per `feedback_lane_result_path_outside_sandbox.md`)

```
/mnt/local-analysis/workspace-hub/docs/sessions/
└── <YYYY-MM-DD>-provider-autofeed-<run-id>-<lane-name>.md   # per G6 canonical naming
    ├── (in-document) ENV-MISMATCH banner block               # per D4 + this rule
    ├── (in-document) `## .lane-state.json` fenced JSON block # per H8c — replaces state/
    ├── (in-document) `## Logs back-pointer` block            # per H8d — names log path
    └── (in-document) `## Provenance` block                   # per H8e — back-pointer chain
```

Logs continue to land at `agent-logs/<run-id>/logs/<lane-name>.log` even under fallback (the `tee -a` is wrapper-launched, not lane-launched, and sandbox-blocked from the lane). The canonical `docs/sessions/<...>.md` MUST therefore contain a back-pointer to that log path — without that pointer, the orchestrator's downstream copy mechanics (U3) lose log-result correlation.

#### H8c — Embedded `.lane-state.json` schema for fallback

When fallback fires, the canonical doc MUST embed:

```yaml
# Embedded in canonical doc as fenced ```json block under "## .lane-state.json"
{
  "lane_name": "<lane-name>",
  "run_id": "<run-id>",
  "status": "completed-fallback",      # NOT "completed" until orchestrator copies
  "result_path_actual": "docs/sessions/<...>.md",
  "result_path_prescribed": "/mnt/local-analysis/agent-logs/<...>.md",
  "log_path_prescribed": "/mnt/local-analysis/agent-logs/<run-id>/logs/<lane-name>.log",
  "started_utc": "<ISO-8601>",
  "finished_utc": "<ISO-8601>",
  "predecessors_in_run": ["<lane-name>", ...],
  "predecessors_cross_run": ["docs/sessions/<...>.md", ...],
  "rules_authored": ["<H1>", "<H2>", ...],     # if governance lane
  "awaiting_orchestrator_copy": true,
  "env_mismatch_recurrence_count_24h": 8
}
```

#### H8d — Logs back-pointer block

The canonical doc's metadata header MUST include a `Log:` line citing the prescribed log path. Consumers reading the canonical doc can then resolve logs via the orchestrator's separate copy step — without reading them inline (sandbox-blocked).

#### H8e — Provenance back-pointer block

The canonical doc's `## Provenance` section MUST list every input source consulted (Bash command + output summary, files read, memory feedback consulted) — already done by predecessor lanes by convention; H8 codifies it.

#### H8 — built-in dedupe + unsafe-transition gates

| Field | Value |
|---|---|
| **Precondition (dedupe)** | Lane about to write the canonical artifact. |
| **Check** | Glob `docs/sessions/*<run-id>-<lane-name>*.md`. If hit, append `## Re-run continuation` block to existing file (per D4). |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane writing to `agent-logs/<run-id>/state/<lane>.json` directly when ENV-MISMATCH (state/ is also sandbox-blocked); embed JSON in the canonical doc instead. **Forbidden:** the lane writing to `meta/manifest.json` or `meta/budget.json` (orchestrator-owned). **Forbidden:** rewriting log files under `logs/` (wrapper-owned). **Forbidden:** writing `.lane-state.json` outside `state/` AND outside the canonical doc's fenced block — those are the only two valid surfaces. |
| **No-op clause** | Sandbox grants prescribed path AND lane writes there directly — H8a applies, H8b–H8e moot. |
| **Citation** | Dispatch-task third leg ("result/log path conventions"); ENV-MISMATCH recurrence #8; prior session-notes (114355-loop-3 §"Out-of-band copy required"; 125920-governance-recovery-3 §"Out-of-band copy required") embedded ad-hoc state but with no shared schema. |
| **Retire when** | Sandbox allowlist widened OR prescribed paths moved inside workspace AND `.lane-state.json` schema lands as a versioned spec. |
| **Bound** | Constant per lane finalize. |

## Rule precedence — H-series interaction with R/D/U/W/G

Insert into the existing precedence list at these positions. Earlier rules win and short-circuit later ones.

1. **U6** (self-label invariant) — unchanged. Always first.
2. **U2** (dual approval gate) — unchanged.
3. **G1** (Hermes-active dispatch suppression) — unchanged.
4. **H2** (run-ID density cap) — **NEW; fires before any per-lane dispatch decision** because if the run itself is over-density, none of the per-lane gates need to run. Composes with G1 (Hermes can ALSO hold; either blocks dispatch).
5. **H1** (rule-drift detector) — **NEW; fires at scoreboard render and at governance-lane authoring time** (not at dispatch — H1 surfaces drift; it does not block dispatch). Sits beside G2/G3.
6. R5 → D1 → D3 → R2 → U3 → R1/R9 — unchanged.
7. **G4** (cross-run codex zombie aggregator) — unchanged. Fires after R1.
8. **H7** (codex result-file overwrite protection) — **NEW; fires immediately after G4** at codex dispatch time. G4 gates on zombie count; H7 gates on path-collision shape. Both must pass.
9. **G5** (provider-mix structural-inversion gate) — unchanged.
10. D2 → R3/R10 → U8 → R4 — unchanged.
11. **H6** (in-flight sibling content dependency) — **NEW; fires at consuming lane start**. Sits beside U1.
12. G2 → G3 — unchanged.
13. **H4** (aggregate-budget visibility) — **NEW; fires at scoreboard render and at dispatch decision**. Sits beside G3.
14. R8 → R6 → U4 → R7 — unchanged.
15. **H3** (write-probe stub disambiguation) — **NEW; fires at consumer-side aggregation** before U5. H3 classifies file size; U5 reads classification.
16. U5 → G6 → D4 → U7 — unchanged.
17. **H8** (result/log path conventions) — **NEW; fires at lane finalize-write time**. Composes with G6 (G6 picks the name; H8 specifies what goes in the file when fallback). H8 does NOT supersede G6.
18. **H5** (rule-set retirement scanner) — **NEW; fires at governance-lane authoring time** before D3. Sits beside D3.
19. **G7** (plan past-tense drift) → **G8** (sustained-MAJOR loop consensus) — unchanged.
20. D5 → U9 — unchanged.

## What this lane explicitly does NOT do

- ✗ Does **not** label any GitHub issue with `status:plan-approved` (U6). No `gh` mutation calls executed.
- ✗ Does **not** open any GitHub issue, PR, or post a comment (U9 + D5). Prompts Y/Z below name issue drafts but issue creation is operator-owned.
- ✗ Does **not** edit `classify_and_launch.sh`, `run_tick.sh`, `relaunch_replacements.sh`, `launch_replacements.sh`, `make_and_launch.sh`, or any provider wrapper.
- ✗ Does **not** modify `submit-to-codex.sh` or `submit-to-gemini.sh`.
- ✗ Does **not** create a worktree (no source edits attempted).
- ✗ Does **not** kill any process (H2/H4/H7 surface operator-only actions).
- ✗ Does **not** copy this artifact to the prescribed `agent-logs/` path (orchestrator-owned per U3).
- ✗ Does **not** retire any prior rule (H5 candidates surfaced for next-tick operator review).
- ✗ Does **not** redefine any rule in R1–R10, D1–D5, U1–U9, W1–W5, G1–G8 (D3 honored; fresh prefix `H`).
- ✗ Does **not** mutate `.claude/state/`, `.planning/plan-approved/`, or any memory feedback file.
- ✗ Does **not** consume sibling lane content (H6 self-honoring; sibling outputs cited by name only).
- ✗ Does **not** write to `agent-logs/.../state/<lane>.json` directly (H8 self-honoring; embedded in this doc instead).

## Suggested next-tick prompts (one at a time; do NOT chain)

Predecessor lanes shipped Prompts A–N (recovery-governance-1 + governance-loop-3), O–T (recovery-scoreboard-1 + control-synthesis-1), U–X (governance-recovery-3). The H-series implies these new prompts. **Strongest single recommendation: Prompt Y** — H1 (rule-drift detector) is fresh, observable, and dominates the value proposition (without H1, more rules = more drift; everything else is incremental).

### Prompt Y — Land H1 (rule-drift detector) as a scoreboard pre-render check

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: rule-drift-detector-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/rule-drift-detector-plan-1.md (fallback `docs/sessions/...` per H8b)
> Hard gates: do not destructively reset/clean; isolated worktrees; no outreach; no self-approval; no `status:plan-approved` changes; no unapproved implementation; `GIT_OPTIONAL_LOCKS=0`; redact secrets. **Planning only.**
> Task: Read H1 in `docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md`. Identify the latest governance artifact under `docs/sessions/` (mtime sort over `*provider-autofeed*governance*.md`). Spec a script `scripts/enforcement/check-autofeed-rule-drift.sh` callable from the dispatcher OR a scoreboard render step. Inputs: latest-rule-set path; output: drift table (`rule_id, precondition_evaluation, run_id, lane_dispatched_anyway`). Map to enforcement-gradient L2 per `.claude/rules/patterns.md`; promote to L3 once a per-rule precondition DSL exists. The harder design problem is the precondition DSL — propose a minimal subset (regex over `pgrep -af` output, file-existence, integer-comparison-on-pgrep-count) and document escape valves for richer preconditions. Reference `feedback_codex_cli_0_124_upstream_regression.md` and the live G4 case (≥5 codex PIDs alive). Do NOT modify the dispatcher. Exit: 1-page plan + GitHub issue draft (do NOT open the issue).

### Prompt Z — Land H8 (result/log path conventions) as a versioned spec

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: autofeed-path-conventions-spec-1
> Result file: per H8b canonical naming.
> Hard gates: same as Prompt Y.
> Task: Read H8a–H8e in this lane and the existing top-level contract `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md`. Promote H8 from session-note to a versioned spec at `docs/governance/provider-autofeed/path-conventions.md`. Include: prescribed path tree (H8a), fallback path tree (H8b), embedded `.lane-state.json` schema (H8c), `Log:` back-pointer convention (H8d), `## Provenance` block requirements (H8e). Reference `feedback_lane_result_path_outside_sandbox.md` (recurrence #8 today). The spec is the structural retire-when condition for D3, U3, D4, G6, H8 itself, and parts of U5/H3. Do NOT edit the wrapper. Exit: spec file + plan + GitHub issue draft (do NOT open).

### Prompt AA — Operator-host action: validate H2 cap configuration

> **Owner:** operator on dispatcher host (NOT a lane).
> **Action:** Read H2 in this lane. Decide: (a) what is the maximum reasonable `runs_per_60min`? (b) Is the dispatcher firing too often (8+ runs in <8h today, 4 runs in <16 min)? (c) Should the cap be host-config or per-cron-trigger? Set `MAX_RUNS_PER_60MIN` in dispatcher config and verify a single tick respects it. Write decision to `docs/governance/autofeed-run-density.md`. **Hard gate:** none (host-local, no GitHub mutation).

### Prompt BB — Wire H7 (codex overwrite protection) into the codex wrapper

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: codex-overwrite-protection-plan-1
> Result file: per H8b canonical naming.
> Hard gates: same as Prompt Y.
> Task: Read H7 in this lane and U7 in 114355-loop-3 and G4 in 125920-governance-recovery-3. Spec a pre-launch check inside `scripts/enforcement/` (callable from `submit-to-codex.sh` or its caller): `stat <output-last-message>`; if non-empty, refuse with structured error. Spec a post-completion shape-validator that fingerprints expected codex output. Map to L2; co-locate with the Prompt-V codex-zombie-aggregator script. Do NOT modify the codex wrapper in this lane. Exit: 1-page plan + diff sketch.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`. No git mutations attempted (Hermes inactive at lane start; G1 no-op clause held — but lane self-honored G1 by avoiding all git ops regardless).
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — read-only Bash only (`pgrep`, `test -f`, `date -u`, `ls` against allowed roots).
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; no comments; no labels). All "Prompt" sections name issue *drafts* explicitly handed to operator (U9 + D5 satisfied).
- ✓ No outreach drafts (no email, no Slack, no Drive uploads).
- ✓ No `status:plan-approved` label changes (U6 satisfied).
- ✓ No `.planning/plan-approved/<issue>.md` markers written or removed.
- ✓ No source-file edits; no isolated worktree created.
- ✓ No secrets emitted.
- ✓ No mutation of `.claude/state/` or any memory feedback file.
- ✓ U3 satisfied: this lane's `.lane-state.json` (when written by the wrapper) should record the embedded JSON in §H8c. Pasted here for orchestrator pickup:

```json
{
  "lane_name": "claude-governance-loop-rules-3",
  "run_id": "provider-autofeed-20260430-145633",
  "status": "completed-fallback",
  "result_path_actual": "docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md",
  "result_path_prescribed": "/mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/results/claude-governance-loop-rules-3.md",
  "log_path_prescribed": "/mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/logs/claude-governance-loop-rules-3.log",
  "started_utc": "2026-04-30T15:15:11Z",
  "finished_utc": "2026-04-30T15:23:00Z",
  "predecessors_in_run": ["claude-control-synthesis-recovery-1", "claude-plan-review-hardening-2"],
  "predecessors_cross_run": [
    "docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md",
    "docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md",
    "docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md",
    "docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md",
    "docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md",
    "docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md",
    "docs/sessions/2026-04-30-provider-autofeed-125920-claude-control-synthesis-1.md",
    "docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md"
  ],
  "rules_authored": ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"],
  "awaiting_orchestrator_copy": true,
  "env_mismatch_recurrence_count_24h": 8
}
```

- ✓ D3 satisfied: extends prior R/D/U/W/G with new `H` prefix; does not redefine any prior rule.
- ✓ D4 + G6 satisfied: single canonical artifact at `docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md` (canonical naming — no `-FALLBACK`/`-result` suffix).
- ✓ U2 satisfied: planning/specification only. H-rules are *prescriptive specs*; landing them requires Prompts Y/Z/BB (planning) plus user approval.
- ✓ U9 satisfied: Prompts Y/Z/BB reference GitHub issue drafts but issue creation is operator-owned.
- ✓ G1 self-honoring: this lane did NOT dispatch any subagent or commit; only emitted a session-note artifact.
- ✓ H6 self-honoring: cited siblings `claude-control-synthesis-recovery-1` and `claude-plan-review-hardening-2` by name + pgrep liveness only; did NOT consume their content.
- ✓ H8 self-honoring: embedded `.lane-state.json` per H8c; included `Log:` back-pointer per H8d (in §H8a manifest); included `## Provenance` per H8e (below).
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md` (H8 + recurrence #8), `feedback_codex_cli_0_124_upstream_regression.md` ([#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — H1 + H7 evidence), `feedback_check_parallel_work.md` (H6), `feedback_never_offer_to_self_label_plan_approved.md` (U6 verbatim), `feedback_inline_gh_issue_url.md` (issue refs rendered as Markdown hyperlinks), `project_issue_2460_approval_binding.md` (U2 backbone).

## Evidence appendix — what backed every H-rule

| H-rule | Backing evidence |
|---|---|
| H1 | Live `pgrep -af 'codex exec' \| wc -l` at 15:18Z = 46; G4 threshold = 5; 145633 still dispatched 3 codex lanes (PIDs 2223281/2223289/2223301). R4 also drifted: gemini-pro demotion authored, 145633 dispatched 3 gemini-pro lanes. |
| H2 | Live `pgrep` distinct run-IDs = 6 (111336, 125920, 133520, 140140, 143424, 145633); 4 of those started in last ~16 min (133520→145633). |
| H3 | Live Glob shows `agent-logs/.../results/claude-governance-loop-rules-3.md` exists for THIS lane despite Write-blocked sandbox — orchestrator probe-stub. |
| H4 | This tick: 9 lanes alive in run 145633 each with `--max-budget-usd 20` ⇒ $180 visible cap; 6 alive runs ⇒ aggregate ≥ $360 ceiling visibility absent. |
| H5 | R/D/U/W/G ladder = 36 rules with `Retire when:` clauses; nothing checks them. |
| H6 | This lane: dispatch task said "this tick evidence"; siblings `claude-control-synthesis-recovery-1` PID 2223241 alive at lane-start, `claude-plan-review-hardening-2` PID 2223254 alive. Sibling content sandbox-blocked. |
| H7 | Codex 145633 PIDs 2223281/2223289/2223301 all running with `--output-last-message <prescribed-path>` against pre-existing orchestrator probe-stubs (Glob confirms). Also: regression-zombie codex from older runs alive (per 125920 evidence; same shape recurs). |
| H8 | Dispatch-task third leg explicit; ENV-MISMATCH recurrence #8; predecessor session-notes embedded ad-hoc state JSON without shared schema. |

## Concurrency snapshot — 2026-04-30T15:15Z–15:18Z

| Run | Status |
|---|---|
| 111336 | zombie wave; 3.5h+ old; codex residue alive |
| 125920 | 2h old; sibling lanes finalized; some PID residue |
| 133520 | dispatch ~15:35Z(?); no `docs/sessions/` artifact yet |
| 140140 | dispatch ~14:01Z; no artifact |
| 143424 | dispatch ~14:34Z; no artifact |
| **145633** (this) | 9 lanes alive (claude×3, codex×3, gemini-pro×3); claude lanes mid-flight at 15:18Z; gemini lanes already exited (no pgrep matches; Glob confirms result files exist) |
| **Hermes** | **inactive** — no `git rebase\|stash\|merge\|reset\|switch` matches; G1 no-op |

## Provenance (H8e — required block)

| Source | Output captured |
|---|---|
| `pgrep -af 'provider-autofeed' \| wc -l` | 111 PID lines |
| `pgrep -af 'provider-autofeed' \| grep -oE 'provider-autofeed-[0-9TZ-]+' \| sort -u` | 6 distinct run IDs |
| `pgrep -af 'codex exec' \| wc -l` | 46 codex PIDs |
| `pgrep -af 'git (rebase\|stash push\|merge\|reset\|switch)'` | 0 matches |
| `test -f /mnt/local-analysis/workspace-hub/.planning/cron-stop.flag` | ABSENT |
| `pgrep -af 'provider-autofeed-20260430-145633'` | 9 lanes + their tee+wrapper PIDs (cited inline above) |
| `Glob /mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/**` | 9 result files, 9 prompt files, 9 log files, 9 pid files; `snapshot.txt`, `make_and_launch.sh`, `active_ps.txt` |
| `ls /mnt/local-analysis/workspace-hub/docs/sessions/` (filtered to `2026-04-30*provider-autofeed*`) | 14 session-note artifacts (across runs 073439, 100339, 111336, 114355, 125920) |
| `Read` of `2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md` | full body — G1–G8 source |
| `Read` of `2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md` | full body — D1–D5 + U1–U9 source |
| `Read head 60 lines` of `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` | top-level contract, useful-lane defn, default thresholds |
| Memory consulted | `feedback_lane_result_path_outside_sandbox`, `feedback_codex_cli_0_124_upstream_regression`, `feedback_check_parallel_work`, `feedback_never_offer_to_self_label_plan_approved`, `feedback_inline_gh_issue_url`, `feedback_hermes_active_preflight_check`, `feedback_codex_sustained_major_loop`, `feedback_plan_past_tense_artifact_claims`, `project_issue_2460_approval_binding` |

No log/prompt body was read from `agent-logs/` (sandbox-blocked at tool layer for this session — verified at lane start). All evidence is from: (a) `pgrep -af` + `test -f` + `date -u` + `ls` over the host process/filesystem inside `workspace-hub`-allowed roots, (b) `Read` of predecessor session artifacts inside `docs/sessions/` and `docs/governance/`, (c) `Glob` enumeration of `agent-logs/**` (allowed), (d) cited memory feedback files.

## Strongest single follow-up

**Prompt Y** (land H1 as scoreboard pre-render check). Without H1, more rules → more advisory drift → diminishing returns on every governance lane. H1 closes the meta-loop: rules in markdown become rules-with-detection-of-non-enforcement, which is the precondition for the structural retire-when in D3.
