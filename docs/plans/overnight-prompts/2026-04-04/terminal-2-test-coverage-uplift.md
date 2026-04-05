# Terminal 2: #1824 — Uplift digitalmodel test coverage 2.95% -> 20%
# Agent: Codex (bounded implementation, skeleton test writing)
# Estimated: 4-6 hours
# Repo: digitalmodel (branch feat/1824-test-uplift, DO NOT commit to main)
# Branch strategy avoids git contention with Terminal 1 on main

We are in /mnt/local-analysis/workspace-hub/digitalmodel.
Execute these tasks in order. Use `uv run` for all Python. Do NOT ask the user any questions.

## SETUP (do this first)

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
git checkout main
git pull origin main
git checkout -b feat/1824-test-uplift
```

All commits go to this branch. Push periodically:
```bash
git push origin feat/1824-test-uplift
```

## Context

digitalmodel has 11,565 tests collected but only 2.95% coverage. The repo has:
- 206 structural module files (739 functions) — highest leverage
- Hydrodynamics modules (825 functions) — second highest
- 954 test files already exist, but many packages have zero or minimal tests
- geotechnical/ tests are handled by Terminal 1 — DO NOT touch

Source layout: src/digitalmodel/<domain>/<module>.py
Test layout: tests/<domain>/test_<module>.py

## Strategy

For each target domain, write skeleton tests following this pattern:
1. Import test — verify the module is importable
2. Class instantiation — create objects with valid params
3. Pure function tests — call functions with known inputs, assert type/sign/range
4. Edge case — invalid inputs raise ValueError/TypeError
5. Mock external deps with pytest.importorskip or monkeypatch sys.modules

DO NOT require network, licenses, or external mounts for tests to pass.
Use `pytest.importorskip("OrcFxAPI")` for licensed deps.
Use `monkeypatch.setitem(sys.modules, "matplotlib", MagicMock())` for optional viz deps.

## TASK 1: Structural domain — wall thickness and pipe capacity (highest priority)

Target modules (read each source file first):
- src/digitalmodel/structural/wall_thickness/
- src/digitalmodel/structural/pipe_capacity/
- src/digitalmodel/structural/fatigue/
- src/digitalmodel/structural/buckling/

For each module found:
1. Read the source to understand function signatures and dependencies
2. Create tests/structural/<subpackage>/test_<module>.py
3. Write 3-5 tests per module minimum
4. Run: `uv run pytest tests/structural/<subpackage>/ -v --tb=short`
5. Fix any failures

Commit after each subpackage: "test(structural): skeleton tests for <subpackage> (#1824)"

## TASK 2: Hydrodynamics domain

Target modules:
- src/digitalmodel/hydrodynamics/
- Focus on: wave_spectra, rao, morison, diffraction if they exist

Same pattern: read source, write skeleton tests, run, fix, commit.
Commit: "test(hydrodynamics): skeleton tests for <subpackage> (#1824)"

## TASK 3: Pipeline domain

Target modules:
- src/digitalmodel/pipeline/

Same pattern.
Commit: "test(pipeline): skeleton tests for <subpackage> (#1824)"

## TASK 4: Naval architecture domain

Target modules:
- src/digitalmodel/naval_architecture/

Same pattern.
Commit: "test(naval_architecture): skeleton tests for <subpackage> (#1824)"

## TASK 5: Cathodic protection domain

Target modules:
- src/digitalmodel/cathodic_protection/

Same pattern.
Commit: "test(cathodic_protection): skeleton tests for <subpackage> (#1824)"

## TASK 6: Run full test suite and report

```bash
uv run pytest tests/ -v --tb=no -q 2>&1 | tail -20
```

Count: total tests collected, passed, failed, skipped, errors.
Compare to baseline of 11,565 tests.

## TASK 7: Post progress comment on GH issue

```bash
gh issue comment 1824 --repo vamseeachanta/workspace-hub --body "Overnight branch feat/1824-test-uplift:
- Structural: X new test files, Y tests
- Hydrodynamics: X new test files, Y tests
- Pipeline: X new test files, Y tests
- Naval architecture: X new test files, Y tests
- Cathodic protection: X new test files, Y tests
- Total new tests: N
- Branch ready for review and merge to main"
```

## KEY PITFALLS

1. Use `pytest.importorskip("OrcFxAPI")` for OrcaFlex deps — DO NOT try to import directly
2. For matplotlib: mock via monkeypatch, don't import
3. Check __init__.py imports before testing — if they eagerly import missing deps, all tests fail
4. First pytest run compiles 32K bytecode files — set timeout=300
5. This is a BRANCH — push to feat/1824-test-uplift, never to main
6. If `git push` fails with auth issues, just commit locally — we'll push in the morning

## IMPORTANT BOUNDARIES

Do NOT write to:
- tests/geotechnical/ (owned by Terminal 1)
- src/digitalmodel/geotechnical/ (owned by Terminal 1)
- data/document-index/ (owned by Terminal 3)
- Any workspace-hub files outside digitalmodel/

Only write to:
- digitalmodel/tests/structural/
- digitalmodel/tests/hydrodynamics/
- digitalmodel/tests/pipeline/
- digitalmodel/tests/naval_architecture/
- digitalmodel/tests/cathodic_protection/
- digitalmodel/tests/metocean/
- digitalmodel/tests/subsea/
