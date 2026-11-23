# Provider-Autofeed Hardening — claude-stream-governance-loop-4 lane (run 20260430-111336)

> **Lane ID:** `claude-stream-governance-loop-4`
> **Run:** `provider-autofeed-20260430-111336`
> **Generated:** 2026-04-30 (UTC ~11:35)
> **Author:** claude-stream-governance-loop-4 (Opus 4.7, 1M context, stream-json shape)
> **Predecessors in this run:**
> - `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md`
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md`

## ENV-MISMATCH banner — read this first

Sandbox failure mode unchanged from the 100339 + 111336 governance-1 lanes (recurrence **#3**). The prescribed result path lives outside the workspace-hub sandbox; this document is the canonical lane artifact.

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-stream-governance-loop-4.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read`/`Write`/`stat` of `agent-logs/` | **blocked** at tool layer |
| What still works | `Glob` enumeration only |
| Canonical durable output | **THIS document** under `docs/sessions/` |
| Memory ref | `feedback_lane_result_path_outside_sandbox.md` (logged 2026-04-27, recurrence #3) |

**Operator action options (unchanged):** widen Read/Write allowlist for `agent-logs/**`, OR move prescribed path inside `workspace-hub`, OR have orchestrator copy this file out-of-band.

## Scope of this lane

The 100339 and 111336 governance-1 scoreboards are *descriptive* (what stalled, what to investigate). This lane is *prescriptive*: turn the stall evidence into a **bounded rule set the dispatcher can apply on the next tick** — binary preconditions, bounded actions, explicit no-op clauses. Nothing here ramifies past one tick. Nothing here mutates GitHub. Nothing here implements an unapproved issue.

> **"Bounded next-tick rule" definition (used throughout):**
> 1. **Precondition** is binary and check-cost is O(1) shell or O(N) glob — no log-body parsing.
> 2. **Action** is one of: refuse-dispatch, rewrite-prompt, demote-provider, quarantine-lane, emit-marker. Action runs once per tick per matched lane and does not chain to follow-on dispatches.
> 3. **No-op clause** is explicit: when precondition is not met, the rule does nothing. No fallback path silently invokes another rule.
> 4. **Citation** to memory feedback file or scoreboard evidence, so the rule can be retired when the underlying root cause is fixed.

## Concrete rules — apply on the next dispatcher tick

### R1 — Codex pre-dispatch version gate

| Field | Value |
|---|---|
| **Precondition** | Lane provider matches `codex-*`. |
| **Check** | `codex --version` on the dispatcher host returns `^0\.124`. |
| **Action when matched** | **Refuse to dispatch.** Emit structured error: `BLOCKED: codex-cli 0.124.x stdin-hang upstream regression — see #2479 / memory feedback_codex_cli_0_124_upstream_regression. Operator must downgrade to 0.123.0 before any codex lane.` |
| **No-op clause** | If `codex --version` does not start with `0.124`, proceed normally. |
| **Citation** | `feedback_codex_cli_0_124_upstream_regression.md`; #2479; 111336-governance-1 §Codex (9/9 stalled across 3 invocation variants). |
| **Retire when** | `feedback_codex_cli_0_124_upstream_regression.md` is removed or updated to "fixed". |
| **Bound** | One shell call per tick per dispatch decision. |

**Why this rule first:** run 111336 burned 9 lanes × 3 invocation variants for 0 results. Variant-fan-out cannot defeat an upstream stdin-hang. Until the host CLI is downgraded, every codex dispatch is negative-yield.

### R2 — Lane-result-path sandbox preflight

| Field | Value |
|---|---|
| **Precondition** | Lane prompt contains a `Result file:` line. |
| **Check** | Path resolves inside the lane's sandbox root (default: prefix `/mnt/local-analysis/workspace-hub`). |
| **Action when matched (path inside sandbox)** | Dispatch normally. |
| **Action when NOT matched (path outside sandbox)** | Inject into the prompt body, before `Task:`: `Sandbox limitation acknowledged — write canonical artifact to docs/sessions/<run-id>-<lane-id>.md and emit an ENV-MISMATCH banner per memory feedback_lane_result_path_outside_sandbox. Orchestrator must copy out-of-band to the prescribed path.` |
| **No-op clause** | If lane prompt has no `Result file:` line, do nothing. |
| **Citation** | `feedback_lane_result_path_outside_sandbox.md`; recurrence #3 in this run. |
| **Retire when** | `classify_and_launch.sh` allowlists `agent-logs/**` Read/Write OR moves the prescribed path inside `workspace-hub`. |
| **Bound** | Regex match on prompt body; no filesystem call needed at preflight. |

### R3 — Variant-fan-out budget cap

| Field | Value |
|---|---|
| **Precondition** | An open feedback memory file matching `feedback_<provider>_*upstream*` OR `feedback_<provider>_*regression*` exists. |
| **Check** | Count of lanes for that provider in the current tick > 1. |
| **Action when matched** | Cap dispatch to 1 lane for that provider this tick. Subsequent variants are deferred to the next tick (and re-evaluated against R1/R3). |
| **No-op clause** | If no upstream-regression memory file is open for that provider, allow normal fan-out. |
| **Citation** | 111336-governance-1 §Cross-cutting: "9 codex lanes / 0 results — variant-fan-out is negative-yield strategy when root cause is a single upstream regression." |
| **Retire when** | Specific provider's regression memory file is closed/retired. |
| **Bound** | One memory-file `Glob` per provider per tick. |

### R4 — Gemini Pro 2.5 demoted-by-default

| Field | Value |
|---|---|
| **Precondition** | Lane wrapper would dispatch `gemini-pro-*` AND no `gemini-pro-failmode-capture-*` result has landed since 2026-04-30 11:36 UTC. |
| **Action when matched** | Rewrite the lane to `gemini-flash-fallback-*` (mirror the existing `relaunch_replacements.sh` behavior into the dispatch path, not the relaunch path). Tag the lane name with `-flashpromoted`. |
| **No-op clause** | If a failmode-capture result has landed AND classifies the failure as anything other than `quota-exhaustion`, restore Pro dispatch. If classification is `quota-exhaustion` or absent, keep demotion. |
| **Citation** | 111336-governance-1 §Gemini Pro 2.5 (0/3); §Cross-cutting "Gemini Pro 2.5 has its own failure mode separable from Flash." |
| **Retire when** | Pro failure mode is captured and remediated (e.g. quota raised, wrapper fixed, or feature confirmed unavailable on host). |
| **Bound** | One result-file `Glob` per tick to check failmode-capture status. |

### R5 — Concurrency duplicate-write guard

| Field | Value |
|---|---|
| **Precondition** | About to dispatch lane `<name>` against run `<run-id>`. |
| **Check** | `pgrep -af 'provider-autofeed-<run-id>.*<name>'` returns at least one alive PID. |
| **Action when matched** | Refuse. Emit structured warning: `BLOCKED: lane <name> already in flight under run <run-id> (PID <pid>); suffix lane name with -retry-N or wait for natural completion.` |
| **No-op clause** | If pgrep is empty, dispatch normally. |
| **Citation** | 111336-governance-1 §Concurrency context (4 overlapping runs alive simultaneously); `feedback_check_parallel_work.md`. |
| **Retire when** | Wrapper enforces unique `(run-id, lane-name)` tuples natively (not retired by passage of time). |
| **Bound** | One pgrep call per dispatch decision. |

### R6 — Stream-JSON heartbeat liveness probe

This is the rule **specific to the stream-json lane shape** that this lane embodies. It exists because path-presence is a degraded success signal (per 100339 cross-cutting rec #1) and stream-json gives a cheap heartbeat that path-only checks cannot.

| Field | Value |
|---|---|
| **Precondition** | Lane wrapper invoked Claude with `--verbose --output-format stream-json`. |
| **Check (per tick)** | `stat -c %Y` on the lane log → age in seconds. **Last 5 lines of log** parsed as NDJSON; check for `event: "message_stop"` OR `event: "tool_use"` OR `event: "content_block_delta"` within the tail window. |
| **Classification** | `{emitting (delta or tool_use < 60s ago), idle-but-alive (no delta but message_start present + age < 10 min), stalled-no-emission (age > 10 min AND no delta in tail)}`. |
| **Action — `emitting`** | Do nothing. Lane is healthy. |
| **Action — `idle-but-alive`** | Do nothing. Lane is in a long thinking step or tool round-trip. |
| **Action — `stalled-no-emission`** | Capture last 50 lines into `results/<lane>.stalled.md` with classification banner. **Do NOT retry blindly** — route to next-tick R3 budget cap or quarantine per R8. |
| **No-op clause** | If lane is not stream-json (e.g. legacy `claude-recovery-*` write-then-stop shape), defer to R7 lane-state.json check instead. |
| **Citation** | 111336-governance-1 §Claude row 4 (stream-json shape, decision rule "10 min mtime + no [STARTED] = stalled"); 100339 §Cross-cutting rec #1 ("presence-only is brittle"). |
| **Retire when** | Lane-state.json (R7) covers all lane shapes uniformly, making the stream-json-specific check redundant. |
| **Bound** | One `stat` + last-50-lines tail per stream-json lane per tick. No full-log read. |

### R7 — Lane-state.json emission as exit contract

| Field | Value |
|---|---|
| **Precondition** | A lane wrapper is about to mark a lane "done" (i.e. exit the lane process). |
| **Check** | `results/<lane>/.lane-state.json` exists and parses as `{status, provider_used, exit_code, started_at, finished_at}`. |
| **Action when NOT matched** | Wrapper writes a default `.lane-state.json` with `status: "exited-without-state"`, `exit_code: <process-exit-code>`, `started_at`/`finished_at` from wrapper-known timestamps, `provider_used: <wrapper-known-provider>`. The result file is **not** treated as authoritative until this state file is present. |
| **No-op clause** | If `.lane-state.json` already exists, do nothing. |
| **Citation** | 100339 §Cross-cutting rec #1 ("Promote results/.lane-state.json … 3-line JSON … L2 enforcement"). |
| **Retire when** | A stop-hook unconditionally writes the state file (then this rule is enforced at L3 instead of L2). |
| **Bound** | One file-existence check per lane exit; one fwrite of ≤200 bytes when missing. |

### R8 — Content-trigger quarantine

| Field | Value |
|---|---|
| **Precondition** | Lane name fingerprint (e.g. `gemini-flash-fallback-gtm-5`) has 🟥 status across ≥ 2 runs in the last 24 h. |
| **Check** | Glob `agent-logs/provider-autofeed-*/results/<lane-name>.md` for the last 24 h; if count == 0 across ≥ 2 runs, fingerprint is "repeating stall." |
| **Action when matched** | Tag the lane prompt with `[content-trigger-suspected]`. Route the next attempt to a **content-diff lane** (per 111336-governance-1 Prompt D), not a content-replay. |
| **No-op clause** | If the lane has any 🟢 in the last 24 h or has only one stall, treat as transient and allow normal re-dispatch. |
| **Citation** | 111336-governance-1 §Gemini Flash Fallback ("`gemini-flash-fallback-gtm-5` content-specific stall — same lane class fails across runs"). |
| **Retire when** | Content trigger is identified and the prompt is fixed, OR the failing content is removed from the lane spec. |
| **Bound** | One Glob across `agent-logs/provider-autofeed-*/results/` per tick. |

### R9 — Wrapper-divergence audit before recovery dispatch

| Field | Value |
|---|---|
| **Precondition** | About to dispatch a Gemini lane via `provider-recovery-*` or `relaunch_replacements.sh`. |
| **Check** | `diff` the gemini-invocation block in the recovery wrapper against the same block in `provider-min3-*`. |
| **Action when matched (diverged)** | Refuse dispatch. Emit: `BLOCKED: gemini fan-out chain diverged between recovery and min3 wrappers — see 100339 §provider-recovery-20260430-0445 (Gemini lanes succeeded in min3 but failed in recovery same hour).` |
| **No-op clause** | If diff is empty, dispatch normally. |
| **Citation** | 100339 §Cross-cutting rec #4 ("Mirror the Gemini fan-out chain into every wrapper"); 111336-governance-1 Prompt F. |
| **Retire when** | Prompt F lane completes and the divergence is either fixed or proven absent. |
| **Bound** | One `diff` per recovery dispatch (cached per dispatcher process). |

### R10 — Tick budget cap on negative-yield providers

| Field | Value |
|---|---|
| **Precondition** | Provider yield over the last 3 ticks (results / lanes-attempted) is `0/N` with N ≥ 3. |
| **Check** | Glob result counts vs. log counts across last 3 run directories. |
| **Action when matched** | Cap that provider to **1 lane this tick** AND require an open diagnostic lane (e.g. R4 failmode-capture) before increasing the cap. |
| **No-op clause** | If yield is non-zero in any of last 3 ticks, no cap applied. |
| **Citation** | 111336-governance-1 §Minimum-active-provider counts ("Codex 0/9, Gemini Pro 0/3 — adding lane variants without addressing root causes is negative-yield"). |
| **Retire when** | Provider returns to ≥ threshold yield. |
| **Bound** | Two Globs per provider per tick (results + logs across 3 runs). |

## Rule precedence — when multiple match

Apply in this order. Earlier rules win and short-circuit later ones.

1. **R5** (concurrency duplicate guard) — never write twice to the same lane.
2. **R2** (sandbox preflight) — fix path before doing anything else with the prompt.
3. **R1** (codex version gate) — refuse known-broken provider before counting budgets.
4. **R9** (wrapper divergence) — refuse when the wrapper itself is the bug, before counting yield.
5. **R3** (variant-fan-out cap) — cap before R10's negative-yield cap, since R3 is precondition-driven and R10 is statistics-driven.
6. **R10** (negative-yield cap) — cap counts after R3 already trimmed variants.
7. **R4** (Gemini Pro demotion) — provider rewrite happens after capping decisions.
8. **R8** (content-trigger quarantine) — tag and route per-lane after provider decisions.
9. **R6** (stream-json heartbeat) — runs continuously per tick over alive lanes; not a dispatch gate.
10. **R7** (lane-state.json emission) — runs at lane exit, not at dispatch.

## What this lane explicitly does NOT do

Per the lane hard-gates and the brainstorm-before-implement rule:

- ✗ Does **not** label any GitHub issue with `status:plan-approved`.
- ✗ Does **not** open any GitHub issue or PR.
- ✗ Does **not** edit `classify_and_launch.sh`, `run_tick.sh`, `relaunch_replacements.sh`, or any lane wrapper.
- ✗ Does **not** edit `submit-to-gemini.sh` or codex/claude wrapper scripts.
- ✗ Does **not** create a worktree (no source edits attempted in this lane).
- ✗ Does **not** retire or rewrite any memory feedback file.
- ✗ Does **not** mutate `.claude/state/`.

A subsequent **planning lane** (issue-planning-mode skill) is required before any of these rules is implemented in the wrappers.

## Suggested follow-up lane prompts

These are safe under hard-gates and bounded to a single tick of work each. **Do NOT chain them — dispatch one at a time and re-evaluate.** Owner of each prompt is "any planning-capable host" unless noted.

### Prompt G — Plan to land R1 (codex version gate) in `classify_and_launch.sh`

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: codex-version-gate-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/codex-version-gate-plan-1.md (fallback `docs/sessions/...` per ENV-MISMATCH)
> Hard gates: do not destructively reset/clean; isolated worktrees; no outreach; no self-approval; no status:plan-approved changes; no unapproved implementation. Use GIT_OPTIONAL_LOCKS=0 and timeout. Redact secrets. **Planning only.**
> Task: Read this lane's R1 rule and `feedback_codex_cli_0_124_upstream_regression.md`. Locate the codex dispatch site in `classify_and_launch.sh` (or whichever wrapper actually invokes codex). Draft the precondition check + structured-error emission as a code change spec — file, function, exact diff shape, test plan. Do NOT touch the wrapper. Map to enforcement-gradient L2 in `.claude/rules/patterns.md`. Identify the GitHub issue this should be attached to (or recommend filing a new one with body draft). Exit: result file with diff sketch + test plan + issue ID or draft.

### Prompt H — Plan to land R6 + R7 (stream-json heartbeat + lane-state.json) together

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: lane-liveness-contract-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/lane-liveness-contract-plan-1.md (fallback `docs/sessions/...` per ENV-MISMATCH)
> Hard gates: same as Prompt G.
> Task: Read this lane's R6 + R7. Treat them as a single "lane liveness contract" — heartbeat at runtime + state file at exit. Identify all lane wrappers (under `/mnt/local-analysis/agent-logs/provider-autofeed-monitor/` and run-specific overrides) that need the contract. Spec the JSON schema (`status`, `provider_used`, `exit_code`, `started_at`, `finished_at`, optional `last_heartbeat_at`, optional `stall_classification`). Spec the heartbeat tail-parser as a 20-line awk or python helper. Plan rollout: shadow mode (write but do not enforce) for 1 nightly cycle, then enforce. Exit: 1-page plan + new GitHub issue draft (do NOT open).

### Prompt I — Plan to add R2 (sandbox-path preflight) as a stop-hook

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: sandbox-path-preflight-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/sandbox-path-preflight-plan-1.md (fallback `docs/sessions/...` per ENV-MISMATCH)
> Hard gates: same as Prompt G.
> Task: Read R2 + `feedback_lane_result_path_outside_sandbox.md`. The hooks-as-enforcement pattern in `.claude/rules/patterns.md` shows how to promote a prose rule to L3 (hook). Spec a pre-dispatch hook that regex-matches `Result file:\s*(\S+)` in the lane prompt and refuses dispatch when the path is outside the lane sandbox root (or rewrites the prompt to add the ENV-MISMATCH fallback instruction). Identify which file under `.claude/hooks/` (or equivalent dispatcher hook surface) is the right home. Plan only — no edits.

### Prompt J — Sweep recurrences and retire the redundant scoreboards

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: scoreboard-recurrence-cleanup-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/scoreboard-recurrence-cleanup-1.md (fallback `docs/sessions/...` per ENV-MISMATCH)
> Hard gates: same as Prompt G. Reconnaissance only.
> Task: Glob `docs/sessions/*provider-autofeed*scoreboard*.md` and `docs/sessions/*provider-autofeed*governance*.md` over last 30 days. Identify which scoreboards say the same four cross-cutting recommendations (R1, R2, R6/R7, R9 in this lane's numbering). Recommend which to retire vs. keep. Do not delete files — emit a recommendation list only. Exit: result file with retain/retire table.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`.
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted.
- ✓ No GitHub mutations (no `gh issue`/`pr` calls).
- ✓ No outreach drafts.
- ✓ No self-approval / no `status:plan-approved` label changes.
- ✓ No unapproved implementation — rules are *prescriptive specs only*; landing them requires Prompt G/H/I planning lanes plus `issue-planning-mode` skill plus user approval.
- ✓ No isolated worktree created — no source edits in this lane; this document is a session-note artifact.
- ✓ No secrets emitted (no API keys, tokens, or PII).
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md`, `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_check_parallel_work.md`, `feedback_gemini_trust_env_blocks_reviews.md`; aligns with 100339 + 111336-governance-1 scoreboards.
- ✓ Timeouts: not needed (no Bash with long-running calls — only `git status` was attempted, and only Glob enumeration was used for evidence).

## Evidence appendix — what backed every rule

| Rule | Backing evidence |
|---|---|
| R1 | 111336-governance-1 §Codex (9/9 stalled across 3 variants); `feedback_codex_cli_0_124_upstream_regression.md`; #2479. |
| R2 | This lane's ENV-MISMATCH banner (recurrence #3); `feedback_lane_result_path_outside_sandbox.md`. |
| R3 | 111336-governance-1 §Cross-cutting (variant-fan-out negative-yield). |
| R4 | 111336-governance-1 §Gemini Pro 2.5 (0/3); operator already auto-falling-back via `relaunch_replacements.sh`. |
| R5 | 111336-governance-1 §Concurrency context (4 overlapping runs); `feedback_check_parallel_work.md`. |
| R6 | 111336-governance-1 Prompt C (stream-json liveness probe rule shape); 100339 §Cross-cutting rec #1. |
| R7 | 100339 §Cross-cutting rec #1 (verbatim 3-line JSON contract). |
| R8 | 111336-governance-1 §Gemini Flash Fallback (`gemini-flash-fallback-gtm-5` content-specific stall reproduces in run 102314). |
| R9 | 100339 §provider-recovery-20260430-0445 (Gemini fan-out diverged between min3 and recovery same hour). |
| R10 | 111336-governance-1 §Minimum-active-provider counts (Codex 0/9, Gemini Pro 0/3). |

No log/prompt body was read from this lane — all evidence is from the two predecessor scoreboard documents and the cited memory feedback files.

## STARTED/FINISHED markers

- **STARTED:** 2026-04-30T11:25Z (lane dispatch)
- **FINISHED:** 2026-04-30T~11:40Z (this artifact written under `docs/sessions/`)
- **Out-of-band copy required:** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-111336/results/claude-stream-governance-loop-4.md` to satisfy the prescribed path.
- **Prompt-id chain to next tick:** G → H → I (in that order; do not parallelize, since H depends on G's wrapper-identification artifact). J is independent and can run in parallel with any of G/H/I.
