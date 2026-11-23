# Plan for #3841: fix(digitalmodel/tests): OrcaFlex statics tests lack the solver marker

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-11-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3841
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-11-18-plan-3841-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py` — file has `pytest.mark.skipif(not ORCAFLEX_AVAILABLE)` at lines 35–36 and `pytest.mark.timeout(1800)` at line 41, but NO `@pytest.mark.solver`. Eight `CalculateStatics()` calls exist at lines 296, 402, 472, 485, 506, 675, 720, 744 — all inside session-scoped fixtures.
- Found: `digitalmodel/pytest.ini:45` — `solver: Tests requiring OrcFxAPI on licensed machine (deselect with '-m "not solver"')` — marker is registered; mechanism exists but is unused in this file.
- Gap: No `@pytest.mark.solver` applied to any test class or method in `test_modular_vs_monolithic.py`.
- Gap: Docstring contradiction: line 9 and line 684 both state CalculateStatics is too expensive for in-test use, while the same file contains 8 actual calls.
- Gap: No prior audit of `digitalmodel/tests/` for other files with the same shape (CalculateStatics gated only by `ORCAFLEX_AVAILABLE`).

### Standards

| Standard | Status | Source |
|---|---|---|
| Not applicable (test harness issue) | N/A | — |

### LLM Wiki pages consulted

- No relevant wiki pages for this test-marking issue.

### Documents consulted

- Issue [#3841](https://github.com/vamseeachanta/workspace-hub/issues/3841) — full problem statement, 8 call-site line numbers, observed >20-min licence seat hold.
- Issue [#3838](https://github.com/vamseeachanta/workspace-hub/issues/3838) — OrcaFlex counting-contract (dependency; not blocking this fix).
- Issue [#3839](https://github.com/vamseeachanta/workspace-hub/issues/3839) — OrcaFlex integrity work (dependency; not blocking this fix).
- `docs/plans/` — no prior plan for #3841 (confirmed: `ls docs/plans/*3841*` returns empty).

### Gaps identified

- `@pytest.mark.solver` absent from all test classes in `test_modular_vs_monolithic.py` that transitively invoke CalculateStatics through their fixtures.
- Docstrings at lines 9 and 684 contradict the actual code; they describe a load-from-.sim pattern that is not implemented.
- Broader audit of `digitalmodel/tests/` for similar unmarked statics calls: out of scope for this plan (item 3 from issue) but filed as a follow-on.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-11-18T07:30Z via `gh issue view`):
- `#3841` — OPEN — fix(digitalmodel/tests): OrcaFlex statics tests lack the solver marker (0 PRs confirmed)
- `#3839` — OPEN (dependency; not blocking this plan)

**File existence** (verified 2026-11-18):
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py`
- EXISTS: `digitalmodel/pytest.ini`
- MISSING (new — this plan creates): no new files; single-file change only

**Line excerpts** (`pytest.ini:43-46`):
```
[pytest]
...
markers =
    solver: Tests requiring OrcFxAPI on licensed machine (deselect with '-m "not solver"')
```

**CalculateStatics call sites** (`grep -n "CalculateStatics" test_modular_vs_monolithic.py`):
```
296:        model.CalculateStatics()
402:    model.CalculateStatics()
472:    model.CalculateStatics()
485:    model.CalculateStatics()
506:    model.CalculateStatics()
675:    model.CalculateStatics()
720:    model.CalculateStatics()
744:    model.CalculateStatics()
```
All 8 are inside `@pytest.fixture(scope="session")` bodies, not in test methods directly.

**Solver marker absence** (`grep -n "@pytest.mark.solver" test_modular_vs_monolithic.py`):
```
(empty — no matches)
```

**Test classes present** (`grep -n "^class Test" test_modular_vs_monolithic.py`):
```
308: class TestQuickQA
406: class TestInstantRiser
510: class TestLazyWaveRiser
558: class TestFenderModel
589: class TestPullInAnalysis
765: class TestSmokeGeneration
790: class TestModularStatics
810: class TestStaticResultExtraction
850: class TestModularVsMonolithicComparison
975: class TestCrossValidation30in
1071: class TestAlongLengthNoLoadComparison
```

**Gap proof — no plan for #3841 prior:**
```
$ ls docs/plans/*3841* 2>&1
ls: cannot access 'docs/plans/*3841*': No such file or directory
```

**Reproduction proof:**
```
$ cd /mnt/local-analysis/digitalmodel && uv run pytest tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py -m "not solver" --collect-only 2>&1 | grep "test session\|selected\|deselected" | head -5
<test session starts>
collected 68 items
68 selected, 0 deselected  ← confirms NO tests are deselected by -m "not solver" before this fix
```

- Reproduced at: 2026-11-18T07:30Z (session that generated issue #3841)
- Failure mode: 0 tests deselected by `-m "not solver"`, matching issue claim that the marker is absent and cannot deselect solver tests. YES — matches.

<!-- Verification: sources = issue #3841 (1) + pytest.ini:45 (2) + test file grep (3) + git ls-files/0 PRs (4) → 4 sources; minimum 3 met -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-11-18-issue-3841-orcaflex-solver-marker.md |
| Implementation | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py` |
| Plan review — Claude | scripts/review/results/2026-11-18-plan-3841-claude.md |

---

## Deliverable

`@pytest.mark.solver` added to every test class in `test_modular_vs_monolithic.py` that uses a statics fixture, so `-m "not solver"` deselects them and no licence seat is claimed on a plain `pytest` run; docstring contradictions at lines 9 and 684 reconciled.

---

## Pseudocode

trivial — see files to change

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py` | add `@pytest.mark.solver` to test classes backed by statics fixtures; reconcile docstrings at lines 9 and 684 |
| Update | docs/plans/README.md | add this plan to index |

**Marker placement strategy:** The 8 `CalculateStatics()` calls are in session-scoped fixtures. Marking the test CLASS (not individual methods) with `@pytest.mark.solver` is the correct placement: when the class is deselected by `-m "not solver"`, its session fixtures never run and the licence seat is never claimed.

Classes to mark (those whose session fixtures transitively call CalculateStatics):
- `TestQuickQA` (fixtures `qa_output_dir`, `qa_model` → line 296, 402)
- `TestInstantRiser` (riser fixture → lines 472, 485, 506)
- `TestLazyWaveRiser` and downstream statics classes (fixtures → lines 675, 720, 744)
- Any remaining class whose fixture chain includes a CalculateStatics call — to be confirmed by tracing `fixture(scope="session")` → `CalculateStatics` path at implementation time

Docstring reconciliation: update line 9 and line 684 to remove the false claim that calls are avoided; replace with accurate description of the guard pattern used (`pytest.mark.solver`).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_solver_marker_deselects_statics_classes | `-m "not solver"` deselects all test classes with CalculateStatics fixtures | `pytest --collect-only -m "not solver"` on the file | 0 items collected from statics-backed classes |
| test_solver_marker_selects_statics_classes | `-m solver` selects exactly the marked classes | `pytest --collect-only -m solver` on the file | ≥1 item collected per marked class |
| test_non_statics_classes_not_marked | classes with no CalculateStatics fixture (e.g., TestSmokeGeneration) are NOT marked solver | inspect markers on collected items | TestSmokeGeneration not in `solver` marker set |

The TDD tests are collection-only (`--collect-only`); they assert marker correctness without running actual solves.

---

## Acceptance Criteria

- [ ] `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py --collect-only -m "not solver"` collects 0 items from the statics-backed test classes (confirmed deselection).
- [ ] `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py --collect-only -m solver` collects ≥1 item from each previously-unmarked class that has CalculateStatics fixtures.
- [ ] No regression: non-statics classes (e.g., TestSmokeGeneration) remain collectable without the solver flag.
- [ ] Docstrings at lines 9 and 684 no longer state "too expensive — not called" while the same file calls CalculateStatics.
- [ ] All TDD collection tests pass.
- [ ] Issue #3841 commented with plan link.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |

**Overall result:** pending

---

## Retention

**Basis:** [Boundary policy, Section 8.1](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule)
(#2209): plan files are retained for the issue lifetime plus 30 days.

```json
{
  "issue": "#3841",
  "artifact_class": "plan",
  "issue_state": "open",
  "closed_on": null,
  "retention_days": 30,
  "retention_basis": "../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule",
  "retention_status": "advisory",
  "disposition": "archive"
}
```

---

## Risks and Open Questions

- **Risk:** Some statics classes share fixtures with non-statics classes. Marking a class `solver` deselects ALL its tests, including any that do not solve. Review fixture usage per class before marking to avoid false deselection.
- **Risk:** `scope="session"` fixtures are shared across classes. If a fixture is used by both a marked and an unmarked class, deselection of the marked class does NOT prevent the fixture from running for the unmarked class. Confirm that no unmarked class depends on the same statics fixture.
- **Open:** Item 2 from issue — "replace calls with pre-computed .sim load" — is an optional enhancement. This plan implements item 1 only (marker addition) and partial item 2 (docstring correction). The architectural question of whether the statics should be pre-computed is deferred to a follow-on.
- **Open:** Item 3 (audit `digitalmodel/tests/` for other files with same shape) is out of scope here; to be filed as a follow-on issue after this fix merges.

---

## Complexity: T1

**T1** — single file (`test_modular_vs_monolithic.py`); no new module, no cross-file refactor; change is additive (decorator additions + docstring edits only).
