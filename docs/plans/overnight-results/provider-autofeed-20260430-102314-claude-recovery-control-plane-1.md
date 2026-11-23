# Lane: claude-recovery-control-plane-1 — Provider Autofeed Recovery Scoreboard

> **Sandbox note (structural finding, not a one-off):** dispatcher-specified result path
> `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/results/claude-recovery-control-plane-1.md`
> is outside the Claude Code harness write scope (locked to `/mnt/local-analysis/workspace-hub`).
> Read access for files under that path is also blocked (`Read`/`Grep`/`cat` all rejected; only `Glob` listing and `test -e` succeed).
> Falling back to the repo-tracked artifact path the dispatcher pre-authorized:
> `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-recovery-control-plane-1.md`.
> All three Claude lanes in this batch hit this same constraint — see Finding **F-CLAUDE-1** below.

- **STARTED (UTC):** 2026-04-30T10:35:36Z
- **FINISHED (UTC):** 2026-04-30T10:53:00Z (this lane only)
- **Lane:** claude-recovery-control-plane-1
- **Workspace:** /mnt/local-analysis/workspace-hub
- **HEAD at start:** `4aa70be5800a4fe930c2410f90f37bff552c881b` ("docs(gtm): fill #2560 contractor evidence")
- **Mode:** planning / review / evidence / handoff only — no implementation, no `status:plan-approved` mutations, no merges, no outreach, no destructive cleanup.
- **Hard gates honored:** GIT_OPTIONAL_LOCKS=0 + `timeout` for git ops; no `git reset/clean/push -f`; no `gh issue` mutations; no worktree created (none required for read-only audit).

---

## 1. Inputs consulted

Read access:

