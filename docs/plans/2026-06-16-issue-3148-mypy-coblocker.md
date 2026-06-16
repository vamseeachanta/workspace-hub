# Plan for #3148: make check-all mypy gate passable across ALL tier-1 repos

> **Status:** plan-review (REVISED to T3 after adversarial review — NOT self-approved)
> **Complexity:** T3 (review proved it spans all 4 tier-1 repos + 2 code fixes + 2 gate scripts — was wrongly scoped T2)
> **Date:** 2026-06-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3148
> **Client:** N/A | **Project:** N/A
> **Review:** 1 Claude scope-subagent NON-APPROVE (empirical, all 4 repos); codex+gemini fanout FAILED (SIGTERM/timeout) → degraded, documented.

---

## Why revised (r1 scope review — NON-APPROVE)

The T2 plan fixed only assetutilities. Empirical mypy enumeration on ALL four tier-1 repos (live filesystem) showed **every repo fails the proposed mypy gate**, so the original plan unblocks 1 of 4 and re-breaks the rest. The #3127/#3146 lesson ("verify coverage across the whole set") applied.

### Per-repo mypy reality (reproduced 2026-06-16)
| repo | mypy result | baseline (mypy-baseline.yaml) | problem |
|---|---|---|---|
| assetutilities | exit 2 CRASH (`src/modules/web-contextualization`); after exclude → exit 1, 1215 | 941 | crash + stale baseline + **3** hyphen-dirs (agent-os, web-contextualization, enhanced-create-specs) → count depends on which excluded (1215 vs 1148) |
| digitalmodel | **exit 2 CRASH** — syntax error `src/digitalmodel/specialized/project_management/projectScheduleD01.py:8` | 1 (seeded FROM the crash) | real code bug; exclude won't help |
| worldenergydata | exit 1, **3589**; **cold run 4m08s > 300s → timeout(124)** | 3414 | regression +175 + timeout |
| assethold | exit 1, **355** | 320 | regression +35 |

---

## Design (T3 — full gate-surface mypy fix)

### 1. Per-repo crash/code fixes (prerequisite — a crash must never be ratcheted)
- **assetutilities**: `[tool.mypy] exclude` the hyphenated module dirs. **Decision: enumerate all 3** (`web-contextualization`, `agent-os`, `enhanced-create-specs`) explicitly (glob `-` is too broad/fragile) — and seed the baseline to the resulting count. File a follow-up to rename hyphenated module dirs (not valid Python packages).
- **digitalmodel**: **fix the syntax error** at `projectScheduleD01.py:8` (real bug) — preferred over excluding. If the fix is non-trivial, fall back to a per-file `[[tool.mypy.overrides]] ignore_errors` with a TODO + follow-up issue.

### 2. check-all `run_mypy` baseline-aware (clone merged #3146 ruff)
- `_mypy_baseline_count` helper reads `mypy-baseline.yaml`.
- Exit-code handling (the load-bearing nuance):
  - **0** → PASS.
  - **1** (type errors) → count, PASS when `count <= baseline`, else FAIL (regression).
  - **2** (usage/crash) → **hard FAIL** (never ratchet-pass; a crash yields 0 parsed errors).
  - **124/137** (timeout/OOM, env) → distinct: wrap `run_mypy` in `timeout 300` (match the ratchet); on timeout, **FAIL with an explicit "mypy timed out" reason** (not silently "crash"), and document the warm-cache expectation for CI. (Do NOT silently pass.)
- `MYPY_NO_RATCHET=1` escape (manual zero-tolerance).

### 3. Same exit-2/timeout guard in `check_mypy_ratchet.py._run_mypy` (lines 219-229)
Today it ignores `returncode` and parses crash output as a real count → ratchet-passes a crash. Add: returncode 2 → crash (fail/raise, not count); 124 → timeout. Keeps the two gates (check-all + the opt-in ratchet) from disagreeing on the same repo. Add tests.

### 4. Re-seed ALL baselines (after the crash/code fixes land)
Targeted re-seed each repo to its post-fix actual: assetutilities (post-exclude), digitalmodel (post-syntax-fix), worldenergydata (3589), assethold (355). **Drop the stale `ogmanufacturing` row** (removed from tier-1 in #3012; not on disk). Warm the mypy cache before seeding worldenergydata (avoid the 4-min cold compile skewing/timeouts).

---

## Files to Change
| Action | Path |
|---|---|
| Modify | `assetutilities/pyproject.toml` — `[tool.mypy] exclude` (3 hyphen dirs) |
| Modify | `digitalmodel/.../projectScheduleD01.py` — fix syntax error (or per-module override) |
| Modify | `scripts/quality/check-all.sh` — `run_mypy` baseline-aware + exit-code handling + `timeout` wrapper |
| Modify | `scripts/quality/check_mypy_ratchet.py` — exit-2/timeout guard in `_run_mypy` |
| Modify | `config/quality/mypy-baseline.yaml` — re-seed all 4; drop ogmanufacturing |
| Create | `tests/quality/test_check_all_mypy_ratchet.sh` + ratchet crash test |

---

## TDD Test List
| Test | Verifies |
|---|---|
| mypy_baselined_passes / mypy_regression_fails | ratchet core |
| mypy_crash_exit2_hard_fails (check-all) | crash ≠ pass |
| mypy_ratchet_crash_exit2_fails (check_mypy_ratchet) | sibling gate agrees |
| mypy_timeout_124_fails_with_reason | timeout distinct from crash, not silent |
| mypy_no_ratchet_escape | zero-tolerance escape |
| assetutilities_mypy_runs_after_exclude | exit 1 not 2 |
| digitalmodel_mypy_runs_after_syntax_fix | exit 1 not 2 |

---

## Acceptance Criteria
- [ ] All 4 tier-1 repos: `uv run mypy src/` (with config) exits 0/1 (runs), never 2 (crash).
- [ ] `mypy-baseline.yaml` re-seeded to actuals for all 4; ogmanufacturing removed.
- [ ] check-all `--repo <each>` mypy PASSES via ratchet; +1 regression FAILS; simulated exit-2 FAILS; simulated timeout(124) FAILS-with-reason.
- [ ] `check_mypy_ratchet.py` also fails on exit-2 (no gate disagreement).
- [ ] **End-to-end:** a clean push's check-all (ruff #3146 + mypy #3148) passes for all 4 repos — i.e. the bypass is no longer needed *for check-all* (note: run-all-tests/coverage/secrets are separate pre-push gates).
- [ ] Existing tests + `legal-sanity-scan --diff-only` pass.
- [ ] T3 cross-provider review (Claude+Codex+Gemini) clean; re-check #3148 state immediately before implementing.

---

## Risks / Sequencing
- **Sequence:** per-repo code fixes (assetutilities exclude, digitalmodel syntax) FIRST → warm caches → re-seed baselines → check-all + ratchet wiring + tests. Multiple PRs (per-repo fixes can land independently; workspace-hub wiring last).
- **Risk:** digitalmodel syntax fix may reveal cascading errors (the crash masked everything) — the post-fix count could be large; that's the honest baseline.
- **Risk:** worldenergydata cold-compile timeout on CI — warm-cache or raise the timeout; tested.
- **Risk:** excluding hyphen dirs hides real issues there → follow-up to rename them.

## Complexity: T3
Four repos (two needing code fixes), two gate scripts, full baseline re-seed, exit-code/timeout semantics — systemic; 3-provider review required.
