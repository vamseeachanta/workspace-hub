# Provider-Autofeed Governance Rules — `claude-governance-rules-3` lane (run 20260430-073439)

> **Lane ID:** `claude-governance-rules-3`
> **Run:** `provider-autofeed-20260430-073439`
> **Generated:** 2026-04-30 (UTC; lane STARTED at first tool call ~`docs/sessions/` write time)
> **Author:** `claude-governance-rules-3` (Opus 4.7, 1M context)
> **Task per dispatch prompt:** *codify non-consuming stall signatures and dedupe rules into next-tick operator checklist.*
> **Predecessor governance artifacts cited (do NOT re-emit; this lane EXTENDS):**
> - `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` — canonical contract (§3 floor, §4 health, §5 stall signatures, §6 recovery, §7 routing, §8 cron fragments, §9 operator procedures)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` — Prompts A-F (operator-host preflight + per-failure-mode follow-ups)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md` — bounded rules R1–R10 (version gate, sandbox preflight, fan-out cap, demotion, concurrency, heartbeat, lane-state, content-trigger quarantine, wrapper divergence, yield cap)
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-governance-loop-3.md` — dedupe D1–D5 + unsafe-transition gates U1–U9
> - `docs/sessions/2026-04-30-provider-autofeed-114355-claude-recovery-scoreboard-1.md` — wrapper-drift table (W1–W4) + corrections C1–C5 (three artifact-path conventions in active use)

## ENV-MISMATCH banner — read this first

Sandbox failure of the same shape that recurred ≥5× across 2026-04-30 runs. The dispatch prompt's prescribed result path is outside this lane's sandbox; `Read`/`Write`/`Glob` of `/mnt/local-analysis/agent-logs/` blocked at the tool layer (verified at lane start: `Glob` of run dir denied, `Write` of result-path denied with "File has not been read yet" + `Read` denied with permission error).

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-073439/results/claude-governance-rules-3.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read`/`Write` of `agent-logs/**` | **blocked** at tool layer |
| `Glob` of `agent-logs/**` | **blocked** at tool layer (this lane has stricter sandbox than 114355-recovery-scoreboard-1, where `Glob` of `agent-logs/` was permitted) |
| What still works | `Read`/`Write` inside `workspace-hub`; `Grep`/`Glob` against repo paths under `docs/`, `.claude/` |
| Canonical durable output | **THIS document** under `docs/sessions/` per `feedback_lane_result_path_outside_sandbox.md` |

