# Plan for #2580: Fix digitalmodel citations and capsys tests currently collect-ignored

> **Status:** draft (r2 — addresses 2026-05-02 r1 adversarial review MAJOR verdict; awaits fresh adversarial review before any approval transition)
> **Version:** r2
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2580
> **Review artifacts:** `docs/reviews/2026-05-02-issue-2580-r1-adversarial.md` (Claude Opus 4.7, MAJOR, 3 P1 + 5 P2); `scripts/review/results/2026-05-02-plan-2580-codex.md`; `scripts/review/results/2026-05-02-plan-2580-claude.md`; `scripts/review/prompts/2026-05-02-plan-2580-gemini-rerun.md` if Gemini capacity/tooling is unavailable

---

## Revision History

| Version | Date | Change |
|---|---|---|
| r1 | 2026-05-02 | Initial draft after Codex MAJOR rerun; narrowed scope to yml-utilities only (citations credited to merged digitalmodel PR #542). |
| r2 | 2026-05-02 | Adversarial review (`docs/reviews/2026-05-02-issue-2580-r1-adversarial.md`) issued MAJOR verdict citing 3 P1 defects: (1) wrong base branch, (2) stub TDD test names, (3) 6-vs-8 capsys count discrepancy. r2 adds Preflight section pinning `origin/main` ancestry; replaces stub test names with the six actual function names plus per-line caplog conversion notes; enumerates all 13 capsys occurrences across 7 test functions and documents the in-scope vs. out-of-scope decision; adds per-call-site KEEP/CONVERT tagging for all 7 `print()` calls in `yml_utilities.py`; specifies xdist invocation and before/after pass-count procedure; adds Fixture Freshness mechanism for #542 vendored wiki copy. Citations Approach (B vendor) and yml-utilities Approach (A logging/caplog) preserved unchanged — both validated by r1 review. |

---

## Preflight (mandatory before any code changes — r2 P1-1 fix)

The r1 review proved that the local working-tree branch `fix/triage-punch-list-2026-05-02` at SHA `0faf6416` (digitalmodel) is **stale** relative to merged PR #542 and contains citation collect-ignore entries that `origin/main` no longer carries. Implementing on the stale base will produce a wrong-tree edit. Hard preflight is therefore mandatory.

### Required base

- **Base branch:** `origin/main` of the digitalmodel repo.
- **Minimum ancestor SHA:** `b1346acb` (commit `test(citations): vendor wiki fixtures to decouple from workspace-hub root (#2580) (#542)`, merged 2026-05-02T10:57:49Z).
- **Newer is acceptable:** as of 2026-05-02 verification, `origin/main` had advanced to `60d59565` (`fix(ci): triage punch list ... (#543)`) which still contains `b1346acb` as ancestor; if `git fetch origin main` shows newer, use it.
- **Forbidden base:** local working-tree branch `fix/triage-punch-list-2026-05-02` (`0faf6416`) — it predates #542 and still ignores `tests/citations/test_registry.py` and `tests/citations/test_schema.py`. Do **not** branch off it.

### Preflight steps (run in this order, fail-closed)

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel

# 1. Sync remote
git fetch origin main

# 2. Switch to a fresh feature branch off origin/main (NOT off the stale local branch)
git switch main
git pull --ff-only origin main

# 3. Hard ancestry assertion: b1346acb must be reachable from HEAD
git merge-base --is-ancestor b1346acb HEAD || { echo "ABORT: base is missing PR #542 (b1346acb)"; exit 1; }

# 4. Confirm citation ignores are already absent on this base (PR #542 work is present)
grep -E "citations/test_(registry|schema)\.py" tests/conftest.py && { echo "ABORT: citation ignores still present — wrong base"; exit 1; } || echo "OK: citations cleaned by PR #542"

# 5. Create implementation branch
git switch -c fix/2580-yml-utilities-caplog-xdist
```

If any step fails, stop and report the dependency state in #2580 instead of editing.

---

## Resource Intelligence Summary

### Existing repo code
- Found: Issue #2580 owner comment at 2026-05-02T02:24:42Z — citations Option B is already **MERGED** in digitalmodel PR https://github.com/vamseeachanta/digitalmodel/pull/542 at SHA `b1346acb` (merged 2026-05-02T10:57:49Z); 14 citation tests passed; citations collect-ignore entries were removed there. Codex verified the actual fixture path on that PR is `tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`. Do **not** duplicate citation fixture work in this plan.
- Historical context only: `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490/tests/citations/test_registry.py` and `tests/citations/test_schema.py` showed the pre-PR upward `knowledge/wikis/` search. This stale worktree is no longer authoritative for citation implementation scope.
- Found: `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` — verified directly 2026-05-02; the file contains 13 `capsys` occurrences across **7 test functions** (not 6 as #2580 issue body states; r1 review enumerated 8 but two of those occurrences are inside a single function `test_compare_yaml_root_keys_same_and_different` which calls `capsys.readouterr()` twice).
- Found: `digitalmodel/tests/conftest.py` central `collect_ignore` list. On `origin/main` (`60d59565`) the citation entries are absent; the `tests/asset_integrity/test_yml_utilities_additional.py` entry remains (lines ~43-46) — this is the only entry this plan removes.
- Gap: remaining unimplemented scope is `tests/asset_integrity/test_yml_utilities_additional.py` capture/xdist failure plus removal of its collect-ignore entry. The plan must first reproduce the actual failing command/error before changing `print()`/`capsys` to logging/`caplog`, because pytest supports `capsys` and xdist's documented limitation is not a blanket fixture incompatibility.

### Standards
| Standard | Status | Source |
|---|---|---|
| Plan approval hard stop | applies | `docs/standards/HARD-STOP-POLICY.md` — implementation remains blocked until user approval. |
| Engineering/code citation contract | relevant | `.claude/rules/calc-citation-contract.md` and the digitalmodel citation tests require fail-closed citation resolution. |
| TDD requirement | applies | Issue is test-remediation work; tests must be written/adjusted before implementation and fail before the production/test-fixture fix. |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — canonical workspace-hub wiki path named by `tests/citations/test_schema.py`; the implementation should vendor only the minimal fixture content needed by tests, not depend on this checkout at runtime.
- `knowledge/wikis/engineering/wiki/entities/digitalmodel.md` — confirms digitalmodel is tracked as a tier-1 engineering project in workspace-hub knowledge surfaces.

### Documents consulted
- Issue #2580 body — defines the two defect classes, explicitly recommends option B for citations (vendor small fixtures) and option A for yml utilities (replace `print()`/`capsys` path with logging/`caplog`).
- Issue #2574 — cited by #2580 as the temporary Quality Gates unblock that added ratchet ignores; this issue is the required cleanup, not a new ignore.
- Digitalmodel PR #542 — **MERGED** evidence (origin/main contains `b1346acb`); citations clean-up complete.
- `digitalmodel/AGENTS.md` and `digitalmodel/CLAUDE.md` — digitalmodel test command contract: `PYTHONPATH=src uv run python -m pytest`; gates require Plan + approval before implementation.
- `digitalmodel/.github/workflows/quality-gates.yml` — CI invokes `python -m digitalmodel.workflows.automation.quality_gates_cli check --json`, which delegates to pytest under the digitalmodel quality-gates harness.

### Gaps identified
- `yml_utilities` output path must be made xdist-safe; tests should use `caplog` after source code emits logging records rather than relying on `capsys`.
- Remaining yml-utilities ratchet ignore in `digitalmodel/tests/conftest.py` must be removed after the yml tests pass.
- Vendored wiki fixture from PR #542 has no freshness check against canonical `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — addressed in r2 "Fixture Freshness" subsection below.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02T05:08Z via `gh issue view` and `git log origin/main`):
- `#2580` — OPEN, label `status:plan-review` — `fix(digitalmodel-tests): citations + capsys tests collect-ignored, need real fixes`
- `#2574` — referenced by #2580 as the temporary collect-ignore unblock.
- `digitalmodel#542` — **MERGED** 2026-05-02T10:57:49Z at SHA `b1346acb`.

