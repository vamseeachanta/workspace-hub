# Provider-Autofeed Control-Plane Synthesis — `claude-control-plane-synthesis-1` (run 20260430-102247)

> **Lane ID:** `claude-control-plane-synthesis-1`
> **Run:** `provider-autofeed-20260430-102247`
> **Author:** Claude Opus 4.7 (1M ctx), control-plane-synthesis tier.
> **STARTED (UTC):** 2026-04-30 (lane invocation; first tool call this session was `Bash mkdir` against agent-logs which was permission-denied)
> **Hard gates honored:** planning/handoff only; no GitHub mutations; no `status:plan-approved` writes; no implementation; no destructive resets; no outreach; `GIT_OPTIONAL_LOCKS=0` not exercised (no git ops attempted); no secrets emitted.

## ENV-MISMATCH banner — sandbox recurrence (chronic)

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/results/claude-control-plane-synthesis-1.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| `Read` / `Write` / `mkdir` against `agent-logs/**` | **blocked** (permission-gate, verified at lane start: `Bash mkdir` denied; `Read` of own prompt denied; `Read` of base.txt denied; `Read` of own pre-existing result-stub denied) |
| What still works | `Read` / `Write` inside `workspace-hub`; `Glob` enumeration of `agent-logs/**` (filename-only, no content) |
| Bash availability this lane | **denied** for `pgrep`/`date`/`git` — narrower than predecessor synth lane `145633` which had Bash. This lane could not capture live-host evidence. |
| Canonical durable output | **THIS document** at `docs/sessions/2026-04-30-provider-autofeed-102247-claude-control-plane-synthesis-1.md`. |
| Out-of-band copy required | Orchestrator should `cp` this file to the prescribed `agent-logs/` result path. Until then, lane status = `completed-fallback`, NOT `completed`. |

