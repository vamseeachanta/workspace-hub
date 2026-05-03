# Plan for #2605: chore(digitalmodel): ruff cleanup for naval_architecture/test_vessel_fleet_adapter.py (13 F401)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2605
> **Review artifacts:** /tmp/plan-issue-2605/review.md (single-author adversarial; cross-AI review out-of-scope for this T1 chore)

---

## Resource Intelligence Summary

### Existing repo code
- File: `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` — 868 lines, exists.
- Sibling tests in `digitalmodel/tests/naval_architecture/` use the same `from ... import (register_fleet_vessels, get_ship,)` pattern legitimately at lines 147-150, 179-182, 198-201, 214-217, 239-242, 340-343, 419-422, 738-741, 769-772, 798-803.
- `tests/conftest.py` exists at the digitalmodel repo root (no `naval_architecture/conftest.py`); no autouse fixture references `get_ship`.
- No `__all__` in the test file (`grep -n __all__ tests/naval_architecture/test_vessel_fleet_adapter.py` → empty).
- No existing `# noqa: F401` markers (`grep -n noqa ...` → empty).

### Standards
Not applicable — pure lint cleanup, no engineering standards involved.

### LLM Wiki pages consulted
No relevant wiki pages — this is a tooling/lint chore, not a domain-knowledge change.

