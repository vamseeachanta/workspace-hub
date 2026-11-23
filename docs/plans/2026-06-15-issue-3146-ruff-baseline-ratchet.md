# Plan for #3146: ruff baseline/ratchet so the pre-push gate is passable

> **Status:** plan-review (NOT self-approved)
> **Complexity:** T2 (clone of the proven mypy-ratchet pattern; one new script + baseline + check-all wiring + tests)
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3146
> **Client:** N/A | **Project:** N/A

---

## Resource Intelligence Summary

### The blocking gate
- `.git/hooks/pre-push:158` runs `bash check-all.sh --repo "$repo"` per tier-1 repo — a **hard** gate. `check-all.sh` `run_ruff` does `ruff check .` and FAILs on ANY error, with **no baseline** (`scripts/quality/check-all.sh`, `run_ruff`). This is what blocks pushes.
- Separate opt-in ratchet gates exist for mypy (`:221`, `MYPY_RATCHET_GATE=1`), complexity (`:239`, `COMPLEXITY_RATCHET_GATE=1`), coverage (`:202`). Ruff has none.

### The proven model to mirror (mypy-ratchet, WRK-1092)
- `config/quality/mypy-baseline.yaml`: `schema_version`, `updated_at`, `repos: {<repo>: {error_count, updated_at, note}}`.
- `scripts/quality/check_mypy_ratchet.py`: `actual <= baseline → PASS; actual > baseline → FAIL`; `--init` captures baseline; auto-lowers (no auto-commit) when `actual < baseline`; args `--baseline`, `--repo-root`, `--repo`; already uses the #3136 tier-1 resolver (`_repo_path`).
- Ruff error count is parseable from `ruff check` output (`Found N errors`) — `check-all.sh run_ruff` already extracts it.

### Measured current ruff debt (2026-06-15, clean checkouts @ origin/main)
worldenergydata 3165 · assetutilities 473 · assethold 360 · digitalmodel 0.

### Reproduce (Step 1.5 — confirmed)
`check-all.sh --repo assetutilities` → `ruff: FAIL (473 errors)` → exit 1 → pre-push blocks. 3/4 tier-1 repos affected → chronic `GIT_PRE_PUSH_SKIP`.

### Architectural finding (RESOLVED by inspection — changes the design)
`check-all.sh:158` hard-checks BOTH ruff and mypy. **`run_mypy` is ALSO a hard gate** (any non-zero mypy exit → FAIL; it does NOT consult `mypy-baseline.yaml`). The separate mypy *ratchet* (`pre-push:221`, opt-in `MYPY_RATCHET_GATE=1`) is an ADDITIONAL gate — it does not make check-all's `:158` mypy lenient. So:
- There is **no existing "lenient run_mypy" mechanism to mirror** — the original plan premise was wrong. `run_ruff` baseline-awareness must be built **de novo**.
- **check-all `:158` blocks on BOTH ruff debt AND mypy** — so fixing ruff alone will NOT fully unblock pushes. For `assetutilities`, check-all reports `mypy: FAIL (0 errors, 0 warnings)` — a non-zero mypy exit with zero counted error lines, i.e. likely a **mypy config/crash**, a DISTINCT problem from ruff debt.

---

## Design decision

Make **`check-all.sh run_ruff` baseline-aware DE NOVO** (the blocking gate) — do NOT try to mirror `run_mypy` (it's also hard):
- Add `config/quality/ruff-baseline.yaml` (same data shape as mypy-baseline; seeded via `--init` with the measured counts).
- Add `scripts/quality/check_ruff_ratchet.py` (clone the *ratchet logic* of `check_mypy_ratchet.py`: parse `Found N errors`, compare to baseline, `--init`, auto-lower, reuse the shared `tier1_repos` resolver).
- Wire `run_ruff` to PASS when `actual <= baseline` (regression-only enforcement). Keep a `--no-ratchet`/`--ruff-strict` escape for manual zero-tolerance runs.
- **Scope note (co-blocker):** check-all's hard `run_mypy` ALSO blocks `:158`, so this PR makes the RUFF check passable but does not, by itself, fully unblock pushes. The mypy co-blocker (esp. the `assetutilities` mypy config/crash) is a DISTINCT problem → handle via a sibling issue (recommended) OR expand this PR to also make `run_mypy` consult `mypy-baseline.yaml`. **Recommend: keep #3146 ruff-scoped + file a sibling "make check-all run_mypy baseline-aware / fix assetutilities mypy crash" issue** so each lands testably. Flag for user decision at approval.

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `scripts/quality/check_ruff_ratchet.py` | ruff ratchet (clone of mypy ratchet; shared resolver) |
| Create | `config/quality/ruff-baseline.yaml` | per-repo baseline (via `--init`) |
| Modify | `scripts/quality/check-all.sh` | `run_ruff` baseline-aware; `--no-ratchet` escape |
| Modify | `.git/hooks/pre-push` + installer source | add `RUFF_RATCHET_GATE` parity IF mypy uses a separate gate (match the pattern) |
| Create | `tests/quality/test_check_ruff_ratchet.py` | new-error-fails / baselined-passes / init / auto-lower / resolver |
| Modify | `tests/quality/test_check_all.sh` | run_ruff baseline behavior |
| Update | `docs/plans/README.md` | index |

---

## TDD Test List
| Test | Verifies |
|---|---|
| baselined_debt_passes | repo at exactly its baseline count → PASS (the unblock) |
| new_error_fails | actual = baseline+1 → FAIL (regression caught) |
| improvement_auto_lowers | actual < baseline → PASS + baseline lowered (no auto-commit) |
| init_captures_counts | `--init` writes the measured per-repo counts |
| uses_shared_resolver | resolves sibling-layout repos (post-#3136) |
| strict_escape | `--no-ratchet`/`--ruff-strict` still hard-fails (manual zero-tolerance) |
| schema_invalid_fails_closed | malformed baseline → error, not silent pass |

---

## Acceptance Criteria
- [ ] With `ruff-baseline.yaml` seeded at current counts, the **ruff portion** of `check-all.sh --repo <each tier-1>` PASSES — verified for all 4. (NOTE: full `check-all` may still FAIL on the mypy co-blocker — that's the sibling issue, not this AC.)
- [ ] Introducing one new ruff error in a repo makes the ruff gate FAIL (regression protection intact).
- [x] Sibling issue filed for the check-all `run_mypy` co-blocker → **#3148** (scope decision: keep #3146 ruff-scoped; mypy handled in #3148).
- [ ] Existing `test_check_all*.sh` + mypy/complexity ratchet tests still pass.
- [ ] `legal-sanity-scan.sh --diff-only` passes; no hardcoded abs paths.
- [ ] Cross-provider review (T2 = 2 providers) clean; **re-check #3146 issue state immediately before implementing** (lesson from #3127 parallel-merge).

---

## Risks and Open Questions
- **Risk:** load-bearing gate — a ratchet bug could let new ruff errors through (mitigate: explicit new_error_fails test) or block valid pushes (baseline seeded at measured counts).
- **Risk:** the architectural wrinkle (hard run_mypy vs separate mypy ratchet) — must be understood before wiring ruff, or the fix won't unblock `:158`. TDD pins the actual `run_mypy` gate behavior first.
- **Risk:** baseline staleness — repos accrue/shed errors; auto-lower + `--init` refresh handle the down direction; up direction is intentionally blocked.

## Complexity: T2
A clone of an existing, proven ratchet (mypy) with a baseline data file and check-all wiring; the only non-trivial part is matching `run_ruff`'s gate treatment to `run_mypy`'s.
