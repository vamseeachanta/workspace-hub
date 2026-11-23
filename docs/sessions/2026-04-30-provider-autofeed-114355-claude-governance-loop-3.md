# Provider-Autofeed Governance — claude-governance-loop-3 lane (run 20260430-114355)

> **Lane ID:** `claude-governance-loop-3`
> **Run:** `provider-autofeed-20260430-114355`
> **Generated:** 2026-04-30 ~12:07 UTC (lane STARTED ~11:46 UTC)
> **Author:** `claude-governance-loop-3` (Opus 4.7, 1M context)
> **Predecessors in this run:** sibling lanes `claude-recovery-scoreboard-1` and `claude-plan-review-hardening-2` (both result files exist by Glob; bodies unread from this sandbox).
> **Cross-run predecessors cited (do NOT duplicate):**
> - `docs/sessions/2026-04-30-provider-autofeed-100339-claude-1-control-plane-scoreboard.md` (R1-R4 cross-cutting recommendations source)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-recovery-governance-1.md` (Prompts A-F + recovery scoreboard)
> - `docs/sessions/2026-04-30-provider-autofeed-111336-claude-stream-governance-loop-4.md` (R1-R10 bounded-rule set + Prompts G-J)

## ENV-MISMATCH banner — read this first

Sandbox failure recurrence **#4** in 24 h. The prescribed result path is outside the lane sandbox; `Read`/`Write` of `agent-logs/**` blocked at the tool layer (verified at lane start by attempting both `Read /mnt/local-analysis/agent-logs/.../prompts/claude-governance-loop-3.md` and `Write /mnt/local-analysis/agent-logs/.../results/claude-governance-loop-3.md` — both gated). `Glob` enumeration still works.

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/claude-governance-loop-3.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read`/`Write`/`stat` of `agent-logs/` | **blocked** at tool layer |
| `Bash codex --version` | **also blocked** (single-arg approval gate; could not directly verify host CLI version this lane) |
| What still works | `Glob` enumeration; `Bash pgrep` over the host process table |
| Canonical durable output | **THIS document** under `docs/sessions/` |
| Memory ref | `feedback_lane_result_path_outside_sandbox.md` |

**Operator action remains unchanged from 100339/111336/111336-loop-4:** widen Read/Write allowlist for `agent-logs/**`, OR move prescribed path inside `workspace-hub`, OR have the orchestrator copy this file out-of-band. Recurrence #4 inside 24 h means prose-level memory is no longer enough; this should escalate to a dispatcher hook (per Prompt I in the 111336-loop-4 artifact).

## Scope of THIS lane (narrowed per dispatch task)

The dispatch prompt named two specific deliverables: **dedupe rules** and **unsafe transition gates**. Predecessor lane 111336-loop-4 already drafted ten bounded next-tick rules (R1-R10) covering version gates, sandbox preflight, fan-out caps, demotion, concurrency, heartbeat, lane-state contracts, content-trigger quarantine, wrapper divergence, and yield caps. **This lane does NOT re-emit R1-R10.** It cites and extends with rule classes the predecessor lane underweighted: dedupe (D-series) and unsafe state-machine transitions (U-series).

> **Lane discipline reminder.** Each rule below carries the same shape as 111336-loop-4: O(1)/O(N-glob) precondition, single bounded action per matched lane per tick, explicit no-op clause, citation, retire-when. No rule chains; no rule mutates GitHub; no rule implements an unapproved issue.

## Stall signatures observed in run 114355 (path-presence only — content unverified)

By Glob (the only tool available):

| Lane | prompt | log | result | Note |
|---|---|---|---|---|
| `codex-approved-scout-1` | ✓ | ✓ | ✓ | Result file presence is a **degraded success signal** — codex 0.124 stdin-hang reported in 111336 makes "result file exists" insufficient (see U7). |
| `codex-test-readiness-2` | ✓ | ✓ | ✓ | Same caveat. |
| `codex-worktree-hygiene-3` | ✓ | ✓ | ✓ | Same caveat. |
| `claude-recovery-scoreboard-1` | ✓ | ✓ | ✓ | Result presence cannot be content-verified from this sandbox. |
| `claude-plan-review-hardening-2` | ✓ | ✓ | ✓ | Same. |
| `claude-governance-loop-3` (this lane) | ✓ | ✓ | ✓ | "Result file" enumeration counts the empty/probe artifacts; canonical output is THIS document. |

**Behavioral deltas vs. 111336 (same dispatcher, ~28 min later):**

1. **Variant-fan-out collapsed.** Run 111336 had 9 codex lanes across `-stdin/-json/-arg-devnull` variants. Run 114355 has 3 codex lanes with no variant suffix. Operator implicitly accepted R3 (variant cap) without an explicit retraction. **Good.**
2. **Gemini removed entirely.** Run 111336 had 6 gemini lanes (3 pro + 3 flash-fallback). Run 114355 has 0 gemini lanes. Operator implicitly accepted R4 (gemini-pro demotion) and went further by demoting flash too. **Investigate before next tick** — flash was the *only* yielding provider in 111336 (2/3 results). Removing the only yielding provider while keeping the regression-blocked codex provider is a structural inversion.
3. **`-stream-` infix dropped.** Lane name is `claude-governance-loop-3`, not `claude-stream-governance-loop-4`. Either (a) operator reverted to legacy stop-then-write Claude shape, or (b) the infix was always cosmetic and the wrapper is unchanged. Cannot disambiguate from sandbox; flag for next tick.
4. **Live evidence of unfixed codex 0.124.** `pgrep -af 'provider-autofeed'` at this lane's start showed PID 2128357 — `codex exec ... -` from run 111336 (~33 min earlier) — **still alive**. The host CLI was not downgraded between 111336 and 114355; R1's precondition is still hot. This is direct evidence, not inference, that the operator-host action (Prompt A in the 111336 recovery artifact) has not landed.
5. **Concurrency snapshot:** four overlapping autofeed runs alive at lane start (`102314`, `104814`, `111336`, `114355`). Same shape as 111336-recovery-governance-1 §Concurrency, recurrence #2.

## Dedupe rules — D1 through D5

Bounded next-tick rules; `D` prefix to keep them separable from the 111336-loop-4 R-series. R5 (concurrency duplicate-write guard) and R8 (content-trigger quarantine) are dedupe-adjacent but not sufficient on their own.

### D1 — Lane-name × prompt-content-hash dedupe within a tick

| Field | Value |
|---|---|
| **Precondition** | About to dispatch lane `<name>` with prompt body `<P>` against run `<run-id>`. |
| **Check** | Compute `sha256(<P>)`. Glob `agent-logs/provider-autofeed-<run-id>/prompts/<name>.md` and compare hash. |
| **Action when matched (same name + same hash)** | Refuse. Emit: `BLOCKED: lane <name> with identical prompt already dispatched in run <run-id> — see results/<name>.md.` |
| **Action when matched (same name, different hash)** | Allow, but rename to `<name>-v2` (or next free integer). Same name with different prompt is a different lane. |
| **No-op clause** | If no prior `prompts/<name>.md`, dispatch normally. |
| **Citation** | This lane's own existence — `claude-governance-loop-3` would have collided with 111336's `claude-stream-governance-loop-4` if the integer were not bumped. R5 catches the alive-process case but not the "result already landed" case. |
| **Retire when** | Wrapper enforces `(lane-name, prompt-hash)` uniqueness natively. |
| **Bound** | One sha256 + one Glob per dispatch decision. |

### D2 — Cross-run lane-fingerprint dedupe over 24 h window

| Field | Value |
|---|---|
| **Precondition** | About to dispatch lane class `<class>` (e.g. `gemini-pro-research-queue`, fingerprint = strip trailing integer + provider variant). |
| **Check** | Glob `agent-logs/provider-autofeed-*/results/<class>*.md` over runs in the last 24 h. Count results-with-content (use `.lane-state.json` if R7 has landed; else any non-zero file size). |
| **Action when matched (≥1 success in 24 h)** | Allow normal dispatch. |
| **Action when matched (0 successes across ≥3 attempts in 24 h)** | Tag the prompt `[repeat-stall, attempts=N]`. **Do NOT auto-add a fan-out variant.** Surface to operator as a Prompt-A-class action (host-level investigation). |
| **No-op clause** | First attempt in 24 h, dispatch normally. |
| **Citation** | 111336-recovery-governance-1 §Cross-cutting "variant-fan-out is negative-yield"; `feedback_codex_sustained_major_loop.md` (sustained-loop pattern in cross-review escalates to operator decision, not auto-cycle). |
| **Retire when** | A wrapper-level `--max-attempts-per-class-per-day` flag exists and is honored by the dispatcher. |
| **Bound** | One Glob per class per tick. |

### D3 — Governance-rule-set dedupe (this lane's meta-rule)

| Field | Value |
|---|---|
| **Precondition** | A governance/recovery lane is about to author rules for the dispatcher. |
| **Check** | Glob `docs/sessions/*provider-autofeed*governance*.md` and `docs/sessions/*provider-autofeed*scoreboard*.md` over last 7 days. Read the latest by mtime; collect the rule IDs already in scope. |
| **Action when matched** | New rules MUST extend or refine, not redefine. Use a fresh prefix (`D`/`U`/`G`/...) so rule IDs are stable references. |
| **No-op clause** | If no prior governance artifact in the window, start a fresh `R`-series. |
| **Citation** | Predecessor lane 111336-loop-4 already authored R1-R10. THIS lane uses `D` and `U` prefixes specifically to avoid re-collision. |
| **Retire when** | The rule set is moved out of session-notes into a versioned spec at `docs/governance/provider-autofeed/rules.md` (then dedupe is structural, not by-convention). |
| **Bound** | One Glob + one mtime sort per governance lane. |

### D4 — ENV-MISMATCH artifact dedupe

| Field | Value |
|---|---|
| **Precondition** | Lane writes a fallback artifact to `docs/sessions/<date>-<run>-<lane>.md` per `feedback_lane_result_path_outside_sandbox`. |
| **Check** | Glob `docs/sessions/*<run>*<lane>*.md`. |
| **Action when matched (file already exists)** | Append a `## Re-run continuation` block to the existing file, not a new file. Keep one canonical artifact per (run, lane). |
| **No-op clause** | First write, create the file normally. |
| **Citation** | Operator copy-out-of-band assumes one artifact per lane; multiplying truth defeats reconciliation. The `2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` and `2026-04-30-claude-stream-plan-hardening-3-result.md` artifacts in `docs/sessions/` show the convention is already inconsistent — this rule normalizes it. |
| **Retire when** | Out-of-band copy is automated and the fallback path becomes a transient. |
| **Bound** | One Glob per lane finalize. |

### D5 — Issue-comment dedupe before posting (planning-only safeguard)

| Field | Value |
|---|---|
| **Precondition** | Lane plans to post a `gh issue comment` (per `feedback_gh_issue_comment.md`) summarizing its findings. |
| **Check** | `gh issue view <N> --json comments --jq '.comments[].body'` and grep for the proposed-comment headline (first 80 chars). |
| **Action when matched** | Skip. Already documented; appending a near-duplicate degrades reviewability. |
| **No-op clause** | First posting on this issue from this lane class, post normally. |
| **Citation** | `feedback_gh_issue_comment.md` (post a summary on every issue) AND `feedback_gh_issue_close_silent_comment_drop.md` (close drops comments — don't waste a comment cycle on a duplicate). |
| **Retire when** | A `gh` extension or pre-commit-style hook handles dedupe automatically. |
| **Bound** | One `gh issue view` call per intended post. |

## Unsafe transition gates — U1 through U9

These are **state-machine no-go transitions** the dispatcher must refuse to make on its own. Where R-series rules gate dispatch, U-series rules gate state changes (label flips, "succeeded" verdicts, escalation, finalization). Each U-rule ends with the explicit transition that is forbidden.

### U1 — Lane-N → Lane-N+1 sequencing without verified upstream output

| Field | Value |
|---|---|
| **Precondition** | Lane chain `<class-1>-1 → <class-2>-2 → <class-3>-3` (e.g. `claude-recovery-scoreboard-1 → claude-plan-review-hardening-2 → claude-governance-loop-3` in this run) is in flight in the same tick. |
| **Check** | Lane N+1 starts only after lane N has written `results/<lane-N>/.lane-state.json` with `status: "completed"` (R7 contract) OR the lane-N result file passes a content non-emptiness probe. |
| **Forbidden transition** | Lane N+1's reasoning treats lane N's output as authoritative when lane N is `idle-but-alive` or `stalled-no-emission`. |
| **Action** | Lane N+1 wrapper waits with bounded backoff; if N is still pending after 30 min, lane N+1 emits its own evidence section flagged `[predecessor-pending]` and refuses to cite N. |
| **No-op clause** | If lanes are independent (no name-suffix sequence), no gate. |
| **Citation** | THIS lane's situation: `claude-recovery-scoreboard-1` and `claude-plan-review-hardening-2` results existed at glob time, but their content was unverifiable from sandbox. Default decision: cite ENV-MISMATCH and proceed with `[content-unverified]` flag — which is the rule's "predecessor-pending" branch. |
| **Retire when** | R7 (lane-state.json) lands and is enforced. |
| **Bound** | One existence + content-non-empty check per predecessor. |

### U2 — Planning lane → implementation lane without dual approval marker

| Field | Value |
|---|---|
| **Precondition** | A lane proposes to transition from planning (writing a plan) to implementation (editing source). |
| **Check** | (a) GitHub issue has `status:plan-approved` label live (verify with `gh issue view <N> --json labels`), AND (b) local marker `.planning/plan-approved/<issue>.md` exists. |
| **Forbidden transition** | Self-applying `status:plan-approved` to enable downstream implementation; or implementing on `status:plan-review` based on prior review consensus alone. |
| **Action when one or both gates missing** | Refuse implementation; emit `BLOCKED: planning→implementation requires (a) live status:plan-approved AND (b) .planning/plan-approved/<issue>.md; current state: <which gate is missing>`. |
| **No-op clause** | If the lane is purely planning/review/evidence/handoff, no transition is being attempted; gate does not fire. |
| **Citation** | `feedback_never_offer_to_self_label_plan_approved.md` (user-in-loop is load-bearing across session boundaries); `project_issue_2460_approval_binding.md` (approval markers must be revision-bound). The dispatch prompt itself encodes this gate verbatim. |
| **Retire when** | Never. This is a hard governance invariant, not a phase rule. |
| **Bound** | One `gh` call + one `stat`. |

### U3 — Sandbox fallback artifact → "lane delivered to prescribed path"

| Field | Value |
|---|---|
| **Precondition** | Lane wrote canonical output to `docs/sessions/<...>.md` per ENV-MISMATCH (D4). |
| **Forbidden transition** | Marking the lane's `.lane-state.json` as `status: "completed"` and `result_path: <prescribed-path>`. The prescribed-path file does not yet exist (or is a probe-stub). |
| **Action** | `.lane-state.json` records `status: "completed-fallback"`, `result_path_actual: docs/sessions/<...>.md`, `result_path_prescribed: agent-logs/<...>.md`, `awaiting_orchestrator_copy: true`. The orchestrator's downstream consumers MUST treat `completed-fallback` as separate from `completed`. |
| **No-op clause** | If the lane wrote to the prescribed path successfully, normal completion. |
| **Citation** | `feedback_lane_result_path_outside_sandbox.md`; this lane's recurrence #4 in 24 h. |
| **Retire when** | Sandbox allowlist widened OR prescribed paths moved inside workspace. |
| **Bound** | Two extra fields in the state JSON. |

### U4 — `idle-but-alive` ↛ `stalled-no-emission` (R6 classification handoff)

| Field | Value |
|---|---|
| **Precondition** | A stream-json lane was classified `idle-but-alive` at tick T. |
| **Forbidden transition** | At tick T+1, automatically reclassifying to `stalled-no-emission` purely on age, without re-running the tail-window NDJSON parse. |
| **Action** | At tick T+1, re-run R6's tail parse fresh. A long thinking step or tool round-trip can legitimately keep a lane `idle-but-alive` for 30+ minutes; an age-only escalation produces false stalls. |
| **No-op clause** | If R6 freshly classifies the same lane as `stalled-no-emission`, that *is* the new state — no special handling needed. |
| **Citation** | 111336-loop-4 R6 (heartbeat probe); the classes `idle-but-alive` and `stalled-no-emission` are distinct evidence states — collapsing them by time-only logic loses signal. |
| **Retire when** | The wrapper writes per-tick heartbeat events to `.lane-state.json` and the classifier reads from there, not from log mtime. |
| **Bound** | Same as R6. |

### U5 — Result-file-presence ↛ "lane succeeded"

| Field | Value |
|---|---|
| **Precondition** | A consumer (scoreboard, dispatcher, dashboard) is about to record a lane as ✅ on the basis of `results/<lane>.md` existing. |
| **Forbidden transition** | Result-presence → success without one of: (a) `.lane-state.json` exists with `status: "completed"`, (b) result file size > N bytes (TBD; sentinel ~ 200 B excludes STARTED-only stubs), (c) result file's last line contains a `FINISHED` marker. |
| **Action** | Tag as `delivered-presence-only` (degraded ✅). Do NOT count toward minimum-active-provider yield. |
| **No-op clause** | If any of (a)/(b)/(c) holds, normal ✅. |
| **Citation** | 100339 §Cross-cutting rec #1 ("presence-only is brittle"); R7 in 111336-loop-4. THIS lane's own situation — `claude-governance-loop-3.md` exists in `agent-logs/.../results/` per Glob, but it is a write-probe stub from a sandbox-blocked attempt; the canonical output is here under `docs/sessions/`. |
| **Retire when** | R7 lands. |
| **Bound** | One stat call per lane finalize. |

### U6 — `status:plan-review` → `status:plan-approved` self-label (hard invariant)

| Field | Value |
|---|---|
| **Precondition** | Any lane (or sub-agent it spawns) is about to call `gh issue edit <N> --add-label status:plan-approved`. |
| **Forbidden transition** | Always. |
| **Action** | Refuse. Emit `BLOCKED: status:plan-approved is user-only. Lane may emit a handoff prompt naming the issue and proposed evidence; user applies the label.` |
| **No-op clause** | None. This is unconditional. |
| **Citation** | `feedback_never_offer_to_self_label_plan_approved.md` (verbatim invariant). |
| **Retire when** | Never. |
| **Bound** | One label-string regex check per `gh issue edit` shell call. |

### U7 — Codex result-file ↛ "codex executed"

| Field | Value |
|---|---|
| **Precondition** | A codex lane wrote to its result file. |
| **Forbidden transition** | Treating result presence as evidence of actual codex execution. |
| **Action** | Verify (a) the result file contains a non-trivial number of tokens characteristic of codex output (NOT just a wrapper-emitted STARTED banner), AND (b) the host's `codex --version` does not start with `0.124`, AND (c) the lane log shows codex's "Reading additional input from stdin..." banner is **absent** (its presence is the regression signature). |
| **Forbidden secondary transition** | Treating a codex MAJOR review verdict as load-bearing when codex was UNAVAILABLE during the review (per `feedback_codex_cli_0_124_upstream_regression`). |
| **No-op clause** | If all three conditions hold, normal success treatment. |
| **Citation** | `feedback_codex_cli_0_124_upstream_regression.md` (downgrade unverified from Claude Code Bash); 111336-recovery-governance-1 §Codex (9/9 stalled across variants); live evidence in run 114355: PID 2128357 from run 111336 was still alive at this lane's start, indicating no host downgrade. |
| **Retire when** | Codex 0.124 stdin-hang fixed upstream OR Claude Code Bash propagates EOF. |
| **Bound** | One `wc -c` + one `grep -c` + one `codex --version` per finalize. |

### U8 — Variant fan-out → "exploration completed" (when upstream regression is open)

| Field | Value |
|---|---|
| **Precondition** | A provider has an open upstream-regression memory file (per R3 precondition). The dispatcher has tried ≥2 variants. |
| **Forbidden transition** | Recording the run as "all reasonable variants tried; provider confirmed broken" purely on local variant exhaustion. |
| **Action** | Require the operator-host action (e.g. version downgrade, environment fix) to be attempted in a non-Claude-Code terminal AND a fresh single-variant test passes BEFORE retiring the regression memory file. |
| **No-op clause** | If no upstream-regression memory file is open, normal exploration semantics apply. |
| **Citation** | `feedback_codex_cli_0_124_upstream_regression.md` (Claude Code's Bash tool stdin layer is itself a confound — variant exhaustion inside Claude Code does not prove the provider is broken outside Claude Code). |
| **Retire when** | The cited memory feedback is updated to remove the "downgrade does NOT help from Claude Code's Bash tool" addendum. |
| **Bound** | One memory-file Glob per provider per run. |

### U9 — GitHub issue body draft (in result file) ↛ "issue opened"

| Field | Value |
|---|---|
| **Precondition** | A lane result file contains a section that drafts a `gh issue create` body. |
| **Forbidden transition** | The lane (or any subagent it spawns) calling `gh issue create` for that body. |
| **Action** | Drafts are spec for the orchestrator/user to act on, never auto-executed. The lane's hard-gate compliance section MUST list `gh issue create` in the explicit-NOT-done list when a draft is present. |
| **No-op clause** | If no draft is present, gate does not fire. |
| **Citation** | `feedback_never_offer_to_self_label_plan_approved.md` (generalized: lane outputs are spec, not action — issue creation is user-triggered, not lane-triggered); CLAUDE.md hard gates ("no GitHub mutations"). |
| **Retire when** | Never (issue creation is owned by user/orchestrator). |
| **Bound** | One regex check on result body before lane finalize. |

## Rule precedence — D and U series interaction with R series

Apply in this order. Earlier rules win and short-circuit later ones.

1. **U6** (self-label invariant) — fires before any other rule that might compute a label change.
2. **U2** (dual approval gate) — fires before any planning→implementation transition.
3. **R5** (concurrency duplicate guard) — never write twice to the same lane (already in R-series).
4. **D1** (lane-name × prompt-hash dedupe) — refines R5 to cover the case where the prior write completed before the current dispatch.
5. **D3** (governance-rule-set dedupe) — fires only for governance/recovery lanes; ensures THIS rule set extends, doesn't redefine.
6. **R2** (sandbox preflight) — fixes path before doing anything else with the prompt.
7. **U3** (fallback ↛ "delivered" gate) — fires at lane finalize, after R2's path correction.
8. **R1 / R9** (codex version gate / wrapper divergence) — refuse known-broken provider/wrapper before counting yield.
9. **D2** (cross-run lane-class dedupe) — fires after provider gates; checks whether it's worth retrying at all.
10. **R3 / R10** (variant cap / negative-yield cap) — apply caps after dedupe filters trim.
11. **U8** (variant fan-out → "exploration completed" gate) — fires when R3 trips AND the upstream regression is unresolved.
12. **R4** (Gemini Pro demotion) — provider rewrite happens after capping decisions.
13. **R8** (content-trigger quarantine) — tag and route per-lane after provider decisions.
14. **R6** (stream-json heartbeat) — runs continuously per tick over alive lanes; not a dispatch gate.
15. **U4** (`idle-but-alive` ↛ `stalled-no-emission` reclassification) — gates classifier output, not dispatch.
16. **R7** (lane-state.json emission) — runs at lane exit, not at dispatch.
17. **U5 / U7** (presence-only ↛ "succeeded" / codex result-file ↛ "executed") — fire at consumer-side aggregation (scoreboard build, yield counting), not at dispatch.
18. **D4** (ENV-MISMATCH artifact dedupe) — fires at write time, not dispatch.
19. **D5** (issue-comment dedupe) — fires at outbound-comment time.
20. **U9** (issue-body-draft ↛ issue-creation gate) — fires at lane finalize.

## What this lane explicitly does NOT do

- ✗ Does **not** label any GitHub issue with `status:plan-approved` (U6).
- ✗ Does **not** open any GitHub issue or PR (U9).
- ✗ Does **not** post a `gh issue comment` (D5 deferred).
- ✗ Does **not** edit `classify_and_launch.sh`, `run_tick.sh`, `relaunch_replacements.sh`, or any lane wrapper.
- ✗ Does **not** edit `submit-to-codex.sh`, `submit-to-gemini.sh`, or any provider wrapper.
- ✗ Does **not** create a worktree (no source edits attempted).
- ✗ Does **not** retire or rewrite any memory feedback file.
- ✗ Does **not** mutate `.claude/state/` or `.planning/plan-approved/`.
- ✗ Does **not** copy this artifact to the prescribed `agent-logs/` path (orchestrator-owned per U3).
- ✗ Does **not** attempt to downgrade or test the codex CLI from this Bash tool (U8 + memory feedback explicitly).

## Suggested follow-up lane prompts (ONE at a time, do NOT chain)

These are bounded, hard-gate-safe, and each names exit conditions. The 111336-loop-4 lane already named Prompts G/H/I/J for landing R1/R6+R7/R2-as-hook/scoreboard-cleanup. The prompts below extend that set with D-series and U-series implementation paths. **Strongest single recommendation:** Prompt K (escalate sandbox-allowlist to a hook), since the underlying issue has now recurred 4× in 24 h and prose memory is no longer load-bearing.

### Prompt K — Escalate `feedback_lane_result_path_outside_sandbox` to a dispatcher hook

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: sandbox-path-hook-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/sandbox-path-hook-plan-1.md (fallback `docs/sessions/...` per ENV-MISMATCH)
> Hard gates: do not destructively reset/clean; isolated worktrees; no outreach; no self-approval; no `status:plan-approved` changes; no unapproved implementation; `GIT_OPTIONAL_LOCKS=0`; redact secrets. **Planning only.**
> Task: Recurrence #4 in 24 h means a prose memory rule cannot keep up. Identify the dispatcher entry point (likely `/mnt/local-analysis/agent-logs/provider-autofeed-monitor/classify_and_launch.sh` or its caller). Spec a pre-dispatch check: extract `Result file:\s*(\S+)` from the lane prompt; if the path does not start with the lane sandbox root, **either** (a) refuse dispatch with structured error, **or** (b) rewrite the prompt to inject the docs/sessions/ fallback instruction AND a post-lane copy-out-of-band step. Document tradeoff and pick one. Map to enforcement-gradient L3 (hook) per `.claude/rules/patterns.md`. Do NOT touch the wrapper. Exit: 1-page plan + GitHub issue draft (do NOT open the issue).

### Prompt L — Implement D1 + D2 as a dispatcher pre-flight script

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: dispatch-dedupe-script-plan-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/dispatch-dedupe-script-plan-1.md (fallback `docs/sessions/...`)
> Hard gates: same as Prompt K.
> Task: Read D1 + D2 in this lane. Spec a single shell script `scripts/enforcement/check-lane-dispatch-dedupe.sh` callable from the dispatcher (or pre-commit-style). It accepts `<run-id> <lane-name> <prompt-file>` and exits non-zero if D1 or D2 trips. Map to enforcement-gradient L2 per `.claude/rules/patterns.md`. Do NOT write the script — produce a 1-page plan including diff sketch, test cases (collide same-name same-hash, collide same-name diff-hash, no-collision), and rollback. Exit: result file with the plan.

### Prompt M — Operator-side triage of the inverted provider mix in run 114355

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: provider-mix-triage-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/provider-mix-triage-1.md (fallback `docs/sessions/...`)
> Hard gates: same as Prompt K.
> Task: Run 114355 dropped gemini entirely while keeping codex (regression-blocked). This is structurally inverted — gemini-flash was 67% yield in 111336 and codex was 0%. Read the dispatcher source (likely `classify_and_launch.sh` in `provider-autofeed-monitor/`) and any per-run override (`provider-autofeed-20260430-114355/manifest.json` or equivalent) to identify whether the gemini drop was intentional, a bug, or a config drift. Confirm or refute that PID 2128357 (codex from 111336) is still alive at the time you run; if so, that's evidence the host CLI was not downgraded between runs. Recommend whether next tick should restore gemini-flash. Do NOT modify anything. Exit: result file with binary verdict and recommendation.

### Prompt N — Audit the `docs/sessions/` ENV-MISMATCH artifact convention

> Workspace: /mnt/local-analysis/workspace-hub
> Lane: env-mismatch-artifact-audit-1
> Result file: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/env-mismatch-artifact-audit-1.md (fallback `docs/sessions/...`)
> Hard gates: same as Prompt K. **Reconnaissance only.**
> Task: Glob `docs/sessions/2026-04-30-*provider-autofeed*` and `docs/sessions/2026-04-30-*-FALLBACK.md` and `docs/sessions/2026-04-30-*-result.md`. Identify naming-convention drift (the 114355 run already uses `-FALLBACK` and `-result` suffixes inconsistently). Recommend a single canonical filename pattern per D4. Do NOT rename files. Exit: result file with retain/rename recommendations table.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`.
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted.
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; U9 satisfied for the issue drafts implied in Prompts K/L/M/N).
- ✓ No outreach drafts.
- ✓ No self-approval / no `status:plan-approved` label changes (U6 satisfied).
- ✓ No unapproved implementation — D-series and U-series are *prescriptive specs only*; landing them requires Prompts K/L (planning) plus `issue-planning-mode` skill plus user approval.
- ✓ No isolated worktree created — no source edits in this lane; this document is a session-note artifact.
- ✓ No secrets emitted.
- ✓ Memory-aligned: cites `feedback_lane_result_path_outside_sandbox.md`, `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_never_offer_to_self_label_plan_approved.md`, `feedback_check_parallel_work.md`, `feedback_gh_issue_comment.md`, `feedback_gh_issue_close_silent_comment_drop.md`, `feedback_codex_sustained_major_loop.md`, `project_issue_2460_approval_binding.md`.
- ✓ Timeouts: `Bash pgrep` was the only Bash call that touched live state; bounded by tool-layer limits.
- ✓ U3 satisfied: this lane's `.lane-state.json` (when written by the wrapper) should record `status: "completed-fallback"`, NOT `"completed"`, until the orchestrator out-of-band-copies this file.

## Evidence appendix — what backed every rule

| Rule | Backing evidence |
|---|---|
| D1 | THIS lane's collision-avoidance with 111336's `claude-stream-governance-loop-4` (same family, integer bumped to 3); generalizes R5. |
| D2 | 111336-recovery-governance-1 §Cross-cutting (variant fan-out negative-yield); `feedback_codex_sustained_major_loop.md`. |
| D3 | 111336-loop-4 already authored R1-R10 — reusing that prefix would silently overwrite. THIS lane uses `D` and `U`. |
| D4 | `docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` and `2026-04-30-claude-stream-plan-hardening-3-result.md` use different suffix conventions for the same artifact class. |
| D5 | `feedback_gh_issue_comment.md` + `feedback_gh_issue_close_silent_comment_drop.md`. |
| U1 | THIS lane's situation: predecessor lanes 1/2 in 114355 had result files but content was unverifiable from sandbox; default to `[predecessor-pending]` flag, which is the rule's branch. |
| U2 | CLAUDE.md hard gates verbatim; `feedback_never_offer_to_self_label_plan_approved.md`; `project_issue_2460_approval_binding.md`. |
| U3 | `feedback_lane_result_path_outside_sandbox.md`; recurrence #4 in 24 h. |
| U4 | 111336-loop-4 R6 (heartbeat probe) — `idle-but-alive` and `stalled-no-emission` are evidence-distinct states. |
| U5 | 100339 §Cross-cutting rec #1 (presence-only is brittle); 111336-loop-4 R7 (lane-state.json contract). |
| U6 | `feedback_never_offer_to_self_label_plan_approved.md` (verbatim hard invariant). |
| U7 | `feedback_codex_cli_0_124_upstream_regression.md` AND live evidence: PID 2128357 (`codex exec ... -` from 111336) still alive at this lane's start, ~33 min after dispatch. |
| U8 | `feedback_codex_cli_0_124_upstream_regression.md` addendum: "Downgrade does NOT help from Claude Code's Bash tool." |
| U9 | CLAUDE.md hard gates ("no unapproved implementation"); generalization of U6 to issue creation. |

No log/prompt body was read from this lane (sandbox-blocked). All evidence is from: (a) Glob enumeration of `agent-logs/provider-autofeed-20260430-114355/**`, (b) `Bash pgrep -af 'provider-autofeed'` snapshot at lane start, (c) two predecessor session artifacts under `docs/sessions/`, (d) the cited memory feedback files.

## Concurrency snapshot (taken at lane start)

`pgrep -af 'provider-autofeed'` showed 4 alive runs at lane start:

| Run | Status |
|---|---|
| 102314 | `claude-recovery-control-plane-1` PID 2086417 still alive (~104 min); `gemini-flash-gtm-risk-5` PID 2088647 alive via `relaunch_replacements.sh` |
| 104814 | gemini lanes (`gemini-flash-1-research-queue-expansion`, `gemini-flash-2-gtm-legal-risk`) and `codex-1-approved-marker-scout` alive |
| 111336 | `codex-stdin-approved-scout-1` PID 2128357 alive (~33 min after dispatch — direct evidence of unfixed 0.124 stdin-hang) |
| 114355 | this lane + 5 sibling lanes |

This snapshot is itself the strongest evidence for U7 (codex result-file ↛ "executed") and U8 (variant fan-out exhaustion is not exploration completion when the regression is open).

## STARTED/FINISHED markers

- **STARTED:** 2026-04-30T~11:46Z (lane dispatch by orchestrator; Glob enumeration began ~11:46Z)
- **FINISHED:** 2026-04-30T~12:10Z (this artifact written under `docs/sessions/`)
- **Out-of-band copy required (U3):** orchestrator should `cp` this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/claude-governance-loop-3.md` to satisfy the prescribed path. Until that copy lands, the lane's effective status is `completed-fallback`, not `completed`.
- **Prompt-id chain to next tick:** K is highest priority (escalate to hook) and independent. L depends on D1/D2 spec being read but otherwise standalone. M is operator-host-flavored and can run in parallel with K and L. N is independent. **Do NOT chain — dispatch one at a time and re-evaluate per D2.**
