# Tier-1 approval-state audit — 2026-05-08

## Scope
Live GitHub and local evidence audit for the tier-1 repos: workspace-hub, digitalmodel, assetutilities, worldenergydata, assethold, aceengineer-website, and aceengineer-strategy. This audit is intentionally evidence-first: a live `status:plan-approved` label is not treated as executable unless a matching plan and local approval marker also exist, with no `status:plan-review` conflict and no existing `status:working` state.

## Repo-level matrix

| Repo | Approved | Fully evidenced | Missing plan | Missing marker | Conflicts | Working/WIP | Plan-review open | Dirty count | Local state |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| workspace-hub | 23 | 8 | 8 | 11 | 0 | 14 | 7 | 0 | `main` `eecdf049c35b` vs `eecdf049c35b` `0/0` |
| digitalmodel | 85 | 78 | 7 | 7 | 0 | 1 | 1 | 0 | `main` `0aa64ef2060a` vs `0aa64ef2060a` `0/0` |
| assetutilities | 22 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | `main` `3284e1a5a2dd` vs `3284e1a5a2dd` `0/0` |
| worldenergydata | 57 | 2 | 11 | 55 | 0 | 0 | 2 | 0 | `main` `ef38cb693559` vs `ef38cb693559` `0/0` |
| assethold | 28 | 27 | 0 | 1 | 0 | 0 | 0 | 0 | `main` `096071baad9b` vs `096071baad9b` `0/0` |
| aceengineer-website | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | `main` `df75720842af` vs `df75720842af` `0/0` |
| aceengineer-strategy | 4 | 0 | 2 | 4 | 0 | 0 | 1 | 0 | `main` `9057555e35f8` vs `9057555e35f8` `0/0` |

## Classification counts
- EXECUTABLE_CANDIDATE: 131
- GOVERNANCE_DRIFT: 74
- IMPLEMENTATION_STATE_AUDIT: 15
- LABEL_CONFLICT: 0
- DIRTY_CLONE_RISK: 0

## Clean execution-candidate pool