### Documents consulted
- Issue #2605 body — claims 13 F401 in `test_vessel_fleet_adapter.py`. **Live ruff disagrees** (see Evidence): the file has only 1 F401; the other 12 are in sibling files in the same directory.
- `.claude/rules/coding-style.md` — "Prefer targeted single-site edits over bulk find-replace — verify each change site." Aligns with one-line fix.
- Recent commits on the file (`git log --oneline -5`): `84ca3085` (PR #2062 added drilling rig fleet adapter, the import block at L198-201 dates from this PR).

### Gaps identified
- **Issue body is wrong:** the title says "13 F401" but only 1 F401 is in the named file. The plan must decide: fix only the file named in the issue (1 line), or expand scope to all 13 in the directory.
- Recommended scope: stay strictly within the file named in the issue title (test_vessel_fleet_adapter.py). The other 12 F401 belong to sibling test files and should be tracked under separate issues to keep PR scope honest and reviewable.

### Evidence (embedded verification)

**Live ruff scan** (verified 2026-05-02 via `cd digitalmodel && .venv/bin/ruff check src/digitalmodel/naval_architecture/ tests/naval_architecture/ --output-format=concise`):
```
src/digitalmodel/naval_architecture/gyradius.py:18:20: F401 [*] `typing.Union` imported but unused
tests/naval_architecture/test_damage_stability.py:5:8: F401 [*] `math` imported but unused
tests/naval_architecture/test_damage_stability.py:8:8: F401 [*] `yaml` imported but unused
tests/naval_architecture/test_floating_platform_stability.py:10:5: F401 [*] `digitalmodel.naval_architecture.floating_platform_stability.StabilityCriteria` imported but unused
tests/naval_architecture/test_floating_platform_stability_extended.py:24:5: F401 [*] `digitalmodel.naval_architecture.floating_platform_stability.StabilityCriteria` imported but unused
tests/naval_architecture/test_gyradius.py:5:8: F401 [*] `math` imported but unused
tests/naval_architecture/test_gyradius_extended.py:23:5: F401 [*] `digitalmodel.naval_architecture.gyradius.GyradiusResult` imported but unused
tests/naval_architecture/test_hull_form.py:5:8: F401 [*] `math` imported but unused
tests/naval_architecture/test_knowledge.py:9:8: F401 [*] `pytest` imported but unused
tests/naval_architecture/test_maneuverability.py:12:8: F401 [*] `math` imported but unused
tests/naval_architecture/test_seakeeping.py:5:8: F401 [*] `math` imported but unused
tests/naval_architecture/test_ship_dimensions_template.py:8:8: F401 [*] `pytest` imported but unused
tests/naval_architecture/test_vessel_fleet_adapter.py:200:13: F401 [*] `digitalmodel.naval_architecture.ship_data.get_ship` imported but unused
Found 13 errors. [*] 13 fixable with the `--fix` option.
```
Of these 13, **only 1** is in `test_vessel_fleet_adapter.py`. The issue title is a directory-level count miscredited to a single file.

**The single F401 site** (`sed -n 197,206p tests/naval_architecture/test_vessel_fleet_adapter.py` equivalent — read confirmed):
```python
    def test_overwrite_when_requested(self):
        from digitalmodel.naval_architecture.ship_data import (
            register_fleet_vessels,
            get_ship,
        )

        register_fleet_vessels([THIALF_RECORD])
        added, skipped = register_fleet_vessels([THIALF_RECORD], overwrite=True)
        assert added == 1
        assert skipped == 0
```
Inside this method body, `get_ship` is never called — only `register_fleet_vessels` is used (lines 203, 204). The same `(register_fleet_vessels, get_ship)` import pattern is legitimately used in 8 other test methods in the same file where both names get called. So this is a genuine unused import, isolated to one method.

**`get_ship` usage census in this file** (`grep -n "get_ship" tests/naval_architecture/test_vessel_fleet_adapter.py` — 27 hits): all but the L200 site call `get_ship(...)` later in the same method body. L200 is the only orphan.

**No re-export / side-effect / fixture tie** (verified via greps):
- `grep -n "__all__\|noqa" tests/naval_architecture/test_vessel_fleet_adapter.py` → empty
- `grep -n "fixture\|conftest" tests/naval_architecture/test_vessel_fleet_adapter.py` → only `pytest.fixture` decorators on L661 and L826, neither references `get_ship`.
- No `naval_architecture/conftest.py` (`ls tests/naval_architecture/conftest.py` → no such file).
- The `digitalmodel.naval_architecture.ship_data` module has no module-level side effect that requires importing `get_ship` to run — `register_fleet_vessels` and `get_ship` are sibling names from the same already-loaded module.

**Ruff `--fix --diff` preview** (verified safe):
```
@@ -197,7 +197,6 @@
     def test_overwrite_when_requested(self):
         from digitalmodel.naval_architecture.ship_data import (
             register_fleet_vessels,
-            get_ship,
         )
```
Single-line removal; `register_fleet_vessels` (used) stays. Would fix 1 error.

**Source count:** 4 (issue body, live ruff scan, file read, sibling-import grep) — meets ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | /tmp/plan-issue-2605/plan.md (final commit path: docs/plans/2026-05-02-issue-2605-ruff-cleanup-test-vessel-fleet-adapter.md) |
| Code change | digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py |
| Plan review (single-author adversarial) | /tmp/plan-issue-2605/review.md |

---

## Deliverable

`digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` will pass `ruff check` (zero F401 in this file), with all 30+ existing pytest cases still passing — by removing one unused `get_ship` import from `test_overwrite_when_requested` (line 200).

---

## Pseudocode

Trivial — see Files to Change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | Remove unused `get_ship` import at line 200 inside `test_overwrite_when_requested`. Keep `register_fleet_vessels` (line 199 — used at L203, L204). |

**Out of scope for this issue (will be split into follow-up issues):** the other 12 F401 in `tests/naval_architecture/` and `src/digitalmodel/naval_architecture/gyradius.py:18`. Issue #2605's title scopes the work to `test_vessel_fleet_adapter.py`; widening here would change PR scope without reviewer signoff.

---

## TDD Test List

This is a lint cleanup, not new functionality, so the TDD here is regression-protection of the existing 30+ tests.

| Test phase | Command | Expected |
|---|---|---|
| Pre-fix baseline | `cd digitalmodel && .venv/bin/python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -q` | All currently-passing tests pass (establish green baseline) |
| Pre-fix lint | `cd digitalmodel && .venv/bin/ruff check tests/naval_architecture/test_vessel_fleet_adapter.py` | 1 F401 reported at L200 |
| Apply fix | `cd digitalmodel && .venv/bin/ruff check tests/naval_architecture/test_vessel_fleet_adapter.py --fix` | "Fixed 1 error" |
| Post-fix lint | `cd digitalmodel && .venv/bin/ruff check tests/naval_architecture/test_vessel_fleet_adapter.py` | "All checks passed" |
| Post-fix tests | `cd digitalmodel && .venv/bin/python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -q` | Same pass count as pre-fix baseline (no regression) |
| Specifically | `cd digitalmodel && .venv/bin/python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py::TestRegisterFleetVessels::test_overwrite_when_requested -v` | PASSED (this is the test that lost the import) |
| Random-order check | `cd digitalmodel && .venv/bin/python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -q -p randomly` | Same pass count (defends against pytest-randomly ordering effect, which the file already mitigates with `overwrite=True`) |

---

## Acceptance Criteria

- [ ] `cd digitalmodel && .venv/bin/ruff check tests/naval_architecture/test_vessel_fleet_adapter.py` exits 0 with "All checks passed"
- [ ] `cd digitalmodel && .venv/bin/python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -q` passes with the same case count as pre-fix
- [ ] `test_overwrite_when_requested` specifically still PASSES
- [ ] Diff is exactly 1 line removed; no other lines mutated
- [ ] No new `# noqa` markers introduced
- [ ] Issue title's "13 F401" mismatch is acknowledged in the PR body and follow-up issue(s) are filed for the remaining 12

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (single-author) | MINOR | Issue title scope mismatch (13 vs. 1); pseudo-risk that ruff's nested-import-block edit could mangle parens — verified safe via `--diff`. |

**Overall result:** PASS — proceed to user approval; cross-AI review unnecessary for a 1-line lint fix.

---

## Risks and Open Questions

- **Risk:** Ruff's auto-fix on a parenthesised multi-import block (`from X import (a, b,)`) leaves a single-name parenthesised block (`from X import (a,)`). This is valid Python and matches what `--diff` previewed. Verified.
- **Risk:** Pytest-randomly ordering — the surrounding tests in `TestRegisterFleetVessels` already use `overwrite=True` defensively where ordering matters; removing `get_ship` does not change runtime behaviour.
- **Risk:** A future test maintainer might re-introduce a `get_ship(...)` assertion in `test_overwrite_when_requested` and forget the import. **Mitigation:** none required — they will hit a `NameError` immediately on first run, which is the system working correctly.
- **Open Q1:** Should the plan expand scope to all 13 F401 (including the 12 outside the named file)? **Recommendation:** No — keep PR scope to the named file; file follow-up issues for the remaining 12. Defer to user.
- **Open Q2:** Is `test_overwrite_when_requested` *missing* a `get_ship` assertion that the author intended to write (i.e., is the unused import a symptom of an incomplete test rather than a stale import)? Looking at L197-206: the test asserts only the (added, skipped) counts; it does not verify post-overwrite data. A stronger version would assert `get_ship("THIALF")["loa_ft"] == THIALF_RECORD["LOA_M"] / 0.3048` to prove the overwrite actually mutated state. **Recommendation:** Note in PR body; do NOT expand this PR's scope, but file a separate follow-up issue to harden the assertion. Defer to user.

---

## Complexity: T1

**T1** — single-line edit, auto-fixable by tooling, no new modules, no API change, no docs/wiki update needed. Ruff's `--diff` already proves the change is safe.
