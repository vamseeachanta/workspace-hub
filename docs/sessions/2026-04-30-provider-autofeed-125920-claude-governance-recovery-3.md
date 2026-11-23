# Provider-Autofeed Governance/Recovery — `claude-governance-recovery-3` (run 20260430-125920)

> **Lane ID:** `claude-governance-recovery-3`
> **Run:** `provider-autofeed-20260430-125920`
> **Author:** Claude Opus 4.7 (1M ctx), recovery-tier sandbox.
> **STARTED:** 2026-04-30T13:11:49Z (first tool call of this lane); my own `claude -p` invocation visible in pgrep at PID range adjacent to 2188235 (`launch.sh` shell PID for this lane wrapper).
> **Predecessors in same run (do NOT duplicate; cite by ID):** sibling `claude-control-synthesis-1` (PID 2188200, output already at `docs/sessions/2026-04-30-provider-autofeed-125920-claude-control-synthesis-1.md`); sibling `claude-plan-review-hardening-2` (PID 2188219, in-flight at write time).
> **Cross-run predecessors cited (do NOT redefine; extend only):**
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` (recovery scoreboard + Prompts A–F)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md` (R1–R10 bounded next-tick rules + Prompts G–J)
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` (W1–W4 wrappers, conventions C1–C5, Prompts O–S — comprehensive baseline)
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md` (D1–D5 dedupe + U1–U9 unsafe-transition gates)
> - `docs/sessions/2026-04-30-provider-autofeed-125920-claude-control-synthesis-1.md` (W5 zombie-wave + decision matrix + cross-run D1 extension + Prompt T)

## ENV-MISMATCH banner — sandbox recurrence #7 in 24h

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-125920/results/claude-governance-recovery-3.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| Read/Write/stat of `agent-logs/**` | **blocked** at tool layer (verified — first attempts to `Glob` and `Bash ls` agent-logs were denied/timed-out) |
| What still works | `Read`/`Write` inside `workspace-hub`; Bash `pgrep -af`, `test -f`, `find` against allowed roots |
| Canonical durable output | **THIS document** under `docs/sessions/` per `feedback_lane_result_path_outside_sandbox.md` |

Per D4 (governance-loop-3 §Dedupe-rules), one canonical artifact per (run, lane). Per U3, my `.lane-state.json` should record `status: "completed-fallback"`, `result_path_actual: docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md`, `result_path_prescribed: agent-logs/.../125920/results/claude-governance-recovery-3.md`, `awaiting_orchestrator_copy: true`. Recurrence #7 in 24h ⇒ Prompt K (escalation to dispatcher hook) is now critical-priority.

## Lane scope — narrow, by dispatch prompt

The orchestrator asked for: **"convert current non-consuming stall signatures and recent lane evidence into next-tick autofeed rules with dedupe and unsafe-transition gates."**

A *non-consuming stall signature* is a signal the autofeed loop emits but no current rule reads. It accumulates in scoreboards (`pgrep` lines, file presence, memory-feedback hits, naming-convention drift) without driving a next-tick recovery action. The R-/D-/U-/W-series shipped today cover ~30 rules; this lane surfaces signatures **still uncovered as of run 125920** and pairs each with both a dedupe condition AND an unsafe-transition gate so the rule itself cannot go feral.

I use prefix **`G`** (governance/recovery) per D3 (governance-rule-set dedupe — fresh prefix to keep IDs stable references).

## Live evidence captured at lane start (2026-04-30T13:11Z–13:13Z)

| Source | Output | Implication |
|---|---|---|
| `pgrep -af 'provider-autofeed' \| wc -l` | **127 lines** | unchanged from sibling control-synthesis-1 ~30s earlier — concurrent snapshot |
| Distinct active run-IDs | `073439, 102314, 104814, 111336, 114355, 120344, 125920` (**7**) | matches sibling §1 |
| `test -f .planning/cron-stop.flag` | **ABSENT** | autofeed still firing; operator has not signalled halt |
| `pgrep -af 'codex exec'` | **13+ codex PIDs alive** including run 114355 (PIDs 2145230, 2145244, 2145246, 2145255, 2145256, 2145258, 2145296, 2145299, 2145342) and run 073439 (PID 2172737) | direct evidence U7/U8 still hot — codex 0.124 stdin-hang unresolved across ≥2 runs at 90+ min each |
| **`pgrep -af 'git (rebase\|stash push\|merge\|reset\|switch)'`** | **3 active git mutations:** `git rebase --autostash --onto df3b416…` PID 2190414, `git merge FETCH_HEAD` PID 2193359, `git rebase --abort` PID 2204239 | **Hermes is active RIGHT NOW** per `feedback_hermes_active_preflight_check.md` — direct trigger for parallel-commit revert hazard, NOT covered by any existing R/D/U/W rule |