| Repo | Issue | Title | Evidence | URL |
|---|---:|---|---|---|
| workspace-hub | #2563 | Set up Telegram mobile access for Hermes AI control | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/workspace-hub/issues/2563 |
| workspace-hub | #2533 | feat(repo-portfolio): review and revise mission/objective statements across active repos | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/workspace-hub/issues/2533 |
| workspace-hub | #2523 | feat(workstations): add reusable Hermes preflight readiness checker | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/workspace-hub/issues/2523 |
| digitalmodel | #578 | W2W motion-compensated gangway operability module (DNV-ST-0358) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/578 |
| digitalmodel | #577 | Safety Case / MAH ALARP framework module (NORSOK Z-013, UK HSE SCR-2015) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/577 |
| digitalmodel | #576 | FOWT watch-circle envelope check vs dynamic-cable curvature (DNV-RP-0360) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/576 |
| digitalmodel | #575 | FOWT coupled aero-hydro response Python facade (IEC 61400-3-2, DNV-RP-0286) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/575 |
| digitalmodel | #574 | Wiki standards-page family for FOWT (IEC 61400-3-2, DNV-ST-0119, DNV-RP-0286, DNV-ST-0126, DNV-ST-0358, DNV-RP-0360, API RP 2SIM) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/574 |
| digitalmodel | #573 | fix(marine_ops): DNV-RP-F103 calibration drift in test_cathodic_protection_dnv.py — clears 16 of 77 marine_ops failures | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/573 |
| digitalmodel | #566 | fix(marine_ops): batched residue clusters R1+R5+R7+R8 — clears ~10 of 77 marine_ops failures | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/566 |
| digitalmodel | #565 | fix(marine_ops): test_hydro_coefficients.py::TestIntegration::test_csv_to_visualization_workflow — needs investigation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/565 |
| digitalmodel | #564 | fix(marine_ops): test_ocimf_mooring_integration.py::test_environmental_forces_to_mooring_tension — needs investigation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/564 |
| digitalmodel | #563 | fix(marine_ops): test_marine_eng_performance.py::test_ocimf_database_performance — needs investigation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/563 |
| digitalmodel | #562 | fix(marine_ops): test_marine_eng_performance.py::test_complete_workflow_performance — numpy.bool_ not JSON serializable | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/562 |
| digitalmodel | #561 | fix(marine_ops): test_ocimf_mooring_integration.py::test_combined_environmental_forces — wrong test premise (current dominates) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/561 |
| digitalmodel | #560 | fix(marine_ops): test_hydro_rao_integration.py::test_coupling_terms_affect_response — needs investigation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/560 |
| digitalmodel | #559 | fix(marine_ops): test_hydro_rao_integration.py::test_full_matrix_interpolation — strict-greater on equal floats (use >=) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/559 |
| digitalmodel | #558 | fix(marine_ops): test_hydro_rao_integration.py::test_damping_affects_phase — phase 138° not near -90° (sign convention) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/558 |
| digitalmodel | #557 | fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_boundary_warnings — DID NOT WARN on out-of-range query | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/557 |
| digitalmodel | #556 | fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_get_coefficients_interpolation — CYw=-3.56 not in [0,1.5] | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/556 |
| digitalmodel | #554 | fix(marine_ops): catenary solver bracketing + sinh overflow — clears 21 of 77 marine_ops failures | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/554 |
| digitalmodel | #537 | OrcaFlex: manifest.yml not written when all runs skipped — clarify docstring + behavior | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/537 |
| digitalmodel | #536 | OrcaFlex: per-iteration model_validate perf for large sweep matrices | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/536 |
| digitalmodel | #535 | OrcaFlex: apply_dotted_override should chain ValidationError with dotted-path context | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/535 |
| digitalmodel | #534 | OrcaFlex: _apply_overrides direct-call StopIteration guard | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/534 |
| digitalmodel | #531 | OrcaFlex: follow-up — 9 pre-existing test failures across 5 files not covered by #510 plan scope | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/531 |
| digitalmodel | #530 | OrcaFlex tests: hoist class-scoped fixtures in test_orcaflex_converter_enhanced.py to module level | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/530 |
| digitalmodel | #529 | OrcaFlex: convert_batch() parallel path doesn't aggregate success counts into self.stats | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/529 |
| digitalmodel | #523 | Harvest #517 subprocess review into actionable implementation tasks for #515 program | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/523 |
| digitalmodel | #522 | Codify ultra-constrained Claude subprocess prompt patterns for issue-scope reviews | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/522 |
| digitalmodel | #519 | Classify and fix General/Environment/Groups fidelity gaps in OrcaFlex generation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/519 |
| digitalmodel | #518 | Add model-library regression tests for strict-vs-generated OrcaFlex semantic diffs | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/518 |
| digitalmodel | #517 | Define OrcaFlex YAML semantic-diff taxonomy and comparison policy | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/517 |
| digitalmodel | #514 | Resolve or document the conftest ignore policy around async checkpoint tests | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/514 |
| digitalmodel | #512 | Fix GTM Demo 2 --from-cache path and make GTM validation tests hermetic | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/512 |
| digitalmodel | #509 | OrcaFlex: add pre-commit hook for YAML-strict validation on spec changes | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/509 |
| digitalmodel | #508 | OrcaFlex spec upgrader v2: rewrite generic specs to domain-specific sections | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/508 |
| digitalmodel | #507 | OrcaFlex reference: complete Orcina help ingestion — environment, waves, current pages | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/507 |
| digitalmodel | #506 | Add PassingShipSpec and JumperInstallationSpec schemas for non-generic specs | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/506 |
| digitalmodel | #494 | Enhance flexible pipe modeling — API 17B/17J compliance | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/494 |
| digitalmodel | #493 | Implement river/shallow-water current profile modeling | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/493 |
| digitalmodel | #491 | Implement ROV intervention modeling module (API 17H) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/491 |
| digitalmodel | #490 | Implement capping stack analysis module (API 17W) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/490 |
| digitalmodel | #489 | Implement HIPPS modeling module (API 17O) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/489 |
| digitalmodel | #488 | Implement subsea umbilical and control systems module (API 17E, 17F) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/488 |
| digitalmodel | #487 | Implement towing and marine operations analysis module | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/487 |
| digitalmodel | #485 | Implement subsea manifold aggregation module (API 17P) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/485 |
| digitalmodel | #484 | Implement subsea tree modeling module (API 17D) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/484 |
| digitalmodel | #483 | sub: curves.py decomposition -- break up 29,666-line monolith | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/483 |
| digitalmodel | #481 | Convert PLET-PLEM workbook via Windows cowork | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/481 |
| digitalmodel | #480 | BUG: Verify PLET-PLEM jumper segment lengths from SZ_Ballymore_Jumper_MF.xlsm | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/480 |
| digitalmodel | #479 | HTML/PDF report renderer for jumper installation analysis | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/479 |
| digitalmodel | #478 | OrcaFlex model generator integration - spec.yml to .dat pipeline | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/478 |
| digitalmodel | #475 | Add pytest test suite for jumper_lift.py (81 tests) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/475 |
| digitalmodel | #472 | Implement Go/No-Go decision logic per DNV-RP-H103 | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/472 |
| digitalmodel | #471 | STORY: Jumper Installation Analysis Pipeline — spec.yml to OrcaFlex | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/471 |
| digitalmodel | #470 | Seakeeping analysis using OpenFOAM — CFD-based ship motion simulation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/470 |
| digitalmodel | #469 | Assess AI agent session artifact dirs across machines (.codex, .gemini, .claude/skills) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/469 |
| digitalmodel | #467 | Subsea structure installation analysis — vessel performance and real-time motion feedback | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/467 |
| digitalmodel | #466 | Parametric hull analysis — steady speed, passing ship, narrow water environments | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/466 |
| digitalmodel | #465 | Capytaine ship hull benchmarking — OC4 semi-sub + WAMIT validation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/465 |
| digitalmodel | #464 | Add hydrodynamic BEM analysis module (Capytaine) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/464 |
| digitalmodel | #463 | Populate ship-dimensions dataset from ship plans (manual curation follow-on) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/463 |
| digitalmodel | #461 | Recover ship-dimensions template artifact from WRK-1339 Child E | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/461 |
| digitalmodel | #457 | Ship dimensions template + loader (WRK-1380) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/457 |
| digitalmodel | #284 | WRK-133: Update OrcaFlex license agreement with addresses and 3rd-party terms | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/284 |
| digitalmodel | #283 | WRK-131: Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/283 |
| digitalmodel | #281 | WRK-121: Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/281 |
| digitalmodel | #280 | WRK-064: 'OrcaFlex format converter: license-required validation and backward-compat | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/280 |
| digitalmodel | #277 | WRK-1251: FreeCAD deep parametric engineering — hull generation, FEM chain, design table studies | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/277 |
| digitalmodel | #272 | WRK-662: analysis(digitalmodel): engineering standards citation audit — version + clause consistency via Gemini | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/272 |
| digitalmodel | #271 | WRK-631: feat(frontierdeepwater): Microsoft Teams chatbot integration — Phase 2 deployment for both clients | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/271 |
| digitalmodel | #270 | WRK-630: feat(client2): engineering AI demo — diffraction + plate FFS + GoA + maritime legal workflows + demo package | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/270 |
| digitalmodel | #269 | WRK-629: feat(client2): engineering AI demo — diffraction + plate FFS + GoA + maritime legal system prompts + knowledge base | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/269 |
| digitalmodel | #584 | WRK-558: feat(digitalmodel/marine): Implement API RP 2SM — API RP 2SM 1st Ed & Addendum (2001 & 2007) Design, | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/584 |
| digitalmodel | #583 | WRK-557: feat(digitalmodel/marine): Implement API RP 572 — API RP 572 2nd Ed (2001) Inspection of Pressure Ve | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/583 |
| digitalmodel | #582 | WRK-556: feat(digitalmodel/marine): Implement API RP 2I — API RP 2I 3rd Ed (2008) In-service Inspection of M | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/582 |
| digitalmodel | #581 | WRK-539: feat(digitalmodel/structural): Implement API RP 2A — API RP 2A WSD | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/581 |
| digitalmodel | #580 | WRK-5066: Production engineering study — literature, methods and implementation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/580 |
| digitalmodel | #579 | WRK-494: feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/digitalmodel/issues/579 |
| assetutilities | #78 | chore(repo-structure): normalize assetutilities folder/file structure | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/78 |
| assetutilities | #75 | Simplify CI test environment to use the declared test dependency path | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/75 |
| assetutilities | #72 | Cleanup: resolve merge markers blocking editable install and downstream pytest | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/72 |
| assetutilities | #60 | repo | package development | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/60 |
| assetutilities | #59 | yaml_utilities | Variable Definition | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/59 |
| assetutilities | #58 | YAML Plotting | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/58 |
| assetutilities | #56 | productivity | Meetings | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/56 |
| assetutilities | #52 | YAML file split | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/52 |
| assetutilities | #42 | productivity | PB Hardware and Utility Readiness | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/42 |
| assetutilities | #41 | tech debt | Clean code | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/41 |
| assetutilities | #40 |  productivity | Marketing | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/40 |
| assetutilities | #39 | productivity | email clean up | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/39 |
| assetutilities | #38 | productivity | Knowledge Management | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/38 |
| assetutilities | #37 | Scalability | Process, People | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/37 |
| assetutilities | #36 | productivity | Consolidate hardware | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/36 |
| assetutilities | #35 | productivity | Consolidate repos | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/35 |
| assetutilities | #33 | productivity | Consolidate data | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/33 |
| assetutilities | #31 | tech debt | ACMA | Source Files | Sync vs. Copy | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/31 |
| assetutilities | #30 | tech debt | AI agents | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/30 |
| assetutilities | #29 | tech debt | switch engine to registry design pattern | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/29 |
| assetutilities | #28 | tech debt | switch to loguru | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/28 |
| assetutilities | #19 | tech debt | git | branch, computer and multiuser merge | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assetutilities/issues/19 |
| worldenergydata | #353 | fix(scheduler): diagnose uv/scheduler no-op command timeouts | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/worldenergydata/issues/353 |
| worldenergydata | #278 | Restore broken modules.* compatibility shims after bsee and marine_safety consolidation | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/worldenergydata/issues/278 |
| assethold | #46 | follow-up(ci): reconcile duplicate non-package reporting path_utils helper | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/46 |
| assethold | #45 | follow-up(ci): clean or retire auxiliary agent-os Python files excluded from package lint gate | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/45 |
| assethold | #44 | Decide --render-charts default dir (fail-loud vs ./dashboard-charts/) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/44 |
| assethold | #43 | Wire insider_tracker into WatchlistRunner.insider_flags_provider | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/43 |
| assethold | #42 | Wire settings.cache_ttl_hours through StockDataSource consumers (orphan config) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/42 |
| assethold | #40 | Phase 1.5 — pre-market/after-hours support + configurable bell buffer | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/40 |
| assethold | #37 | chore: update git origin to vamseeachanta/assethold canonical URL | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/37 |
| assethold | #36 | Multifamily sensitivity and stress-test scenarios (TODOs a–e) | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/36 |
| assethold | #34 | Assess and integrate real-time stock price feeds across modules | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/34 |
| assethold | #33 | Architecture documentation — module diagram, MkDocs build, data format specs | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/33 |
| assethold | #32 | Complete skeletal modules — fixed_interest, multifamily, net_lease | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/32 |
| assethold | #31 | Enforce quality gates — test coverage, mypy, loguru initialization | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/31 |
| assethold | #28 | Portfolio future outlook — probabilistic high/low projection bands | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/28 |
| assethold | #27 | Portfolio performance benchmark vs SPY | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/27 |
| assethold | #26 | Dividend reinvestment and ex-date calendar | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/26 |
| assethold | #25 | Tax lot aging report — long-term capital gains optimizer | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/25 |
| assethold | #24 | Market disruption monitor — 30-min cron during volatile sessions | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/24 |
| assethold | #23 | WhatsApp trade signals at market open and close | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/23 |
| assethold | #22 | Daily portfolio report as PDF emailed to inbox | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/22 |
| assethold | #21 | Portfolio Dashboard: Automated Allocation Tracking & Daily Review | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/21 |
| assethold | #18 | WRK-1199: Fama-French factor model | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/18 |
| assethold | #17 | WRK-1198: Dividend yield forecasting | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/17 |
| assethold | #12 | Running Task List | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/12 |
| assethold | #11 | repo | guidelines | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/11 |
| assethold | #8 | Literature | Running Board | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/8 |
| assethold | #7 | Portfolio value  | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/7 |
| assethold | #5 | Breakout | Trends | Backtesting | plan + approval marker; not working; clean clone | https://github.com/vamseeachanta/assethold/issues/5 |

