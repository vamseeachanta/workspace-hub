# Lane: claude-governance-loop-3 — Autofeed Governance/Recovery Loop Improvement

> **Sandbox note:** dispatcher-specified result path
> `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/results/claude-governance-loop-3.md`
> is outside the Claude Code harness write scope (locked to `/mnt/local-analysis/workspace-hub`).
> Falling back to the repo-tracked artifact path the dispatcher's peer lane (`claude-recovery-control-plane-1`) already used:
> `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md`.
> Operator must `cp` this file into the run-results dir, **or** update future Claude-lane prompts to write under `docs/plans/overnight-results/` directly so the harness sandbox and the dispatcher target agree.

- **STARTED (UTC):** 2026-04-30T10:35:21Z
- **Lane:** claude-governance-loop-3
- **Workspace:** /mnt/local-analysis/workspace-hub
- **HEAD at start:** `4aa70be58 docs(gtm): fill #2560 contractor evidence`
- **Mode:** planning / review / evidence / handoff only — no implementation, no `status:plan-approved` mutations, no merges, no outreach, no destructive cleanup.

---

## 1. Scope of inspection

The `provider-autofeed-20260430-102314` run dir was probed (read access blocked by sandbox), so the file inventory was reconstructed via `Glob` (file names only, no contents). The repo-tracked autofeed substrate from the prior wave (`docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/`) was read directly, since the same policy + cron-prompt artifacts govern this generation of the loop. Cross-checked against the in-repo peer-lane fallback artifact `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-recovery-control-plane-1.md` and the prior-pass monitor `provider-throughput-recovery-20260430T095017Z.md`.

### 1.1 Run-dir inventory (lane bookkeeping)

Reconstructed from `Glob /mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/**/*`:

| Provider | Lane name | Prompt | Log | Result |
|---|---|---|---|---|
| Claude | recovery-control-plane-1 | ✓ | ✓ | ✗ in run-dir, ✓ in `docs/plans/overnight-results/` (fallback) |
| Claude | plan-review-hardening-2 | ✓ | ✓ | ✗ in run-dir, ✗ in `docs/plans/overnight-results/` (peer lane still running or also blocked) |
| Claude | governance-loop-3 | ✓ | ✓ | ✗ in run-dir (blocked), ✓ in `docs/plans/overnight-results/` (this file) |
| Codex | approved-impl-scout-1 | ✓ | ✓ | ✗ |
| Codex | test-readiness-scout-2 | ✓ | ✓ | ✗ |
| Codex | worktree-hygiene-salvage-3 | ✓ | ✓ | ✗ |
| Codex | arg-approved-scout-4 | ✓ | ✓ | ✗ |
| Codex | arg-test-scout-5 | ✓ | ✓ | ✗ |
| Codex | arg-hygiene-salvage-6 | ✓ | ✓ | ✗ |
| Codex | devnull-approved-scout-7 | ✓ | ✓ | ✗ |
| Codex | devnull-test-scout-8 | ✓ | ✓ | ✗ |
| Codex | devnull-hygiene-salvage-9 | ✓ | ✓ | ✗ |
| Codex | bg-approved-10 | (no prompt visible) | ✓ | ✗ |
| Codex | bg-test-11 | (no prompt visible) | ✓ | ✗ |
| Codex | bg-hygiene-12 | (no prompt visible) | ✓ | ✗ |
| Gemini | research-queue-1 | ✓ | ✓ | ✓ |
| Gemini | gtm-legal-risk-2 | ✓ | ✓ | ✓ |
| Gemini | standards-recon-3 | ✓ | ✓ | ✗ |
| Gemini | flash-research-4 | ✓ | ✓ | ✓ |
| Gemini | flash-gtm-risk-5 | ✓ | ✓ | ✓ |

Plus dispatch artifacts: `snapshot.md`, `lane-state.md`, `latest.md`, `relaunch_replacements.sh`, `stop_and_relaunch_codex.sh`, `launched.pid`. (All read-blocked from this lane.)