The Hermes-active observation is the **load-bearing fresh signal of this lane**. Every prior governance lane today missed it (none of 100339, 111336-recovery, 111336-loop-4, 114355-recovery, 114355-loop-3, or 125920-control-synthesis ran the `pgrep -af 'git rebase'` check). It is direct evidence that **the autofeed loop is firing while Hermes is mid-rebase** — and any lane that landed a commit on main during this window risked silent revert.

## Non-consuming stall signature catalog

The 8 rows below are each (a) observable today via Bash/Glob, (b) NOT consumed by any rule in R1–R10 / D1–D5 / U1–U9 / W1–W5, and (c) potential next-tick rule subjects.

| # | Signature | Observable via | Currently consumed by | Coverage gap |
|---|---|---|---|---|
| S1 | Hermes git mutating-ops alive at lane dispatch | `pgrep -af 'git (rebase\|stash push\|merge\|reset\|switch)'` returns ≥1 line | (none) | No rule gates lane dispatch on Hermes activity |
| S2 | `launch_replacements.sh` wrappers alive 90+ min after dispatch | `pgrep -af 'launch_replacements'` + etime | W2 names the race but does not classify the long-lived wait | No "long-wait wrappers are normal, not a stall" classifier |
| S3 | Run-N zombie wave (run age >5h, no claude/codex children) | per-run pgrep + child count | W5 names the symptom but emits no rule | No reap-recommendation generator with bounded action |
| S4 | Codex 0.124 zombies surviving across run boundaries | `pgrep -af 'codex exec'` cross-referenced with run IDs in pgrep cmdline | U7 covers single-lane verdict; not aggregate | No cross-run zombie-count gate that suppresses next-tick codex dispatch |
| S5 | Provider-mix structural inversion (only-yielding provider dropped while regression-blocked one kept) | per-run lane manifest diff | R4 demotes gemini-pro; doesn't watch for the inversion shape | No "did the only-yielding provider just get cut" gate |
| S6 | `docs/sessions/` naming-convention drift (`-FALLBACK.md`, `-result.md`, no-suffix) | `Glob docs/sessions/2026-04-30-*provider-autofeed*` | D4 names the dedupe but no canonicalization | No filename-shape lint at write time |
| S7 | Plan body containing past-tense artifact claims (e.g., "we shipped X") for not-yet-merged work | regex on plan body before consumption | (none — memory feedback only) | No autofeed gate stops a planning lane from being consumed as authoritative when it lies about past tense |
| S8 | Codex sustained-MAJOR loop (3+ rounds with consensus-vs-minority pattern) | review-history JSON | (none — memory feedback only) | No autofeed escalation surfaces consensus instead of cycling |

Below, each signature ⇒ one **G-rule** with both dedupe and unsafe-transition built in.

## G-series — next-tick autofeed rules (each with embedded dedupe + unsafe-transition gate)

### G1 — Hermes-active lane-dispatch suppression (consumes S1)

| Field | Value |
|---|---|
| **Precondition** | About to dispatch any lane (or the lane is about to commit / push / merge) on `/mnt/local-analysis/workspace-hub`. |
| **Check** | `pgrep -af 'git (rebase\|stash push\|merge\|reset\|switch)' \| grep -v ' grep '` returns ≥1 line whose CWD or argv references `workspace-hub` or its branches. |
| **Action when matched** | **Hold** the dispatch (do not spawn the lane wrapper). Emit telemetry line `HERMES-ACTIVE-HOLD lane=<name> hermes_pids=<list> waited_for_quiescence=Y/N`. Retry once after 60s of quiescence (no matching PIDs for 60 consecutive seconds). After 2 holds, surface `OPERATOR-HERMES-CONFLICT` and STOP — do not auto-relaunch. |
| **Built-in dedupe** | Hash `(hermes_pid_set, lane_name)`; if same set already triggered hold for same lane in this tick, do NOT emit a second telemetry row. One hold per (Hermes wave, lane) per tick. |
| **Built-in unsafe-transition gate** | **Forbidden:** killing Hermes PIDs, calling `git rebase --abort` from a lane, or "force-pushing past Hermes" because the lane has its own commit. Lane must yield. Lane wrapper must NOT advance the lane state past `dispatching` while G1 is holding. |
| **No-op clause** | If pgrep returns zero git-mutating PIDs, dispatch normally. |
| **Citation** | `feedback_hermes_active_preflight_check.md` (Hermes cleanup loops can revert parallel commits; preflight required); live evidence in run 125920 at 13:11Z (3 git PIDs alive while sibling lanes were dispatching). |
| **Retire when** | Hermes is reworked to use a worktree+feature-branch model OR a lock file (`.git/HERMES_ACTIVE`) + `pre-merge-commit` hook makes the gate structural. |
| **Bound** | 1 `pgrep` call + 1 telemetry row per dispatch decision. |

