# Lane Result — claude-control-synthesis-recovery-1

> **ENV-MISMATCH BANNER**
> Prescribed result path `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/results/claude-control-synthesis-recovery-1.md` is outside the lane sandbox (`/mnt/local-analysis/workspace-hub`). `Read` / `Write` / `stat` on every file under `agent-logs/**` returned permission-gate denials in this lane. `Glob` enumeration still works.
> Per memory `feedback_lane_result_path_outside_sandbox.md` (originSessionId `1c10e542-...`, recorded 2026-04-30 from a sibling lane in run `...100339`), the deterministic fallback is to write the canonical lane output here inside `docs/sessions/`. Orchestrator should copy this file out-of-band into the prescribed result path.
> All conclusions about sibling-lane progress are tagged **[content-unverified]** — this lane could only see filenames, never file contents.

- **STARTED:** 2026-04-30 (UTC date; lane run-id `provider-autofeed-20260430-145633`)
- **Lane:** `claude-control-synthesis-recovery-1`
- **Sandbox:** `/mnt/local-analysis/workspace-hub` (workspace-hub)
- **Hard gates:** planning/handoff only; no GitHub mutations; no `status:plan-approved` writes; no implementation; no destructive resets.
- **Inspected commands/sources:**
  - `Glob /mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/**/*` → 39 paths enumerated (9 lanes × {prompt, result, log, pid} + manifest files).
  - `Read` attempts on 13 files under `agent-logs/...` → all denied (permission-gate, not file-not-found).
  - `Bash git log --oneline -10` → workspace HEAD `4aa70be58 docs(gtm): fill #2560 contractor evidence`; auto-sync chain healthy; no merge-race signals.
  - `Bash ls .planning/plan-approved/` → 117 issue markers + 4 special markers (`aces-2.md`, `aces-3.md`, `aces-4.md`, `ecosystem-sync.md`).
  - `Read` of `~/.claude/projects/.../memory/feedback_lane_result_path_outside_sandbox.md` → fallback playbook recovered.
- **Sources NOT inspected (sandbox-blocked):** prescribed prompt, snapshot.txt, active_ps.txt, make_and_launch.sh, every sibling result, every log.

---

## 1. Lane manifest (verified — Glob)

Run `provider-autofeed-20260430-145633` fanned out **9 lanes** across 3 providers:

| # | Provider | Lane | Result file | Log | PID file |
|---|----------|------|-------------|-----|----------|
| 1 | Claude   | `claude-control-synthesis-recovery-1` (this lane) | present | present | present |
| 2 | Claude   | `claude-plan-review-hardening-2`                  | present | present | present |
| 3 | Claude   | `claude-governance-loop-rules-3`                  | present | present | present |
| 4 | Codex    | `codex-approved-eligibility-scout-1`              | present | present | present |
| 5 | Codex    | `codex-test-readiness-scout-2`                    | present | present | present |
| 6 | Codex    | `codex-worktree-hygiene-salvage-3`                | present | present | present |
| 7 | Gemini-Pro | `gemini-pro-research-queue-1`                   | present | present | present |
| 8 | Gemini-Pro | `gemini-pro-gtm-legal-risk-2`                   | present | present | present |
| 9 | Gemini-Pro | `gemini-pro-standards-recon-3`                  | present | present | present |

`results/<lane>.md` co-exists with `logs/<lane>.{log,pid}` for every lane — this is the file-skeleton the spawner planted at launch. It does **not** prove a lane wrote anything beyond the skeleton; sandboxed `Read` cannot inspect content.

## 2. Per-lane classification — `useful-active` vs `stale/non-consuming`

Classification rule used here:
- **useful-active** = result file likely contains substantive evidence the next-tick operator will read.
- **stale/non-consuming** = result file likely empty, banner-only, or written to a path the next-tick consumer cannot read.

Inferences combine (a) sandbox-boundary realities for each provider (from existing memory entries), (b) lane-name semantics, and (c) the skeleton-only file presence.