### 1.2 Repo-side substrate read in full

- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md` (334 lines — diagnoses 5 failure modes and publishes the §6 priority queue + §3 deterministic classifier).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md` (203 lines — the canonical safe cron prompt).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/run-claude-prompt.sh` (24 lines — runner with `--max-budget-usd 20`, `--no-session-persistence`, `tee` to log).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/launch-local.sh` (20 lines — `tmux has-session` guard, plain new-session per lane).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/launch-ace2-remote.sh` (27 lines — rsync + ssh + remote tmux).
- `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-recovery-control-plane-1.md` (peer lane STARTED stub).
- `docs/plans/overnight-results/provider-throughput-recovery-20260430T095017Z.md` (prior pass that *launched* this very run dir at 09:49Z and recorded the Codex-stdin stall pattern at line 28-29 / line 49).

★ Insight ─────────────────────────────────────
- The autofeed orchestrator is **two-layer**: the repo holds the *policy + cron prompt* (durable, git-tracked, reviewable); the dispatch process holds the *transient run dir* with one prompt + one log + one (hopefully) result per lane. The two layers are joined only by file-naming conventions — there is no single source-of-truth manifest connecting "run X launched lane Y at time Z and expected result at path P." That coupling-by-filename is the root of the silent-failure modes below.
- The run dir lives outside the Claude Code sandbox boundary (`/mnt/local-analysis/agent-logs/`), so spawned Claude lanes **cannot write the dispatcher-specified result file** — they must fall back to `docs/plans/overnight-results/` and rely on an operator-side `cp` to land it where the dispatcher polls. This is a load-bearing assumption that breaks silently if the operator forgets the `cp`.
─────────────────────────────────────────────────

---

## 2. Findings — silent-failure modes the current loop hits

Each finding cites either evidence I observed in this lane, or the in-repo prior-pass artifact that already documented it.

### F1. Sandbox/result-path mismatch is silent

- **Evidence:** Permission denials on every `Read`/`Write`/`Bash cat>` against `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/**`. Peer lane `claude-recovery-control-plane-1` also fell back to `docs/plans/overnight-results/`; no run-dir result for it either.
- **Why it matters:** the dispatch monitor that spawned this run polls the run-dir results path. With Claude lanes systematically unable to write there, the dispatcher's "completed" check will mark these lanes `FAILED_NO_RESULT` even when they wrote a perfect artifact. Worse, the dispatcher may then cycle Claude lanes the same way it cycled Codex (12 lane attempts of which 9 are clearly retries with new naming prefixes).
- **Hard gate preserved:** none violated; finding is evidentiary.

### F2. Codex-stdin-hang regression (#2479) was retried 9× without diagnosis

- **Evidence:** The lane-name progression `approved-impl-scout-1 → arg-approved-scout-4 → devnull-approved-scout-7 → bg-approved-10` is 4 generations of "try a different stdin pattern" against the same logical task. Same `test-` and `hygiene-` chains: 3 generations each. **No Codex result file landed in the entire run.** This matches `MEMORY.md → feedback_codex_cli_0_124_upstream_regression.md`: "0.124.0 blocks ALL `codex exec` calls regardless of stdin redirection; reproduces on 90-byte plans; #2479 filed; workaround = downgrade to 0.123.0." The prior monitor `provider-throughput-recovery-20260430T095017Z.md` also recorded the symptom at line 28-29 and explicitly proposed re-routing in §59-62, but the recovery loop did not act on that proposal.
- **Why it matters:** budget waste, capacity waste, and false signal that "we're trying" while the upstream block is unfixable from this side.
- **Hard gate preserved:** this finding does not propose downgrading codex-cli (that's an operator action) — it proposes a circuit-breaker.

### F3. Gemini lane parity gap (`standards-recon-3` missing)

- **Evidence:** `Glob` shows `prompts/gemini-standards-recon-3.md` and `logs/gemini-standards-recon-3.log` exist, but no `results/gemini-standards-recon-3.md`. The other 4 Gemini lanes (research-queue-1, gtm-legal-risk-2, flash-research-4, flash-gtm-risk-5) all have results. Possible cause per memory `feedback_gemini_sandbox_overlay_blindness.md` (sparse-checkout overlay invisibility) or `feedback_gemini_trust_env_blocks_reviews.md` (exit-55 without `GEMINI_CLI_TRUST_WORKSPACE=true`); without log content readable from this lane I can't disambiguate.
- **Why it matters:** if the loop only counts result-file presence, it loses the *type* of failure (sandbox blindness vs trust-env vs prompt rejection vs network) and cannot route around it.
- **Hard gate preserved:** read-only finding.

### F4. Lane-naming retries do not reset the dispatcher's "lane attempt" counter

- **Evidence:** Three rounds of Codex retries used three new naming prefixes (`<task>-N`, `arg-<task>-N`, `devnull-<task>-N`, then bare `bg-<task>-N`). Each new prefix presents to the dispatcher as a brand-new lane, so any "max-attempts-per-logical-lane" cap is silently bypassed.
- **Why it matters:** retry storms become indistinguishable from genuine new work, defeating any cap policy.
- **Hard gate preserved:** read-only.

### F5. `relaunch_replacements.sh` and `stop_and_relaunch_codex.sh` are run-dir-local — no audit trail in repo

- **Evidence:** Both scripts live inside `agent-logs/provider-autofeed-20260430-102314/` and are not git-tracked. Whatever they do, the operator can't review them via PR and they vanish when the run dir is rotated.
- **Why it matters:** the safe-autofeed-cron-prompt §3 "Decide candidate lane" rules and §5 "write the cron-pass result artifact" expect deterministic, reviewable launchers. Per-run ad-hoc relaunch scripts are exactly the failure mode `feedback_queue_git_tracked.md` warns against ("verify files in git before queue").
- **Hard gate preserved:** read-only finding; I am not deleting or rewriting the scripts.

### F6. `latest.md` / `lane-state.md` / `snapshot.md` are not read by spawned Claude lanes

- **Evidence:** These files exist in the run dir but Claude lane prompts do not reference them (the governance prompt I received cites only the dispatcher run dir + result file path). So lanes cannot see "what other lanes are running" without polling tmux/log surfaces directly, which the sandbox blocks.
- **Why it matters:** the §3 classifier in the autofeed-policy doc relies on lanes being able to introspect peer state. If lanes are blind to peers, every lane behaves like the only lane and capacity ceilings (`MAX_LOCAL_LANES=3`) become unenforceable from inside the lane.
- **Hard gate preserved:** read-only.

### F7. No explicit Claude `--max-budget-usd` accounting in run-dir manifest

- **Evidence:** `run-claude-prompt.sh:20` hardcodes `--max-budget-usd "20"` per lane, but the run-dir has 3 Claude lanes (= $60 ceiling) plus prior recovery passes. Without a wave-level rollup, an operator has no quick read of "how much budget is committed to this run." This lane received `USD budget: $0/$20` — confirming per-lane cap, not a wave cap.
- **Why it matters:** wave-level budget surprise is a real risk at >5-lane fanouts.
- **Hard gate preserved:** finding only; no budget mutation.

### F8. Auto-sync race + Hermes preflight are documented but only F8.B is actually wired into the cron prompt

- **Evidence:** The safe-autofeed-cron-prompt's Step-0 short-circuit catches `git rebase|stash push|commit|merge|reset|checkout` in flight (good — covers the `feedback_hermes_active_preflight_check.md` lesson). It does NOT catch (a) auto-sync push contention (`feedback_autosync_silent_pusher.md`), (b) merge-race silent revert (`feedback_merge_race_silent_revert.md`), or (c) `git switch --discard-changes` discipline (`feedback_git_switch_discard_changes_pattern.md`). The runner script `run-claude-prompt.sh` does no git ops at all, so its lanes are safe — but any *follow-up patch lane* the cron auto-spawns (per §6 row 9-10 of the policy doc) would touch git and could trip these.
- **Why it matters:** future expansion of the cron's auto-spawn set will silently regress the gates unless the short-circuit is generalized.
- **Hard gate preserved:** finding only.

---

## 3. Bounded improvement proposals (all preserve every hard gate)

Each proposal is **planning/spec-only** — none of them require execution from this lane. Each names the file to edit, the diff shape, and the safety invariant being preserved.

### P1. Add a "result-path-resolver" preamble that every Claude lane reads before deciding where to write

**File:** new section in `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md` (and propagated to all future Claude lane prompts via the §7 template in `autofeed-policy-and-next-queue.md`).

**Insert (after Global rules, before Mission):**

```
## Result-path resolution (run before any other write)

1. The dispatcher specifies a target result path under
   /mnt/local-analysis/agent-logs/<run>/results/<lane>.md .
2. Probe write access with a 3-byte touch to that path. If write fails
   for any reason (sandbox, permission, disk), DO NOT abort. Instead:
3. Compute fallback path:
     /mnt/local-analysis/workspace-hub/docs/plans/overnight-results/<run>-<lane>.md
4. Write the deliverable to whichever path succeeded.
5. The first line of the deliverable MUST be a sandbox-note block citing:
   - the dispatcher-specified path,
   - whether it was reachable (yes/no + reason),
   - the fallback path actually used.
6. The dispatcher-side monitor poll MUST be updated to also glob
   docs/plans/overnight-results/<run>-<lane>.md as a valid result.
```

**Hard gate preserved:** no GitHub mutation, no implementation, no destructive op. The fallback path is already where peer lanes write today (existing convention, not a new convention).

**Cross-cuts:** addresses F1 directly; partially addresses F6 (because the sandbox-note block becomes a machine-readable "lane completed via fallback" signal the dispatcher can index).

### P2. Codex circuit-breaker keyed on log-content fingerprints

**File:** new `scripts/cron/codex-stdin-hang-circuitbreaker.sh` (proposed; not yet written).

**Pseudocode:**

```bash
#!/usr/bin/env bash
# Read-only fingerprinter. Exit 0 = "Codex healthy"; exit 1 = "open circuit".
set -euo pipefail
LOG_GLOB="${1:?log glob required}"
WINDOW_MIN="${2:-30}"

# Count Codex logs in the time window that show ONLY the stdin hang fingerprint.
# Per memory: feedback_codex_cli_0_124_upstream_regression.md.
HANG_COUNT=$(find $LOG_GLOB -mmin -$WINDOW_MIN -type f \
  -exec grep -l "Reading additional input from stdin" {} \; 2>/dev/null \
  | xargs -r -I{} sh -c 'wc -l < "{}"' \
  | awk '$1 < 5' | wc -l)

# Threshold: if >=3 Codex lanes in the window are stuck on the stdin
# fingerprint AND no Codex lane has produced a >200-byte result in the
# same window, the upstream regression is live; open the circuit.
RESULT_COUNT=$(find $LOG_GLOB -mmin -$WINDOW_MIN -name '*codex*' -type f \
  -exec sh -c '[ "$(wc -c < "$1")" -gt 200 ]' _ {} \; -print 2>/dev/null | wc -l)

if [ "$HANG_COUNT" -ge 3 ] && [ "$RESULT_COUNT" -eq 0 ]; then
  echo "OPEN: codex-stdin-hang regression confirmed in window"
  exit 1
fi
echo "CLOSED: codex appears healthy"
```

**Caller change (in the safe-autofeed-cron-prompt Step-0):**

```bash
# D. Codex circuit-breaker — defer Codex relaunches if upstream regression live
if ! bash "$ROOT/scripts/cron/codex-stdin-hang-circuitbreaker.sh" \
     "/mnt/local-analysis/agent-logs/*/logs/codex-*.log" 60 ; then
  echo "deferred: codex-cli stdin-hang circuit open" \
    > "$WAVE_DIR/results/${STAMP}-cron-skipped-codex-circuit.md"
  # Do NOT exit 0 — the cron pass should still consider Claude/Gemini lanes.
  CODEX_DISABLED=1