**Operator action (unchanged across the day's recurrences):** widen Read/Write allowlist for `agent-logs/**`, OR move prescribed paths inside `workspace-hub`, OR have the orchestrator copy this artifact to the prescribed path out-of-band. Recurrence is now well past the prose-memory load-bearing point — promote to L3 dispatcher hook per Prompt K (114355-governance-loop-3) and Prompt O (114355-recovery-scoreboard-1).

## Scope of THIS lane

The dispatch prompt names two specific deliverables and one synthesis target:

1. **Non-consuming stall signatures** — a class of stall the predecessor §5 (recovery contract) and R6 (heartbeat probe) underweight. These are stalls where the lane **never spent budget** — no LLM round-trip, no provider invocation, sometimes no log mtime update — yet path-presence makes them look ✅. Treating them as completions inflates yield and starves the floor. Codified below as **NC1–NC6**.
2. **Dedupe rules** — extends D1–D5 (114355-governance-loop-3) with four new rules (**D6–D9**) that close gaps surfaced by C1–C5 corrections in 114355-recovery-scoreboard-1: multi-convention artifact paths, wrapper-pre-written stubs, cross-run task fingerprinting, and stale-stub vs real-content arbitration.
3. **Next-tick operator checklist** — a single ordered, bounded checklist (§NCK) the operator (or a future watchdog) runs at every dispatch tick. Synthesizes contract §4/§5/§9, R1–R10, D1–D9, U1–U9, and NC1–NC6 into ten action steps with O(1)/O(N-glob) checks and explicit fail-closed clauses.

> **Lane discipline reminder.** No rule chains; no rule mutates GitHub; no rule implements an unapproved issue. U2 + U6 + U9 in the predecessor lane are honored in full. Each new rule below carries the same shape: bounded precondition, single bounded check, explicit no-op clause, citation, retire-when.

## Non-consuming stall signatures (NC1–NC6)

These signatures detect lanes that **path-present** as ✅ but burned **zero budget on the actual provider**. Distinct from §5 of the contract, which catches stalls *during* execution.

### NC1 — Wrapper-pre-written STARTED stub, no provider invocation

| Field | Value |
|---|---|
| **Match shape** | Result file's first non-blank line is `STARTED <iso8601>` (or `# <lane-id>\nSTARTED <iso8601>`) AND file size ≤ `STUB_BYTES_MAX` (recommend 512 B) AND no subsequent content beyond the stub block. |
| **What it means** | Run-120344-shape wrapper used `printf 'STARTED %s\n' "$(date -u ...)" > "$RUN/results/$LANE.md"` at lane spawn. The lane process either (a) never began consuming, (b) crashed before first write, or (c) is still running but has produced nothing. Distinguishing (a/b/c) requires a process-table check. |
| **Distinct from** | "stalled-no-emission" (R6) — that requires log mtime *was* fresh and consumed time. NC1 is the case where the wrapper, not the lane, wrote everything we see. |
| **Operator check** | (i) `wc -c < <result-file>` → if ≤ 512, candidate stub. (ii) `pgrep -af '<lane-id>'` → confirm whether the lane process exists. (iii) `stat -c %Y <log-file>` vs `<result-file>` mtime → if log mtime ≪ result mtime by ≥ `WINDOW_S`, the wrapper wrote the result then the provider never produced log output. |
| **Action** | Reclassify as `delivered-stub-only` (a degraded variant of U5's `delivered-presence-only`). Do NOT count toward the §3 floor. Drive recovery as if the lane were stalled. |
| **Citation** | 114355-recovery-scoreboard-1 §"Wrapper drift" (run-120344's pre-write STARTED stamp); U5 (presence ↛ succeeded). |
| **Retire when** | The wrapper's stub bytes are documented and the watchdog can subtract them from "real content" cleanly (i.e. byte-floor is set per the wrapper variant's stub size). |
| **Bound** | One `wc -c` + one `stat` + one `pgrep -c` per lane finalize. |

### NC2 — Sandbox-init refusal with single-line BLOCKED log

| Field | Value |
|---|---|
| **Match shape** | Log file last (and often only) line is `BLOCKED: <reason>` (per recovery contract §8.1 instruction). Result file may or may not exist; if it exists, it's stub-shape (NC1). |
| **What it means** | Lane recognized at startup that its sandbox cannot satisfy the dispatch (e.g. cannot `Read` the prompt at the prescribed path; cannot `Write` to `agent-logs/`). It exited cleanly without invoking the provider. **Zero budget burn.** |
| **Distinct from** | NC1 — NC2 has explicit log evidence of a refusal-at-init; NC1 may be silent. |
| **Operator check** | `tail -1 <log-file>` matches `^BLOCKED: ` (or `^DEGRADED: ` for the Gemini variant per recovery contract §8.3). |
| **Action** | Recovery is the same as the corresponding `feedback_*` for the sandbox class (e.g. `feedback_lane_result_path_outside_sandbox` if reason mentions a path; `feedback_codex_sandbox_no_execution` if reason mentions exec). **Do NOT relaunch on the same provider with the same prescribed path** — the cause is structural. |
| **Citation** | Recovery contract §8.1 ("If you hit a sandbox block, emit a single line `BLOCKED: <reason>` and exit; do not retry."). |
| **Retire when** | Sandbox allowlists are codified per Prompt K and the dispatcher pre-rewrites prescribed paths (no lane should *need* to emit BLOCKED). |
| **Bound** | One `tail -1` per lane finalize. |

### NC3 — `permission_denied` on first prompt-read attempt

| Field | Value |
|---|---|
| **Match shape** | Log body contains `permission_denied` OR `Permission denied (os error 13)` OR `EACCES` AND no subsequent line evidences a provider invocation banner (e.g. no `[Claude]`, `codex-cli/`, `Gemini CLI` startup). |
| **What it means** | Tool-layer sandbox refused the prompt-read; the agent's main-loop tool call failed before the provider was ever consulted. |
| **Distinct from** | NC2 (NC3 is a tool-layer error, not a lane-level voluntary refusal). |
| **Operator check** | `grep -E 'permission_denied|EACCES|Permission denied' <log>` returns ≥1 hit AND `grep -E '\[Claude\]|codex-cli/|Gemini CLI' <log>` returns 0. |
| **Action** | Same as NC2. The path that was denied is structural; relaunching loops. |
| **Citation** | Recovery contract §5.3 (Claude `permission_denied` signature, observed 2026-04-30); this lane's own ENV-MISMATCH banner (denied `Read` of own prompt at lane init). |
| **Retire when** | NC2 retire condition holds. |
| **Bound** | Two greps per lane finalize. |

### NC4 — Codex-CLI 0.124 stdin-hang manifesting as zero log growth past WINDOW_S

| Field | Value |
|---|---|
| **Match shape** | Codex lane log header shows `codex-cli/0.124.\d+` AND `Reading from stdin` (or equivalent banner), and the log has not grown by ≥ `WINDOW_S` (default 180s). Result file is absent or stub-shape. PID may still be alive (the process is wedged on stdin read). |
| **What it means** | Upstream regression `feedback_codex_cli_0_124_upstream_regression`. Lane is alive but **not consuming the prompt** — the read syscall has not returned. From a budget standpoint this *can* burn wall-clock but never invokes the LLM. |
| **Distinct from** | "stalled-no-emission" generally — NC4 names the specific regression and is fail-closed at provider level (do not relaunch codex until host CLI ≠ 0.124). |
| **Operator check** | `head -3 <log>` matches `codex-cli/0\.124`; `stat -c %Y <log>` gives age ≥ WINDOW_S; `pgrep -af 'codex exec.*<lane-id>'` returns ≥1 PID. |
| **Action** | Refuse codex relaunch globally (recovery contract §7.3 banned-versions latch). Re-route task to Claude or Gemini per §7.2 soft preferences. **Live evidence (114355-recovery-scoreboard-1):** PID 2128357 was still alive ~33 min after dispatch — host downgrade has not landed; this NC stays hot until [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) closes. |
| **Citation** | `feedback_codex_cli_0_124_upstream_regression`; recovery contract §5.1 first row + §7.3; predecessor 111336-loop-4 R1; U7 (codex result-file ↛ "executed"). |
| **Retire when** | `codex --version` on dispatcher host parses as ≥ 0.125 (or ≤ 0.123) AND a single sanity prompt yields. |
| **Bound** | One `head -3` + one `stat` + one `pgrep` per codex lane finalize. |

### NC5 — Wrapper-spawn race: result-file mtime *predates* lane-PID start time

| Field | Value |
|---|---|
| **Match shape** | The result file exists; its mtime is **earlier than** the start time of any process matching the lane name (or there is no matching PID and the result file is < 1 KiB). Implication: the wrapper-stamped stub is the only artifact and the lane process either never started or already exited. |
| **What it means** | Same family as NC1 but explicitly time-ordered. Useful when the wrapper variant is unknown — instead of relying on stub-byte size, this rule uses the temporal ordering. |
| **Operator check** | `stat -c %Y <result-file>` vs `ps -o lstart= -p $(pgrep -f '<lane-id>')` (formatted to epoch). If result-mtime < pid-start OR pid is empty: stub-only. |
| **Action** | Same as NC1. |
| **Citation** | 114355-recovery-scoreboard-1 §"Wrapper drift" — runs without 120344-shape pre-write fall through to NC1's byte heuristic; runs with it need NC5 to stay correct. |
| **Retire when** | The wrapper-variant catalog is durable and per-variant stub size is exact (then NC1 byte-floor is sufficient). |
| **Bound** | One `stat` + one `ps` per lane finalize. |

### NC6 — Lane-process not in process table AND result file empty/stub

| Field | Value |
|---|---|
| **Match shape** | `pgrep -f '<lane-id>'` returns 0 AND result file size is 0 or stub-shape AND log file is absent or empty. |
| **What it means** | The lane was dispatched but the wrapper never forked the lane process (or it exited with `Killed`/`SIGTERM` before producing anything). **Pure non-consuming case** — easiest to detect, often the most diagnostic for orchestrator bugs. |
| **Distinct from** | NC1 (which requires a stub-shape result file present); NC6 also catches "no result file at all". |
| **Operator check** | (i) `pgrep -c -f '<lane-id>'` → 0. (ii) `wc -c < <result>` → 0 (or file absent). (iii) `wc -c < <log>` → 0 (or file absent). |
| **Action** | Inspect orchestrator logs (`/mnt/local-analysis/agent-logs/provider-autofeed-monitor/snapshot-*.md` or run-tick output) for the lane's spawn line. If the spawn line is absent: dispatcher dropped the lane; relaunch with a D1-bumped name. If the spawn line is present but the PID did not survive: capture exit code if available, classify as orchestrator-side failure, surface to operator before relaunching. |
| **Citation** | 114355-recovery-scoreboard-1 corrections C1/C3 ("missing-result-file signal is dominated by naming-convention drift, not by actual stalls" — but in NC6's narrower case, the lane truly never started). |
| **Retire when** | R7 (`.lane-state.json` per lane) lands and records `dispatcher_spawn_ts` distinctly from `lane_first_write_ts`; then the absence of `lane_first_write_ts` is the canonical signal. |
| **Bound** | One `pgrep` + two `wc -c` per lane finalize. |

## Dedupe rules — D6–D9 (extend D1–D5)

Each refines a gap surfaced by 114355-recovery-scoreboard-1 corrections C1–C5 or by the run-120344 wrapper change.

### D6 — Path-convention enumeration before D4 collision check

| Field | Value |
|---|---|
| **Precondition** | A lane is about to write its fallback artifact (per ENV-MISMATCH) and needs to verify D4 ("one canonical artifact per (run, lane)"). |
| **Check** | Glob ALL of these conventions for `<run>` × `<lane>`: `docs/sessions/2026-04-30-*<run>*<lane>*.md`; `docs/sessions/2026-04-30-*<lane>*-FALLBACK.md`; `docs/sessions/2026-04-30-*<lane>*-result.md`; `docs/plans/overnight-results/provider-autofeed-*<run>*<lane>*.md`; `docs/handoffs/provider-autofeed-*<run>*/<lane>*.md`; `docs/governance/staging-autofeed-recovery-contract/<lane>*.md`. |
| **Action when matched (any path)** | Append `## Re-run continuation` to the first-by-mtime existing file rather than create a sibling. If the prior write is in a different convention than this lane's intended write, append to the prior convention's file (do not migrate it). |
| **No-op clause** | If zero of the six conventions match, write to `docs/sessions/<date>-<run>-<lane>.md` (the convention this lane prefers). |
| **Citation** | 114355-recovery-scoreboard-1 C2 (three conventions in active use); C5 (handoffs/ adds a fourth). D4 only enumerated `docs/sessions/`. |
| **Retire when** | A single canonical convention is enforced by the dispatcher (Prompt N from 114355-governance-loop-3 lands) and the older artifacts are consolidated. |
| **Bound** | Six Glob calls per fallback-artifact write. |

### D7 — Cross-run task-fingerprint dedupe (independent of lane name)

| Field | Value |
|---|---|
| **Precondition** | About to dispatch lane `<lane-name>` whose prompt is task-class `<task-class>` (e.g. `adversarial-review-2564`, `governance-recovery-contract`, `gtm-risk-scan`). Lane names rotate integers; the task class is the stable fingerprint. |
| **Check** | Compute `task_class` by stripping provider prefix and integer suffix from `<lane-name>`. Glob across all artifact path conventions (D6) for files whose lane name matches `*<task_class>*` OR whose body header names the same task. Read the most recent by mtime; check whether the task is `completed` (R7 status) or `delivered-presence-only` (U5) or `delivered-stub-only` (NC1). |
| **Action when matched (`completed` within last 24 h)** | Refuse new dispatch unless the orchestrator passes `--force` flag with operator approval (NOT lane self-approval — U6). Emit `BLOCKED: task <task_class> completed in <run-id> at <ts>; lane=<prior-lane>; artifact=<path>`. |
| **Action when matched (`delivered-presence-only`/`delivered-stub-only`)** | Allow dispatch but on a **different provider** (per recovery contract §7.2). Same provider would likely re-stall the same way. |
| **No-op clause** | If no prior task in any convention's enumeration, dispatch normally. |
| **Citation** | 114355-recovery-scoreboard-1 correction C1 (`adversarial-review-2564` was complete under `docs/plans/overnight-results/` while named "stalled" by the predecessor scoreboard). D2 caught lane-class within a 24 h window but missed cross-convention completions. |
| **Retire when** | A unified completion ledger exists (R7 + a single artifact-path convention). |
| **Bound** | One task-fingerprint extraction + 6 Globs (D6 reuse) per dispatch decision. |

### D8 — Stub-vs-real-content arbitration (resolves NC1 + NC5 cases)

| Field | Value |
|---|---|
| **Precondition** | Multiple artifacts exist for the same `(run, lane)`: a stub at the prescribed `agent-logs/` path AND real content at a `docs/sessions/`/`docs/plans/overnight-results/`/`docs/handoffs/` fallback. |
| **Rule** | The artifact whose first non-empty paragraph contains substantive content (≥ 1 KiB body excluding stub header) is **canonical**. The stub is informational only; consumers MUST NOT count the stub as a delivery. |
| **Check** | For each artifact: (i) `wc -c <file>` → exclude if ≤ `STUB_BYTES_MAX` (512 B); (ii) `head -50 <file>` → exclude if it terminates after the STARTED block. |
| **Action** | Update consumer-side aggregation to dereference the stub to the canonical fallback. The orchestrator's out-of-band copy step should overwrite the stub with the fallback's content (not the other way). |
| **No-op clause** | If only one artifact exists, it is canonical regardless of size (even a stub counts as "presence-only" per U5; D8 only fires when there's a choice). |
| **Citation** | NC1 + NC5; 114355-recovery-scoreboard-1 §"3 conventions" — the stub at the prescribed path co-exists with the real artifact at the fallback for *every* ENV-MISMATCH lane today. Without D8, scoreboards double-count. |
| **Retire when** | The wrapper either (a) does not pre-write a stub, or (b) pre-writes the stub and copies the fallback in atomically, eliminating the divergence. |
| **Bound** | Per-(run, lane), one `wc -c` + one `head -50` per candidate artifact. |

### D9 — Watchdog-emitted FLOOR_BREACH alert dedupe

| Field | Value |
|---|---|
| **Precondition** | The recovery-contract watchdog (§8.5) is about to emit a `FLOOR_BREACH <provider>` alert. |
| **Check** | Read the prior tick's watchdog output (cron typically pipes to `/var/log/autofeed-watchdog.log` or equivalent). Compute `(provider, breach_count)` for last 30 min. If the same `(provider, breach_count_band)` has already fired ≥3 times in the window, the breach is **stuck** — no new info per re-emission. |
| **Action when matched** | Emit a single suppressed-form alert: `FLOOR_BREACH_SUSTAINED <provider>: ${N} ticks; see prior alerts at <ts1, ts2, ts3>` instead of repeating the full payload. After 6 sustained ticks, escalate: `FLOOR_BREACH_ESCALATE <provider>: contract §9.1 operator action required`. |
| **No-op clause** | First or second occurrence in 30 min: emit normally. |
| **Citation** | `feedback_email_cross_noise.md` (alert deduplication is good ops hygiene); recovery contract §9.1 (operator procedure assumes one alert = one action). |
| **Retire when** | Operator alert sink natively dedupes (e.g. PagerDuty/OpsGenie ack window). |
| **Bound** | One log-tail + one regex per cron tick. |

## Next-tick operator checklist (NCK1–NCK10)

Single ordered checklist, each step bounded and named; intended for a **human operator at every dispatch tick** *or* for a watchdog-style script that walks the same sequence. Steps fail-closed: if a precondition is unmet, the operator must record the breach and **not** proceed to dispatch new work on the affected provider.

> **Convention.** Every step ends with a *passes-iff* clause and a *fail-closed* clause. The operator advances only when *passes-iff* is true; else the lane stays paused until manual escalation.

### NCK1 — Sandbox preflight (R2 + U3 enforcement)

- **Action:** Confirm the dispatcher's planned `Result file:` path for every queued lane is under `/mnt/local-analysis/workspace-hub/**` (or the lane's tier sandbox root). If `agent-logs/**`, **rewrite** the prompt to emit a `docs/sessions/<date>-<run>-<lane>.md` fallback per `feedback_lane_result_path_outside_sandbox` and mandate an out-of-band copy after lane finalize.
- **Passes-iff:** Every queued lane's result path is sandbox-resident OR has the rewrite-and-copy pair installed.
- **Fail-closed:** If even one queued lane has a path outside the sandbox without rewrite, do not dispatch the run; surface to operator. (Recurrence is now ≥5 in 24 h.)

### NCK2 — Codex-CLI version preflight (recovery contract §7.3)

- **Action:** On the dispatcher host, run `codex --version`. Compare against `CODEX_CLI_BANNED_VERSIONS = ["0.124.0", "0.124.1", "0.124.2"]`.
- **Passes-iff:** Version ≤ 0.123 OR ≥ 0.125 AND not in banned set.
- **Fail-closed:** Skip all `codex-*` lanes for this tick. Re-route via routing §7.2 soft preferences. Do NOT attempt downgrade from the dispatcher process — host privilege required (Prompt A from 111336-recovery-governance-1). Emit `[autofeed] codex skipped: CLI 0.124.x banned (#2479)` in tick log.

### NCK3 — Hermes & background-rebase preflight

- **Action:** `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` AND `pgrep -af 'hermes'`.
- **Passes-iff:** No active Hermes cleanup loop AND no concurrent rebase/merge that touches `main` of a workspace any lane plans to commit into.
- **Fail-closed:** Either (a) defer dispatch by one tick, or (b) dispatch only into isolated worktrees (per `feedback_hermes_active_preflight_check` and `feedback_multi_agent_commit_serialization`). Never dispatch lanes that share a non-worktree HEAD with an active Hermes loop.

### NCK4 — Concurrent-runs sweep (parallel-work check)

- **Action:** `pgrep -af 'provider-autofeed'`. Group by run-id. Note alive-but-old runs (≥ 60 min since dispatch with stale log mtime).
- **Passes-iff:** At most one alive run per (run-id × lane-name) pair; no zombie runs holding `agent-logs/.../current-run.txt` lock.
- **Fail-closed:** If a zombie run is detected (e.g. PID 2086414 alive for run `102314` ~117 min per 114355-recovery-scoreboard-1), do NOT relaunch any lane in that run-dir until `current-run.txt` rotates. (W2 race per 114355-recovery-scoreboard-1: late relaunches re-read `current-run.txt` and write into the wrong run-dir.)

### NCK5 — Cross-provider triangulation budget check

- **Action:** Count *available* providers per `recovery-contract §3` floor: claude (≥3), codex (gated by NCK2), gemini (gated by `GEMINI_CLI_TRUST_WORKSPACE`).
- **Passes-iff:** ≥2 providers above the floor for any lane class needing triangulation (cross-review, adversarial review, multi-author plans).
- **Fail-closed:** If only 1 provider is available, fall back to single-author r3 with provenance per `feedback_permission_gate_blocks_cross_review` — do NOT skip the review entirely, and do NOT pad the lane count with same-provider variants (`feedback_codex_sustained_major_loop` anti-pattern).

### NCK6 — Path-convention enumeration of prior writes (D6 + D7 application)

- **Action:** For every queued lane, enumerate the six conventions in D6. For every existing artifact, classify as `completed` / `delivered-presence-only` / `delivered-stub-only` / `partial-with-redo-marker`.
- **Passes-iff:** No queued lane is a duplicate of an already-`completed` task (D7) AND no queued lane will collide with an existing artifact path (D6).
- **Fail-closed:** Apply D7's "completed" branch (refuse with `BLOCKED:`); apply D6's "append continuation" branch for collisions. Bump lane integer suffix to next free if the prompt body differs (D1).

### NCK7 — Stub-vs-real-content arbitration (D8 + NC1/NC5 application)

- **Action:** For every artifact discovered in NCK6, run D8 arbitration. If a stub at `agent-logs/.../results/` co-exists with real content at a fallback path, mark the stub as informational and the fallback as canonical. If the orchestrator owns out-of-band copy, ensure the next copy step writes the fallback over the stub (not vice versa).
- **Passes-iff:** No `(run, lane)` has two artifacts disputing canonicality.
- **Fail-closed:** Pause out-of-band copy for that lane; surface the divergence to the operator with both paths, byte sizes, and mtimes.

### NCK8 — Provider-floor evaluation (recovery contract §3 + watchdog §8.5)

- **Action:** Run the `autofeed-watchdog.sh` shape from §8.5. Count `LIVE_PER_PROV` per provider over the active run.
- **Passes-iff:** Each provider ≥ 3 live per recovery contract §3 floor.
- **Fail-closed:** If a provider is below floor, run NCK9 (stall-signature scan) before deciding recovery. Apply D9 dedupe to alert emission.

### NCK9 — Stall-signature scan (recovery contract §5 + NC1–NC6)

- **Action:** For each lane below floor or marked stale by mtime: run §5 regex scans (per provider) AND the NC1–NC6 checks. Classify each lane as one of: `useful` / `stalled-no-emission` / `delivered-presence-only` / `delivered-stub-only` (NC1) / `init-blocked` (NC2/NC3) / `codex-stdin-hang` (NC4) / `wrapper-race` (NC5) / `never-started` (NC6) / `unknown`.
- **Passes-iff:** Every lane has a definite class (no `unknown`).
- **Fail-closed:** For `unknown`, capture the lane's last 500 log lines + result artifact (if any) into a fresh GitHub issue draft (do NOT open it — U9 + recovery contract §9.1) and surface to operator. Do NOT auto-relaunch unclassified lanes.

### NCK10 — Bounded recovery decisions (recovery contract §6 + R3 + R10 caps)

- **Action:** For each classified non-useful lane, apply the §6 recovery decision table, capped by:
  - `MAX_RELAUNCH_PER_LANE = 2` (3 total attempts).
  - R3 variant cap (no fan-out into provider-variant proliferation when the upstream regression is open — U8).
  - R10 yield cap (do not exceed the per-tick relaunch budget).
- **Passes-iff:** All recovery actions selected are within budget AND honor the routing constraints in §7.1 hard-blocks.
- **Fail-closed:** Mark the affected provider as **degraded** for `DEGRADE_LATCH_S = 1800` (30 min); emit `FLOOR_BREACH_ESCALATE` per D9 if this is the third sustained breach in the window. Do NOT auto-route work to surviving lanes beyond ceiling — that masks the gap (recovery contract §3).

## Rule-precedence integration

Layer the new NC- and D6–D9 rules onto the predecessor R/D/U precedence (114355-governance-loop-3 §"Rule precedence"):

| Order | Rule | Phase |
|---|---|---|
| 1 | U6 (self-label invariant) | dispatch |
| 2 | U2 (dual approval gate) | dispatch |
| 3 | NCK1 / R2 (sandbox preflight) | dispatch |
| 4 | NCK2 / R1 (codex version) | dispatch |
| 5 | NCK3 (Hermes/rebase preflight) | dispatch |
| 6 | NCK4 (concurrent-runs sweep) | dispatch |
| 7 | NCK6 + D6 + D7 (artifact-path dedupe) | dispatch |
| 8 | D1 (lane-name × prompt-hash dedupe) | dispatch |
| 9 | NCK5 + D2 (cross-run lane-class dedupe + triangulation budget) | dispatch |
| 10 | R3 / R10 (variant cap / yield cap) | dispatch |
| 11 | U8 (variant-fan-out → "exploration completed" gate) | dispatch |
| 12 | R4 (Gemini Pro demotion) | dispatch |
| 13 | R8 (content-trigger quarantine) | dispatch |
| 14 | R6 + U4 + NC4 (heartbeat / classification / codex stdin-hang) | tick (ongoing) |
| 15 | R7 (lane-state.json emission) | lane exit |
| 16 | NC1 / NC5 / NC6 (non-consuming stub detection) | lane exit / consumer aggregation |
| 17 | NC2 / NC3 (sandbox/permission init failures) | lane exit |
| 18 | NCK7 + D8 (stub-vs-real-content arbitration) | consumer aggregation |
| 19 | U5 / U7 (presence-only / codex result-file ↛ "executed") | consumer aggregation |
| 20 | NCK8 + NCK9 + NCK10 (floor → signatures → recovery) | watchdog tick |
| 21 | D9 (watchdog alert dedupe) | watchdog emission |
| 22 | D4 + D5 (artifact / issue-comment dedupe) | write-time |
| 23 | U9 (issue-body-draft ↛ issue-creation gate) | lane finalize |

## What this lane explicitly does NOT do

- ✗ Does **not** label any GitHub issue with `status:plan-approved` (U6; `feedback_never_offer_to_self_label_plan_approved`).
- ✗ Does **not** open any GitHub issue or PR (U9; recovery contract §9 promotion procedure unchanged).
- ✗ Does **not** post a `gh issue comment` (D5).
- ✗ Does **not** edit `classify_and_launch.sh`, `run_tick.sh`, `relaunch_replacements.sh`, `launch_replacements.sh`, or any provider wrapper (`submit-to-codex.sh`, `submit-to-gemini.sh`).
- ✗ Does **not** modify any file under `/mnt/local-analysis/agent-logs/` (sandbox-blocked anyway).
- ✗ Does **not** create a worktree (no source edits attempted).
- ✗ Does **not** retire or rewrite any memory feedback file.
- ✗ Does **not** mutate `.claude/state/` or `.planning/plan-approved/`.
- ✗ Does **not** copy this artifact to the prescribed `agent-logs/` path (orchestrator-owned per U3).
- ✗ Does **not** attempt to downgrade or test the codex CLI from this Bash tool (NCK2 + `feedback_codex_cli_0_124_upstream_regression` explicitly).

## Suggested follow-up lane prompts (ONE at a time; do NOT chain)

The 111336-loop-4 lane named Prompts G/H/I/J. The 114355-governance-loop-3 lane named K/L/M/N. The 114355-recovery-scoreboard-1 lane named O/P/Q/R/S. **This lane proposes T and U.** All hard-gate-safe; all bounded; each names exit conditions.

### Prompt T — Implement NCK1–NCK10 as a single watchdog script (planning only)

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: nck-watchdog-script-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/nck-watchdog-script-plan-1.md (fallback `docs/sessions/...` per ENV-MISMATCH; D6 enumeration applies)
> Hard gates: do not destructively reset/clean; isolated worktrees if any source edits; no outreach; no self-approval; no `status:plan-approved` changes; no unapproved implementation; `GIT_OPTIONAL_LOCKS=0`; redact secrets. **Planning only.**
> Task: Read NCK1–NCK10 + NC1–NC6 + D6–D9 in this artifact. Spec a single shell script `scripts/enforcement/autofeed-next-tick-checklist.sh` that the cron calls before every dispatch tick. The script's exit codes encode the fail-closed branch (e.g. 0 = pass, 64 = NCK1 sandbox-path breach, 65 = NCK2 codex banned, etc.). Map to enforcement-gradient L2 per `.claude/rules/patterns.md`. Identify whether to layer on top of `autofeed-watchdog.sh` (recovery contract §8.5) or replace it. Do NOT write the script — produce a 1-page plan including diff sketch, test cases (one per fail-closed branch), and a rollback note. Exit: result file with the plan.

### Prompt U — Audit the wrapper-stub byte-floor for D8 / NC1

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: wrapper-stub-byte-floor-audit-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-<next-run>/results/wrapper-stub-byte-floor-audit-1.md (fallback per D6)
> Hard gates: as Prompt T. **Reconnaissance only.**
> Task: From a host with read access to `/mnt/local-analysis/agent-logs/`, sample the result-file sizes of N=20 stub-only lanes across runs 100339, 102314, 104814, 111336, 114355, 120344, 073439. Compute the actual stub byte distribution per wrapper variant. Recommend an exact `STUB_BYTES_MAX` per variant (today's NC1 default of 512 B is a guess). Produce a small table mapping wrapper-variant → stub-byte-floor. Do NOT modify any wrapper. Exit: result file with the table + recommended NC1 update.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`.
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted (no source edits).
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; U9 satisfied for the issue draft implied in Prompts T/U — drafts only, not opened).
- ✓ No outreach drafts.
- ✓ No self-approval / no `status:plan-approved` label changes (U6 satisfied).
- ✓ No unapproved implementation — NC- and D-series and the NCK checklist are *prescriptive specs only*; landing them requires Prompt T (planning) plus `issue-planning-mode` skill plus user approval.
- ✓ No isolated worktree created — no source edits attempted; this document is a session-note artifact under `docs/sessions/`.
- ✓ No secrets emitted (no API keys, tokens, PII).
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md` (recurrence ≥5), `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_hermes_active_preflight_check.md`, `feedback_multi_agent_commit_serialization.md`, `feedback_permission_gate_blocks_cross_review.md`, `feedback_codex_sustained_major_loop.md`, `feedback_never_offer_to_self_label_plan_approved.md`, `feedback_email_cross_noise.md`, `project_issue_2460_approval_binding.md`, `feedback_check_parallel_work.md`, `feedback_inline_gh_issue_url.md`.
- ✓ Tool calls were bounded: `Read` of three predecessor session artifacts + the recovery contract; `Glob` on `docs/sessions/` and `docs/governance/` only (workspace-resident); no Bash calls to `agent-logs/**`.
- ✓ U3 satisfied: lane-state effective status is `completed-fallback` not `completed` until orchestrator out-of-band-copies this artifact to the prescribed path.
- ✓ D4 satisfied: prior `Glob 2026-04-30-*governance-rules*` returned no files — first canonical artifact for `(073439, claude-governance-rules-3)`.
- ✓ D6 satisfied: cross-convention enumeration (`docs/sessions/*`, `docs/plans/overnight-results/*073439*`, `docs/governance/staging-autofeed-recovery-contract/*`, `docs/sessions/*next-tick*`, `docs/sessions/*operator-checklist*`) returned no collisions.

## Evidence appendix — what backed every section

| Section | Backing evidence |
|---|---|
| ENV-MISMATCH banner | `Glob`/`Read`/`Write` against `/mnt/local-analysis/agent-logs/...` denied at lane init (verified by tool-layer permission errors, NOT inferred). |
| NC1–NC6 codification | Cross-references against recovery contract §4/§5; 114355-recovery-scoreboard-1 §"Wrapper drift" table (W2 race, W3 codex variants); 111336-recovery-governance-1 codex-stdin/json/arg-devnull stall observations. |
| D6 (six conventions) | 114355-recovery-scoreboard-1 corrections C1, C2, C5 (three to four conventions in active use); D4 in 114355-governance-loop-3 only enumerated `docs/sessions/`. |
| D7 (cross-run task fingerprint) | C1 (`adversarial-review-2564` complete under `docs/plans/overnight-results/` while named "stalled" by predecessor scoreboard); D2 in 114355-governance-loop-3 covered class within window but not cross-convention. |
| D8 (stub-vs-real-content) | NC1 + NC5; 114355-recovery-scoreboard-1 §"Wrapper drift" (run-120344 pre-write of STARTED stub creates dual-artifact divergence by design). |
| D9 (watchdog alert dedupe) | `feedback_email_cross_noise.md` (alert dedupe is good ops hygiene); recovery contract §9.1 (one alert = one action). |
| NCK1–NCK10 ordering | Synthesized from R1–R10, D1–D9, U1–U9, NC1–NC6, recovery contract §3/§4/§5/§6/§7/§8/§9. The integration table makes the layering explicit. |
| Predecessor citations | `Read` of three prior session artifacts under `docs/sessions/2026-04-30-*` + the staging recovery contract under `docs/governance/staging-autofeed-recovery-contract/`. |

No log/prompt body was read from `agent-logs/` (sandbox-blocked). All evidence is from: (a) `Glob` enumeration of `docs/sessions/`, `docs/governance/`, `docs/plans/overnight-results/`; (b) `Read` of four predecessor governance/recovery artifacts under `docs/`; (c) cited memory feedback files indexed in `MEMORY.md`.

## STARTED / FINISHED markers

- **STARTED:** 2026-04-30T~now (lane dispatched by orchestrator at run-id `20260430-073439`; first tool call established sandbox boundary; ENV-MISMATCH branch entered).
- **FINISHED:** 2026-04-30T~now (this artifact written under `docs/sessions/`).
- **Out-of-band copy required (U3):** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-073439/results/claude-governance-rules-3.md` to satisfy the prescribed path; until that copy lands, lane status is `completed-fallback`, not `completed`. The prescribed-path file (if any exists) is wrapper-pre-written stub per NC1 and is NOT this content.
- **Prompt-id chain to next tick:** **T** (NCK script planning) is the strongest single recommendation because it operationalizes the entire checklist. **U** (wrapper-stub byte-floor audit) is the tightest dependency for D8/NC1 to fire correctly. **Do NOT chain — dispatch one at a time and re-evaluate per D2.**