## Repo-structure normalization wave audit

| Repo | Issue | Live labels/classification | Plan | Approval marker | Local state | Action |
|---|---:|---|---|---|---|---|
| workspace-hub | #2656 | priority:high, cat:engineering, cat:harness, domain:repo-organization, status:plan-approved; **GOVERNANCE_DRIFT** | yes: docs/plans/2026-05-08-issue-2656-repo-structure-normalization.md | NO | `main eecdf049c35b eecdf049c35b 0/0 dirty=0` | Do not launch until missing plan/approval marker is reconciled or regenerated. |
| assetutilities | #78 | status:plan-approved; **EXECUTABLE_CANDIDATE** | yes: docs/plans/2026-05-08-issue-78-repo-structure-normalization.md | yes | `main 3284e1a5a2dd 3284e1a5a2dd 0/0 dirty=0` | Launch first; already has full gate evidence. |
| worldenergydata | #394 | priority:high, cat:engineering, status:plan-approved; **GOVERNANCE_DRIFT** | NO | NO | `main ef38cb693559 ef38cb693559 0/0 dirty=0` | Do not launch until missing plan/approval marker is reconciled or regenerated. |
| assethold | #49 | cat:engineering, priority:high, status:plan-approved; **GOVERNANCE_DRIFT** | yes: docs/plans/2026-05-08-issue-49-repo-structure-normalization.md | NO | `main 096071baad9b 096071baad9b 0/0 dirty=0` | Do not launch until missing plan/approval marker is reconciled or regenerated. |
| aceengineer-website | #13 | priority:high, status:plan-approved; **GOVERNANCE_DRIFT** | yes: docs/plans/2026-05-08-issue-13-repo-structure-normalization.md | NO | `main df75720842af df75720842af 0/0 dirty=0` | Do not launch until missing plan/approval marker is reconciled or regenerated. |
| aceengineer-strategy | #19 | strategy, status:plan-approved; **GOVERNANCE_DRIFT** | yes: docs/plans/2026-05-08-issue-19-repo-structure-normalization.md | NO | `main 9057555e35f8 9057555e35f8 0/0 dirty=0` | Do not launch until missing plan/approval marker is reconciled or regenerated. |

