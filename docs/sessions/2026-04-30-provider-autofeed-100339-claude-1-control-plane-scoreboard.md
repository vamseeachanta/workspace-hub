# Provider-Autofeed Control-Plane Scoreboard — claude-1 lane (run 20260430-100339)

> **Lane ID:** `claude-1-control-plane-scoreboard`
> **Run:** `provider-autofeed-20260430-100339`
> **Generated:** 2026-04-30 (UTC ~10:03)
> **Author:** claude-1 lane (Opus 4.7, 1M context)

## ENV-MISMATCH banner — read this first

The orchestrator passed a result file path **outside** this lane's sandbox:

| Item | Value |
|---|---|
| Prescribed result path | `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-100339/results/claude-1-control-plane-scoreboard.md` |
| Lane sandbox root | `/mnt/local-analysis/workspace-hub` |
| Read access to `agent-logs/` | **blocked** (`stat`, `cat`, `Read` all denied) |
| Write access to `agent-logs/` | **blocked** (`Write` denied for both existing and new files under that tree) |
| What still works from this lane | `Glob` for path enumeration only — file contents unreadable |

**Operator action required (one of):**
1. Widen the allowlist for this lane to include `/mnt/local-analysis/agent-logs/**` (Read/Write), or
2. Relocate the lane result path inside `workspace-hub` (e.g. `.claude/state/lane-handoffs/...`), or
3. Treat this in-workspace document as the canonical lane output and copy it into the prescribed path out-of-band.

Until then, **this scoreboard is built from path enumeration only** — no log/prompt/result file contents were inspected from this lane. Confidence is reduced accordingly, and findings flagged with `[content-unverified]` where reading log bodies would have changed strength.

## Scoreboard — by run, newest first

Legend:
- ✅ `result.md` present in `results/` (delivered, content unverified from this lane)
- 🟥 `log` present, `result.md` absent (stalled or never wrote output)
- 🔁 `.rerun.log` present (orchestrator retried at least once)
- ⚙️ provider-fallback variant logs present (`.g25flash` / `.g25pro` / `.openrouter`)

### Run `provider-autofeed-20260430-100339` (current — this lane)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| codex-1-approved-marker-scout | ✓ | ✓ | ✅ |
| codex-2-test-readiness-scout | ✓ | ✓ | ✅ |
| codex-3-worktree-salvage | ✓ | ✓ | ✅ |
| claude-1-control-plane-scoreboard | ✓ | ✓ | ✅ (placeholder file existed pre-run; **this lane could not overwrite it** due to sandbox; canonical output = THIS document) |
| claude-2-plan-review-hardening | ✓ | ✓ | ✅ |
| claude-3-governance-recovery-contract | ✓ | ✓ | ✅ |

**Read:** all six lanes appear nominally complete by file presence. Content of codex-1/2/3 results not verifiable from this lane — recommend a non-sandboxed reviewer cross-check against the codex-cli upstream stdin-hang regression (memory: `feedback_codex_cli_0_124_upstream_regression`) before treating codex-* results as authoritative.

### Run `provider-autofeed-20260430T094906Z` (mid-morning, ~5h ago)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| claude-control-plane-synthesis | ✓ | ✓ | 🟥 |
| claude-adversarial-review-2564 | ✓ | ✓ | 🟥 |
| codex-approved-execution-scout | ✓ | ✓ | 🟥 |
| codex-worktree-stall-salvage | ✓ | ✓ | 🟥 |
| gemini-plan-risk-recon | ✓ | ✓ | 🟥 |

**Read:** *no* `results/` directory in the Glob enumeration for this run. Five lanes started, zero results delivered. Either the run is still in-flight (unlikely after >5h), the orchestrator failed to materialize results, or all five lanes hit terminal errors. **High-leverage stall** — the adversarial review of #2564 is on this batch.

### Run `provider-min3-20260430-0459` (this morning, ~5h ago)