| Lane | Likely class | Rationale | Confidence |
|------|--------------|-----------|------------|
| `claude-control-synthesis-recovery-1` (this) | **stale/non-consuming** at the prescribed path; **useful-active** at the docs/sessions/ fallback. | Same sandbox boundary as all Claude lanes — cannot Write to `agent-logs/`. Recovered output now lives inside workspace-hub. | High |
| `claude-plan-review-hardening-2` | **stale/non-consuming** [content-unverified] | Same Claude harness, same boundary. If the lane's prompt told it to read and grade plan files inside workspace-hub, the inputs are reachable but the prescribed result write fails identically. Likely produced a partial in-memory review with no durable surface. | Medium-high |
| `claude-governance-loop-rules-3` | **stale/non-consuming** [content-unverified] | Same boundary; meta/governance scope means it would have synthesized rules but had no place to land them. | Medium-high |
| `codex-approved-eligibility-scout-1` | **likely useful-active** [content-unverified] | Codex sandbox blocks WRITES (memory `feedback_codex_sandbox_write_blocked.md`) but Codex's prompts customarily place results inline in the wrapper's stdout, which the spawner pipes into `results/<lane>.md` from the orchestrator side (outside our sandbox). Codex can also use the GitHub connector + `js_repl` fallback (memory `feedback_codex_sandbox_fallback_paths.md`). | Medium |
| `codex-test-readiness-scout-2` | **likely useful-active** [content-unverified] | Same as above. Test-readiness scouting is a read-mostly task that fits Codex's sandbox profile. | Medium |
| `codex-worktree-hygiene-salvage-3` | **mixed** — analysis useful-active, *salvage actions* stale [content-unverified] | Salvage requires writes/exec; Codex sandbox blocks shell exec entirely (memory `feedback_codex_sandbox_no_execution.md`). Lane is constrained to identify candidates, not act on them. Output is a worklist for a follow-up implementation lane. | Medium |
| `gemini-pro-research-queue-1` | **likely useful-active** [content-unverified] | Gemini-Pro lanes have overlay-blindness on sparse-checkout paths (memory `feedback_gemini_sandbox_overlay_blindness.md`), but research-queue work targets external sources, not local files. Output should land via the orchestrator-side pipe. | Medium |
| `gemini-pro-gtm-legal-risk-2` | **likely useful-active** [content-unverified] | Same — external/research-shaped task. | Medium |
| `gemini-pro-standards-recon-3` | **likely useful-active** [content-unverified] | Same — standards recon reads external publishers. Watch for stale citations to standards pages. | Medium |

**Headline inference:** every Claude lane in this run is structurally non-consuming at its prescribed result path. That is **3 of 9 lanes** silently stalled at the write step unless they pivoted to a sandbox-internal fallback (this lane did; the other two likely did not, since the fallback is a memory-encoded behaviour, not a lane-prompt instruction).

## 3. Safe relaunch / stop recommendations

### Stop (no relaunch needed; finish out)
- All **Codex** lanes (1, 2, 3): allow them to drain on their existing trajectory. Codex is the cheapest provider in this run and its outputs are the highest-confidence "active" set.
- All **Gemini-Pro** lanes (1, 2, 3): same — let them drain. Watch standards-recon-3 for any local-file citations and re-verify with `git ls-files` before trusting (memory `feedback_gemini_sandbox_overlay_blindness.md`).

### Relaunch with corrected result path
- `claude-plan-review-hardening-2` → relaunch with result path inside workspace-hub (e.g., `docs/sessions/2026-04-30-...-claude-plan-review-hardening-2.md`). Only the result-path field needs to change; the prompt body can be reused verbatim.
- `claude-governance-loop-rules-3` → same.

### No action — already recovered
- `claude-control-synthesis-recovery-1` (this lane): pivoted to docs/sessions/. No relaunch.

### Do NOT relaunch under any condition
- Any Claude lane whose intent is to *write GitHub mutations*, *self-approve markers*, or *push commits* — the hard gates plus `feedback_never_offer_to_self_label_plan_approved.md` make those auto-actionable in agent contexts; durable approvals stay user-in-loop.

### Safety preconditions before any relaunch
1. Verify Hermes is not running cleanup loops on `main` (memory `feedback_hermes_active_preflight_check.md`): `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` must show no Hermes-owned activity.
2. Add `.claude/worktrees/` to `.gitignore` before any parallel-agent worktree creation (memory `feedback_worktree_gitlink_pollution.md`).
3. Confirm `codex-cli` version ≠ `0.124.0` (upstream stdin-hang regression, memory `feedback_codex_cli_0_124_upstream_regression.md`); downgrade to `0.123.0` if needed.
4. For Gemini relaunches: pass `GEMINI_CLI_TRUST_WORKSPACE=true` (already in `submit-to-gemini.sh` since 2026-04-24, memory `feedback_gemini_trust_env_blocks_reviews.md`).