## Governance drift examples

- workspace-hub #2656: missing approval marker — chore(repo-structure): normalize workspace-hub folder/file structure (https://github.com/vamseeachanta/workspace-hub/issues/2656)
- workspace-hub #2628: missing approval marker — epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern (https://github.com/vamseeachanta/workspace-hub/issues/2628)
- workspace-hub #2552: missing approval marker — docs(security): external contributor and unsolicited paid-help response runbook (https://github.com/vamseeachanta/workspace-hub/issues/2552)
- workspace-hub #2550: missing approval marker — chore(security): codify public repo interaction-limit renewal in scheduled tasks (https://github.com/vamseeachanta/workspace-hub/issues/2550)
- workspace-hub #2152: missing plan — test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage (https://github.com/vamseeachanta/workspace-hub/issues/2152)
- workspace-hub #2112: missing plan — data(field-dev): backfill SubseaIQ equipment counts to unblock cost benchmarking (https://github.com/vamseeachanta/workspace-hub/issues/2112)
- digitalmodel #515: missing plan + approval marker — Clarify and close semantic-equivalence gaps between spec/LLM-friendly YAML and OrcaFlex strict YAML (https://github.com/vamseeachanta/digitalmodel/issues/515)
- digitalmodel #503: missing plan + approval marker — Ingest OrcaFlex/OrcaWave online help into LLM-accessible format (https://github.com/vamseeachanta/digitalmodel/issues/503)
- digitalmodel #501: missing plan + approval marker — OrcaWave: expand QTF config + field points + irregular frequency method (https://github.com/vamseeachanta/digitalmodel/issues/501)
- digitalmodel #500: missing plan + approval marker — OrcaWave: mesh file pre-flight validation + auto-copy in runner (https://github.com/vamseeachanta/digitalmodel/issues/500)
- digitalmodel #486: missing plan + approval marker — Implement subsea connectors and jumpers module (API 17R) (https://github.com/vamseeachanta/digitalmodel/issues/486)
- digitalmodel #282: missing plan + approval marker — WRK-130: Standardize analysis reporting for each OrcaWave structure type (https://github.com/vamseeachanta/digitalmodel/issues/282)
- digitalmodel #279: missing plan + approval marker — WRK-129: Standardize analysis reporting for each OrcaFlex structure type (https://github.com/vamseeachanta/digitalmodel/issues/279)
- worldenergydata #394: missing plan + approval marker — chore(repo-structure): normalize worldenergydata folder/file structure (https://github.com/vamseeachanta/worldenergydata/issues/394)
- worldenergydata #368: missing approval marker — chore(hygiene): periodic verifier for recently-closed issues — catch claimed-shipped vs not-actually-shipped drift (https://github.com/vamseeachanta/worldenergydata/issues/368)
- worldenergydata #367: missing approval marker — refactor(bsee): migrate ProductionAPI12 NPV from legacy path to FDAS forward layer (#357 follow-up) (https://github.com/vamseeachanta/worldenergydata/issues/367)
- worldenergydata #366: missing approval marker — feat(data): HSE bulk deduplication + ingest pipeline (unlocks 6.8 GB at /mnt/ace) (https://github.com/vamseeachanta/worldenergydata/issues/366)
- worldenergydata #365: missing approval marker — feat(data): BSEE binary tier decompression + ingest pipeline (unlocks 2.7 GB) (https://github.com/vamseeachanta/worldenergydata/issues/365)
- worldenergydata #364: missing approval marker — docs(gtm): publish capability matrix — production-ready vs sample-only vs roadmap (https://github.com/vamseeachanta/worldenergydata/issues/364)
- worldenergydata #363: missing approval marker — feat(api): public Python query API for HSE module — parity with marine_safety surface (https://github.com/vamseeachanta/worldenergydata/issues/363)
- worldenergydata #362: missing approval marker — feat(report): operator cost benchmarking from annual disclosures (HTML + notebook) (https://github.com/vamseeachanta/worldenergydata/issues/362)
- worldenergydata #361: missing approval marker — feat(provenance): adopt calc-citation-contract for worldenergydata calc outputs (https://github.com/vamseeachanta/worldenergydata/issues/361)
- worldenergydata #360: missing approval marker — ops(scheduler): verify and instrument refresh health — last successful run 2026-03-25 (37 days stale) (https://github.com/vamseeachanta/worldenergydata/issues/360)
- worldenergydata #352: missing approval marker — audit(cli): verify public CLI examples and smoke-test pathways (https://github.com/vamseeachanta/worldenergydata/issues/352)
- worldenergydata #351: missing approval marker — audit(scheduler): prepare source refresh runtime readiness matrix (https://github.com/vamseeachanta/worldenergydata/issues/351)
- worldenergydata #350: missing approval marker — audit(data): build data completeness and freshness scorecard (https://github.com/vamseeachanta/worldenergydata/issues/350)
- worldenergydata #349: missing approval marker — audit(repo): build capability inventory and module readiness matrix (https://github.com/vamseeachanta/worldenergydata/issues/349)
- worldenergydata #344: missing approval marker — feat(cost): add restatement/version lineage for annual disclosure records (https://github.com/vamseeachanta/worldenergydata/issues/344)
- worldenergydata #343: missing approval marker — feat(cost): build major-operator annual statement source registry and yearly coverage tracker (https://github.com/vamseeachanta/worldenergydata/issues/343)
- worldenergydata #342: missing approval marker — bug(cost): restore broken proxy comparison regression boundary (https://github.com/vamseeachanta/worldenergydata/issues/342)
- ... 44 additional governance-drift issues omitted from this summary.