### G2 — Long-wait wrapper classifier (consumes S2; refines W2)

| Field | Value |
|---|---|
| **Precondition** | A scoreboard or recovery lane is about to mark a `launch_replacements.sh`/`relaunch_replacements.sh` PID as "stuck" or "stale wrapper". |
| **Check** | For each matched wrapper PID: read `/proc/<pid>/stat` to get start-time; compare against the lane's spawned-child PIDs (claude or codex). If a child is alive AND child age < 7200s, the wrapper is **`waiting-on-child`**, not stale. |
| **Action when matched (waiting-on-child)** | Tag wrapper status `waiting-on-child` (NOT `stale-wrapper`). Do NOT emit a kill recommendation. |
| **Action when matched (no live child OR child age ≥ 7200s)** | Tag `truly-stale`. Emit operator-only kill recommendation. |
| **Built-in dedupe** | Per-tick: hash `(wrapper_pid, status_tag)`. Don't re-emit the same status row twice in the same tick. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane killing wrappers from inside the sandbox. Wrappers are killed only by the operator OR by the dispatcher's age-based reaper (does not yet exist; see G3). |
| **No-op clause** | If pgrep returns no wrapper PIDs, no row. |
| **Citation** | Sibling control-synthesis-1 §1b (W2 long-lived; "Not a bug; just long-lived" — formalizing it here). 114355-recovery-scoreboard-1 §W1–W4. |
| **Retire when** | Wrapper exits when child exits (stop-and-write contract); long-wait class disappears. |
| **Bound** | 1 `/proc/<pid>/stat` read per wrapper per tick. |

### G3 — Stale-run reap recommendation generator (consumes S3; promotes W5 to actionable)

| Field | Value |
|---|---|
| **Precondition** | A run-id is alive in pgrep AND `now() - run_start_ts > 5h`. |
| **Check** | For each old run, count child PIDs matching `claude\|codex` whose argv references this run-id. If 0, the run is a `zombie-tee-only` wave (only `tee -a logs/...` PIDs hanging around). |
| **Action when matched** | Emit a structured operator action: `kill -TERM <orphan-tee-pids>` AND a follow-up recommendation to add an age-based reaper to the dispatcher (Prompt T already requested this). Do NOT emit if the run already has a `reap-recommended.<run-id>.flag` written this 24h window. |
| **Built-in dedupe** | One reap recommendation per run-id per 24h. Hash key: `(run_id, day_bucket)`. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane calling `kill` from inside the sandbox. The lane *recommends*; the operator *acts*. **Forbidden:** killing PIDs whose argv contains `claude\|codex` (these may be in long-thinking; G2 covers them). **Forbidden:** killing the dispatcher root (`classify_and_launch.sh`) without operator confirmation (dispatcher mid-flight kill loses the in-tick state). |
| **No-op clause** | If all alive runs are < 5h old, no recommendation. |
| **Citation** | Sibling control-synthesis-1 §3 W5 (run 073439 zombie wave at 5.5h+); 114355-recovery-scoreboard-1 §W1–W4. |
| **Retire when** | Dispatcher gains an age-based reaper that runs per tick (Prompt T item). |
| **Bound** | 1 `pgrep -af 'provider-autofeed-<r>'` per old run per tick. |

### G4 — Cross-run codex zombie aggregator (consumes S4; extends U7/U8)

