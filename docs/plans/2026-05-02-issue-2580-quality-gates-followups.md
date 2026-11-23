# Quality Gates Followups for #2580 — post-#543 main RED state

> **Status:** evidence capture (Lane 2 — followups tracker, parallel to Lane 1 plan revision)
> **Date:** 2026-05-02
> **Parent issue:** [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580)
> **Source CI run:** Quality Gates run id `25250371336` (job `74041413408`), digitalmodel main `60d59565` ("fix(ci): triage punch list — economics importorskip, curves.py deletion, drilling_riser CSV vendor, maxfail bump (#543)"), 2026-05-02 10:57Z–11:01Z.
> **Local digitalmodel HEAD inspected:** `0faf6416` (auto-sync 2026-05-02 — one commit on top of `60d59565`, no test-tree changes).

---

## Decision rationale (already established)

[#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) narrowly fixes the 10 named tests it owns (citations + capsys yml-utilities). Quality Gates on `60d59565` reports `Tests: 3000 passed, 20 failed, 0 errors` — the other **20 failures are out of [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580)'s primary scope** but need tracked followups so Quality Gates can eventually green. Closing [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) will not green Quality Gates by itself.

---

## Evidence access — and its limits

`gh run view 25250371336 --log-failed --repo vamseeachanta/digitalmodel` and `gh run view --job 74041413408 --log` both return the same single-line embedded JSON `output_tail` field. The Quality Gates CLI (`digitalmodel.workflows.automation.quality_gates_cli`) wraps pytest stdout into a JSON metric and only retains the **trailing chunk** of output. The downloaded artifact `quality-gate-results/reports/quality_gates_results.json` confirms this — `output_tail` length 8.6 KB, contains exactly **one** `FAILED tests/...` line and the pytest tail-banner `=========== 20 failed, 3000 passed, 46 skipped in 108.67s ============` plus `!!!! stopping after 20 failures !!!!`.

**Concretely identified nodeid (1 of 20):**
- `tests/hydrodynamics/diffraction/test_benchmark_runner.py::TestRunFromResults::test_run_from_results_success` — `assert False is True` from `BenchmarkRunResult(... error_message="'NoneType' object is not callable", success=False).success`

**The other 19 nodeids are NOT recoverable from this run's logs.** They were emitted to pytest stdout earlier in the run (when each test failed) but are not in the trailing `output_tail` window because pytest's `=== short test summary info ===` block is cut off by the wrap.

**Adjacent-evidence inference (NOT confirmed):** the `output_tail` traceback fragments and printed banner text point strongly at three test modules as the source of most of the remaining 19:

| Test module | Signature in `output_tail` | Notes |
|---|---|---|
| `tests/hydrodynamics/diffraction/test_batch_processor.py` | `Unknown source type: unknown_solver`, `Unknown source type: bad_type`, `RuntimeError: disk full`, `GoodVessel`/`BadVessel`, `test_export_creates_json`, `test_export_empty_report` (28 tests in file) | Last touched by `73a39b41 feat(orcawave): emit taxonomy-aware semantic diffs (#521)` and `bfaf228b test(diffraction): CLI/exporter test coverage — 84 tests for 3 modules (#1785)` — both POST-#2574. |
| `tests/hydrodynamics/diffraction/test_benchmark_runner.py` | `test_run_from_results_success` (confirmed), 11 tests in file total | Same recent-commit lineage. |
| `tests/hydrodynamics/bemrosetta/test_converters.py` | `test_full_conversion_workflow`, `test_conversion_with_qtf_produces_qtf_file`, `TestVessel` artifacts (26 tests in file) | Same recent-commit lineage. |

These three modules total 65 test functions, so 20 failures concentrated in them is plausible but **not proven**. The categorical counts below are best-effort and should be re-validated by re-running CI with `pytest --maxfail=999` or by parsing the JUnit XML if that gets uploaded.

---

## Followup tracking table

| Test nodeid | Category | Top error | Followup issue (#NNNN or "TBD") |
|---|---|---|---|
| `tests/hydrodynamics/diffraction/test_benchmark_runner.py::TestRunFromResults::test_run_from_results_success` | NEW post-#2574 (real bug — benchmark runner returns `success=False` with `'NoneType' object is not callable`) | `assert False is True` where result.error_message=`"'NoneType' object is not callable"` | TBD |
| 19 other nodeids — NOT recovered from CI logs (truncated by `output_tail` JSON wrap in Quality Gates CLI) | UNKNOWN — see "Evidence access" section | — | TBD — see remediation below |

---

## Categorical breakdown — best-effort estimate

> **Confidence:** LOW. Only 1 of 20 nodeids concretely recovered. The breakdown below is inferred from `output_tail` fragments and the recent-commit history of likely-impacted modules.

| Category | Estimated count | Rationale |
|---|---|---|
| **NEW post-#2574** (now-collected tests revealing real bugs in recently added diffraction/bemrosetta modules) | ~12 | The `test_benchmark_runner.py` `TestRunFromResults::test_run_from_results_success` failure is real-bug shaped (`NoneType not callable` propagated through batch processor). `test_batch_processor.py` and `test_converters.py` last landed via #1785 / #521 and may be exercising fresh integrations. |
| **Newly-flaky** (timing or env-dependent) | ~3 | `output_tail` shows a `disk full` mock that can be sensitive to tmp_path collisions under xdist. |
| **Import errors** (missing deps in CI image) | ~5 | The `output_tail` mentions `Warning: Could not import reservoir modules: cannot import name 'ReservoirProperties' from 'digitalmodel.reservoir'` — at least one import problem is present in the run. |
| **Other** | ~0 | — |
| **Total** | 20 (matches CI report) | — |

The "12 / 5 / 3 / 0" split is the recommended categorical summary to use in the [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) comment, with explicit "estimate, not enumeration" caveat.

---

## Local repro on `60d59565` — 2026-05-02 23:46Z (REPLACES inferred estimates above)

**Command:** local pytest run without `--maxfail` (mirroring CI invocation otherwise), captured to `/tmp/qg-repro-60d59565.log` (1.4 MB). Run was killed mid-execution after capturing significant evidence; pytest never emitted its `=== short test summary ===` block. Final test still in progress at kill: `tests/solvers/orcaflex/test_pipeline_schematic.py::TestIntegration::test_full_workflow`.

**Concrete counts (unique nodeids, deduplicated):**

| Status | Count | Source |
|---|---|---|
| FAILED | **184** unique | `grep -oE "tests/.+\.py::.+ FAILED" /tmp/qg-repro-60d59565.log \| sort -u \| wc -l` |
| ERROR | **60** unique | `grep -oE "tests/.+\.py::.+ ERROR" /tmp/qg-repro-60d59565.log \| sort -u \| wc -l` |
| **Total broken** | **244** | sum of unique nodeids across both states |

**Critical finding:** Quality Gates' "20 failures" was the `pytest --maxfail=20` short-circuit, NOT the true count. Real number is **~12× larger** than CI reported, and the run was killed before completing collection — true total may be even higher.

### Failure-bucket breakdown (FAILED)

| Bucket | Unique FAILED | Most-affected modules |
|---|---|---|
| `marine_ops/` | **77** | `legacy/test_mooring_catenary.py`, `test_mooring_catenary.py`, `test_cathodic_protection_dnv.py`, `legacy/test_component_database.py`, `test_unified_rao_reader.py`, `environmental_loading/test_ocimf.py`, `legacy/test_wave_spectra.py`, `test_catenary_adapter.py`, `integration/test_*` |
| `solvers/` | **33** | `orcaflex/test_orcaflex_cli.py` (26), `orcaflex/modular_generator/`, `orcaflex/mooring-tension-iteration/`, `orcaflex/reporting/test_*_fixture_snapshot.py` |
| `hydrodynamics/` | **25** | `diffraction/test_cli_integration.py` (12), `diffraction/test_benchmark_runner.py` (4), `diffraction/test_solver_smoke_unit.py`, `diffraction/test_unit_box_benchmark.py` |
| `infrastructure/` | **20** | `core/test_database_manager.py` (14), `core/test_cache.py` (4), `contracts/test_api_contracts.py` |
| `field_development/` | **16** | `test_economics.py` (TestCarbonSensitivity, TestFiscalRegimeTaxAdjustment, TestScheduleDeclineIntegration) |
| `orcaflex/` | **4** | `test_mooring_design.py` catenary, `test_installation_analysis.py` DAF |
| Other | **9** | naval_architecture (2), reservoir (2), orcawave (2), solver (2), contracts (2), simple_engine (1) |
| **Total FAILED** | **184** | |

### Error-bucket breakdown (ERROR — collection-time, fixture problems)

| Bucket | Unique ERROR | Most-affected modules |
|---|---|---|
| `infrastructure/` | **36** | `core/test_cache.py` (28 — Redis fixture missing), `core/test_database_manager.py` (8 — SQL fixture missing) |
| `solvers/` | **13** | `blender_automation/test_batch_processor.py` (4), `orcaflex/modular_generator/test_campaign_generator.py` (6), `orcaflex/test_orcaflex_converter_enhanced.py` (3) |
| `orcawave/` | **5** | `test_builder_orchestration.py` (4), `test_report_builder.py` (1) |
| `hydrodynamics/` | **3** | `passing_ship/test_passing_ship_cli.py` (2), `aqwa/test_aqwa_lis_parser_real_data.py` |
| `data_systems/` | **3** | `test_config_loader.py` validate_schema |
| **Total ERROR** | **60** | |

### Inferred root-cause clusters (need verification before issue-creation)

- **Marine ops mass-failure (77)** — concentration in `legacy/`, `catenary/`, `test_mooring_catenary.py` (12 tests), `test_cathodic_protection_dnv.py` (16 tests) suggests a SHARED dependency or fixture broke. Likely 1-3 root causes, not 77.
- **OrcaFlex CLI (26)** — all 26 in `test_orcaflex_cli.py` likely mean the CLI command isn't registered/findable on PATH in the local env. Single fix.
- **Infrastructure cache+db_manager (36 ERROR + 18 FAILED)** — Redis/SQL service deps absent locally. Likely already known via pre-existing collect_ignore patterns; verify against [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) inventory.
- **Field-dev economics (16)** — TestCarbonSensitivity, TestFiscalRegimeTaxAdjustment, TestScheduleDeclineIntegration — these look like REAL bugs in a feature that #543 thought was working. Cross-check against [#2076](https://github.com/vamseeachanta/workspace-hub/issues/2076) / [#2079](https://github.com/vamseeachanta/workspace-hub/issues/2079) / [#2081](https://github.com/vamseeachanta/workspace-hub/issues/2081) closeout.
- **Hydrodynamics diffraction (25 + 3 ERROR)** — `test_cli_integration.py` 12 failures all CLI-flavored — same CLI-not-on-PATH pattern as orcaflex CLI? Or a different root cause? Needs investigation.

### Implication for [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580)

- [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) narrowly fixes 10 tests (4% of the 244-failure surface). Closing it does NOT and CANNOT green Quality Gates.
- The collect_ignore audit ([#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585)) covered 26 *muted* tests. The 244 unique nodeids found here are *active failures* — separate population.
- Quality Gates greenness is not a [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) acceptance criterion and should not be presented as one.

---

## Remediation paths

1. **Complete a clean local repro** — re-run pytest with `--maxfail=999` from a fresh worktree at `60d59565`, let it run to completion, parse the `=== short test summary ===` block. Currently blocked by 1.4 MB log capture being incomplete.
2. **Patch the Quality Gates CLI** to upload the full `pytest --tb=short` log as a separate artifact (not just JSON-wrapped tail). One-line fix in `digitalmodel/src/digitalmodel/workflows/automation/quality_gates_cli.py`. Independent of [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580).
3. **Re-trigger Quality Gates workflow on `60d59565` with `pytest --maxfail=999`** as a one-shot to capture the full failure inventory in CI.

---

## Recommendation to main session — REVISED

Original Lane 3 recommendation was **(b)** "one issue per category" assuming 3-4 categories of 20 failures.

**Revised recommendation: (d) — file ONE umbrella issue scoped to "post-#543 main is 244+ test failures, not 20"**, with sub-issues per bucket as evidence accumulates. Rationale:
- The bucket counts (77/33/25/20/16/...) suggest most failures cluster around shared root causes (e.g. one missing service dep affecting 30+ tests). A flat "one-issue-per-bucket" approach risks creating issues whose triage immediately collapses them back into one.
- File the umbrella WITHOUT pre-categorizing into "real bug vs flake vs import error" — those determinations need per-bucket investigation.
- Reference [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) (the *muted* 26) as a sister tracker, but make clear this umbrella covers the *active* 244.

If main session prefers per-bucket issues immediately, the buckets to file are: `marine_ops` (77), `solvers/orcaflex` (33), `hydrodynamics` (28), `infrastructure` (56 incl. ERRORs), `field_development` (16), `other` (~14).

---

## Constraints honored by Lane 2

- Read-only on digitalmodel CI: only `gh run view` and `gh run download` of artifacts (download is read-only).
- No mutations to digitalmodel code or `tests/conftest.py`.
- [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) is not closed/relabeled by Lane 2.
- No new GitHub issues created by Lane 2.
- Single comment will be posted to [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) (verified OPEN at `gh issue view 2580 --json state` returned `OPEN` 2026-05-02).
- Lane 2 wrote this file; it did NOT directly edit `2026-05-02-issue-2580-digitalmodel-collect-ignore-test-fixes.md`. Main session reconciles the two.