## Already-working / implementation-state audit pool

- workspace-hub #2402: feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2402
- workspace-hub #2403: feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2403
- workspace-hub #2327: digitalmodel: CadQuery spike for parametric offshore geometry generation — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2327
- workspace-hub #2269: feat(openfoam): standardize ESI v2312 baseline workflow and validation — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2269
- workspace-hub #2229: feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2229
- workspace-hub #2129: chore(harness): automate issue-state drift and redundancy audit across GitHub + analysis artifacts — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2129
- workspace-hub #2124: feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2124
- workspace-hub #2125: feat(llm-wiki): auto-refresh ingestion on new Orcina releases — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2125
- workspace-hub #2055: feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2055
- workspace-hub #2046: Audit compliance of strict issue planning workflow after rollout — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/2046
- workspace-hub #1962: FEATURE: Tier-1 Repo Ecosystem Refactoring — audit, plan, execute with Claude Code plan mode — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/1962
- workspace-hub #1782: epic: zero-loss agent learnings — git-track ALL AI agent memories, corrections, patterns, and insights — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/1782
- workspace-hub #1583: Hermes config parity via repo ecosystem templates — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/1583
- workspace-hub #1264: WRK-1365: OrcaFlex frame analysis — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/workspace-hub/issues/1264
- digitalmodel #504: OrcaFlex buoys builder refactor: split 611-line mega-builder into focused builders — labels include working/WIP; audit branch/PR/current artifacts before new assignment. https://github.com/vamseeachanta/digitalmodel/issues/504

