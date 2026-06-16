# Plan for #3148: check-all run_mypy baseline-aware + fix assetutilities mypy crash

> **Status:** plan-review (NOT self-approved)
> **Complexity:** T2 (mirrors the merged #3146 ruff-ratchet pattern + a one-line assetutilities mypy-config fix)
> **Date:** 2026-06-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3148
> **Client:** N/A | **Project:** N/A

---

## Resource Intelligence Summary

Two distinct sub-problems (both make check-all's `:158` gate fail on mypy):

### A. check-all `run_mypy` is a hard gate with no baseline
`scripts/quality/check-all.sh` `run_mypy` runs `uv run mypy src/` and FAILs on any non-zero exit — it does NOT consult `config/quality/mypy-baseline.yaml` (which already exists, seeded; e.g. assetutilities=941). The mypy *ratchet* (`check_mypy_ratchet.py`, pre-push opt-in) is a SEPARATE gate; it does not make check-all's `:158` mypy lenient. Same shape as #3146 (ruff), now solved — mirror that fix.

### B. assetutilities mypy CRASHES (not type-errors)
**Reproduced:** `cd /mnt/local-analysis/assetutilities && uv run mypy src/` → `web-contextualization is not a valid Python package name`, **exit 2**. Root cause: `src/modules/web-contextualization` — a hyphenated dir is not a valid Python package, so mypy aborts (exit 2) before type-checking → check-all reports `mypy: FAIL (0 errors)`. **With `--exclude 'web-contextualization'`, mypy runs normally: exit 1, 1215 errors in 137 files.** (The 941 in the current baseline is stale / from a different invocation — re-seed.)

### Proven pattern to mirror
Merged #3146: `_ruff_baseline_count` helper in check-all + ratchet logic (`PASS when count <= baseline`, `RUFF_NO_RATCHET=1` escape) + `check_ruff_ratchet.py`. `mypy-baseline.yaml` + `check_mypy_ratchet.py` already exist — only the check-all WIRING is missing.

---

## Design

1. **Fix B first (assetutilities):** add `web-contextualization` (or a glob for hyphenated module dirs) to `[tool.mypy] exclude` in `assetutilities/pyproject.toml`, so mypy runs instead of crashing. This is prerequisite — a crashed mypy must not be ratcheted (see nuance).
2. **Fix A (workspace-hub):** make check-all `run_mypy` baseline-aware, mirroring #3146:
   - `_mypy_baseline_count` helper reads `config/quality/mypy-baseline.yaml`.
   - `run_mypy`: exit 0 → PASS; **exit ≥2 → hard FAIL (crash/usage — NEVER ratchet-pass)**; exit 1 → count errors, PASS when `count <= baseline`, FAIL on regression. `MYPY_NO_RATCHET=1` escape.
   - **Re-seed** `mypy-baseline.yaml` for assetutilities to the post-fix count (1215) via `check_mypy_ratchet.py --init` (or targeted), so the ratchet is accurate after the crash fix.

### Critical design nuance (vs #3146 ruff)
mypy exit codes differ from ruff: **exit 2 = crash/usage error**, exit 1 = type errors, 0 = clean. A crashed mypy yields 0 parsed errors — `0 <= baseline` would FALSELY PASS. So `run_mypy` MUST treat exit ≥2 as a hard failure, independent of the baseline. (This is exactly the bug class behind B — a crash masquerading as "0 errors".)

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Modify | `assetutilities/pyproject.toml` (`[tool.mypy] exclude`) | stop mypy crashing on `src/modules/web-contextualization` |
| Modify | `scripts/quality/check-all.sh` | `_mypy_baseline_count` + baseline-aware `run_mypy` (exit-2 hard-fail) |
| Modify | `config/quality/mypy-baseline.yaml` | re-seed assetutilities to post-fix count (~1215) |
| Create | `tests/quality/test_check_all_mypy_ratchet.sh` (or extend `test_check_all.sh`) | baselined-passes / new-error-fails / crash(exit2)-fails / exclude-fixes-crash |

---

## TDD Test List
| Test | Verifies |
|---|---|
| mypy_baselined_passes | repo at/under baseline → check-all mypy PASS |
| mypy_regression_fails | count > baseline → FAIL |
| mypy_crash_exit2_hard_fails | mypy exit 2 (mocked) → FAIL, NOT a baseline-pass (the key nuance) |
| mypy_no_ratchet_escape | `MYPY_NO_RATCHET=1` → hard zero-tolerance |
| assetutilities_mypy_runs_after_exclude | with the pyproject exclude, mypy exits 1 (runs) not 2 (crash) |

---

## Acceptance Criteria
- [ ] `cd assetutilities && uv run mypy src/` no longer exits 2 (crash) — runs and reports type errors (exit 1).
- [ ] `mypy-baseline.yaml` assetutilities count reflects the post-fix actual (re-seeded).
- [ ] check-all `--repo assetutilities` mypy PASSES via ratchet (count <= baseline); a +1 regression FAILS; a simulated crash (exit 2) FAILS.
- [ ] Existing `test_check_all.sh` + `check_mypy_ratchet` tests still pass.
- [ ] `legal-sanity-scan --diff-only` passes.
- [ ] Cross-provider review (T2) clean; **re-check #3148 state immediately before implementing** (parallel-merge lesson from #3127/#3146).

---

## Risks and Open Questions
- **Risk:** excluding `web-contextualization` hides any real type issues in that module. Acceptable — it's not an importable package (hyphen); if it should be checked, rename it (separate). Document the exclusion reason.
- **Risk:** crash-vs-clean conflation (exit 2 passing as 0) — explicitly tested (`mypy_crash_exit2_hard_fails`).
- **Risk:** two-repo change (assetutilities + workspace-hub) → two PRs (one per repo). Land assetutilities exclude first, then re-seed baseline, then workspace-hub wiring.
- **Open:** glob-exclude all hyphenated module dirs vs just this one? Recommend just this one + a follow-up to lint for hyphenated package dirs.

## Complexity: T2
A near-clone of the merged #3146 ruff wiring + a one-line assetutilities mypy-exclude + baseline re-seed; the only novel piece is the exit-2-hard-fail nuance (well-contained + explicitly tested).