| Lane | Prompt | Log | Rerun | Provider-variants | Result |
|---|---|---|---|---|---|
| claude-1-control-synthesis | ✓ | ✓ | 🔁 | — | 🟥 |
| claude-2-plan-review-hardening | ✓ | ✓ | 🔁 | — | 🟥 |
| claude-3-governance-autofeed | ✓ | ✓ | 🔁 | — | 🟥 |
| codex-1-approved-implementation-scout | ✓ | ✓ | — | — | 🟥 |
| codex-2-test-repair-scout | ✓ | ✓ | — | — | 🟥 |
| codex-3-worktree-hygiene-salvage | ✓ | ✓ | — | — | 🟥 |
| gemini-1-research-queue-expansion | ✓ | ✓ | — | ⚙️ g25flash, g25pro, openrouter | ✅ |
| gemini-2-gtm-legal-risk | ✓ | ✓ | — | ⚙️ g25flash, g25pro, openrouter | ✅ |
| gemini-3-standards-recon | ✓ | ✓ | — | ⚙️ g25flash, g25pro, openrouter | ✅ |
| (run also has `manifest.txt`) | | | | | |

**Read:**
- **Gemini fan-out is working** — all three Gemini lanes delivered results across three model surfaces. Confirms the `submit-to-gemini.sh` durable fix (memory: `feedback_gemini_trust_env_blocks_reviews`).
- **Claude-1/2/3 retried once and still stalled** (`.rerun.log` present, no `result.md`). Likely candidate: the rerun also hit the same failure mode the first run did — root cause not visible from path metadata.
- **Codex-1/2/3 stalled with no rerun.** Highly consistent with the codex-cli 0.124.0 upstream stdin-hang (memory: `feedback_codex_cli_0_124_upstream_regression`, #2479) — codex would never produce output and the supervisor correctly stopped throwing tokens at a known-broken binary.

### Run `provider-recovery-20260430-0445` (~6h ago)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| claude-control-plane-recovery | ✓ | ✓ | 🟥 |
| codex-approved-implementation | ✓ | ✓ | 🟥 |
| codex-worktree-recovery | ✓ | ✓ | 🟥 |
| gemini-research-recon | ✓ | ✓ | 🟥 |
| gemini-gtm-risk-scan | ✓ | ✓ | 🟥 |

**Read:** entire recovery batch stalled. Notable: the Gemini lanes here did **not** produce results, while the same provider's lanes in `provider-min3-20260430-0459` did. Suggests the recovery wrapper does not invoke the same fan-out chain — worth verifying.

### Run `nightly-20260430-more-lanes-0431` (~6h ago)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| batch6-approved-execution-scout | ✓ | ✓ | 🟥 |
| batch7-post-merge-closeout-audit | ✓ | ✓ | 🟥 |
| batch8-plan-review-artifact-inline-rerun | ✓ | ✓ | 🟥 |
| batch9-gtm-evidence-gate | ✓ | ✓ | 🟥 |
| batch10-provider-queue-autofeed | ✓ | ✓ | 🟥 |

**Read:** zero results. Five batches added to nightly's already-low yield (see next).

### Run `nightly-20260429-2239` (overnight)

| Lane | Prompt | Log | Result |
|---|---|---|---|
| batch1 | ✓ | ✓ | 🟥 |
| batch2 | ✓ | ✓ | 🟥 |
| batch3 | ✓ | ✓ | 🟥 |
| batch4 | ✓ | ✓ | 🟥 |
| batch5-worktree-provider-throughput-report | ✓ | ✓ | ✅ |

**Read:** 1/5 yield. The successful one is, ironically, the throughput report. The other four overnight batches are silent.

### Auxiliary state — `provider-autofeed-monitor/`

| File | Status |
|---|---|
| `snapshot-20260430-100206.md` | exists, **not readable from this lane** |
| `lane-state-20260430-100304.md` | exists, **not readable from this lane** |
| `latest.md` | exists, **not readable from this lane** |

Operator with broader access should treat these as authoritative over this scoreboard, since they almost certainly carry actual log-body inspection.

## Recovery queue — priority order

Priority is leverage × likelihood-of-low-cost-recovery. Top of queue first.

1. **🔴 P0 — re-dispatch `claude-adversarial-review-2564` (`provider-autofeed-20260430T094906Z`).**
   Adversarial reviews are the merge gate for the #2460 approval-binding family (memory: `project_issue_2460_approval_binding`); a missing review blocks the whole approval/implementation pipeline. Cost is one Claude lane; payoff is unblocking everything downstream.
2. **🔴 P0 — re-dispatch `claude-control-plane-synthesis` (`provider-autofeed-20260430T094906Z`).**
   Without a synthesis, the orchestrator's own scoreboard for that wave is missing. (This very lane is the same role for the *current* wave — and you just saw what happens when the result path is mis-configured.)
3. **🟧 P1 — investigate codex-cli version on the dispatching host before any further codex re-dispatch.**
   Per `feedback_codex_cli_0_124_upstream_regression` (installed 2026-04-23, blocks ALL `codex exec` calls regardless of stdin), the workaround is **downgrade to 0.123.0**. Re-dispatching codex-1/2/3 of `provider-min3-...` or `provider-recovery-...` *without* the downgrade is wasted budget. Owner: dispatcher host.
4. **🟧 P1 — re-dispatch `claude-1/2/3` of `provider-min3-20260430-0459`.**
   These already retried once; second rerun is justifiable only after capturing what actually killed the first two attempts (memory not yet written for this failure mode → diagnostic step required first).
5. **🟨 P2 — replay `provider-recovery-20260430-0445` *after* the Gemini fan-out chain is mirrored from `provider-min3-...` into the recovery wrapper.**
   The same provider succeeded in min3 and failed in recovery within the same hour — strongly suggests wrapper divergence, not provider failure.
6. **🟨 P2 — close out `nightly-20260430-more-lanes-0431` (batch6–10) and `nightly-20260429-2239` (batch1–4).**
   Lower leverage (overnight nightly batches are designed to tolerate misses); fold into next nightly cycle rather than ad-hoc replay.

## Cross-cutting recommendations

- **Promote a `results/.lane-state.json` per run** (presence-only is brittle). A 3-line JSON from each lane wrapper (`status`, `provider_used`, `exit_code`) would let any future scoreboard distinguish "stalled" from "completed-empty" without reading log bodies. Maps to the enforcement-gradient L2 pattern (`.claude/rules/patterns.md`).
- **Standardize the lane-result path inside the sandbox.** Today: `agent-logs/<run>/results/<lane>.md` lives outside the workspace, which is what made *this* lane unable to write its prescribed output. Either make `agent-logs` a subtree of `workspace-hub` (or symlink it in) or add it to the lane allowlist by default.
- **Fold the codex-cli 0.124.0 known-bad fingerprint into pre-dispatch checks.** `codex --version` on the dispatcher → if `0.124.x`, refuse to dispatch any codex lane and emit a structured error. Saves the cost of the next stall wave.
- **Mirror the Gemini fan-out chain into every wrapper that dispatches gemini lanes** (current divergence between `provider-min3` and `provider-recovery` is the smoking gun).

## Evidence appendix — Glob enumeration only

The full enumeration backing this scoreboard is the `Glob /mnt/local-analysis/agent-logs/**` listing captured in this lane's reasoning. No log/prompt/result file body was read. Operators with read access to `agent-logs/` should cross-check the ✅ rows above against actual content before acting on the recovery queue — particularly the codex-1/2/3 results in the **current** run, since codex-cli upstream regression makes "log file present" a less-reliable success signal than usual.

## Hard-gate compliance (this lane)

- ✓ No destructive `reset`/`clean`
- ✓ `GIT_OPTIONAL_LOCKS=0` not needed — no git mutations attempted
- ✓ No GitHub mutations (no `gh issue`/`pr` calls)
- ✓ No outreach drafts
- ✓ No self-approval / no `status:plan-approved` label changes
- ✓ No unapproved implementation
- ✓ No secrets emitted (no API keys, tokens, or PII appear in this document)
