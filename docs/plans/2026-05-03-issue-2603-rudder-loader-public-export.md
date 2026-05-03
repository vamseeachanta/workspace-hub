# Plan for #2603: re-export `load_packaged_rudder_stock_torque_yaml` from `naval_architecture/__init__.py`

> **Status:** plan-review
> **Complexity:** T1
> **Date:** 2026-05-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2603
> **Review artifacts:** scripts/review/results/2026-05-03-plan-2603-claude.md (single-author r1, no cross-provider review per scope)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py:228` — `load_packaged_rudder_stock_torque_yaml() -> RudderStockTorqueInput` exists.
- Found: same module line 336 — `run_rudder_stock_torque_sweep(config: RudderStockTorqueInput) -> dict[str, Any]` exists.
- Gap: `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` does NOT import from the `rudder_stock_torque` module at all. **Both** `load_packaged_rudder_stock_torque_yaml` AND `run_rudder_stock_torque_sweep` are missing from public exports, not just the loader (the original report under-counted).
- Found: yaw side at `__init__.py:53-58` exports `load_packaged_typical_ship_yaml`, `load_yaw_moment_input`, `rudder_yaw_moment`, `run_yaw_moment_sweep`, `write_yaw_moment_results` — confirms the established export pattern (loader + runner + writer + helpers).

### Standards
Not applicable — this is a Python public-API hygiene fix, not a standards-derived calculation.

### LLM Wiki pages consulted
No relevant wiki pages — naval-arch maneuvering wiki entries describe physics, not Python API surfaces.

### Documents consulted
- `docs/reports/2566-naval-arch-ci-validation.md` — origin of this follow-up; reports the failing test verbatim and the loader's missing-export evidence.
- Failing test: `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py:396-421` — `test_public_import_surface_outside_pytest_path_injection` runs `uv run --no-sync python -c "from digitalmodel.naval_architecture import load_packaged_rudder_stock_torque_yaml, run_rudder_stock_torque_sweep; ..."` in a subprocess that cannot rely on pytest's `sys.path` injection.
- Related issue [#2604](https://github.com/vamseeachanta/workspace-hub/issues/2604) — different test failure (test-string match), unrelated scope.

### Gaps identified
- `from digitalmodel.naval_architecture.rudder_stock_torque import (...)` block missing from `__init__.py`.
- Two names missing from `__all__`: `load_packaged_rudder_stock_torque_yaml`, `run_rudder_stock_torque_sweep`.
- Optional gap: `write_rudder_stock_torque_results`, `write_rudder_stock_torque_charts`, `build_rudder_stock_torque_heatmap_grid` exist in the module but are not test-required. **Decision (revised per r1 P3-1):** strict YAGNI — export ONLY the two test-required names. Yaw side parity (`write_yaw_moment_results`) is symmetry, but adding it without a test creates avoidable public-API surface. File a separate "rudder writer parity" follow-up if external consumers need it.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view`):
- `#2603` — OPEN — `fix(digitalmodel): re-export load_packaged_rudder_stock_torque_yaml from naval_architecture/__init__.py`
- `#2566` — CLOSED — parent validation report referencing this loader gap

**File existence** (`ls -la` 2026-05-03):
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` (~110 lines)
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py` (~625 lines)
- EXISTS: `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py`

**Line excerpts** (`sed -n 396,421p test_rudder_stock_torque_sweep.py`):
```
def test_public_import_surface_outside_pytest_path_injection():
    repo_root = Path(__file__).parents[2]
    result = subprocess.run(
        [
            "uv", "run", "--no-sync", "--with", "pyyaml", "python", "-c",
            (
                "from digitalmodel.naval_architecture import "
                "load_packaged_rudder_stock_torque_yaml, "
                "run_rudder_stock_torque_sweep; "
                "cfg=load_packaged_rudder_stock_torque_yaml(); "
                "assert len(run_rudder_stock_torque_sweep(cfg)['rows']) == 35"
            ),
        ],
        cwd=repo_root,
        env={**os.environ, "PYTHONPATH": "src"},
        ...
    )
    assert result.returncode == 0, result.stdout + result.stderr
```

**Gap proofs** (`grep -c rudder_stock_torque digitalmodel/src/digitalmodel/naval_architecture/__init__.py`):
- Returns `0` → confirms the rudder_stock_torque module has zero references in __init__.py.

