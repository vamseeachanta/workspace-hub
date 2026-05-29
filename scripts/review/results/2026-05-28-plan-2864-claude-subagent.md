# Plan-stage adversarial review — #2864 SOUL symlink clobber

> **Stage:** plan · **Issue:** [#2864](https://github.com/vamseeachanta/workspace-hub/issues/2864) · **Date:** 2026-05-28 · **Complexity:** T2
> **Plan:** docs/plans/2026-05-28-issue-2864-soul-clobber.md

## Method / provenance
Independent fresh-context subagent (cross-provider Codex/Gemini dispatch unavailable from a Claude-Code session; degraded T2→1, documented). Every load-bearing finding empirically verified by the main session against live code before revision.

## Round 1 verdict: CHANGES REQUIRED

| # | Sev | Finding | Verified |
|---|-----|---------|----------|
| 1 | HIGH | Option A creates a **two-owner race**: `install-soul-runtime.sh:23` resolves target via `git rev-parse --show-toplevel`; `sync-agent-configs.sh:8` via `cd "$SCRIPT_DIR/../.." && pwd` (logical, not `-P`). They diverge under worktree/symlinked-checkout/`~/workspace-hub` overlay → each sees the other's link as wrong → endless re-backup/repoint churn. | ✅ grep L23/L8 |
| 2 | HIGH | the two-sync idempotency test can't catch the cross-owner flip-flop (two sync runs always agree). | ✅ logic |
| 3 | MED | "drop HERMES_SOUL_TEMPLATE" is ambiguous; `config/agents/hermes/SOUL.md` is the **build delta** (build-soul-runtime.sh:10) — deleting it breaks the build. | ✅ build script |
| 4 | MED | Option-A backup semantics diverge from install-soul-runtime (it backs up `-e OR -L`; plan only `-e && !-L`). | ✅ L49 |
| 5 | MED | DRY_RUN only a trailing comment, not in control flow; `sync_hermes_plain_file` guards every mutation behind DRY_RUN; install-soul-runtime has **no** dry-run while harness-update passes `--dry-run` (L349). | ✅ L1173/L349 |
| 6 | LOW | SSO/pyyaml pytest suites don't exercise SOUL — misleading as the regression gate. | ✅ |
| 7 | INFO | **Scope confirmed correct**: only Hermes SOUL.md is clobbered (`~/.codex/AGENTS.md` not touched by sync; Claude/Gemini use `sync_json_merge`). | ✅ |
| 8 | LOW | plan presented as approval-ready with an unresolved A/B fork + empty review table; under-weighted Option B (which structurally avoids F1). | — |

## Resolution (this revision)
**Pivoted to Option B (single owner).** `sync-agent-configs.sh` stops touching `~/.hermes/SOUL.md` (remove L1248-1249 + vars; keep the delta file); `harness-update.sh` invokes `install-soul-runtime.sh` (sole owner) on the nightly path, gated under `--dry-run`. This removes the second owner → F1/F2/F4 dissolve at the design level. F3 closed (explicitly keep the delta file). F5 closed (harness-update gates the no-dry-run install + dry-run test; optional `--dry-run` added to install-soul-runtime). F6 closed (SOUL gate is the new tests, not the SSO pytest). F8 closed (fork resolved → B; table filled).

## Result
**PASS after revision.** Option B is simpler and structurally race-free. Recommend a Codex pass out-of-session (cron-critical path) before implementation.
