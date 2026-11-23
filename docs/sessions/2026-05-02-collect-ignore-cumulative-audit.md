# digitalmodel collect_ignore — Cumulative Audit (2026-05-02)

Source: `digitalmodel/tests/conftest.py:9-51`. Blame: `git -C digitalmodel blame -w tests/conftest.py`. Two commits author every entry — `2c185d2d` (2026-03-24, "fresh repo after slimming", 26 entries) and `4515cd01` (2026-05-01, via #2574, 3 entries).

## Inventory
All paths relative to `digitalmodel/tests/`.

| # | Path | Tracking Issue | Issue State | Added | Comment group |
|---|---|---|---|---|---|
| 1 | `marine_ops/artificial_lift/dynacard/test_vision_benchmark.py` | none | — | 2c185d2d 2026-03-24 | Missing local modules |
| 2 | `solvers/orcaflex/examples_integration/test_converter.py` | none | — | 2c185d2d | Missing local modules |
| 3 | `solvers/orcaflex/examples_integration/test_single_download.py` | none | — | 2c185d2d | Missing local modules |
| 4 | `structural/fatigue_analysis/test_reference_seastate_scaling.py` | none | — | 2c185d2d | Missing local modules |
| 5 | `visualization/design_tools/pilot_program/test_case_1_separator.py` | none | — | 2c185d2d | Missing local modules |
| 6 | `solvers/orcaflex/test_orcaflex_unit.py` | none | — | 2c185d2d | Missing src modules |
| 7 | `structural/fatigue_apps/test_load_scaling.py` | none | — | 2c185d2d | Missing src modules |
| 8 | `subsea/pipeline/test_on_bottom_stability.py` | none | — | 2c185d2d | Missing src modules |
| 9 | `test_plate_capacity.py` | none | — | 2c185d2d | Missing src modules |
| 10–17 | `visualization/test_{anomaly_detection,comparative_analysis,component_classifier,csv_parser,data_validator,loading_decoder,sensitivity_analysis,statistical_analysis}.py` | none | — | 2c185d2d | Deleted orcaflex-dashboard |
| 18–20 | `workflows/orcawave/test_{com_connection,end_to_end,integration}.py` | none | — | 2c185d2d | Platform-specific / optional deps |
| 21 | `workflows/standalone/markitdown/test_converter.py` | none | — | 2c185d2d | Platform-specific / optional deps |
| 22 | `test_workflow_checkpoints.py` | none | — | 2c185d2d | pytest-asyncio / hypothesis conflict |
| 23 | `marine_ops/marine_engineering/test_component_database.py` | none | — | 2c185d2d | Data file deps not in git |
| 24 | `hydrodynamics/hull_library/test_hull_library_expansion.py` | none | — | 2c185d2d | Data file deps not in git |
| 25 | `specialized/cathodic_protection/test_abs_ship_variants_wrk271.py` | none | — | 2c185d2d | CP random-ordering shared state |
| 26 | `specialized/cathodic_protection/test_cathodic_protection_b401.py` | none | — | 2c185d2d | CP random-ordering shared state |
| 27 | `citations/test_registry.py` | [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) | OPEN, `status:plan-review` | 4515cd01 2026-05-01 | Citations workspace-hub root |
| 28 | `citations/test_schema.py` | [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) | OPEN, `status:plan-review` | 4515cd01 | Citations workspace-hub root |
| 29 | `asset_integrity/test_yml_utilities_additional.py` | [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580) | OPEN, `status:plan-review` | 4515cd01 | capsys under pytest-xdist |

Totals: 29 entries. With tracking issue: 3. Without: 26.

## Findings
- **Verdict: DIRTY.** 26 of 29 entries (90%) have no tracking issue — process bug, all introduced in a single 2026-03-24 slim-down commit without follow-ups.
- **Stale entries (issue closed but entry remains):** none — #2580 is OPEN.
- **Untracked entries (no issue ref):** rows 1–26 above, six failure-mode buckets.
- **Orphan issues (open, plausibly relevant, not in conftest):** [#2414](https://github.com/vamseeachanta/workspace-hub/issues/2414) "autobuild or skip missing local git fixtures" — title closely matches rows 1–9 + 23–24 buckets, possible dropped link. [#2005](https://github.com/vamseeachanta/workspace-hub/issues/2005) covers worldenergydata collection-timeout (different surface, mention only). #1824, #1889, #1925, #172 are coverage/curation, not collect-skip.

## CI History (digitalmodel main, last 30 runs)
`gh run list --repo vamseeachanta/digitalmodel --branch main --limit 30`. Total 30: green 7, red 23, other 0. All 7 green are `Build API Docs`; all red are `Quality Gates` (21) or `Graph Update: uv in /.` (2). **Quality Gates is still red on main** post-#2574 (2026-05-02 10:57 UTC red). Pattern: single-workflow concentrated failure on the same surface #2580 targets.

## Recommendation
Conditions for closing #2580 cleanly:
1. **Scope #2580 to its 3 entries only.** Issue body explicitly covers `citations/test_registry.py`, `citations/test_schema.py`, `asset_integrity/test_yml_utilities_additional.py`. Do not bundle the 26 pre-existing entries into the close-out PR.
2. **File a separate umbrella issue (or six per-bucket issues) before closing #2580** so the 26 untracked entries are no longer documented-but-unowned. Link the new issue(s) inline in `conftest.py` next to each comment block.
3. **Cross-check #2414** against rows 1–9 and 23–24 — link or close as superseded.
4. **Close-out PR contract for #2580:** (a) deletes exactly the 3 lines from `4515cd01`, (b) shows the 10 named tests in #2580 passing under a Quality Gates run on the PR, (c) leaves rows 1–26 untouched, (d) adds the umbrella-issue link as a top-of-list comment.
5. **Verify Quality Gates green attribution narrowly.** Quality Gates is red on main right now for reasons beyond #2580's 3 entries; close-out attestation must say "the 10 named tests pass" not "Quality Gates is green" (per `commit_attestation_narrow_scope` memory). Otherwise the close is misleading.