## Next executable wave recommendation

1. **Primary lane:** `assetutilities#78` is the only repo-structure normalization issue that currently satisfies all execution evidence checks (`status:plan-approved`, plan file, approval marker, no `status:working`, clean/synced clone). It should be the first implementation lane; rerun the full baseline before edits because the prior baseline was interrupted.
2. **Governance-reconciliation lanes before launch:** `workspace-hub#2656`, `worldenergydata#394`, `assethold#49`, `aceengineer-website#13`, and `aceengineer-strategy#19` are live approved but are missing local approval markers and/or local plan artifacts. Reconcile those markers/plans before assigning implementation workers.
3. **Do not execute:** `digitalmodel#596` remains `status:plan-review`; it has plan/review artifacts but lacks approval label/marker. Keep it in plan-review until user approval and marker creation.
4. **WIP cap:** start with one implementation lane plus up to two governance-reconciliation lanes. Avoid a broad multiagent execution wave until each lane has plan + marker + clean isolated worktree proof.

## Launch gates

- Create/use isolated clean worktrees for each execution lane; do not work in dirty root/nested clones.
- Post an execution-start comment only after the evidence gate is complete for that issue.
- Run repo baseline validation before edits and final canonical validation before closeout.
- Close only after push/merge, branch/worktree cleanup, and clean/synced proof in the same window.