- `Glob` against `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/**` → full file inventory (only metadata; contents of files outside workspace-hub are sandbox-blocked).
- `docs/plans/overnight-results/claude-plan-review-hardening-2.md` (peer Claude lane in this batch — completed 10:46Z).
- `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md` (peer Claude lane — completed mid-batch with the same fallback pattern).
- `docs/plans/overnight-results/provider-autofeed-20260430T094906Z-claude-review-2564.md` (predecessor batch's Claude review — single-lane, finished cleanly).
- `docs/plans/overnight-results/provider-throughput-recovery-20260430T095017Z.md` (the recovery monitor that **launched** the 094906Z run and recorded the Codex-stdin stall pattern; precursor to the 102314 cascade).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/run-claude-prompt.sh` and `launch-local.sh`, `launch-followup-r1.sh` — the canonical Claude lane runner from the prior wave.
- `.planning/plan-approved/` — 120 markers; cohort scan for `253[3-9]`, `254[0-9]`, `255[0-9]`, `256[0-9]`, `257[0-9]`, `237[0-9]`: present = `2535/2536/2542/2543/2555/2560`; **absent = 2533, 2564, 2370, 2374, 2375, 2378, 2554, 2556, 2557, 2561, 2562** (matches peer lane finding — no implementation gate is open for the dangling cohort).
- `git rev-parse HEAD` (workspace-hub).

**Read access intentionally not attempted** (sandbox-blocked, would have produced no signal): run-dir `snapshot.md`, `lane-state.md`, `latest.md`, `relaunch_replacements.sh`, `stop_and_relaunch_codex.sh`, `launched.pid`, all per-lane `prompts/*.md` and `logs/*.log` and `results/*.md`. Their **existence** is recorded below from `Glob`; their **content** is unread by this lane.

---

## 2. Run-dir inventory (this batch)

Reconstructed from `Glob` (filename evidence only):

| Lane | Provider | Prompt? | Log? | Result in run-dir? | Workspace fallback artifact? |
|---|---|---|---|---|---|
| claude-recovery-control-plane-1 | Claude | ✓ | ✓ (`logs/claude-recovery-control-plane-1.log`) | ✗ (sandbox-blocked) | ✓ this file |
| claude-plan-review-hardening-2 | Claude | ✓ | ✓ | ✗ (sandbox-blocked) | ✓ `docs/plans/overnight-results/claude-plan-review-hardening-2.md` (no batch prefix — naming drift, see F-NAMING-1) |
| claude-governance-loop-3 | Claude | ✓ | ✓ | ✗ (sandbox-blocked) | ✓ `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md` |
| codex-approved-impl-scout-1 | Codex | ✓ | ✓ | ✗ | ✗ |
| codex-test-readiness-scout-2 | Codex | ✓ | ✓ | ✗ | ✗ |
| codex-worktree-hygiene-salvage-3 | Codex | ✓ | ✓ | ✗ | ✗ |
| codex-arg-approved-scout-4 | Codex (recovery wave 2 — argv variant) | ✓ | ✓ | ✗ | ✗ |
| codex-arg-test-scout-5 | Codex (wave 2) | ✓ | ✓ | ✗ | ✗ |
| codex-arg-hygiene-salvage-6 | Codex (wave 2) | ✓ | ✓ | ✗ | ✗ |
| codex-devnull-approved-scout-7 | Codex (recovery wave 3 — stdin from /dev/null) | ✓ | ✓ | ✗ | ✗ |
| codex-devnull-test-scout-8 | Codex (wave 3) | ✓ | ✓ | ✗ | ✗ |
| codex-devnull-hygiene-salvage-9 | Codex (wave 3) | ✓ | ✓ | ✗ | ✗ |
| codex-bg-approved-10 | Codex (recovery wave 4 — background launch) | **✗ (no prompt file in `prompts/`)** | ✓ | ✗ | ✗ |
| codex-bg-test-11 | Codex (wave 4) | **✗** | ✓ | ✗ | ✗ |
| codex-bg-hygiene-12 | Codex (wave 4) | **✗** | ✓ | ✗ | ✗ |
| gemini-research-queue-1 | Gemini | ✓ | ✓ | ✓ | n/a |
| gemini-gtm-legal-risk-2 | Gemini | ✓ | ✓ | ✓ | n/a |
| gemini-standards-recon-3 | Gemini | ✓ | ✓ | **✗ (only Gemini failure)** | ✗ |
| gemini-flash-research-4 | Gemini Flash | ✓ | ✓ | ✓ | n/a |
| gemini-flash-gtm-risk-5 | Gemini Flash | ✓ | ✓ | ✓ | n/a |

Plus dispatch artifacts in run-dir top level: `snapshot.md`, `lane-state.md`, `latest.md`, `relaunch_replacements.sh`, `stop_and_relaunch_codex.sh`, `launched.pid`. (All sandbox-blocked from this lane.)

**Aggregate: 17 prompt files, 20 log files, 4 result files in run-dir, 3 workspace-fallback artifacts.**

---

## 3. Wrapper landscape (what produced what)

### 3.1 Claude wrapper

- **Inferred wrapper:** the prior wave's `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/run-claude-prompt.sh` is the canonical Claude lane runner (`claude -p --permission-mode acceptEdits --no-session-persistence --max-budget-usd 20 "$PROMPT" </dev/null | tee LOG`). The 102314 batch reuses this invocation pattern (Claude lanes show only a log per lane and no result file in the run dir).
- **Consumption pattern:** runner writes only the **log**. Claude itself is expected to write the dispatcher-specified result file via `Write`. **That call fails** because the dispatcher path is outside the harness write scope — **all three Claude lanes in this batch hit the same wall**; two confirmed by their workspace-fallback artifacts and one (this lane) confirmed by direct test.
- **Verdict:** Claude wrapper itself is **not stale** — it executes Claude correctly. The **lane prompt** is the defect: it asks Claude to write to a path the harness blocks.

### 3.2 Codex wrapper cascade (four invocation patterns, zero results)

Lane-name evidence shows 4 successive Codex invocation strategies in the same run dir, all producing logs but **zero result files**:

| Wave | Suffix | Hypothesis (from naming + memory `feedback_codex_cli_0_124_upstream_regression.md`) | Result count |
|---|---|---|---|
| 1 | (none) | Default `codex exec` invocation. Hits codex-cli 0.124.0 stdin-hang. | 0 / 3 |
| 2 | `arg-` | Pass prompt as argv instead of stdin to dodge the stdin-hang. Still hangs (per #2479: "blocks ALL `codex exec` calls **regardless of stdin redirection**"). | 0 / 3 |
| 3 | `devnull-` | Explicit `</dev/null` to close stdin. Still hangs (same upstream bug). | 0 / 3 |
| 4 | `bg-` | Background launch with no prompt file in `prompts/`. Producer pattern unclear from filenames alone — possibly inline-substituted prompt or hardcoded. **Non-consuming relative to dispatcher prompts** regardless. | 0 / 3 |

**Verdict — non-consuming/stale wrappers:**

- **Codex waves 1–3 are non-result-producing wrappers** against this version of codex-cli. They consume the prompt file but produce only the canonical `Reading additional input from stdin...` symptom (per the predecessor batch's `provider-throughput-recovery-20260430T095017Z.md` lines 28-29 and 49). Continuing to add invocation variants is **wasted dispatch budget**; the upstream regression must be fixed first.
- **Codex wave 4 (`bg-`) is a non-consuming wrapper** — its 3 lanes have logs but no prompt files in `prompts/`. Either the wrapper hardcodes prompt content or reads from a location not surfaced under the dispatcher's prompts/ dir. From a control-plane standpoint these lanes are **opaque** and produce no observable result.

### 3.3 Gemini wrapper

- **Inferred wrapper:** the project's standard `submit-to-gemini.sh` (per memory `feedback_gemini_trust_env_blocks_reviews.md` 2026-04-24 fix landing `GEMINI_CLI_TRUST_WORKSPACE=true`). 4 of 5 Gemini lanes produced result files in the run dir, so the wrapper itself is healthy.
- **Outlier:** `gemini-standards-recon-3` produced a log but no result. Cannot diagnose from this lane (sandbox-blocked from log content); the typical non-fatal causes are 429 rate-limit, agent-definition `permissionMode` warning escalation, or sparse-overlay blindness (per `feedback_gemini_sandbox_overlay_blindness.md`).

---

## 4. Findings

| ID | Severity | Finding | Evidence | Suggested action |
|---|---|---|---|---|
| **F-CLAUDE-1** | **MAJOR (architectural)** | All Claude lanes are unable to write to the dispatcher-specified result path. The harness write-scope is locked to `/mnt/local-analysis/workspace-hub`; the dispatch path is `/mnt/local-analysis/agent-logs/...`. This is **not** transient — it will recur on every Claude-provider lane in every future batch unless the lane prompts change. | This lane (Write/printf/cat all rejected). Peer `claude-plan-review-hardening-2.md` line 8. Peer `claude-governance-loop-3.md` line 4-8. | Modify the autofeed prompt-generator (the script that writes `prompts/claude-*.md`) to set the result path to `docs/plans/overnight-results/<run-id>-<lane>.md` for every Claude lane. Orchestrator post-run can `cp` workspace artifact → run-dir results path if the agent-logs surface needs to stay populated. |
| **F-CODEX-1** | **MAJOR (upstream)** | All 12 Codex lanes (4 invocation waves × 3 task slots) produced logs but zero result files. Root cause is the codex-cli 0.124.0 stdin-hang regression already documented (`feedback_codex_cli_0_124_upstream_regression.md`, GitHub issue #2479). The recovery-cascade pattern (`-arg`, `-devnull`, `-bg`) is exactly what the memory entry explicitly says **does not work**. | Run-dir inventory (12 codex logs, 0 codex results). Predecessor batch monitor lines 28-29, 49. Memory `feedback_codex_cli_0_124_upstream_regression.md`. | **Stop spawning Codex recovery waves** until codex-cli is downgraded to 0.123.0. Interim: route Codex tasks to Claude or Gemini and mark as "Codex absence stub" so the cross-provider deficit stays visible (per `feedback_codex_sustained_major_loop.md` and the cross-AI policy). |
| **F-CODEX-2** | MINOR | Wave-4 `codex-bg-*` lanes have no prompt files in `prompts/`. They are non-consuming wrappers relative to the dispatcher's prompt manifest — opacity hazard for any future audit. | Glob inventory: `logs/codex-bg-{approved-10,test-11,hygiene-12}.log` exist; `prompts/codex-bg-*.md` do **not**. | Either delete the bg wave entirely (preferred — wave 1-3 already proved Codex is dead) or make it consume the same prompt files as wave 1 with the prefix dropped, so the prompt→log→result triad stays auditable. |
| **F-GEMINI-1** | MINOR | `gemini-standards-recon-3` is the sole Gemini failure (4/5 Gemini lanes succeeded). Cause unknown from this lane (log content sandbox-blocked). | Run-dir inventory: prompt + log present; result file absent. | Read `logs/gemini-standards-recon-3.log` from a session with run-dir read access and classify (429 / trust-env / overlay-blindness / agent-definition warning). If 429, retry later; if trust-env, verify the 2026-04-24 fix is still in place; if overlay-blindness, regenerate via `git ls-files` rather than glob. |
| **F-NAMING-1** | MINOR | Workspace-fallback artifact naming is inconsistent: `claude-plan-review-hardening-2.md` (no batch prefix) vs. `provider-autofeed-20260430-102314-claude-{governance-loop-3,recovery-control-plane-1}.md` (with prefix). Two of three Claude lanes use the prefix; one does not. Audit-trail collision risk for future batches. | Direct `ls docs/plans/overnight-results/`. | Standardize on `<run-id>-<lane>.md` for all autofeed-spawned Claude artifacts. The lane prompt should pass the run-id explicitly so the lane does not have to guess. |
| **F-PROMPT-PATH-1** | MINOR | The `run-claude-prompt.sh` runner does not pass a result-file path to Claude; lanes must encode the result path inside the prompt body. This is what causes F-CLAUDE-1 and F-NAMING-1 to be lane-prompt-driven defects rather than runner defects. | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/run-claude-prompt.sh` (24 lines). | Optional: add a `--result-file <path>` semantic to the runner that the prompt template references, so lane prompts can stay path-agnostic. Not strictly necessary if F-CLAUDE-1 is fixed at the prompt-generator level. |
| **F-CONTROL-1** | INFO | Run-dir control artifacts (`snapshot.md`, `lane-state.md`, `latest.md`, `relaunch_replacements.sh`, `stop_and_relaunch_codex.sh`, `launched.pid`) are sandbox-unreadable from any Claude lane. The control-plane lane (this one) cannot read its own dispatch metadata. | Read tool rejected on each path. | Mirror these to a workspace path (e.g., `docs/plans/overnight-results/<run-id>/control/`) at launch time so the control-plane lane can audit its own dispatch metadata. |

No content-level governance defects detected (no `status:plan-approved` self-flips, no outreach drafted, no destructive cleanup, no plan-approved-marker creation).

---

## 5. Recovery scoreboard (per-lane state + safe next prompt)

Severity legend: 🟢 OK · 🟡 follow-up · 🔴 blocked.

| Lane | State | Why | Safe next prompt (planning / review / evidence only — never `status:plan-approved`) |
|---|---|---|---|
| claude-recovery-control-plane-1 | 🟢 | This artifact landed (workspace fallback). | "Update the autofeed prompt-generator to point Claude lanes at `docs/plans/overnight-results/<run-id>-<lane>.md`. Generate a one-shot migration patch that rewrites future `prompts/claude-*.md` only — do not retro-patch this batch." |
| claude-plan-review-hardening-2 | 🟢 | Sibling artifact present (no batch prefix — see F-NAMING-1). | "Rename `docs/plans/overnight-results/claude-plan-review-hardening-2.md` to `provider-autofeed-20260430-102314-claude-plan-review-hardening-2.md` so the audit trail aligns with the other two Claude lanes in this batch. Do not touch the artifact body." |
| claude-governance-loop-3 | 🟢 | Workspace fallback artifact present, batch-prefixed. | "No action required. Optionally `cp` to run-dir results path if the orchestrator needs the agent-logs surface populated." |
| codex-approved-impl-scout-1 | 🔴 | codex-cli 0.124.0 stdin-hang (#2479). | "Do not retry. Add a Codex absence stub at `<run-dir>/results/codex-approved-impl-scout-1.md` citing `#2479` and `feedback_codex_cli_0_124_upstream_regression.md`. Repeat for lanes 2-12. Do not relabel any GitHub issue." |
| codex-test-readiness-scout-2 | 🔴 | Same upstream blocker. | Same absence-stub pattern. |
| codex-worktree-hygiene-salvage-3 | 🔴 | Same upstream blocker. | Same. |
| codex-arg-{4,5,6} | 🔴 | Wave-2 invocation variant; same upstream blocker. | Same. |
| codex-devnull-{7,8,9} | 🔴 | Wave-3 invocation variant; same upstream blocker. | Same. |
| codex-bg-{10,11,12} | 🔴 | Wave-4 + non-consuming (no prompt file). | "Delete `logs/codex-bg-{approved-10,test-11,hygiene-12}.log` after confirming none contain a partial result, and remove the bg wave from `relaunch_replacements.sh` / `stop_and_relaunch_codex.sh`. Document the upstream-regression cause in the batch's `latest.md`." |
| gemini-research-queue-1 | 🟢 | Result file present in run-dir. | "Read result and integrate into the next research-queue digest. No further action this batch." |
| gemini-gtm-legal-risk-2 | 🟢 | Result file present. | "Read result; no autofeed follow-up." |
| gemini-standards-recon-3 | 🟡 | Log present, result absent (sole Gemini failure). | "From a session with read access to `/mnt/local-analysis/agent-logs/...`, read `logs/gemini-standards-recon-3.log` and classify the failure (429 vs trust-env vs overlay-blindness vs agent-definition warning escalation). Do not relaunch yet — pick the recovery flag based on the cause." |
| gemini-flash-research-4 | 🟢 | Result file present. | "Read result; no autofeed follow-up." |
| gemini-flash-gtm-risk-5 | 🟢 | Result file present. | "Read result; no autofeed follow-up." |

---

## 6. Cross-cutting blockers (carried into the next autofeed pass)

1. **codex-cli 0.124.0 stdin-hang (#2479).** Until downgrade to 0.123.0 (or upstream fix), every Codex lane in every batch will produce a log and no result. **Stop the recovery cascade** and use absence stubs.
2. **Harness sandbox `/mnt/local-analysis/workspace-hub`-only write scope.** Affects every Claude lane in every batch. Fix at the prompt-generator level (F-CLAUDE-1).
3. **Plan-approved boundary (`feedback_never_offer_to_self_label_plan_approved.md`).** No issue in the dangling cohort (#2533/#2564/#2370/#2374/#2375/#2378/#2554/#2556/#2557/#2561/#2562) has a `.planning/plan-approved/<n>.md` marker. The user-in-loop gate is intact across this batch.
4. **Multi-agent commit serialization (`feedback_multi_agent_commit_serialization.md`).** This lane writes only one workspace file and does not commit. The peer Claude lanes do likewise; the orchestrator post-run must serialize the commit pass (or each lane must own its own filename, which they do — only `claude-plan-review-hardening-2.md` deviates per F-NAMING-1).
5. **Wrapper-cache vs. repo-tree (`feedback_plugin_cache_not_repo_tracked.md`).** No relevance to this batch — all wrappers in scope are in either the run-dir (auto-generated) or `docs/plans/overnight-prompts/`, both of which are repo-tracked surfaces.

---

## 7. Authoritative artifact pointers

- Run dir: `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/` (sandbox-readable for `Glob` only; not for `Read`/`Grep`).
- Peer Claude lane (workspace fallback, full plan-review coverage): `/mnt/local-analysis/workspace-hub/docs/plans/overnight-results/claude-plan-review-hardening-2.md` (FINISHED 10:46Z).
- Peer Claude lane (workspace fallback, governance-loop): `/mnt/local-analysis/workspace-hub/docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md`.
- Predecessor batch's Claude review (single-lane, finished cleanly): `/mnt/local-analysis/workspace-hub/docs/plans/overnight-results/provider-autofeed-20260430T094906Z-claude-review-2564.md`.
- Recovery monitor that launched the predecessor batch and recorded the Codex-stdin pattern: `/mnt/local-analysis/workspace-hub/docs/plans/overnight-results/provider-throughput-recovery-20260430T095017Z.md`.
- Canonical Claude lane runner (used by the prior wave; same invocation pattern in this batch): `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/run-claude-prompt.sh`.
- Tmux fan-out launcher (prior wave): `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/launch-local.sh`.
- Memory entries that govern the fixes: `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_codex_sustained_major_loop.md`, `feedback_permission_gate_blocks_cross_review.md`, `feedback_gemini_trust_env_blocks_reviews.md`, `feedback_never_offer_to_self_label_plan_approved.md`, `feedback_multi_agent_commit_serialization.md`.
- Plan-approved markers: `/mnt/local-analysis/workspace-hub/.planning/plan-approved/` (120 files; cohort scan in §1).

---

## 8. Lane attestations

- No GitHub labels added/removed.
- No issue approved (no `status:plan-approved` flip).
- No file under `.planning/plan-approved/` created or modified.
- No git commits made by this lane.
- No worktree created (none required for read-only audit; would be permitted under hard gates if needed).
- No outreach drafted, no destructive ops attempted, no secrets handled.
- This lane only **read** workspace files + `Glob`-listed the run dir + **wrote** this single artifact.
- Result file written to the workspace path; cross-write to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/results/claude-recovery-control-plane-1.md` is **architecturally blocked by harness sandbox** (F-CLAUDE-1). Workspace copy is canonical; orchestrator should mirror manually if the agent-logs path is required.

---

## 9. Top-3 next safe follow-up prompts (for the orchestrator, not this lane)

1. **Fix the Claude-lane sandbox mismatch (root-cause, blocks all future Claude lanes).** "Patch the autofeed prompt-generator so that every `prompts/claude-*.md` file instructs the lane to write its result to `docs/plans/overnight-results/<run-id>-<lane>.md` (workspace path), not to `<run-dir>/results/<lane>.md`. Add a post-run mirroring step (`cp <workspace-artifact> <run-dir>/results/<lane>.md`) if the agent-logs surface needs to stay populated. Do not retro-patch the 102314 batch; only future batches."
2. **Stop the Codex recovery cascade and downgrade.** "Stop spawning Codex `arg`, `devnull`, and `bg` recovery waves. Either (a) `npm install -g @openai/codex@0.123.0` to roll back per `feedback_codex_cli_0_124_upstream_regression.md`, or (b) write Codex absence stubs for lanes 1-9 of the 102314 batch citing #2479 + the memory entry, and route the originally-Codex tasks to Claude or Gemini in the next batch. Delete the `bg-*` wave artifacts (no prompt files; non-consuming) per F-CODEX-2."
3. **Diagnose the lone Gemini failure.** "From a session with read access to `/mnt/local-analysis/agent-logs/`, read `provider-autofeed-20260430-102314/logs/gemini-standards-recon-3.log` end-to-end and classify the failure (429 / trust-env / overlay-blindness / agent-def warning escalation). Do not relaunch until the cause is named, then pick the matching recovery (retry / `GEMINI_CLI_TRUST_WORKSPACE=true` / `git ls-files`-based regen / agent-definition repair)."

— end of lane —