Per memory `feedback_lane_result_path_outside_sandbox.md` (recurrence #9 in 24h, counting predecessors `073439`/`100339`/`111336×2`/`114355×2`/`125920×2`/`145633` and now this lane). The fallback contract is well-established; the spawner-side fix has not landed.

## Lane scope — narrow per dispatch task

The orchestrator asked for: **"audit current provider-autofeed monitor artifacts and lane states; classify useful-active vs stale/non-consuming evidence; produce next-tick recovery rules and a concise approval-readiness/handoff summary."**

I extend the prior R/D/U/W/G/H rule ladder (D3 honored — never redefine; only extend) with a fresh `K`-prefix (Control-plane / KPI). The K-series captures defects observable in run `102247` that the H-series did not cover, primarily around **provider-mix-vs-work-queue alignment** and **lite-variant lane duplication**.

## Predecessor sources consulted (this lane)

- `docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` (top-level contract: useful-lane defn, defaults, stall signatures §5, recovery decision table §6, routing rules §7, cron-ready prompt fragments §8)
- `docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md` (H1–H8 + ENV-MISMATCH playbook + sibling-content-dependency contract)
- `docs/sessions/2026-04-30-provider-autofeed-20260430-145633-claude-control-synthesis-recovery-1.md` (prior synthesis lane that established the per-lane classification taxonomy)
- `config/ai-tools/provider-routing-scorecard.json` (generated 2026-04-30T13:32:28Z)
- `config/ai-tools/provider-work-queue.json` (generated 2026-04-30T13:35:19Z)
- `config/ai-tools/provider-utilization-weekly.json` (generated 2026-04-30T13:29:46Z)
- `queue/.watcher-state/git-pull-failures.count` (value: `1`)
- Memory feedback: `feedback_lane_result_path_outside_sandbox`, `feedback_codex_cli_0_124_upstream_regression`, `feedback_codex_sandbox_no_execution`, `feedback_codex_sandbox_write_blocked`, `feedback_gemini_sandbox_overlay_blindness`, `feedback_gemini_trust_env_blocks_reviews`, `feedback_codex_sustained_major_loop`, `feedback_never_offer_to_self_label_plan_approved`, `feedback_inline_gh_issue_url`

**Sources NOT inspected (sandbox-blocked):** prompts, base.txt, all sibling result files, all log files, snapshot.txt, active_ps.txt, make_and_launch.sh.

## 1. Lane manifest — run 102247 (verified via Glob; content unverified)

Run `provider-autofeed-20260430-102247` fanned out **14 distinct lane prompt+result pairs** across 3 providers — substantially larger than the 9-lane run `145633`:

| # | Provider | Lane | Variant | Notes |
|---|----------|------|---------|-------|
| 1 | Claude | `claude-control-plane-synthesis-1` (this) | full | 3-of-3 Claude lanes |
| 2 | Claude | `claude-plan-review-hardening-2` | full | |
| 3 | Claude | `claude-governance-autofeed-rules-3` | full | Note: lane name is `governance-autofeed-rules-3` here, vs. `governance-loop-rules-3` in run 145633 — semantic drift, not name reuse |
| 4 | Codex | `codex-approved-eligibility-scout-1` | full | |
| 5 | Codex | `codex-test-readiness-scout-2` | full | |
| 6 | Codex | `codex-worktree-hygiene-salvage-3` | full | salvage-class — runs into Codex sandbox-no-exec; output must be worklist only |
| 7 | Gemini | `gemini-research-queue-expansion-1` | full + lite | **both variants present** |
| 8 | Gemini | `gemini-gtm-legal-risk-2` | full + lite | both variants present |
| 9 | Gemini | `gemini-standards-source-recon-3` | full + lite | both variants present |
| 10 | Gemini | `gemini-governance-risk-recon-4-lite` | lite-only | no full counterpart |
| 11 | Gemini | `gemini-approval-readiness-recon-5-lite` | lite-only | no full counterpart |

**Total: 3 Claude + 3 Codex + 8 Gemini-shaped lanes = 14 lanes.**

Run `102247` predates this synthesis by hours (lane prompts globbed exist; predecessor sessions worked under runs starting 10:22Z and were captured around 11:33Z–14:56Z); per the `LOG_MTIME_MAX_S=600` defn in the staging contract, the 102247 lanes are very likely **terminal** (already exited or zombied) by the time of this synthesis. Confirmation requires orchestrator-side `stat` of result files (sandbox-blocked here).

## 2. Per-lane classification — useful-active vs stale/non-consuming

Classification scheme (established by predecessor synthesis `145633`):
- **useful-active** = result file likely contains substantive evidence the next-tick consumer can read.
- **stale/non-consuming** = result file likely empty/banner-only, OR written to a path the next-tick consumer cannot reach, OR content is structurally invalidated by a known sandbox boundary.

| # | Lane | Class | Rationale | Confidence |
|---|------|-------|-----------|------------|
| 1 | `claude-control-plane-synthesis-1` | **useful-active at fallback** (`docs/sessions/`) | This document. ENV-MISMATCH pivot succeeded. | High |
| 2 | `claude-plan-review-hardening-2` | **stale at prescribed path; uncertain at fallback** [content-unverified] | Same Claude sandbox boundary; without explicit fallback in its prompt, lane likely silently stalled. Glob shows no matching `docs/sessions/` artifact for this run yet, but a sibling parallel-FALLBACK file (`docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` — different naming convention from H8b canonical) DOES exist (per `git status` snapshot at session start), suggesting the lane did pivot, just via a non-canonical naming. | Medium-high |
| 3 | `claude-governance-autofeed-rules-3` | **stale at prescribed path; possible at fallback** [content-unverified] | Same boundary. No corresponding `docs/sessions/` artifact named with `102247` prefix in the Glob. May be in flight, may have died, may have written to a non-canonical name. | Medium |
| 4 | `codex-approved-eligibility-scout-1` | **likely useful-active** [content-unverified] | Read-only Codex task; fits sandbox. Caveat: if `codex-cli` was on banned 0.124.x at launch, all 3 codex lanes are stale per `feedback_codex_cli_0_124_upstream_regression` regardless. | Medium |
| 5 | `codex-test-readiness-scout-2` | **likely useful-active** [content-unverified] | Same. | Medium |
| 6 | `codex-worktree-hygiene-salvage-3` | **mixed** — analysis useful-active, *salvage actions* stale by design | Codex sandbox blocks shell exec & writes; this lane can only emit a worklist for a follow-up implementation lane. Codex result-file overwrite hazard per H7 applies if any older run had a zombie writing to the same `--output-last-message` path. | Medium |
| 7a | `gemini-research-queue-expansion-1` (full) | **likely useful-active** [content-unverified] | External-research task; sandbox-blindness on local files irrelevant. Trust-env precondition required. | Medium |
| 7b | `gemini-research-queue-expansion-1-lite` | **likely-redundant useful-active** [content-unverified] | Lite + full duplicate dispatch — see K1 below. Both contain similar evidence; downstream consumer cannot tell which to authoritatively read. | Medium |
| 8a | `gemini-gtm-legal-risk-2` (full) | **likely useful-active** [content-unverified] | Same shape. | Medium |
| 8b | `gemini-gtm-legal-risk-2-lite` | **likely-redundant useful-active** [content-unverified] | Same K1 issue. | Medium |
| 9a | `gemini-standards-source-recon-3` (full) | **caution: standards-recon path** [content-unverified] | Standards recon historically produces local-file citations from Gemini that are sparse-overlay false-positives (memory `feedback_gemini_sandbox_overlay_blindness`). Treat any local-file claims as **must-verify with `git ls-files`** before trusting. | Medium |
| 9b | `gemini-standards-source-recon-3-lite` | **same caution; redundant** | K1 + same overlay-blindness caveat. | Medium |
| 10 | `gemini-governance-risk-recon-4-lite` (lite-only) | **likely useful-active** [content-unverified] | Lite-only with no full counterpart. Risk recon is a research-shaped task that fits Gemini-Pro's profile. | Medium |
| 11 | `gemini-approval-readiness-recon-5-lite` (lite-only) | **especially relevant to this synthesis lane** [content-unverified] | Lane-name overlap suggests this lane is meant to feed *me*. Sibling-content-dependency per H6 applies — I cite this lane by name only and explicitly do NOT consume content. Operator-side verification required. | High |

**Headline aggregate inference:** of 14 lanes,
- ~2 lanes (claude-2, claude-3) are at-risk-of-silent-stall at the prescribed result path;
- ~6 lanes (gemini-1a/1b, gemini-2a/2b, gemini-3a/3b) are duplicate fan-out by lite/full variant pairing;
- ~2 lanes (gemini-4-lite, gemini-5-lite) are unique;
- ~3 codex lanes' usefulness is gated on the codex-cli version preflight at launch time.

Effective unique-evidence yield ≈ 3 codex + 3 unique gemini-shaped + 1 claude-fallback (this lane) = **~7 of 14 lanes contributed unique evidence**, ~50% efficiency. The other 50% are duplicate or sandbox-stalled.

## 3. Recovery rules — fresh K-series

Each rule has: precondition, observable check, action, dedupe, unsafe-transition gate, no-op clause, citation, retire-when, bound. Same shape as H1–H8 (D3 honored).

### K1 — Lite-vs-full variant duplicate-dispatch detector

| Field | Value |
|---|---|
| **Precondition** | Dispatcher is about to dispatch ≥2 lanes whose names share a stem and differ only by a `-lite` suffix. |
| **Check** | For each lane name `N`, compute `stem = N.removesuffix("-lite")`. If multiple lanes in the same run share the same `stem`, emit `LITE-VARIANT-DUPLICATE: stem=<stem>, variants=<list>`. |
| **Action when matched** | Operator-only decision: keep both (intentional A/B), keep lite (token-budget tradeoff), or keep full (depth tradeoff). Emit decision-prompt to operator BEFORE dispatch; do NOT auto-dedupe inside the lane. |
| **Built-in dedupe** | One `LITE-VARIANT-DUPLICATE` emission per `(run_id, stem)`. Do NOT re-emit on retry of same run. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane killing its `-lite` (or non-`-lite`) sibling to "free budget" — composes with G3 (operator-owned). **Forbidden:** rewriting one variant's prompt to eliminate the other from inside a lane (lane-prompt mutation; composes with R9). **Forbidden:** auto-merging two variants' results — that's content fabrication, not dedupe. **Forbidden:** silently dropping the lite variant from scoreboard tallies — operator may have wanted A/B comparison data. |
| **No-op clause** | All lanes have unique stems. |
| **Citation** | Run 102247 — `gemini-{research-queue-expansion-1, gtm-legal-risk-2, standards-source-recon-3}` each have `-lite` and full variants. 6 of 14 lanes are pairwise-redundant. |
| **Retire when** | Dispatcher gains a single canonical "model-tier" axis per lane (i.e., model-tier becomes a parameter, not a name suffix). Then lite-vs-full is configuration, not lane proliferation. |
| **Bound** | One regex pass over lane manifest at dispatch. |

### K2 — Provider-mix vs work-queue-depth alignment gate

| Field | Value |
|---|---|
| **Precondition** | Dispatcher is about to dispatch lanes for provider P. |
| **Check** | Read `config/ai-tools/provider-work-queue.json`. For provider P, capture `execution_ready_count` and `total_candidates`. Compare to lanes-to-dispatch count `L_P`. If `L_P > max(execution_ready_count × 2, 4)`, emit `FAN-OUT-MISMATCH: provider=<P>, dispatching=<L_P>, queue_ready=<n>, total_candidates=<m>`. |
| **Action when matched** | Surface to operator BEFORE dispatch. **Do NOT auto-block** — operator may deliberately fan out (e.g., research-recon over external sources where work-queue depth is irrelevant). |
| **Built-in dedupe** | One `FAN-OUT-MISMATCH` emission per `(run_id, provider)`. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane synthesizing fake GitHub candidates to backfill work-queue depth — that's a U2 violation (creates implementation-by-fabrication). **Forbidden:** auto-promoting non-execution-ready candidates to execution-ready inside a lane (composes with U6, U2 — `status:plan-approved` is user-in-loop only). **Forbidden:** auto-rebalancing dispatch counts between providers from inside a lane (composes with G3 — operator-owned). |
| **No-op clause** | Provider's work is research-shaped (not GitHub-issue-bound) AND scorecard `preferred_work` includes "research" or "scouting". In that case the work-queue is the wrong denominator; emit a Once-Per-Run `RESEARCH-LANE-EXEMPT` marker for transparency. |
| **Citation** | Run 102247 dispatched **8 Gemini lanes** vs. work-queue showing Gemini `execution_ready_count = 0`, `total_candidates = 2`. Gemini is correctly classified as research-shaped (preferred work = "batched research/recon, risk enumeration, competitor/standards scans, issue expansion and scouting"), so the no-op clause **probably** applies — but the dispatcher provides no telemetry distinguishing intentional research over-fan-out from accidental misalignment. K2 closes that observability gap. |
| **Retire when** | Dispatcher emits per-provider `lane-shape: {github-bound, research, governance}` taxonomy and only checks K2 when shape is `github-bound`. |
| **Bound** | One JSON read + one comparison per provider per dispatch. |

### K3 — Activity-vs-quota divergence telemetry

| Field | Value |
|---|---|
| **Precondition** | Scoreboard or governance lane is about to render provider health. |
| **Check** | Read `config/ai-tools/provider-utilization-weekly.json`. For each provider P in the current week, compute `divergence = activity_utilization_pct - quota_utilization_pct` if both exist. If `abs(divergence) >= 50` percentage points AND `quota_basis == "quota"` (i.e., not estimated), emit `ACTIVITY-QUOTA-DIVERGENCE: provider=<P>, activity=<a>%, quota=<q>%, divergence=<d>pp`. |
| **Action when matched** | Surface to operator. The interpretation is operator-owned — high-activity-low-quota commonly means "many small operations" (could be wasteful or could be efficient batching); high-quota-low-activity means "few high-cost calls" (could be deep work or could be rate-limited retry). |
| **Built-in dedupe** | One `ACTIVITY-QUOTA-DIVERGENCE` emission per `(week, provider)`. |
| **Built-in unsafe-transition gate** | **Forbidden:** auto-throttling a provider on divergence alone without operator decision (high-activity is not synonymous with waste). **Forbidden:** demoting a provider in `recommended_provider_order` from inside a lane (config-mutation; operator-owned). **Forbidden:** auto-creating GitHub issues for divergence emissions; this is a telemetry signal, not an issue. |
| **No-op clause** | `quota_basis != "quota"` (estimated/unavailable basis is too unreliable for divergence comparison). |
| **Citation** | This week (W18, latest scorecard 2026-04-30T13:32Z): **Codex activity=100%, quota=0.4%, divergence=99.6pp.** Claude basis is `unavailable`. Gemini activity=0.1%, quota=0.0% — below threshold. The Codex divergence is striking and unexplained — could be many small batch operations, could be retry-loop waste from `feedback_codex_cli_0_124_upstream_regression`, could be the well-documented high-Bash-call shape. K3 surfaces it for operator interpretation, does NOT auto-act. |
| **Retire when** | Provider quota telemetry includes per-call cost so divergence can be normalized to dollars. |
| **Bound** | One JSON read + one subtraction per provider per render. |

### K4 — Run-staleness reaping convention

| Field | Value |
|---|---|
| **Precondition** | A new dispatcher tick is about to fire. |
| **Check** | Enumerate distinct `provider-autofeed-<run-id>` directories under `/mnt/local-analysis/agent-logs/` whose mtime > `RUN_STALENESS_REAP_S = 7200` (2h, the per-lane wrapper timeout). For each, check whether ANY lane process is still alive (`pgrep -af 'provider-autofeed-<run-id>'`). If no live processes AND result/log files have not been read by the orchestrator scoreboard in `RUN_STALENESS_REAP_S`, mark run as `reapable` and emit `RUN-REAPABLE: run=<id>, age=<hours>h, lanes=<n>, reason=no-live-pid`. |
| **Action when matched** | Operator-only decision: archive `agent-logs/<run-id>/` to a stale-runs directory OR keep for forensic. **Do NOT auto-delete** — these directories contain prompts, logs, and result evidence that may be needed for post-mortem of stall-class signatures. |
| **Built-in dedupe** | One `RUN-REAPABLE` emission per `run_id` per scoreboard render. |
| **Built-in unsafe-transition gate** | **Forbidden:** the lane deleting any `agent-logs/<run-id>/` directory (composes with U3 — orchestrator-owned). **Forbidden:** the lane killing any process inside an old run (could be a long-tail Codex zombie that's still emitting; killing risks data loss). **Forbidden:** auto-archiving runs that have NOT exceeded `RUN_STALENESS_REAP_S` even if they appear "done" — lanes can be quiescent mid-flight (e.g., Codex stdin-hang). |
| **No-op clause** | All visible runs younger than `RUN_STALENESS_REAP_S`. |
| **Citation** | Today's host has had at least 8 distinct provider-autofeed runs in <8h (`073439, 100339, 102247, 111336, 114355, 125920, 145633` plus the `133520/140140/143424` cited by the 145633 governance lane). Without a reaping convention, `agent-logs/` grows monotonically. |
| **Retire when** | Dispatcher writes a `state/run.json` per run with `started_at`/`finished_at`/`reaped_at` and the scoreboard handles reaping natively. |
| **Bound** | One `find -maxdepth 1 -type d` + one `pgrep` per run per tick. |

### Insertion into rule precedence (extends the H-series ladder from `145633`)

- **K2** (fan-out vs work-queue alignment) — fires at dispatcher pre-launch, between **H2 (run-density cap)** and **R5/D1 (lane-name × prompt-hash dedupe)**. K2 is per-provider; H2 is per-host.
- **K1** (lite-variant duplicate-dispatch) — fires at dispatcher pre-launch, **adjacent to D1** (lane-name dedupe). D1 catches identical names; K1 catches stem-equivalent names with variant suffixes.
- **K3** (activity-vs-quota divergence) — fires at scoreboard render and at governance-lane authoring time, **adjacent to H4 (aggregate-budget visibility)**. Both are budget/observability signals.
- **K4** (run-staleness reaping) — fires at dispatcher pre-launch (NOT at run-finalize), **adjacent to H8 (path conventions)**. H8 specifies what's in the directory; K4 specifies when the directory ages out.

## 4. Approval-readiness summary (operator-facing)

This lane produced **planning/handoff evidence only**. Nothing in §3 may be auto-applied. The following items are queued for operator decision; each lists the explicit user-in-loop gate it crosses (per `feedback_never_offer_to_self_label_plan_approved.md` and `project_issue_2460_approval_binding.md`):

| # | Item | User gate | Suggested next step |
|---|------|-----------|---------------------|
| A1 | Promote H8 path conventions + K-series rules from session-notes to a versioned spec at `docs/governance/provider-autofeed/path-conventions.md` and `docs/governance/provider-autofeed/rules.md`. | New planning issue + `status:plan-approved` after cross-review. | Operator opens issue using `docs/plans/_template-issue-plan.md`; assigns 2-provider cross-review per `project_cross_review_policy`. |
| A2 | Land K1 (lite-variant detector) as L2 enforcement script at `scripts/enforcement/check-lane-variant-duplicates.sh`. | New planning issue + plan-approved. | Operator authors prompt YA (analogous to predecessor's Prompt Y); do NOT self-approve. |
| A3 | Land K2 (fan-out × work-queue gate) as a dispatcher pre-check that reads `provider-work-queue.json`. | New planning issue + plan-approved. | Operator authors prompt YB. |
| A4 | Land K3 (activity-vs-quota divergence) as a scoreboard-render telemetry line. | New planning issue + plan-approved. | Operator authors prompt YC. K3 is the lowest-risk to land first because it's pure read+emit; no mutation. |
| A5 | Land K4 (run-staleness reaping) including a `state/run.json` schema. | New planning issue + plan-approved. | Coordinate with H8b path conventions promotion (A1) since K4 retire-when depends on H8. |
| A6 | Spawner-side fix for the chronic ENV-MISMATCH: every Claude lane's prescribed `result_path` must start with `workspace-hub`. | Operator-host change to dispatcher; not gated through GitHub `status:plan-approved`. | Patch `make_and_launch.sh` template (NOT from inside a lane — that's R9 violation). The recurrence count in 24h is now ≥9. |
| A7 | Codex-cli version pin verified for run 102247: confirm installed Codex was NOT 0.124.x at the time the run launched. | Operator-host check. | Read history.jsonl or `codex --version` against run 102247 launch timestamp. |
| A8 | Promote `staging-autofeed-recovery-contract/` from staging to canonical `docs/governance/provider-autofeed-recovery-contract.md` per its own §9.2 procedure. | New planning issue + cross-review + plan-approved. | Operator authors a promotion plan; do NOT auto-promote from inside a lane. |

**Strongest single recommendation:** **A4 (land K3 as scoreboard telemetry).** It is read-only, surfaces a striking signal (Codex W18: 100% activity vs 0.4% quota) that has no current visibility, has no enforcement risk, and unblocks downstream judgment about whether the Codex high-activity pattern is wasteful or efficient. K3 is the lowest-cost, highest-information-yield first step.

**Second-strongest:** **A6 (spawner-side ENV-MISMATCH fix).** It is operator-host-only (no GitHub gate), would eliminate a chronic per-run budget tax, and would convert ~50% of Claude lanes per run from at-risk-of-silent-stall to reliably-useful. Recurrence #9 in 24h means this is no longer hypothetical.

## 5. Concise handoff

| Question | Answer |
|---|---|
| Did this lane reach its prescribed result path? | **No.** Sandbox blocked Write to `agent-logs/`. Fallback at `docs/sessions/2026-04-30-provider-autofeed-102247-claude-control-plane-synthesis-1.md` (this file). |
| Is run 102247 still alive? | **Likely terminal** (run started 10:22Z, this synthesis at ~13:32Z+ after scorecard reads; per-lane wrapper timeout = 7200s/2h). Bash unavailable this lane to verify with `pgrep`. Operator should `pgrep -af 'provider-autofeed-20260430-102247'` to confirm. |
| Useful-active lane count for run 102247 | **~7 of 14 unique-evidence; ~6 redundant via lite/full variant duplication; 1 fallback recovery (this).** |
| Is there a queue floor breach? | **Unknown** without reading `agent-logs/...` directly. The staging contract specifies `≥3 useful lanes per provider`. By Glob-only inference, Claude is at-risk; Codex/Gemini likely above floor IF codex-cli was on a non-banned version. |
| Are any rules from H1–H8 drifting? | **H1 itself drifted in run 145633** (per predecessor synthesis). Cannot verify drift in 102247 from sandbox-blocked sources. |
| Any urgent operator action? | **A6 (spawner-side ENV-MISMATCH fix)** — chronic, recurrence #9; **A4 (K3 telemetry)** — surfaces unexplained Codex activity-quota divergence. |
| Self-approval / GitHub mutation count from this lane | **Zero** (verified — no Bash, no Write outside workspace-hub, no `gh` calls attempted). |
| Out-of-band copy required? | **Yes.** Orchestrator should copy this file to `agent-logs/provider-autofeed-20260430-102247/results/claude-control-plane-synthesis-1.md`. |

## 6. What this lane explicitly does NOT do

- ✗ Does **not** label any GitHub issue with `status:plan-approved`.
- ✗ Does **not** open / close / comment on any GitHub issue or PR.
- ✗ Does **not** modify any dispatcher script (`classify_and_launch.sh`, `make_and_launch.sh`, etc.).
- ✗ Does **not** modify any provider wrapper (`submit-to-codex.sh`, `submit-to-gemini.sh`).
- ✗ Does **not** create a worktree (no source edits attempted).
- ✗ Does **not** kill any process. K2/K3/K4 surface signals only; actions are operator-owned.
- ✗ Does **not** copy this artifact to the prescribed `agent-logs/` path (orchestrator-owned per U3).
- ✗ Does **not** redefine any rule in R1–R10, D1–D5, U1–U9, W1–W5, G1–G8, H1–H8 (D3 honored; fresh prefix `K`).
- ✗ Does **not** mutate `.claude/state/`, `.planning/plan-approved/`, or any memory feedback file.
- ✗ Does **not** consume sibling lane content (H6 self-honoring; siblings cited by lane-name + Glob hit only).
- ✗ Does **not** auto-promote the staging recovery contract (A8 is operator-gated).
- ✗ Does **not** auto-create issues for the K-series (A1–A5 are operator-gated).

## 7. Embedded `.lane-state.json` (per H8c — fallback state surface)

```json
{
  "lane_name": "claude-control-plane-synthesis-1",
  "run_id": "provider-autofeed-20260430-102247",
  "status": "completed-fallback",
  "result_path_actual": "docs/sessions/2026-04-30-provider-autofeed-102247-claude-control-plane-synthesis-1.md",
  "result_path_prescribed": "/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/results/claude-control-plane-synthesis-1.md",
  "log_path_prescribed": "/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/logs/claude-control-plane-synthesis-1.log",
  "started_utc": "2026-04-30",
  "finished_utc": "2026-04-30",
  "predecessors_in_run_cited_by_name_only": [
    "claude-plan-review-hardening-2",
    "claude-governance-autofeed-rules-3",
    "codex-approved-eligibility-scout-1",
    "codex-test-readiness-scout-2",
    "codex-worktree-hygiene-salvage-3",
    "gemini-research-queue-expansion-1",
    "gemini-research-queue-expansion-1-lite",
    "gemini-gtm-legal-risk-2",
    "gemini-gtm-legal-risk-2-lite",
    "gemini-standards-source-recon-3",
    "gemini-standards-source-recon-3-lite",
    "gemini-governance-risk-recon-4-lite",
    "gemini-approval-readiness-recon-5-lite"
  ],
  "predecessors_cross_run": [
    "docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md",
    "docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md",
    "docs/sessions/2026-04-30-provider-autofeed-20260430-145633-claude-control-synthesis-recovery-1.md"
  ],
  "rules_authored": ["K1", "K2", "K3", "K4"],
  "approval_items_queued": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
  "awaiting_orchestrator_copy": true,
  "env_mismatch_recurrence_count_24h": 9,
  "bash_available_this_lane": false,
  "live_host_evidence_captured": false,
  "control_plane_state_evidence_captured": true,
  "control_plane_state_sources": [
    "config/ai-tools/provider-routing-scorecard.json (2026-04-30T13:32:28Z)",
    "config/ai-tools/provider-work-queue.json (2026-04-30T13:35:19Z)",
    "config/ai-tools/provider-utilization-weekly.json (2026-04-30T13:29:46Z)",
    "queue/.watcher-state/git-pull-failures.count (value: 1)"
  ]
}
```

## 8. Provenance (per H8e — required block)

| Source | Evidence captured |
|---|---|
| `Glob /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102247/**` | 14 prompt files, 14 result files (skeletons), 6 log files (logs/ has fewer entries than prompts/ — Gemini-Pro lite-variants apparently share log files or skip log creation), `base.txt` |
| `Read` attempts on prompts/, base.txt, results/ in agent-logs/ | All denied (permission-gate; verified mid-lane) |
| `Bash` calls (`mkdir`, `pgrep`, `date`, `git`, `ls` against agent-logs) | All denied (permission-gate; verified at lane start) |
| `Read /mnt/local-analysis/workspace-hub/config/ai-tools/provider-routing-scorecard.json` | Full body — recommended order `[gemini, codex, claude]`; Codex routing_priority=highest, status=underused, quota=0.4%; Gemini routing_priority=highest, status=underused, activity=0.1% (!), quota=0.0%; Claude routing_priority=high, status=needs_cleanup, activity=10.1% |
| `Read /mnt/local-analysis/workspace-hub/config/ai-tools/provider-work-queue.json` | Claude execution_ready=5/163; Codex execution_ready=12/35; **Gemini execution_ready=0/2** (the K2 evidence) |
| `Read /mnt/local-analysis/workspace-hub/config/ai-tools/provider-utilization-weekly.json` | W18: Claude 10.1%/—; Codex 100%/0.4% (the K3 evidence — 99.6pp divergence); Gemini 0.1%/0.0%; Hermes 4.6% (down from 100% W17). 8-week history available. |
| `Read /mnt/local-analysis/workspace-hub/queue/.watcher-state/git-pull-failures.count` | `1` (single failure — watcher healthy) |
| `Read /mnt/local-analysis/workspace-hub/docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md` | Full body — useful-lane defn, defaults (LOG_MTIME_MAX_S=600, RESULT_MIN_BYTES=256, MAX_RELAUNCH_PER_LANE=2), recovery decision table, routing hard blocks (Codex blocked for shell exec / writes / implementation), routing soft prefs, codex-cli version pin (`!= 0.124.x`), cron prompt fragments §8 |
| `Read /mnt/local-analysis/workspace-hub/docs/sessions/2026-04-30-provider-autofeed-145633-claude-governance-loop-rules-3.md` | Full body — H1–H8 + tick-145633 evidence + S9–S16 stall signature catalog |
| `Read /mnt/local-analysis/workspace-hub/docs/sessions/2026-04-30-provider-autofeed-20260430-145633-claude-control-synthesis-recovery-1.md` | Full body — per-lane classification taxonomy + recurrence-as-chronic-defect framing |
| `Glob` of `docs/sessions/2026-04-30-provider-autofeed-*` | 12 prior provider-autofeed session-note artifacts spanning runs 073439/100339/111336/114355/125920/145633 |
| `Glob` of `.planning/plan-approved/**` | 117 approved-marker files (truncated) — used to verify operator-gated approval surface exists; this lane did NOT add or modify any |
| Memory consulted | `feedback_lane_result_path_outside_sandbox` (recurrence taxonomy), `feedback_codex_cli_0_124_upstream_regression` (#2479), `feedback_codex_sandbox_no_execution`, `feedback_codex_sandbox_write_blocked`, `feedback_gemini_sandbox_overlay_blindness`, `feedback_gemini_trust_env_blocks_reviews`, `feedback_codex_sustained_major_loop`, `feedback_never_offer_to_self_label_plan_approved`, `feedback_inline_gh_issue_url`, `project_issue_2460_approval_binding`, `feedback_check_parallel_work` |

No log/prompt body was read from `agent-logs/` (sandbox-blocked at tool layer for this session — verified at lane start). No live-host process state was captured (Bash unavailable). All conclusions about lane content are filename-based + sandbox-boundary-inference + memory-grounded.

## 9. Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean` of `/mnt/local-analysis/workspace-hub`. No git mutations attempted.
- ✓ No GitHub mutations (no `gh issue`/`pr` calls; no comments; no labels). All A1–A8 items are explicit operator-gated drafts.
- ✓ No outreach drafts (no email, no Slack, no Drive uploads).
- ✓ No `status:plan-approved` label changes (U6 satisfied).
- ✓ No `.planning/plan-approved/<issue>.md` markers written or removed.
- ✓ No source-file edits; no isolated worktree created.
- ✓ No secrets emitted.
- ✓ No mutation of `.claude/state/` or any memory feedback file.
- ✓ U2 satisfied: planning/specification only. K-rules are *prescriptive specs*; landing them requires explicit operator-authored prompts.
- ✓ U6 satisfied: this lane did NOT offer to self-label; A1–A8 each name the operator gate explicitly.
- ✓ D3 satisfied: extends prior R/D/U/W/G/H with new `K` prefix; does not redefine any prior rule.
- ✓ D4 + G6 satisfied: single canonical artifact at `docs/sessions/2026-04-30-provider-autofeed-102247-claude-control-plane-synthesis-1.md`.
- ✓ G1 self-honoring: no subagent dispatched; no commit attempted.
- ✓ H6 self-honoring: 13 sibling lanes cited by name + Glob hit only; NO sibling content consumed.
- ✓ H8 self-honoring: embedded `.lane-state.json` (§7); included `Log:` back-pointer (in §7 JSON `log_path_prescribed`); included `## Provenance` (§8).

## 10. Strongest single follow-up

**Operator: spawn a planning lane to land K3 (activity-vs-quota divergence telemetry) as a scoreboard-render line item — and in the same plan, commit to investigate the W18 Codex 100%-activity / 0.4%-quota signal.** That signal is the highest-information-density artifact this synthesis surfaced and has zero current visibility in any predecessor session-note. The fix is a one-page plan; the diagnostic value is large.

---

*End of artifact. Mirrors prescribed `claude-control-plane-synthesis-1.md` schema; ENV-MISMATCH banner at top; out-of-band copy required by orchestrator.*