| Field | Value |
|---|---|
| **Precondition** | About to dispatch a `codex-*` lane in a new run. |
| **Check** | Count alive `codex exec` PIDs across **all** runs (`pgrep -af 'codex exec'`). |
| **Action when matched (count ≥ 5)** | **Refuse the codex dispatch.** Emit `BLOCKED: <count> codex PIDs alive across <run-list>; provider regression unresolved per feedback_codex_cli_0_124_upstream_regression. Operator must downgrade host CLI before dispatching new codex lanes.` Surface to operator as Prompt-Q-class action. |
| **Action when matched (count 1–4)** | Allow dispatch but tag `codex-degraded-context: <count>-zombies-alive`. |
| **Built-in dedupe** | One `BLOCKED` emission per dispatch decision (dedupe on lane-name + tick); zombie count is a side fact, not re-emitted per zombie. |
| **Built-in unsafe-transition gate** | **Forbidden:** counting "codex result file exists" as a yield while count ≥ 1 — composes with U5 + U7. **Forbidden:** the lane killing the zombies. **Forbidden:** auto-creating fan-out variants when count ≥ 1 (composes with R3 cap and U8 — variant fan-out is negative-yield while regression open). |
| **No-op clause** | Count = 0, normal codex dispatch. |
| **Citation** | `feedback_codex_cli_0_124_upstream_regression.md` (#2479); live evidence run 125920: 13+ codex PIDs alive across runs 073439 + 114355 at 13:11Z; 111336-recovery-governance-1 (9/9 codex stalled). |
| **Retire when** | `feedback_codex_cli_0_124_upstream_regression.md` is retired (host downgrade verified). |
| **Bound** | 1 `pgrep` per dispatch decision. |

### G5 — Provider-mix structural-inversion gate (consumes S5; extends R4)

| Field | Value |
|---|---|
| **Precondition** | About to commit the per-run lane manifest (the set of `<provider>-*` lane names dispatched). |
| **Check** | Diff the proposed manifest against the previous run's manifest. Compute (a) `dropped_providers` = providers present in prev but absent in current; (b) `dropped_yielding_provider`: any provider in `dropped_providers` whose previous-run yield was ≥ 50%. |
| **Action when matched (dropped_yielding_provider non-empty AND a regression-blocked provider remains)** | Emit `STRUCTURAL-INVERSION: dropped <yielders> while keeping <regression_blocked>; this is negative-yield. Surface to operator before dispatch.` Hold the dispatch until operator confirms (writes `.planning/manifest-confirmed.<run-id>.flag`) OR a 30-min timeout expires (then dispatch with a `[structural-inversion-warning]` tag in every lane prompt of that run). |
| **Action when matched (dropped_yielding_provider non-empty, no regression-blocked provider)** | Tag the run `[provider-mix-shifted]`; dispatch. Not a hold. |
| **Built-in dedupe** | One emission per (run-id, manifest-hash). Same manifest hash across two ticks does not re-emit. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane modifying `provider-autofeed-monitor/manifest.json` or any wrapper to "fix" the inversion. The lane *flags*; operator *fixes*. **Forbidden:** auto-restoring a dropped provider (operator may have intentionally cut it for legal/cost reasons not visible to the lane). |
| **No-op clause** | First run of the day (no previous manifest), or manifest unchanged. |
| **Citation** | 114355-loop-3 §"Behavioral deltas" point 2 (gemini removed entirely while codex regression unresolved → structural inversion). Prompt M of that lane is the operator triage, but no rule existed to *prevent* the inversion. |
| **Retire when** | The dispatcher emits a per-run manifest with provider yields and the operator-confirm step is automated. |
| **Bound** | 1 manifest diff per run dispatch. |

### G6 — Docs/sessions filename canonicalizer (consumes S6; extends D4)

| Field | Value |
|---|---|
| **Precondition** | A lane is about to write its fallback artifact to `docs/sessions/`. |
| **Check** | Compute canonical name: `docs/sessions/<YYYY-MM-DD>-provider-autofeed-<run-id>-<lane-name>.md` — **no** `-FALLBACK` or `-result` suffix. |
| **Action when matched (computed name differs from prescribed name)** | Use the canonical name. If a non-canonical artifact already exists for the same (run, lane) (per D4 Glob), append a `## Re-run continuation` block to the canonical one and write a `## Naming-canonicalization` line in the appended block citing the deprecated suffix. |
| **Built-in dedupe** | D4 already covers same-(run, lane) double-write; G6 is the rename gate that fires *before* D4. Combined: at most one canonical file per (run, lane). |
| **Built-in unsafe-transition gate** | **Forbidden:** deleting or renaming an existing `-FALLBACK.md`/`-result.md` artifact from a lane (it may be cited from the orchestrator's out-of-band copy script). Migration is operator-owned (Prompt N of 114355-loop-3). |
| **No-op clause** | If the prescribed path is already canonical, write normally. |
| **Citation** | `docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` and `2026-04-30-claude-stream-plan-hardening-3-result.md` use different suffix conventions for the same artifact class; 114355-loop-3 D4 + Prompt N. |
| **Retire when** | A pre-write hook normalizes filenames structurally. |
| **Bound** | 1 string-compute + 1 Glob per lane finalize. |

### G7 — Plan past-tense drift detector (consumes S7; new memory→autofeed link)

| Field | Value |
|---|---|
| **Precondition** | A consumer (review lane, scoreboard, dashboard) is about to treat a planning artifact as authoritative for downstream action. |
| **Check** | Regex-scan the planning artifact for past-tense artifact claims that would only be true post-merge: `\b(landed|merged|shipped|completed|deployed|implemented|opened issue #\d+|created PR #\d+)\b` cross-referenced with `git log --all --source -- <claimed_file>` returning empty for that file. |
| **Action when matched** | Tag the consumer's reasoning `[plan-past-tense-drift]` and refuse to cite the planning artifact as a load-bearing source. The consumer must verify each past-tense claim against `git log` / `gh` and re-anchor to "proposed" tense in its own output. |
| **Built-in dedupe** | One detection per (planning-file, consumer-lane) pair — once detected and tagged, downstream consumers reuse the tag, not re-scan. Hash: `(plan_file_sha256, consumer_lane_name)`. |
| **Built-in unsafe-transition gate** | **Forbidden:** auto-rewriting the planning artifact's tenses from a downstream lane. The author owns its own document. **Forbidden:** auto-applying `status:plan-approved` based on a plan that contains past-tense drift (composes with U2 + U6). |
| **No-op clause** | Planning artifact contains no past-tense markers, OR all past-tense claims verify against `git log`/`gh`. |
| **Citation** | `feedback_plan_past_tense_artifact_claims.md` (plans describing proposed work as committed artifacts trick reviewers). No prior autofeed rule encoded this. |
| **Retire when** | A pre-commit/pre-write hook on planning artifacts gates past-tense markers structurally. |
| **Bound** | 1 grep + 1 `git log` per past-tense match per consumer. |

### G8 — Sustained-MAJOR loop consensus surfacing (consumes S8; new memory→autofeed link)

| Field | Value |
|---|---|
| **Precondition** | A cross-review cycle has run ≥ 3 rounds AND one provider's verdicts are MAJOR while ≥ 2 other providers' verdicts are MINOR by round 3. |
| **Check** | Scan review-history JSON (or, in absence, the `docs/governance/cross-review/` artifacts) for the (artifact-id, provider, round, verdict) tuples. Compute `majority_verdict` over the last completed round. |
| **Action when matched** | **Stop the loop.** Emit `CONSENSUS-VS-MINORITY: artifact=<id>, majority=<verdict>, minority=<provider>:<verdict>, rounds=<n>. Surfacing for operator decision; will NOT auto-cycle to round <n+1>.` Surface to operator as a single decision point (accept majority, take minority seriously, or split). |
| **Built-in dedupe** | One emission per (artifact-id, round) — re-running the same round does not re-emit. The rule fires once per round transition. |
| **Built-in unsafe-transition gate** | **Forbidden:** auto-cycling to round n+1 while a consensus-vs-minority decision is open. **Forbidden:** auto-merging the artifact based on majority-MINOR alone (operator decision required). **Forbidden:** dropping the minority provider from the next review cycle as a "fix" for the disagreement (composes with G5 — that's a structural-inversion shape). |
| **No-op clause** | < 3 rounds completed, OR all providers converged on same severity. |
| **Citation** | `feedback_codex_sustained_major_loop.md` (#2045, #2289 anti-pattern: when codex MAJOR 3+ rounds while Claude+Gemini MINOR by v3, surface decision instead of auto-cycling). |
| **Retire when** | The cross-review harness has a built-in consensus-detection step that emits this on its own. |
| **Bound** | 1 review-history scan per round-transition decision. |

## Rule precedence — G-series interaction with R/D/U/W

Insert into the existing precedence list (114355-loop-3 §Rule precedence) at these positions. Earlier rules win and short-circuit later ones.

1. **U6** (self-label invariant) — unchanged.
2. **U2** (dual approval gate) — unchanged.
3. **G1** (Hermes-active dispatch suppression) — **NEW; fires before any dispatch attempt** because Hermes can revert any commit lane lands. Composes with R5 (concurrency duplicate guard) — even non-duplicate lanes must hold while Hermes is mutating.
4. R5 → D1 → D3 → R2 → U3 → R1/R9 — unchanged.
5. **G4** (cross-run codex zombie aggregator) — **NEW; fires immediately after R1** (codex version gate). R1 checks host version; G4 checks process residue across runs. Both must pass.
6. **G5** (provider-mix structural-inversion gate) — **NEW; fires before R3/R10 caps** because the inversion shape is a higher-order signal than per-provider variant fan-out.
7. D2 → R3/R10 → U8 → R4 — unchanged.
8. **G2** (long-wait wrapper classifier) — **NEW; runs continuously per tick over alive wrappers; not a dispatch gate.** Sits beside R6.
9. **G3** (stale-run reap recommendation) — **NEW; runs continuously per tick over alive runs; emits operator-only recommendations.** Sits beside G2.
10. R8 → R6 → U4 → R7 — unchanged.
11. **G6** (docs/sessions filename canonicalizer) — **NEW; fires at write time** before D4. Combined: G6 picks the name, D4 prevents duplicate writes.
12. D4 — unchanged (now after G6).
13. U5/U7 — unchanged (consumer-side aggregation).
14. **G7** (plan past-tense drift detector) — **NEW; fires at consumer side** before any consumer treats a plan as authoritative. Composes with U2 (dual approval gate).
15. **G8** (sustained-MAJOR loop consensus surfacing) — **NEW; fires at round-transition** before the cross-review harness auto-advances to round n+1.
16. D5 → U9 — unchanged.

## What this lane explicitly does NOT do

- ✗ Does **not** label any GitHub issue with `status:plan-approved` (U6). No `gh` mutation calls executed.
- ✗ Does **not** open any GitHub issue, PR, or post a comment (U9 + D5).
- ✗ Does **not** edit `classify_and_launch.sh`, `run_tick.sh`, `relaunch_replacements.sh`, `launch_replacements.sh`, or any provider wrapper.
- ✗ Does **not** modify `submit-to-codex.sh` or `submit-to-gemini.sh`.
- ✗ Does **not** create a worktree (no source edits attempted; this is a session-note artifact).
- ✗ Does **not** kill any process (G1/G2/G3/G4 all surface operator-only kill recommendations).
- ✗ Does **not** copy this artifact to the prescribed `agent-logs/` path (orchestrator-owned per U3).
- ✗ Does **not** redefine any rule in R1–R10, D1–D5, U1–U9, W1–W5.
- ✗ Does **not** mutate `.claude/state/` or `.planning/plan-approved/`.
- ✗ Does **not** retire or rewrite any memory feedback file.
- ✗ Does **not** invoke `git rebase --abort` or any git-mutation while Hermes is active (verified Hermes alive at lane start).

## Suggested next-tick prompts (one at a time; do NOT chain)

Predecessor lanes already shipped Prompts A–N (recovery-governance-1, governance-loop-3) and O–T (recovery-scoreboard-1 + control-synthesis-1). The G-series implies these new prompts. **Strongest single recommendation: Prompt U** — Hermes-active is fresh evidence today and unaddressed.

### Prompt U — Land G1 (Hermes-active dispatch suppression) as a dispatcher pre-flight

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: hermes-active-preflight-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/hermes-active-preflight-plan-1.md (fallback `docs/sessions/...` per G6)
> Hard gates: do not destructively reset/clean; isolated worktrees; no outreach; no self-approval; no `status:plan-approved` changes; no unapproved implementation; `GIT_OPTIONAL_LOCKS=0`; redact secrets. **Planning only.**
> Task: Read G1 in `docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md`. Identify the dispatcher entry point (likely `provider-autofeed-monitor/classify_and_launch.sh`). Spec a pre-dispatch shell check: `pgrep -af 'git (rebase|stash push|merge|reset|switch)' | grep -v ' grep '`; if non-empty AND any matched PID's CWD or argv references `workspace-hub`, hold dispatch and emit telemetry per G1's action clause. Map to enforcement-gradient L2 (script) per `.claude/rules/patterns.md`; promote to L3 (hook on `pre-merge-commit`) once the script proves quiet. Document the 60s-quiescence retry, the 2-hold STOP, and the operator-confirmation contract. Reference `feedback_hermes_active_preflight_check.md`. Do NOT touch the wrapper. Exit: 1-page plan + GitHub issue draft (do NOT open the issue).

### Prompt V — Land G4 (cross-run codex zombie aggregator) before next codex relaunch

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: codex-zombie-aggregator-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/codex-zombie-aggregator-plan-1.md (fallback `docs/sessions/...` per G6)
> Hard gates: same as Prompt U.
> Task: Read G4 in this lane and U7/U8 in 114355-loop-3. Spec a pre-codex-dispatch shell check: `pgrep -af 'codex exec' | wc -l`; if ≥5, refuse and surface Prompt-Q-class operator action (host CLI version verification). Compose with R1 (codex version gate) without redundancy — R1 checks the dispatcher host's installed version; G4 checks the process residue. Map to L2; co-locate with the Prompt-L spec (`scripts/enforcement/check-lane-dispatch-dedupe.sh`) so it's a single dispatcher pre-flight script with multiple gates. Do NOT modify any wrapper. Exit: 1-page plan + diff sketch.

### Prompt W — Operator-host action: verify Hermes/autofeed coexistence story

> **Owner:** operator on dispatcher host (NOT a lane).
> **Action:** confirm whether Hermes is *intended* to run concurrent with autofeed dispatch (in which case G1 + a Hermes-side worktree migration are both needed) OR whether Hermes is supposed to halt while autofeed is firing. Read `feedback_hermes_active_preflight_check.md` and any Hermes config under `~/.claude/projects/`. Decide between (a) "halt autofeed during Hermes" (set `cron-stop.flag` + add a Hermes-end hook to clear it), (b) "halt Hermes during autofeed" (Hermes scheduler skip-if-cron-active), (c) "isolate via worktree" (Hermes always operates in `.claude/worktrees/hermes/` so neither blocks the other). Write decision to `docs/governance/hermes-autofeed-coexistence.md` with rationale.
> **Hard gate:** none (host-local, no GitHub mutation).

### Prompt X — Wire G7 (plan past-tense drift detector) into review lanes

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: plan-past-tense-detector-plan-1
> Result file: per G6 canonical naming.
> Hard gates: same as Prompt U.
> Task: Read G7 in this lane and `feedback_plan_past_tense_artifact_claims.md`. Spec a pre-review shell check that runs over any planning artifact a review lane is about to consume. Provide regex patterns, false-positive suppression rules (e.g., past-tense in headings like "Recently merged" sections), and the cross-check against `git log`/`gh`. Map to L2 (script callable from review wrappers) per `.claude/rules/patterns.md`. Do NOT modify any review wrapper in this lane. Exit: plan with file list, change shape, sample pass/fail cases.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`. No git mutations attempted. (Hermes is mid-rebase per pgrep — G1 evidence; this lane explicitly did NOT attempt any git op while Hermes active.)
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — read-only Bash only (`pgrep`, `test -f`).
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; no comments; no labels).
- ✓ No outreach drafts.
- ✓ No `status:plan-approved` label changes (U6 satisfied).
- ✓ No `.planning/plan-approved/<issue>.md` markers written or removed.
- ✓ No source-file edits; no isolated worktree created.
- ✓ No secrets emitted (no API keys, tokens, PII).
- ✓ U3 satisfied: this lane's `.lane-state.json` (when written by the wrapper) should record `status: "completed-fallback"`, `result_path_actual: docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md`, `result_path_prescribed: agent-logs/provider-autofeed-20260430-125920/results/claude-governance-recovery-3.md`, `awaiting_orchestrator_copy: true`.
- ✓ D3 satisfied: extends prior R/D/U/W with new `G` prefix; does not redefine any prior rule.
- ✓ D4/G6 satisfied: single canonical artifact at `docs/sessions/2026-04-30-provider-autofeed-125920-claude-governance-recovery-3.md` (canonical naming per G6 — no `-FALLBACK`/`-result` suffix).
- ✓ U2 satisfied: planning/specification only; no implementation. G-rules are *prescriptive specs*; landing them requires Prompts U/V/X (planning) plus user approval.
- ✓ U9 satisfied: Prompts U/V/X reference GitHub issue drafts but issue creation is operator-owned.
- ✓ G1 self-honoring: this lane did NOT dispatch any subagent or commit while Hermes was active. The lane only emitted a session-note artifact.
- ✓ Memory-aligned: cites `feedback_hermes_active_preflight_check.md` (G1 backbone), `feedback_codex_cli_0_124_upstream_regression.md` (G4 backbone), `feedback_lane_result_path_outside_sandbox.md` (recurrence #7 → ENV-MISMATCH), `feedback_plan_past_tense_artifact_claims.md` (G7 backbone), `feedback_codex_sustained_major_loop.md` (G8 backbone), `feedback_never_offer_to_self_label_plan_approved.md` (U6 verbatim), `project_issue_2460_approval_binding.md`, `feedback_check_parallel_work.md`.

## Evidence appendix — what backed every G-rule

| G-rule | Backing evidence |
|---|---|
| G1 | Live `pgrep -af 'git (rebase\|stash\|merge\|reset\|switch)'` at 13:11Z ⇒ 3 active git mutations (PIDs 2190414, 2193359, 2204239) on `workspace-hub` while sibling lanes were dispatching. `feedback_hermes_active_preflight_check.md`. |
| G2 | Sibling control-synthesis-1 §1b ("launch_replacements.sh wrappers ... 90+ min ... Not a bug; just long-lived"). 114355-recovery-scoreboard-1 W1–W4. |
| G3 | Sibling control-synthesis-1 §3 W5 (run 073439 zombie wave at 5.5h+); 114355-recovery-scoreboard-1 W1–W4. |
| G4 | Live `pgrep -af 'codex exec'` at 13:11Z ⇒ 13+ codex PIDs alive across runs 073439 + 114355 (PIDs 2145230/2145244/2145246/2145255/2145256/2145258/2145296/2145299/2145342/2172737). `feedback_codex_cli_0_124_upstream_regression.md` (#2479). |
| G5 | 114355-loop-3 §"Behavioral deltas" point 2 (gemini removed entirely while codex regression unresolved → structural inversion). 111336-recovery-governance-1 §minimum-active-provider yields. |
| G6 | `docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` and `2026-04-30-claude-stream-plan-hardening-3-result.md` use different suffix conventions for the same artifact class. 114355-loop-3 D4 + Prompt N. |
| G7 | `feedback_plan_past_tense_artifact_claims.md`. |
| G8 | `feedback_codex_sustained_major_loop.md` (#2045, #2289 anti-pattern). |

## Concurrency snapshot — 2026-04-30T13:11Z–13:13Z

| Run | Status |
|---|---|
| 073439 | zombie wave; 5.5h+ old; 1+ codex PID alive (2172737) |
| 102314 | classify_and_launch + relaunch_replacements + gemini-flash lane alive |
| 104814 | codex-fdclosed yield-test still in flight |
| 111336 | 9 codex stdin/json/arg-devnull lanes hung; gemini removed; **PID 2128357 (codex from 111336) cited alive in 114355-loop-3, no longer in current pgrep ⇒ likely reaped or ID rolled** |
| 114355 | 6 launch_replacements.sh wrappers alive ~90 min waiting on codex children (PIDs 2145230+); claude lanes already shipped to docs/sessions/ |
| 120344 | gemini-pro-engineering-standards-3 reaped cleanly (canary for wrapper-fix) |
| 125920 | this run; 3 lanes alive (control-synthesis-1=2188200, plan-review-hardening-2=2188219, governance-recovery-3=this lane wrapper at 2188235) |
| **Hermes** | **Active**: PID 2190414 `git rebase --autostash --onto df3b416...`, PID 2193359 `git merge FETCH_HEAD`, PID 2204239 `git rebase --abort` |

## STARTED / FINISHED

- **STARTED:** 2026-04-30T13:11:49Z (first tool call: `date -u`).
- **FINISHED:** 2026-04-30T~13:18Z (this artifact written).
- **Out-of-band copy required (U3):** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-125920/results/claude-governance-recovery-3.md`. Until that copy lands, lane status is `completed-fallback`, not `completed`.
- **Sibling lanes at write time:** `claude-control-synthesis-1` already finalized (artifact at `docs/sessions/.../125920-claude-control-synthesis-1.md`); `claude-plan-review-hardening-2` (PID 2188219) still in-flight at write time — expected to land under `docs/sessions/` per the FALLBACK convention (G6 will canonicalize the name on next-tick).
- **Strongest single follow-up:** Prompt U (land G1 as dispatcher pre-flight) — Hermes-active is fresh, observable, and unaddressed.

## Provenance

| Source | Output captured |
|---|---|
| `pgrep -af 'provider-autofeed' \| grep -oE 'provider-autofeed-[0-9TZ-]+' \| sort -u` | 7 distinct run IDs (§Live evidence) |
| `pgrep -af 'provider-autofeed' \| wc -l` | 127 PID lines |
| `pgrep -af 'codex exec'` | 13+ PIDs across runs 073439 + 114355 |
| `pgrep -af 'git (rebase\|stash push\|merge\|reset\|switch)'` | 3 Hermes PIDs (G1 evidence) |
| `pgrep -af 'provider-autofeed-20260430-125920'` | 3 lanes alive in current run |
| `test -f .planning/cron-stop.flag` | absent |
| Read of predecessor scoreboards | 5 files (cited at top) |
| Memory consulted | `feedback_hermes_active_preflight_check`, `feedback_codex_cli_0_124_upstream_regression`, `feedback_lane_result_path_outside_sandbox`, `feedback_plan_past_tense_artifact_claims`, `feedback_codex_sustained_major_loop`, `feedback_never_offer_to_self_label_plan_approved`, `project_issue_2460_approval_binding`, `feedback_check_parallel_work` |

No log/prompt body was read from `agent-logs/` (sandbox-blocked). All evidence is from: (a) `pgrep -af` + `test -f` over the host process/filesystem, (b) Read of predecessor session artifacts inside `docs/sessions/`, (c) cited memory feedback files.