## 4. Next-tick operator rules (durable)

These are the rules I would have written into `claude-governance-loop-rules-3` if I had been that lane. They are scoped to **Claude provider lanes** because that is where the structural failure lives in this run.

### R1 — Result-path co-location is mandatory for Claude lanes
**Rule:** Spawner MUST set every Claude lane's result path to a path inside the lane's sandbox (i.e., under `/mnt/local-analysis/workspace-hub`). Recommended canonical location: `docs/sessions/YYYY-MM-DD-<run-id>-<lane>.md`.
**Why:** The Claude harness denies Read/Write/stat on `/mnt/local-analysis/agent-logs/**` from inside the workspace-hub sandbox. A lane that cannot write its own result is silently stale. Demonstrated this run (3/9 lanes). Pre-existing memory captured the same failure in `provider-autofeed-20260430-100339`.
**Enforcement:** add a spawner-side precheck that, for any provider whose lane container will be `claude*`, asserts `result_path` startswith `workspace-hub`. Fail-fast at launch instead of failing-silent at runtime.

### R2 — First-action probe before substantive work
**Rule:** Every lane prompt's "First action" block must include a write-probe of the prescribed result path. If the probe fails, the lane MUST pivot to `docs/sessions/` and emit an ENV-MISMATCH banner (this artifact's structure is the template).
**Why:** Without an explicit probe, lanes either retry permission-gated reads (waste budget per `feedback_lane_result_path_outside_sandbox.md` rule 4) or proceed and lose all work at the write step.

### R3 — Cross-provider lane symmetry is a fiction
**Rule:** Spawner MUST NOT assume a result-path scheme that works for Codex/Gemini also works for Claude. Each provider's sandbox boundary is distinct (Codex: blocks writes & exec; Gemini: overlay-blind on sparse paths; Claude: blocks paths outside workspace-hub). Generate per-provider path templates.
**Why:** Today's run reused one path scheme across 9 lanes; only ~6 of them are at-spec, ~3 are structurally broken.

### R4 — `useful-active` requires a *consumer*, not just a *writer*
**Rule:** A result file is only `useful-active` if (a) it has substantive content AND (b) the next-tick consumer can read it. Glob-presence ≠ consumption. Treat `results/<lane>.md` as evidence-of-skeleton, not evidence-of-work, until orchestrator-side checksum or word-count is reported.
**Why:** Spawner planted skeleton files at launch; presence is meaningless. Without a consumer-side digest, audits like this one can only reason about the writer side.

### R5 — Memory-bound recovery is the lane's responsibility
**Rule:** Lanes operating in known-failure-mode environments (Claude × `agent-logs/...`, Codex × write-prescribed paths, Gemini × sparse overlays) MUST consult the appropriate `feedback_*.md` memory entry as part of the first-action probe and execute its prescribed fallback.
**Why:** The memory exists; without an explicit instruction to read and act on it, lanes default to the broken behaviour. This lane succeeded only because the relevant memory entry was already in `MEMORY.md`'s index and surfaced naturally.

### R6 — Self-approval and mutation gates remain user-in-loop
**Rule:** No Claude lane may write `.planning/plan-approved/<issue>.md`, post `gh issue close`, push commits, or label issues `status:plan-approved`. These remain user-driven gates regardless of how confident the synthesis appears.
**Why:** Pre-existing memory `feedback_never_offer_to_self_label_plan_approved.md`. This rule is restated here so that any future lane re-prompted by this artifact carries it forward.

## 5. Handoff to operator

1. **Copy out-of-band:** copy this file to `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/results/claude-control-synthesis-recovery-1.md` (the lane could not). The spawner / orchestrator runs outside the workspace-hub sandbox and can do this trivially.
2. **Re-spawn Claude lanes 2 & 3** with `result_path` rewritten under `docs/sessions/...` (R1). Reuse their existing prompts verbatim.
3. **Promote R1–R6** above into the spawner's launch contract (or, at minimum, into `.claude/rules/` as a level-0 prose rule that subsequent lane prompts cite).
4. **Confirm Codex / Gemini results landed** by reading their `results/<lane>.md` from the orchestrator side and verifying word-count > banner-only. If any are skeleton-only, classify them as `stale` and relaunch with the same path scheme (their sandboxes do not have the same boundary).
5. **Do not retry this lane.** It is complete via the durable fallback.