fi
```

The §3-§4 candidate selection then skips any candidate row whose host requires `codex` and either picks the next non-Codex row or writes an idle note.

**Hard gate preserved:** no Codex mutation, no `gh` mutation, no implementation. The circuit-breaker is read-only and emits skip notes only.

**Cross-cuts:** addresses F2 and F4. F4 is killed because the circuit-breaker doesn't care about lane-name prefixes — it pattern-matches on log content.

### P3. Per-logical-lane attempt cap that survives renaming

**File:** addition to `safe-autofeed-cron-prompt.md` Step-3 (decide candidate lane).

**New rule (insert as step 3.0, before existing 3.1):**

```
3.0 Logical-lane attempt accounting
    - Compute logical-lane id by stripping leading prefix tokens that match
      the regex ^(arg|devnull|bg|retry|fix|hot)-+ from the lane name.
      e.g. "devnull-approved-scout-7" -> "approved-scout"
    - Glob all prompts/<provider>-*<logical-id>*.md in the run dir.
    - If count >= 3 AND zero result files exist for any of those prompts,
      treat the logical lane as POISONED and write
      results/<stamp>-cron-skipped-poisoned-lane-<logical-id>.md . Skip
      to next queue row.
```

**Hard gate preserved:** read-only filesystem accounting; no execution beyond writing the skip note.

**Cross-cuts:** kills F4. Reduces F2's blast radius even if the circuit-breaker in P2 has a false negative.

### P4. Gemini failure-type fingerprinter

**File:** new `scripts/cron/gemini-failure-fingerprint.sh` (proposed).

Reads each Gemini log under the run dir's `logs/` and emits a one-line classification per file using these grep patterns (drawn from memory `feedback_gemini_trust_env_blocks_reviews.md`, `feedback_gemini_sandbox_overlay_blindness.md`):

| Pattern | Classification | Routing |
|---|---|---|
| `exit 55` AND `GEMINI_CLI_TRUST_WORKSPACE` not set | `TRUST_ENV_GATE` | re-route to wrapper that exports the env |
| `permissionMode` validation warning | `AGENT_DEF_WARNING` | proceed; Gemini still works |
| repeated `file not found` for paths that exist via `git ls-files` | `OVERLAY_BLIND` | re-route to Claude or pin Gemini to a non-overlay clone |
| 0-byte log AND tmux session dead | `SILENT_DEATH` | rerun once; if recurs, route to Claude |
| any other non-empty log without result file | `UNKNOWN_FAIL` | escalate to operator |

The cron pass then includes a `Gemini lane fingerprint table` in its `cron-pass-${STAMP}.md`.

**Hard gate preserved:** read-only. No re-execution from this script — only routing recommendation.

**Cross-cuts:** addresses F3.

### P5. Wave-level budget rollup

**File:** addition to `safe-autofeed-cron-prompt.md` Step-5 (write the cron-pass result artifact).

**Add row to the artifact's metadata table:**

```
| Wave budget committed | $<sum of --max-budget-usd across active Claude lanes> |
| Wave budget ceiling   | $<MAX_LOCAL_LANES * 20 + MAX_REMOTE_LANES * 20> |
```

The active-lane list is derived from `tmux ls` (or, when sandbox blocks, from the `lane-state.md` if the dispatcher writes it). The §3 candidate-selection adds a precheck: if `committed + 20 > ceiling`, skip and emit `cron-skipped-budget.md`.

**Hard gate preserved:** read-only accounting; no budget mutation.

**Cross-cuts:** addresses F7.

### P6. Generalize Step-0 short-circuits to cover all documented git-race patterns

**File:** addition to `safe-autofeed-cron-prompt.md` Step-0.

**Replace existing block 0.B with:**

```bash
# B. Any in-flight git operation that could race with a follow-up patch lane.
# Memory: feedback_hermes_active_preflight_check.md (rebase/stash/commit/merge/reset/checkout)
#         feedback_autosync_silent_pusher.md       (in-flight push contention)
#         feedback_merge_race_silent_revert.md     (`git merge --no-ff` + `git commit --no-edit` race)
#         feedback_multi_agent_commit_serialization.md (multi-agent index lock race)