<!-- Verification: 4 distinct sources (issue body, validation report, failing test, current __init__.py) — exceeds minimum 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2603-rudder-loader-public-export.md` |
| Tests (existing — no new) | `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py` |
| Implementation (modify) | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` |
| Plan review — Claude r1 (MINOR) | `scripts/review/results/2026-05-03-plan-2603-claude.md` |
| Wiki updates | none |
| Docs updates | `docs/plans/README.md` index entry (if maintained — verify on commit) |

---

## Deliverable

After this issue is done: `from digitalmodel.naval_architecture import load_packaged_rudder_stock_torque_yaml, run_rudder_stock_torque_sweep` succeeds in a subprocess that does not rely on pytest's `sys.path` injection, and `test_public_import_surface_outside_pytest_path_injection` passes.

---

## Pseudocode

T1 — trivial. See *Files to Change* and *Implementation diff* below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Add import block from `rudder_stock_torque` module + extend `__all__` |

No test changes (the test is already in place and failing — that's the whole point of the gate).

### Implementation diff (precise)

Insert this import block alphabetically ordered against existing blocks. Anchor: after line 50 (`)` closing the `b1528_sirocco_time_trace` block), before line 51 (`from digitalmodel.naval_architecture.yaw_moment import (`).

Per r1 P3-1: writer export removed from this plan (strict YAGNI — only test-required names). File `write_rudder_stock_torque_results` parity as a separate follow-up if external consumers need it.

```python
from digitalmodel.naval_architecture.rudder_stock_torque import (
    load_packaged_rudder_stock_torque_yaml,
    run_rudder_stock_torque_sweep,
)
```

Add two names to `__all__` using **anchor-based positioning** (existing list uses ASCII sort: PascalCase before lowercase):
- `"load_packaged_rudder_stock_torque_yaml"` — insert immediately after `"load_packaged_typical_ship_yaml"` and before `"load_yaw_moment_input"`
- `"run_rudder_stock_torque_sweep"` — insert immediately after `"run_b1528_time_trace_report"` and before `"run_yaw_moment_sweep"`

---

## TDD Test List

Test already exists. No new test code.

| Test name | What it verifies | Status before plan | Status after plan |
|---|---|---|---|
| `test_public_import_surface_outside_pytest_path_injection` (test_rudder_stock_torque_sweep.py:396) | `from digitalmodel.naval_architecture import load_packaged_rudder_stock_torque_yaml, run_rudder_stock_torque_sweep` succeeds in subprocess + sweep yields 35 rows | FAIL (`ImportError`) | PASS |
| All other tests in `test_rudder_stock_torque_sweep.py` (18 currently passing) | Regression — internal/test-path imports still work | PASS | PASS (unchanged) |

---

## Acceptance Criteria

- [ ] `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` contains the new import block from `rudder_stock_torque`
- [ ] `__all__` contains `load_packaged_rudder_stock_torque_yaml` and `run_rudder_stock_torque_sweep`
- [ ] `cd digitalmodel && uv run pytest tests/naval_architecture/test_rudder_stock_torque_sweep.py::test_public_import_surface_outside_pytest_path_injection -v` PASSES
- [ ] All tests in `test_rudder_stock_torque_sweep.py` pass (was 1 failure pre-plan; implementer records final pass-count in closeout comment)
- [ ] No regressions in `test_yaw_moment_sweep.py` (21 tests still pass)

---

## Risks

- **Yaw side may have a latent equivalent gap.** No `test_public_import_surface_*` exists on the yaw side. The yaw __init__.py imports `load_packaged_typical_ship_yaml` (a generic name shared across modules) — verify it's actually defined in `yaw_moment.py` and not shadowed. **Out of scope for this plan**; flag as separate follow-up if discovered.
- **Naming asymmetry:** yaw uses generic `load_packaged_typical_ship_yaml`, rudder uses module-specific `load_packaged_rudder_stock_torque_yaml`. The plan does NOT propose renaming — that would be a breaking API change. Document the asymmetry as a known issue if useful.
- **Plan-vs-live-state risk:** the digitalmodel local checkout was on `fix/triage-punch-list-2026-05-02` (per #2566 report and #2608) — verify `__init__.py` line numbers cited above against the current checkout HEAD before applying the diff.

---

## Out of Scope

- Renaming `load_packaged_rudder_stock_torque_yaml` to align with yaw's `load_packaged_typical_ship_yaml` naming
- Adding the equivalent `test_public_import_surface_*` for yaw — file as separate follow-up
- Exporting `write_rudder_stock_torque_charts`, `build_rudder_stock_torque_heatmap_grid` (test does not require; yaw side has no chart-helper export precedent)
- Fixing #2604 (test-string match) or #2608 (branch hygiene) — separate follow-ups