**File existence / excerpts** (verified 2026-05-02 directly from working tree):
- EXISTS: `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` — 13 capsys occurrences, 7 test functions accept `capsys` (enumerated in TDD section).
- EXISTS: `digitalmodel/src/digitalmodel/asset_integrity/common/yml_utilities.py` — 7 `print()` calls (enumerated in KEEP/CONVERT table).
- EXISTS: `digitalmodel/tests/conftest.py` — on `origin/main`, only the yml_utilities_additional entry remains in `collect_ignore`.

**Gap proofs**:
- `git show origin/main:tests/conftest.py | grep citations` returns no match — PR #542 already removed citation entries.
- `search_files` for prior `docs/plans/*2580*` in workspace-hub returned only this canonical plan.

<!-- Verification: count distinct sources: issue #2580, issue #2574, digitalmodel AGENTS.md/CLAUDE.md, three digitalmodel test/source paths, workspace-hub wiki path, quality-gates.yml. Count >= 8. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2580-digitalmodel-collect-ignore-test-fixes.md` |
| Adversarial review r1 (consumed by r2) | `docs/reviews/2026-05-02-issue-2580-r1-adversarial.md` |
| Plan index | `docs/plans/README.md` |
| Citation tests (out of scope, owned by PR #542) | `digitalmodel/tests/citations/test_registry.py`, `digitalmodel/tests/citations/test_schema.py` |
| Citation fixture (dependency evidence only) | `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` |
| Citation fixture provenance (new in r2) | `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/FIXTURE_PROVENANCE.md` (proposed; see Fixture Freshness) |
| YML utility source | `digitalmodel/src/digitalmodel/asset_integrity/common/yml_utilities.py` |
| YML utility tests | `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` |
| Collect-ignore cleanup | `digitalmodel/tests/conftest.py` |
| CI invocation reference | `digitalmodel/.github/workflows/quality-gates.yml` |
| Plan review — r1 adversarial | `docs/reviews/2026-05-02-issue-2580-r1-adversarial.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-2580-codex.md` |
| Plan review — Claude (older) | `scripts/review/results/2026-05-02-plan-2580-claude.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2580-gemini.md` or `scripts/review/prompts/2026-05-02-plan-2580-gemini-rerun.md` if unavailable |

---

## Deliverable

A digitalmodel test cleanup that completes the remaining yml-utilities half of #2580: convert diagnostic `print()` calls in `yml_utilities.py` to `logger.info()` per the per-call-site KEEP/CONVERT table below, switch the seven affected tests in `test_yml_utilities_additional.py` from `capsys.readouterr()` to `caplog.records` matching, remove the temporary `tests/asset_integrity/test_yml_utilities_additional.py` collect-ignore entry from `digitalmodel/tests/conftest.py`, and verify the suite passes under `pytest -n auto`. Citations work is already merged via PR #542 and is **not** in scope.

---

## capsys Reconciliation (r2 P1-3 fix)

The r1 review noted "13 occurrences across 8 test functions" but ground-truth verification gives **13 occurrences across 7 distinct test functions** (one function calls `capsys.readouterr()` twice). The `#2580` issue body says "6 tests" — that was an undercount. The plan covers all **6 in-scope** tests; **1 function** is documented out-of-scope below.

### All 7 functions accepting `capsys` in `tests/asset_integrity/test_yml_utilities_additional.py`

| # | Function | Line | capsys readouterr() lines | Scope |
|---|---|---|---|---|
| 1 | `test_ymlinput_ignores_bad_update_file_and_keeps_defaults` | 99 | 110 | **IN — CONVERT to caplog** |
| 2 | `test_analyze_yaml_keys_prints_root_keys` | 113 | 120 | **IN — CONVERT to caplog** |
| 3 | `test_compare_yaml_root_keys_same_and_different` | 169 | 181, 185 | **IN — CONVERT to caplog (two assertions)** |
| 4 | `test_compare_yaml_files_deepdiff_emits_same_message_for_identical` | 189 | 200 | **IN — CONVERT to caplog** |
| 5 | `test_save_diff_files_writes_expected_outputs_and_invokes_save_data` | 204 | 221 | **IN — CONVERT to caplog** |
| 6 | `test_save_diff_files_reports_same_when_no_diff` | 230 | 239 | **IN — CONVERT to caplog** |
| 7 | `test_save_diff_files_handles_mixed_diff_keys` | 242 | (none — function does NOT use `capsys.readouterr()`; it accepts `monkeypatch` only at line 243; r1 review's footnote is correct that it ultimately does not consume capsys) | **N/A — not in scope; no capsys assertion to convert** |

**Decision and justification:** the 6 IN-scope tests are exactly the 6 enumerated in the issue body and match the 6 capsys-consuming functions in the test file. Function #7 (`test_save_diff_files_handles_mixed_diff_keys`) does not in fact assert against `capsys.readouterr()` (its assertions are all against the file system at lines 257-259); it accepts only `monkeypatch`. The r1 review counted 8 by including this function; ground truth at line 243 shows the signature is `(tmp_path: Path, monkeypatch: pytest.MonkeyPatch)` with no `capsys`. **Net: 6 in-scope, 0 out-of-scope-but-equivalent, 1 false-positive in r1 review** — all 6 in-scope tests are covered by this plan; no scope expansion needed.

---

## Per-call-site KEEP vs. CONVERT tagging (r2 P2 fix)

`yml_utilities.py` contains **7 `print()` calls**. CLI surface analysis: `grep -rn "if __name__" digitalmodel/src/digitalmodel/asset_integrity/` shows no `__main__` guard in `yml_utilities.py` itself or in `WorkingWithYAML` callers within asset_integrity/common/. The `WorkingWithYAML` class is consumed only as a library (engine.py, fatigue_analysis.py, pipe_properties.py, orcaflex_*.py) — none of those invocations call the diagnostic methods (`analyze_yaml_keys`, `compare_yaml_root_keys`, `compare_yaml_files_deepdiff`, `save_diff_files`); they call `ymlInput` only. Therefore all diagnostic `print()` calls in the methods covered by the 6 in-scope tests are safe to CONVERT.

| # | Line | Call site (function) | Message | Currently captured by test? | Decision |
|---|---|---|---|---|---|
| 1 | 43 | `ymlInput` (top-level function, not a method) | "Update Input file could not be loaded successfully. Running program default values" | YES — test #1 (line 110) | **CONVERT → `logger.warning(...)`** (failure-mode diagnostic) |
| 2 | 84 | `WorkingWithYAML.analyze_yaml_keys` | `print(file_name_content.keys())` | YES — test #2 (line 120) | **CONVERT → `logger.info("yaml root keys: %s", file_name_content.keys())`** |
| 3 | 93 | `WorkingWithYAML.compare_yaml_root_keys` | "Yaml files have the same root keys" | YES — test #3 first assertion (line 181) | **CONVERT → `logger.info(...)`** |
| 4 | 95 | `WorkingWithYAML.compare_yaml_root_keys` | f"The root keys for {file_name1}: ..." | YES — test #3 second assertion (line 185) | **CONVERT → `logger.info(...)`** |
| 5 | 96 | `WorkingWithYAML.compare_yaml_root_keys` | f"The root keys for {file_name2}: ..." | YES — companion to call 4 | **CONVERT → `logger.info(...)`** |
| 6 | 108 | `WorkingWithYAML.compare_yaml_files_deepdiff` | "Yaml files are the same" | YES — test #4 (line 200) | **CONVERT → `logger.info(...)`** |
| 7 | 135 | `WorkingWithYAML.save_diff_files` (no-diff path) | "Yaml files are the same" | YES — test #6 (line 239) | **CONVERT → `logger.info(...)`** |
| 8 | 162 | `WorkingWithYAML.save_diff_files` (diff path) | "Yaml files are different. See wwyaml files saved..." | YES — test #5 (line 221-222) | **CONVERT → `logger.info(...)`** |

(Count is 8 because `compare_yaml_root_keys` has two adjacent prints at lines 95-96; r1 review enumerated 7 by collapsing them. Either count is correct depending on whether you count statements or `print(` tokens.)

**KEEP entries:** none. No `print()` in `yml_utilities.py` reaches a CLI/`__main__` surface. All conversions are safe.

**Module-level setup (CONVERT prerequisite):** add at top of `yml_utilities.py`:
```python
import logging
logger = logging.getLogger(__name__)
```

---

## Pseudocode

```text
preflight (see Preflight section above):
  fetch origin; switch main; ff-only pull
  hard-assert: git merge-base --is-ancestor b1346acb HEAD
  confirm citation ignores absent (PR #542 present)
  branch off main as fix/2580-yml-utilities-caplog-xdist

capture-baseline (r2 P2 fix — before/after pass count):
  cd digitalmodel
  PYTHONPATH=src uv run pytest --collect-only -q tests/asset_integrity/test_yml_utilities_additional.py tests/citations/ | tail -1  # baseline collected count (with current collect_ignore)
  PYTHONPATH=src uv run pytest -n auto --tb=no -q tests/citations/ | tail -5   # baseline pass: citations should pass (PR #542)
  record numbers in #2580 closeout evidence

repro current xdist failure (preserved from r1):
  temporarily comment out the yml_utilities_additional collect_ignore line
  PYTHONPATH=src uv run pytest -n auto tests/asset_integrity/test_yml_utilities_additional.py
  record exact failure signature; if capture-related under xdist, proceed; else revise plan

logging/caplog remediation:
  edit yml_utilities.py per KEEP/CONVERT table — add module logger, convert 8 print statements
  edit test_yml_utilities_additional.py:
    add caplog.set_level(logging.INFO, logger="digitalmodel.asset_integrity.common.yml_utilities") in each of the 6 in-scope tests
    replace each capsys.readouterr().out check with: any(<expected substring> in r.message for r in caplog.records)
    drop the capsys parameter from each of the 6 function signatures (caplog replaces it)

collect-ignore cleanup:
  remove ONLY the tests/asset_integrity/test_yml_utilities_additional.py entry from tests/conftest.py
  citation entries are already absent on origin/main — no action there

verification (see Verification subsection):
  PYTHONPATH=src uv run pytest -n auto tests/asset_integrity/test_yml_utilities_additional.py tests/citations/
  capture after-counts; confirm no regression
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/asset_integrity/common/yml_utilities.py` | Add module logger; convert 8 diagnostic `print()` statements (lines 43, 84, 93, 95, 96, 108, 135, 162) to `logger.info`/`logger.warning` per KEEP/CONVERT table |
| Modify | `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` | Replace `capsys` parameter and `capsys.readouterr().out` assertions with `caplog.set_level(...)` and `caplog.records` matching for the 6 named in-scope tests |
| Modify | `digitalmodel/tests/conftest.py` | Remove the single remaining #2574 collect-ignore entry for `tests/asset_integrity/test_yml_utilities_additional.py` |
| Add (proposed in r2) | `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/FIXTURE_PROVENANCE.md` | Pin canonical SHA + vendoring date for the wiki fixture (Fixture Freshness mechanism) |
| Update | `docs/plans/README.md` | Index this r2 plan |

---

## TDD Test List (r2 P1-2 fix — actual function names)

Each row names the actual test function from `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` and documents the specific assertion to convert. All six tests currently use `capsys.readouterr().out` substring matching against captured stdout; r2 converts each to `caplog.records` matching at INFO level on the `digitalmodel.asset_integrity.common.yml_utilities` logger.

| Test name (with line) | Source assertion to convert | Replacement assertion |
|---|---|---|
| `test_ymlinput_ignores_bad_update_file_and_keeps_defaults` (line 99) | line 110: `assert "Update Input file could not be loaded successfully" in capsys.readouterr().out` | `assert any("Update Input file could not be loaded successfully" in r.message for r in caplog.records)` (logger emits at WARNING per call-site #1) |
| `test_analyze_yaml_keys_prints_root_keys` (line 113) | line 120-121: `out = capsys.readouterr().out; assert "alpha" in out and "beta" in out` | `messages = " ".join(r.message for r in caplog.records); assert "alpha" in messages and "beta" in messages` |
| `test_compare_yaml_root_keys_same_and_different` (line 169) | line 181-182: `out1 = capsys.readouterr().out; assert "same root keys" in out1` AND line 185-186: `out2 = capsys.readouterr().out; assert "The root keys" in out2` | After first call, snapshot `caplog.records[:]` then `caplog.clear()`; check first batch contains "same root keys"; after second call, check new records contain "The root keys" |
| `test_compare_yaml_files_deepdiff_emits_same_message_for_identical` (line 189) | line 200-201: `out = capsys.readouterr().out; assert "Yaml files are the same" in out` | `assert any("Yaml files are the same" in r.message for r in caplog.records)` |
| `test_save_diff_files_writes_expected_outputs_and_invokes_save_data` (line 204) | line 221-222: `out = capsys.readouterr().out; assert "Yaml files are different" in out` | `assert any("Yaml files are different" in r.message for r in caplog.records)` (other file-system assertions at 223-227 are unchanged) |
| `test_save_diff_files_reports_same_when_no_diff` (line 230) | line 239: `assert "Yaml files are the same" in capsys.readouterr().out` | `assert any("Yaml files are the same" in r.message for r in caplog.records)` |

Plus one regression check (no-source-edit):
| Check | What it verifies |
|---|---|
| `tests/conftest.py` regression check | The `tests/asset_integrity/test_yml_utilities_additional.py` entry no longer appears in `collect_ignore`; citation entries are also absent (already true on origin/main; this asserts no re-introduction). |

---

## Verification (r2 P2 fix — concrete xdist invocation + before/after counts)

### Local repro

Invocation matches the digitalmodel test contract (`PYTHONPATH=src uv run python -m pytest`) plus `pytest-xdist`:

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel

# Before edits — baseline counts (with collect_ignore active)
PYTHONPATH=src uv run pytest --collect-only -q tests/ | tail -1   # expected: ~925+ collected (issue states 925 post-#2574)
PYTHONPATH=src uv run pytest -n auto --tb=no -q tests/citations/ tests/asset_integrity/test_yml_utilities_additional.py 2>&1 | tail -5
# expected before: tests/citations/ → 14 passed; tests/asset_integrity/test_yml_utilities_additional.py → "no tests ran" (collect-ignored)

# After edits — same invocation should pick up the 6 newly-runnable tests
PYTHONPATH=src uv run pytest -n auto tests/asset_integrity/test_yml_utilities_additional.py tests/citations/ 2>&1 | tail -5
# expected after: tests/citations/ → 14 passed; tests/asset_integrity/test_yml_utilities_additional.py → all collected tests passed under xdist (~22 tests including the 6 fixed ones)

# Whole-suite collect count must not regress
PYTHONPATH=src uv run pytest --collect-only -q tests/ | tail -1   # expected: baseline + (number of yml_utilities_additional tests previously ignored)
```

### CI invocation parity

The digitalmodel `quality-gates.yml` workflow at `.github/workflows/quality-gates.yml` invokes `python -m digitalmodel.workflows.automation.quality_gates_cli check --json`, which delegates to pytest under the digitalmodel quality-gates harness. Local repro with `pytest -n auto` is the closest standalone analogue. Verify after-PR CI run shows no new failures and the `tests/asset_integrity/test_yml_utilities_additional.py` line is no longer "collect ignored".

### Pass-count capture

Record three numbers in #2580 closeout comment:
1. **Before total collected:** `pytest --collect-only -q tests/ | tail -1` (with current ignore active)
2. **After total collected:** same command (after ignore removed) — must increase by the count of tests in `test_yml_utilities_additional.py` (verified ~22 from file enumeration)
3. **After pass/fail:** `pytest -n auto --tb=no -q tests/ | tail -5` — expected: prior baseline pass count + new yml-utilities pass count, zero new failures.

---

## Fixture Freshness (r2 P2 fix — vendored wiki staleness)

PR #542 vendored `tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` from canonical `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`. With no freshness mechanism, the vendored copy will silently drift. r2 proposes (out-of-scope-for-#2580 closeout but **a follow-up issue must be filed**, not silently dropped):

### Mechanism A — provenance pin (lightweight, ship with #2580 closeout)

Create `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/FIXTURE_PROVENANCE.md` containing:
- Canonical workspace-hub path: `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`
- Canonical SHA at vendoring time: (capture via `git -C /mnt/local-analysis/workspace-hub log -1 --format=%H -- knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` during implementation)
- Vendoring date: 2026-05-02 (PR #542 merge date)
- Re-vendor cadence: monthly review; next review 2026-06-02.

### Mechanism B — CI staleness check (proposed follow-up issue)

A pre-commit hook or CI step that, **when the workspace-hub canonical file is reachable**, hashes both files and warns (not errors — workspace-hub may not be checked out in digitalmodel CI) if they diverge. Proposed for follow-up after #2580 closes; this plan does NOT block on it.

### Decision

Ship Mechanism A as part of this plan's implementation; file Mechanism B as a follow-up issue at closeout. Cadence: monthly calendar reminder in `.claude/state/session-signals/` (out of scope for the file edits but recorded in plan acceptance).

---

## Acceptance Criteria

- [ ] **Preflight passed:** `git merge-base --is-ancestor b1346acb HEAD` returned 0 in the digitalmodel implementation branch; the implementation branch is rooted at `origin/main`, not at the stale `fix/triage-punch-list-2026-05-02`.
- [ ] PR #542 (or its merge commit `b1346acb`) is present at base; citations tests pass without workspace-hub `knowledge/wikis/` checkout and are not reimplemented by this plan. The dependency fixture path is `tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`.
- [ ] The actual yml failure under xdist is reproduced and recorded before the refactor; if the root cause is not captured stdout under xdist, the implementation follows the observed failure rather than forcing `caplog`.
- [ ] All **six** named `test_yml_utilities_additional.py` tests (functions enumerated in TDD section) pass under `PYTHONPATH=src uv run pytest -n auto`. The seventh function (`test_save_diff_files_handles_mixed_diff_keys`) is unchanged because it does not consume `capsys`.
- [ ] All **8** `print()` call sites in `yml_utilities.py` (lines 43, 84, 93, 95, 96, 108, 135, 162) are converted to `logger.info`/`logger.warning` per KEEP/CONVERT table. No `print()` calls remain. No callers from `engine.py`, `fatigue_analysis.py`, `pipe_properties.py`, or orcaflex/* depend on stdout (verified by `grep -rn "analyze_yaml_keys\|compare_yaml_root_keys\|compare_yaml_files_deepdiff\|save_diff_files" digitalmodel/src/` returning only the source itself).
- [ ] Temporary #2574 collect-ignore entry for `tests/asset_integrity/test_yml_utilities_additional.py` is removed from `digitalmodel/tests/conftest.py`; citation ignore cleanup remains credited to PR #542.
- [ ] Targeted command passes from digitalmodel root: `PYTHONPATH=src uv run pytest -n auto tests/citations/ tests/asset_integrity/test_yml_utilities_additional.py`.
- [ ] Before/after pass counts captured and posted to #2580 closeout per Verification subsection.
- [ ] `FIXTURE_PROVENANCE.md` created with canonical SHA, vendoring date, and review cadence (Mechanism A); follow-up issue filed for Mechanism B.
- [ ] No implementation starts until #2580 has fresh adversarial review evidence (post-r2) and user approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude Opus 4.7 (r1, 2026-05-02) | **MAJOR** | `docs/reviews/2026-05-02-issue-2580-r1-adversarial.md` — 3 P1: stale base branch, stub TDD names, 6-vs-8 capsys count. 5 P2: print/CLI mock-vs-live risk, no xdist invocation, no pass-count capture, fixture freshness, past-tense drift. r2 patches all P1 + the four addressable P2; one P2 (Mechanism B CI hook) is filed as follow-up. |
| Codex (rerun 2026-05-02) | MAJOR | `scripts/review/results/2026-05-02-plan-2580-codex.md` — fixture-path mismatch, unproven xdist root cause, grouped TDD rows, branch-state ambiguity. r2 patches all of these via Preflight, baseline-capture, and named TDD rows. |
| Claude (older same-day) | UNAVAILABLE | `scripts/review/results/2026-05-02-plan-2580-claude.md` — provider timed out; superseded by r1 adversarial review above. |
| Gemini | pending / unavailable artifact if capacity fails | `scripts/review/results/2026-05-02-plan-2580-gemini.md` or rerun prompt artifact |

**Overall result:** r1 MAJOR addressed in this r2 revision. **Status remains `status:plan-review`** — fresh adversarial review required against r2 before any approval transition. Per workspace-hub feedback rule, agent will not self-approve and will not pre-authorize downstream agents.

---

## Risks and Open Questions

- **Risk:** The implementation branch may inadvertently be cut from the stale local working-tree branch instead of `origin/main`. **Mitigation:** mandatory Preflight section above, with `git merge-base --is-ancestor b1346acb HEAD` as a fail-closed gate.
- **Risk:** Vendoring a wiki fixture can drift from canonical workspace-hub content. **Mitigation:** `FIXTURE_PROVENANCE.md` with SHA pin and monthly review; CI staleness check filed as follow-up issue.
- **Risk:** Some yml utility output may intentionally be CLI stdout rather than diagnostics. **Mitigation:** the per-call-site KEEP/CONVERT table verifies (via `grep -rn` of the production callers) that none of the 8 `print()` sites are reached from a `__main__` surface or click command. All 8 are safe to convert. If a future caller adds a CLI surface, it must read from logger handlers, not stdout, by contract.
- **Risk:** `pytest-xdist` may have additional capture quirks beyond capsys. **Mitigation:** Verification subsection runs the full xdist invocation locally; any new failure mode is recorded and either patched or returned as a plan revision rather than silently force-merged.
- **Open:** Exact xdist failure signature must be captured during implementation (one of two outcomes: capsys-under-xdist as #2574 stated, OR a different root cause). The plan's caplog conversion is pre-justified as both more robust *and* xdist-safe regardless of which root cause obtains.

---

## Complexity: T2

Multiple test files (1 source + 1 test), one production utility module, dependency/branch-state verification for PR #542 (now merged), per-call-site KEEP/CONVERT analysis, collect-ignore cleanup, fixture-provenance ship-along, and Verification with before/after counts. TDD and plan approval gate apply. r2 explicitly does not transition labels and does not recommend `status:plan-approved` — fresh adversarial review on r2 is the next gate.