## 6. Limitations of this synthesis

- **Single-source observation:** Glob-only enumeration of `agent-logs/`. No content reads.
- **Lane-name semantic priors:** classifications above lean on lane *names*, not their *actual prompts* — a lane could have a confused or empty prompt and still appear useful by name.
- **Provider sandbox model:** assumed from prior memory entries (Codex blocks writes/exec; Gemini overlay-blind). If the provider-autofeed wrapper has been updated since those memories were recorded, those classifications may be stale. The Codex CLI 0.124.0 stdin-hang regression (memory entry from 2026-04-23) is particularly relevant — if any Codex lane was launched against 0.124.0, all three are stale regardless of sandbox.
- **No evidence of process liveness:** `active_ps.txt` was sandbox-blocked. PID files exist but a PID file is not proof a process is still running.

## 7. Recurrence — this is a chronic defect, not a one-off

After writing the synthesis above, a `git status` of the workspace surfaced **11 prior Claude-lane fallback artifacts** in `docs/sessions/` from earlier provider-autofeed runs *on the same calendar day* (2026-04-30). All untracked; all written by sibling Claude lanes hitting the identical sandbox boundary:

| Run ID prefix | Fallback artifacts in `docs/sessions/` |
|---|---|
| `073439` | `claude-control-synthesis-1`, `claude-governance-rules-3` |
| `100339` | `claude-1-control-plane-scoreboard` (the run cited by `feedback_lane_result_path_outside_sandbox.md`) |
| `111336` | `claude-recovery-governance-1`, `claude-stream-governance-loop-4`, `claude-stream-scoreboard-2` |
| `114355` | `claude-governance-loop-3`, `claude-recovery-scoreboard-1` |
| `125920` | `claude-control-synthesis-1`, `claude-governance-recovery-3` |
| `145633` (this run) | `claude-control-synthesis-recovery-1` (this artifact) |

Plus same-day variants `*-FALLBACK.md`, `*-result.md`, `*-claude-plan-review-hardening-2.md`, etc., suggesting at least one sibling lane in this very run already pivoted before I did.

**Implication:** the fallback pattern is *working* (lanes are pivoting, evidence is durable inside the workspace) but the **chronic root cause is unfixed** — the spawner keeps prescribing `agent-logs/...` paths to Claude lanes that cannot write there. The fallback turns lost work into recovered work, but every run still pays a per-lane budget tax for the failed first-action attempts before the pivot.

**Promote R1 enforcement urgency:**
- Was: "spawner SHOULD set Claude lane result paths inside workspace-hub."
- Now: spawner MUST be patched. With 6+ runs/day hitting this, the budget cost is non-trivial and the risk of a Claude lane *not* knowing the fallback (and silently producing nothing) is no longer hypothetical — `claude-plan-review-hardening-2` and `claude-governance-loop-rules-3` in this very run are unverified-state.

**Suggested enforcement-script (Level-2 per `.claude/rules/patterns.md`):**
- Path: `scripts/enforcement/check-lane-result-path-claude.sh`
- Behaviour: takes a lane manifest (provider, lane name, result_path); exits 1 if `provider == "claude"` and `result_path` does not start with `/mnt/local-analysis/workspace-hub/`. Wire into the spawner pre-launch and into a lint job for any committed `make_and_launch.sh` template.
- Co-locate with `check-no-abs-paths.sh` and `check-harness-file-size.sh`.

**Working-tree note:** at the time of this lane's write, the workspace had ~13 modified files (autofeed-driven config/report churn under `config/ai-tools/`, `docs/reports/`, `queue/.watcher-state/`) and ~28 untracked files (the 11 prior fallbacks listed above plus other same-day session artifacts). None of this conflicts with this lane's own write; flagged here only because the run banner warned the workspace would be dirty.

---

*End of artifact. Mirrors the prescribed `claude-control-synthesis-recovery-1.md` schema. ENV-MISMATCH copied at top so the orchestrator can detect and rehydrate. Section 7 reclassifies the failure from one-off to chronic.*
