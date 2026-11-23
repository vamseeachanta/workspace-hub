# Plan for #510: Fix 20 pre-existing test failures in tests/solvers/orcaflex/

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/510
> **Review artifacts:** scripts/review/results/2026-04-24-plan-510-claude.md | scripts/review/results/2026-04-24-plan-510-codex.md | scripts/review/results/2026-04-24-plan-510-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/generic.py:328-337` — `SINGLETON_SECTIONS` now keyed by `FrictionCoefficients` (old key `SolidFrictionCoefficients` removed). This is the source of truth.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/generic.py:339-367` — `FIELD_TO_SECTION["variable_data_sources"] = "VariableData"` (old value `VariableDataSources` removed).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py:46-82` — Builder emits new keys; confirms old names no longer present in output dict.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/extractor.py:41-50,361-492` — Extractor preserves an alias map so *input parsing* still accepts the old names; this is intentional backward compatibility on the read path only.
- Found: `docs/domains/orcaflex/…` — existing tree, replacement for former `docs/modules/orcaflex/…` directory tree (directory-level rename).
- Gap: None on the source side — there is no product bug. The drift is entirely on the test side (assertions and fixture paths).

### Standards

Not applicable — this is a test-repair issue, not an engineering deliverable against a standard.

### LLM Wiki pages consulted

No relevant wiki pages — the drift is a mechanical rename aftermath, not domain knowledge.

### Documents consulted

- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — parent batch spec; #510 is one of its 10 pods.
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — broader OrcaFlex/OrcaWave epic; does not specify test-suite repair.
- `/tmp/orca-batch-2026-04-24/intel-510.md` — pod Explorer intel (authoritative for this plan).
- `/tmp/orca-batch-2026-04-24/issue-510.json` — issue body enumerates 20 failures + 5 errors across the `tests/solvers/orcaflex/` subtree.
- No prior `digitalmodel/`-local plan exists (the subrepo's `docs/plans/` directory is not present); plans for `digitalmodel/` work land here in `workspace-hub/docs/plans/`.

### Gaps identified

- No implementation gap. All required source symbols (`FrictionCoefficients`, `VariableData`) and all required directory artifacts (`docs/domains/orcaflex/…`) already exist. The gap is purely: **tests reference the pre-rename names and paths**.
- Residual fixture gap: `MONOLITHIC_24IN_SIM` (a `.sim` file >100 MB regenerable only via a licensed OrcaFlex run) is not committed; the existing skip-on-missing guard at `test_modular_vs_monolithic.py:58-60` must continue to fire after the path fix. No new data is required.

### Evidence (embedded verification)

**Issue status** (per pod issue-510.json, batch snapshot 2026-04-24):
- `#510` — OPEN — "Fix 20 pre-existing test failures in tests/solvers/orcaflex/"

**File existence** (per pod intel, confirmed as referenced paths in the failing test files):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/generic.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/extractor.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_generic_builder.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_generic_schema.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_extractor.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py`
- EXISTS: `docs/domains/orcaflex/examples/raw/`
- MISSING (intentional — stale references in tests only): `docs/modules/orcaflex/…`

**Line excerpts** (per pod intel, to be verified inline during implementation):
- `schema/generic.py:328-337` keys `SINGLETON_SECTIONS` with `FrictionCoefficients`
- `schema/generic.py:339-367` maps `variable_data_sources` → `VariableData`
- `test_generic_builder.py:208-279` still asserts `"VariableDataSources" in result` and `"SolidFrictionCoefficients" in result`
- `test_generic_schema.py:355-357,413-415` still asserts stale names
- `test_extractor.py:~329` embeds `"SolidFrictionCoefficients:\n"` in an inline YAML fixture
- `test_modular_vs_monolithic.py:47-88` builds paths from `_DOCS_ROOT / "modules/orcaflex/..."`
- `test_orcaflex_converter_enhanced.py:29` sets `TEST_EXAMPLES_DIR = Path("docs/domains/orcaflex/examples/raw")` (cwd-relative)

**Gap proofs** (to be captured inline at implementation time):
- `grep -rn "VariableDataSources\|SolidFrictionCoefficients" digitalmodel/tests/` — list must shrink to only alias-round-trip extractor cases after fix.
- `grep -rn "docs/modules/orcaflex" digitalmodel/tests/` — must return empty after fix.
- `ls digitalmodel/docs/plans/` — directory does not exist, confirming workspace-hub is the plan home.

<!-- Verification: 6 distinct sources (issue body + intel file + schema/generic.py + generic_builder.py + test files + docs/domains/ tree). Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-510-fix-20-test-failures.md |
| Tests (modify) | digitalmodel/tests/solvers/orcaflex/modular_generator/test_generic_builder.py |
| Tests (modify) | digitalmodel/tests/solvers/orcaflex/modular_generator/test_generic_schema.py |
| Tests (modify) | digitalmodel/tests/solvers/orcaflex/modular_generator/test_extractor.py |
| Tests (modify) | digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py |
| Tests (modify) | digitalmodel/tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py |
| Source of truth (read-only) | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/generic.py |
| Source of truth (read-only) | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-510-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-510-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-510-gemini.md |
| Docs updates | docs/plans/README.md (add this plan to the index) |

---

## Deliverable

All tests under `digitalmodel/tests/solvers/orcaflex/` either pass or legitimately skip; the previously reported 20 failures + 5 errors are resolved via test-side updates only, with zero source-code changes in `digitalmodel/src/`.

---

## Pseudocode

T1 — trivial, mechanical rename-follow-ups. See `Files to Change` for the exact edit points. No algorithmic design required.

The implementer's procedure is:

```
1. cd digitalmodel/
2. uv run pytest tests/solvers/orcaflex/ --collect-only -q    # snapshot collection
3. uv run pytest tests/solvers/orcaflex/ -x --tb=short        # confirm the 20F + 5E baseline
4. For each failing assertion, replace old → new symbol:
     "VariableDataSources"        → "VariableData"
     "SolidFrictionCoefficients"  → "FrictionCoefficients"
   (Preserve legacy-name usages only where the extractor's input-alias behavior is explicitly
    tested — i.e. a test that asserts the extractor accepts the old name as input.)
5. In test_modular_vs_monolithic.py, change _DOCS_ROOT / "modules/orcaflex/..."
   to _DOCS_ROOT / "domains/orcaflex/..." for every such literal.
   Verify with os.path.exists() or pathlib Path.exists() before running.
6. In test_orcaflex_converter_enhanced.py, anchor TEST_EXAMPLES_DIR to the repo root
   via Path(__file__).resolve().parents[N] / "docs/domains/orcaflex/examples/raw"
   so the test works regardless of pytest's cwd.
7. Re-run the suite; verify zero failures, no new skips beyond the pre-existing
   MONOLITHIC_24IN_SIM skip-on-missing guard.
8. Run full digitalmodel regression to confirm no collateral damage.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | digitalmodel/tests/solvers/orcaflex/modular_generator/test_generic_builder.py | Rename `"VariableDataSources"` → `"VariableData"` and `"SolidFrictionCoefficients"` → `"FrictionCoefficients"` in assertions (lines ~208-279). |
| Modify | digitalmodel/tests/solvers/orcaflex/modular_generator/test_generic_schema.py | Update expected values at ~L355-357 and ~L413-415 to match the current schema constants. |
| Modify | digitalmodel/tests/solvers/orcaflex/modular_generator/test_extractor.py | Update inline YAML fixture at ~L329 from `"SolidFrictionCoefficients:\n"` to `"FrictionCoefficients:\n"` — **except** in tests that explicitly exercise the extractor's input-alias round-trip (keep legacy name there). |
| Modify | digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py | Replace `_DOCS_ROOT / "modules/orcaflex/..."` with `_DOCS_ROOT / "domains/orcaflex/..."` at lines 47-88. Verify each resulting Path resolves to an existing artifact; if any artifact is truly missing (not just renamed), add a `pytest.skip("…not committed")` guard rather than invent data. |
| Modify | digitalmodel/tests/solvers/orcaflex/test_orcaflex_converter_enhanced.py | Anchor `TEST_EXAMPLES_DIR` (L29) to `Path(__file__).resolve().parents[N] / "docs/domains/orcaflex/examples/raw"` to decouple from pytest's cwd. Inspect the two `ERROR` tracebacks at L142 (`test_batch_conversion_dat_to_yml`) and L174 (`test_batch_parallel_conversion`) to confirm root cause is cwd/path drift before patching (per Category-4 risk). |
| Update | docs/plans/README.md | Add this plan to the plan index (by date). |

**Hard constraint:** no edits to `digitalmodel/src/` are permitted under this plan. If the implementer finds a failure that seems to require a source change, STOP and escalate — that indicates scope creep (Category-4 error hiding a real regression) and re-triggers adversarial review.

---

## TDD Test List

Failing tests become the acceptance suite. After the fix, each listed test must PASS (or SKIP for the explicitly-excluded heavy-fixture cases).

| Test name | What it verifies | Expected input | Expected outcome |
|---|---|---|---|
| test_generic_builder.py::TestBuildVariableDataSources::test_build_variable_data_sources | Builder emits the `VariableData` section | builder with populated `variable_data_sources` | `"VariableData" in result` |
| test_generic_builder.py::TestBuildSingletonSections::test_build_friction_coefficients | Builder emits `FrictionCoefficients` singleton | builder with friction-coefficient data | `"FrictionCoefficients" in result` |
| test_generic_builder.py::TestBuildSingletonSections::test_none_singleton_is_skipped | Builder skips `None` singletons | None input for friction coefficients | key absent from result |
| test_generic_builder.py::TestBuildSingletonSections::test_empty_singleton_data_is_skipped | Builder skips empty singletons | empty dict for friction coefficients | key absent from result |
| test_generic_schema.py::test_contains_variable_data_sources | Schema constant maps to new name | `FIELD_TO_SECTION["variable_data_sources"]` | `== "VariableData"` |
| test_generic_schema.py::test_solid_friction_coefficients | Schema constant keyed by new name | `SINGLETON_SECTIONS["FrictionCoefficients"]` | `== "friction_coefficients"` |
| test_extractor.py (YAML-fixture test at ~L329) | Extractor parses section with the new name | YAML containing `"FrictionCoefficients:\n…"` | Correctly parsed into `friction_coefficients` field |
| test_modular_vs_monolithic.py::TestQuickQA::* (and TestA01Riser/TestLazyWave/TestFenders/TestPullIn) | Session fixtures resolve to real paths under `docs/domains/orcaflex/…` | path exists check passes | tests run or skip cleanly, no fixture error |
| test_orcaflex_converter_enhanced.py::test_batch_conversion_dat_to_yml | CLI batch conversion works when pytest run from any cwd | `docs/domains/orcaflex/examples/raw` anchored to repo root | pass |
| test_orcaflex_converter_enhanced.py::test_batch_parallel_conversion | Parallel batch conversion works when pytest run from any cwd | same | pass |
| **Regression guard** — extractor alias-round-trip test | Extractor still accepts legacy input names | YAML with `SolidFrictionCoefficients:` / `VariableDataSources:` | Parsed successfully (legacy name preserved as input alias) |

(Exact test-ID list to be re-confirmed via `uv run pytest tests/solvers/orcaflex/ --collect-only -q` before implementation — see Pseudocode step 2.)

---

## Acceptance Criteria

- [ ] `uv run pytest digitalmodel/tests/solvers/orcaflex/ -v` — 0 failures, 0 errors (skips acceptable for the MONOLITHIC_24IN_SIM fixture-gap cases that are already guarded).
- [ ] `uv run pytest digitalmodel/ -q` — no new regressions introduced elsewhere.
- [ ] `grep -rn "VariableDataSources\|SolidFrictionCoefficients" digitalmodel/tests/` returns only the extractor alias-round-trip test cases (explicit legacy-input coverage), zero other hits.
- [ ] `grep -rn "docs/modules/orcaflex" digitalmodel/tests/` returns empty.
- [ ] `git diff digitalmodel/src/` is empty — source code untouched.
- [ ] Plan entry added to `docs/plans/README.md`.
- [ ] Review artifacts posted to `scripts/review/results/` for Claude, Codex, and Gemini.
- [ ] Implementer verified the two `test_orcaflex_converter_enhanced.py` ERROR tracebacks confirm cwd/path-drift root cause (not a hidden regression in `OrcaFlexConverterEnhanced.convert_batch()`).

---

## Adversarial Review Summary

<!-- Filled in after Step 4 (adversarial review) completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | _placeholder — to be filled post-review_ |
| Codex | PENDING | _placeholder — to be filled post-review_ |
| Gemini | PENDING | _placeholder — to be filled post-review_ |

**Overall result:** PENDING

Revisions made based on review:
- _placeholder — record any plan changes driven by adversarial review findings here_

---

## Risks and Open Questions

- **Risk:** The `docs/modules/…` → `docs/domains/…` directory rename may have broken fixtures in other module test suites; recommend follow-up audit (out of scope for #510).
- **Risk:** The two `test_orcaflex_converter_enhanced.py` ERROR tests (`test_batch_conversion_dat_to_yml`, `test_batch_parallel_conversion`) could, in theory, mask a real regression in `OrcaFlexConverterEnhanced.convert_batch()`. **Mandatory mitigation:** the implementer must read the actual error traceback before patching; if the root cause is not cwd/path drift, STOP and escalate (this reopens approval).
- **Risk:** `test_extractor.py` contains a legitimate alias-round-trip test that intentionally uses the legacy names (`SolidFrictionCoefficients`, `VariableDataSources`) as input to verify the extractor's backward-compat alias map. Bulk find-replace would break that test. Use targeted single-site edits (per `.claude/rules/coding-style.md`) and verify each edit.
- **Risk:** Some referenced artifacts under `docs/domains/orcaflex/…` may be present at the path level but missing specific sub-files (e.g. `A01 Lazy wave riser.yml`). If the path-correction reveals truly missing data, add a `pytest.skip("…not committed")` guard — do not invent fixture data.
- **Risk:** Issue body says "20 failures" in the title but the body lists 5 additional errors; the scope here treats both as in-scope (per the "Get to 0 failures" deliverable). If the user intends errors to be out of scope, the plan must be reduced before implementation.
- **Open question:** After the fix, should the legacy section names (`SolidFrictionCoefficients`, `VariableDataSources`) remain supported indefinitely as input aliases in the extractor, or is there a deprecation plan? Not required for #510 but worth tracking.

---

## Complexity: T1

**T1** — The intel-layer work has already resolved the diagnosis (two mechanical renames + one cwd-anchoring fix), there is no algorithmic design, no new module, and no source-code change. All edits are in-place string/path updates across 5 test files. The originally-estimated T2 in the pod intel reflected uncertainty about Category-4 (the 2 converter-enhanced errors); the plan now pins that uncertainty to a single mandatory-traceback-read gate in Acceptance Criteria, so the residual risk is a short-circuit escalation rather than extra design work. Net: this is trivial edit-safety work, T1. (Escalate to T2 only if the Category-4 traceback reveals a real source regression.)