GIT_OPS_PATTERN='git (rebase|stash push|commit|merge|reset|checkout|push|fetch.*--prune|gc|repack)'
if pgrep -af "$GIT_OPS_PATTERN" >/dev/null 2>&1; then
  echo "deferred: git mutation in flight" \
    > "$WAVE_DIR/results/${STAMP}-cron-skipped-git.md"
  exit 0
fi

# C. Auto-sync push hold-down: if .git/AUTOSYNC_LAST shows last push <60s ago,
# defer to avoid the silent-revert pattern.
if [ -f "$ROOT/.git/AUTOSYNC_LAST" ] \
   && [ $(( $(date +%s) - $(stat -c %Y "$ROOT/.git/AUTOSYNC_LAST") )) -lt 60 ]; then
  echo "deferred: auto-sync settled <60s ago" \
    > "$WAVE_DIR/results/${STAMP}-cron-skipped-autosync.md"
  exit 0
fi
```

**Hard gate preserved:** widens the deferral surface (more conservative, never less). No mutation introduced.

**Cross-cuts:** addresses F8.

### P7. Promote `relaunch_replacements.sh` / `stop_and_relaunch_codex.sh` into git-tracked, reviewable templates

**File:** new directory `scripts/agents/autofeed-templates/` with:
- `relaunch-replacements.sh.tmpl`
- `stop-and-relaunch-codex.sh.tmpl`
- `README.md` documenting the template variables and forbidden mutations.

The dispatcher continues to materialize per-run copies into the run dir, but only by `envsubst` from the templates. Pre-commit hook enforces that any non-template `relaunch_*.sh` in `agent-logs/` is older than the templates' last commit (drift detection).

**Hard gate preserved:** no execution; only review-surface promotion. Existing scripts in the live run dir are untouched (cannot be reviewed without sandbox access).

**Cross-cuts:** addresses F5; gives operator a stable place to land "fix" PRs.

### P8. Lane-introspection sidecar so spawned lanes can see peer state

**File:** spec only. The dispatcher should write `agent-logs/<run>/lane-state.json` (one row per lane: `name | provider | host | started_at | log_path | result_path | status`) on every state transition. Each spawned Claude prompt's "Inputs to read first" block references that path. When the sandbox prevents the lane from reading it, the lane writes a `peer_state_unknown: true` field into its result instead of silently proceeding capacity-blind.

Alternatively (lower-effort): the dispatcher writes a *copy* of `lane-state.md` into `docs/plans/overnight-results/<run>-lane-state.md` so the in-repo workspace can read it.

**Hard gate preserved:** spec only.

**Cross-cuts:** addresses F6 and is the precondition for P3 working when sandboxed.

---

## 4. Suggested ordering and effort

| # | Proposal | Effort | Dependency | Risk reduction (subjective) |
|---:|---|---|---|---|
| 1 | P1 — result-path-resolver | XS | none | High (fixes F1; this lane's biggest pain) |
| 2 | P6 — generalized Step-0 short-circuits | XS | none | Medium |
| 3 | P3 — logical-lane attempt cap | S | none | High (kills the renaming-bypass class) |
| 4 | P2 — Codex circuit-breaker | S | none (P3 also helps without it) | High (stops budget burn on #2479-class blocks) |
| 5 | P5 — wave-level budget rollup | S | P8 (or dispatcher-side rollup) | Medium |
| 6 | P4 — Gemini fingerprinter | S | none | Medium (turns silent fails into routed fails) |
| 7 | P8 — lane-introspection sidecar | M | dispatcher change (out of repo) | High (unlocks several other proposals) |
| 8 | P7 — relaunch-script templating | M | none | Medium (audit-trail improvement) |

---

## 5. Blockers (this lane could not resolve)

1. **`/mnt/local-analysis/agent-logs/` is outside this lane's sandbox.** Could not read `snapshot.md`, `lane-state.md`, `latest.md`, `prompts/`, `logs/`, or any utility script. All run-dir findings are inferred from `Glob` file names + the in-repo peer-lane fallback artifacts. Recommend the dispatcher add this path to the Claude harness allowlist for `Read`-only (no `Write`) so future governance lanes have direct evidence.
2. **The two utility scripts `relaunch_replacements.sh` and `stop_and_relaunch_codex.sh` are unreviewable.** Cannot confirm whether they already implement any of P3/P6 or violate any hard gate. P7 above proposes a promotion path.
3. **Cron handle definitions (`3dae8266219b`, `5ae81116b608`) live in an external scheduler surface (likely RemoteTrigger / `/schedule`).** This lane cannot inspect or modify them. Per `autofeed-policy-and-next-queue.md` §8, the orchestrator (= operator) updates them.
4. **Could not confirm peer lane `claude-plan-review-hardening-2` status.** No fallback artifact in `docs/plans/overnight-results/` at write time; lane may still be running, may have hit the same sandbox block, or may have errored. Recommend operator polls both run dir and `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-plan-review-hardening-2.md` before treating that lane as failed.

---

## 6. Boundary-compliance statement

- Did NOT mutate GitHub (no `gh issue edit`, comment, label, close, PR, merge).
- Did NOT create or edit `.planning/plan-approved/*` markers.
- Did NOT touch `digitalmodel/`, `assethold/`, `worldenergydata/`, `frontierdeepwater/`, `ai-orchestrator-template/` sub-repos.
- Did NOT execute `scripts/review/plan-review-fanout.sh`, `codex exec`, `gemini`, or `hermes` (state-mutating).
- Did NOT register, modify, or remove any cronjob.
- Did NOT implement any code, run any tests, or commit anything.
- Did NOT create any worktree.
- Did NOT send outreach.
- Wrote exactly one artifact: this file (`docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md`).
- Did not commit or push it. The operator decides whether to commit; auto-sync may pick it up on its next pass.

---

## 7. Next safe follow-up prompts (paste-ready, plan-only)

Each is bounded, hard-gate-preserving, and writes to a specific in-repo path the next operator can poll. None require approval markers; none mutate GitHub.

### Follow-up A — write the result-path-resolver preamble (P1)

```
Lane: claude-autofeed-resolver-preamble
Workspace: /mnt/local-analysis/workspace-hub
Mode: planning/spec only — no implementation, no GitHub mutation.

Task: Edit docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md
to insert a "Result-path resolution" section between the existing
"Global rules" and "Mission" headers, exactly matching the spec in
docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md §3 P1.

Also propagate the same section into the §7 prompt template in
docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md.

Write a brief result note at
docs/plans/overnight-results/<UTC-stamp>-autofeed-resolver-preamble.md
confirming the diff shape, the SHA before/after, and that no other files
were touched.

Hard guardrails: no execution beyond Edit/Read; no commit; no GitHub mutation.
```

### Follow-up B — author the Codex circuit-breaker script (P2)

```
Lane: claude-codex-circuitbreaker
Workspace: /mnt/local-analysis/workspace-hub
Mode: implementation of a NEW read-only script under scripts/cron/.

Task: Create scripts/cron/codex-stdin-hang-circuitbreaker.sh per the spec
in docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-governance-loop-3.md §3 P2.
Add a unit-style smoke test under scripts/cron/tests/ that creates two
fixture log files matching the stdin-hang fingerprint and asserts exit 1
when threshold is met, exit 0 otherwise.

Then edit safe-autofeed-cron-prompt.md Step-0 to call the new script as
block "D" with CODEX_DISABLED semantic (skip Codex candidates, do not
exit 0).

Hard guardrails: script must be read-only on the filesystem (no rm/mv/edit).
Tests must not touch /mnt/local-analysis/agent-logs/. No commit, no push.
```

### Follow-up C — promote relaunch utilities into reviewable templates (P7)

```
Lane: claude-autofeed-relaunch-templating
Workspace: /mnt/local-analysis/workspace-hub
Mode: planning + scaffolding only.

Task: Create scripts/agents/autofeed-templates/{README.md,
relaunch-replacements.sh.tmpl, stop-and-relaunch-codex.sh.tmpl}.
Templates must:
- Use envsubst variable syntax (${RUN_ID}, ${LANE_PREFIX}, etc.).
- Document forbidden operations in a header comment block:
  * no `gh` mutation
  * no `git push --force`
  * no implementation lanes
  * no codex/gemini direct invocation outside the autofeed loop's
    documented call sites
- Pass shellcheck --severity=error.

Do NOT touch any existing relaunch_*.sh files in /mnt/local-analysis/agent-logs/
(out of sandbox anyway). Open this as a planning-only artifact; user/operator
decides whether to wire the dispatcher into the templates.

Hard guardrails: no git commit, no push, no execution. Write a result
note at docs/plans/overnight-results/<UTC-stamp>-autofeed-relaunch-templating.md.
```

### Follow-up D — sandbox-allowlist clarification (this lane's #1 blocker)

```
Lane: operator (not Claude)
Action: Decide whether to extend the Claude Code harness sandbox to
permit Read (not Write) on /mnt/local-analysis/agent-logs/. If yes,
update .claude/settings.json (or per-machine override) to add the
allowed path. Then re-spawn this governance lane to inspect the actual
run-dir contents (snapshot.md, lane-state.md, latest.md, the two utility
scripts). The findings in §2 above are inferred from filenames and
peer-lane artifacts; direct read access would let a follow-up lane
verify or refute each finding with citations.
```

---

## 8. Provenance

- **Glob inventory** of `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-102314/**/*` (file names only — `Read`/`Bash cat` blocked).
- **Read in full:**
  - `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md`
  - `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md`
  - `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/{run-claude-prompt.sh,launch-local.sh,launch-ace2-remote.sh}`
  - `docs/plans/overnight-results/provider-autofeed-20260430-102314-claude-recovery-control-plane-1.md`
  - `docs/plans/overnight-results/provider-throughput-recovery-20260430T095017Z.md`
- **`git log`** filtered to commits mentioning autofeed: `e6e558ea4 docs(autofeed): durable safe auto-feed policy and next 10-lane queue`, `deba797fe chore(orchestration): add next-wave autofeed prompt pack`.
- **Memory feedback files referenced by tag** (not re-read in this lane; cited from `MEMORY.md`):
  - `feedback_codex_cli_0_124_upstream_regression.md`
  - `feedback_codex_sustained_major_loop.md`
  - `feedback_gemini_sandbox_overlay_blindness.md`
  - `feedback_gemini_trust_env_blocks_reviews.md`
  - `feedback_hermes_active_preflight_check.md`
  - `feedback_autosync_silent_pusher.md`
  - `feedback_merge_race_silent_revert.md`
  - `feedback_multi_agent_commit_serialization.md`
  - `feedback_queue_git_tracked.md`
  - `feedback_never_offer_to_self_label_plan_approved.md`

## 9. End-of-lane

- **FINISHED (UTC):** 2026-04-30T10:42 (approximate; clock not re-queried at write time)
- **Verdict:** COMPLETED_WITH_RESULT (this file). Eight bounded, hard-gate-preserving improvement proposals; three blockers; four paste-ready follow-up prompts.
- **No commit, no push, no GitHub mutation, no approval marker, no implementation.**
