# Domain Kanban — domain:marine

Generated: 2026-05-06

Scope: Issues routed to `domain:marine`

## Repo distribution

| Repo | Open issues |
| --- | --- |
| workspace-hub | 35 |
| digitalmodel | 37 |
| assetutilities | 0 |
| worldenergydata | 1 |
| assethold | 0 |
| aceengineer-website | 0 |
| aceengineer-strategy | 0 |

## Lane counts

| Lane | Count |
| --- | --- |
| Blocked / Waiting | 0 |
| In Progress / Status Working | 3 |
| State Conflict / Hygiene | 0 |
| Plan Review / Needs Approval | 1 |
| Approved Label Drift / Repair Before Execution | 4 |
| Ready / Plan Approved | 19 |
| Other Status / Triage | 0 |
| Planning Needed / Future Backlog | 46 |
| Done / Recently Closed | 15 |

## Review lanes

### Blocked / Waiting (0)

_None._

### In Progress / Status Working (3)

- [digitalmodel#504](https://github.com/vamseeachanta/digitalmodel/issues/504) — OrcaFlex buoys builder refactor: split 611-line mega-builder into focused builders _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:working, status:plan-approved)_
- [workspace-hub#2124](https://github.com/vamseeachanta/workspace-hub/issues/2124) — feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials _(agent: `agent:codex`, priority: `MEDIUM`, domains: `domain:marine, domain:knowledge-management`; labels: enhancement, priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, status:working)_
- [workspace-hub#2125](https://github.com/vamseeachanta/workspace-hub/issues/2125) — feat(llm-wiki): auto-refresh ingestion on new Orcina releases _(agent: `agent:codex`, priority: `MEDIUM`, domains: `domain:marine, domain:knowledge-management`; labels: enhancement, priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, status:working)_

### State Conflict / Hygiene (0)

_None._

### Plan Review / Needs Approval (1)

- [digitalmodel#559](https://github.com/vamseeachanta/digitalmodel/issues/559) — fix(marine_ops): test_hydro_rao_integration.py::test_full_matrix_interpolation — strict-greater on equal floats (use >=) _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-review)_

### Approved Label Drift / Repair Before Execution (4)

- [digitalmodel#500](https://github.com/vamseeachanta/digitalmodel/issues/500) — OrcaWave: mesh file pre-flight validation + auto-copy in runner _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#501](https://github.com/vamseeachanta/digitalmodel/issues/501) — OrcaWave: expand QTF config + field points + irregular frequency method _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#503](https://github.com/vamseeachanta/digitalmodel/issues/503) — Ingest OrcaFlex/OrcaWave online help into LLM-accessible format _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [worldenergydata#278](https://github.com/vamseeachanta/worldenergydata/issues/278) — Restore broken modules.* compatibility shims after bsee and marine_safety consolidation _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: status:plan-approved)_

### Ready / Plan Approved (19)

- [digitalmodel#507](https://github.com/vamseeachanta/digitalmodel/issues/507) — OrcaFlex reference: complete Orcina help ingestion — environment, waves, current pages _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: documentation, status:plan-approved)_
- [digitalmodel#508](https://github.com/vamseeachanta/digitalmodel/issues/508) — OrcaFlex spec upgrader v2: rewrite generic specs to domain-specific sections _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#509](https://github.com/vamseeachanta/digitalmodel/issues/509) — OrcaFlex: add pre-commit hook for YAML-strict validation on spec changes _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#529](https://github.com/vamseeachanta/digitalmodel/issues/529) — OrcaFlex: convert_batch() parallel path doesn't aggregate success counts into self.stats _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#530](https://github.com/vamseeachanta/digitalmodel/issues/530) — OrcaFlex tests: hoist class-scoped fixtures in test_orcaflex_converter_enhanced.py to module level _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#531](https://github.com/vamseeachanta/digitalmodel/issues/531) — OrcaFlex: follow-up — 9 pre-existing test failures across 5 files not covered by #510 plan scope _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#534](https://github.com/vamseeachanta/digitalmodel/issues/534) — OrcaFlex: _apply_overrides direct-call StopIteration guard _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#535](https://github.com/vamseeachanta/digitalmodel/issues/535) — OrcaFlex: apply_dotted_override should chain ValidationError with dotted-path context _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#536](https://github.com/vamseeachanta/digitalmodel/issues/536) — OrcaFlex: per-iteration model_validate perf for large sweep matrices _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#537](https://github.com/vamseeachanta/digitalmodel/issues/537) — OrcaFlex: manifest.yml not written when all runs skipped — clarify docstring + behavior _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:plan-approved)_
- [digitalmodel#556](https://github.com/vamseeachanta/digitalmodel/issues/556) — fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_get_coefficients_interpolation — CYw=-3.56 not in [0,1.5] _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#557](https://github.com/vamseeachanta/digitalmodel/issues/557) — fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_boundary_warnings — DID NOT WARN on out-of-range query _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#558](https://github.com/vamseeachanta/digitalmodel/issues/558) — fix(marine_ops): test_hydro_rao_integration.py::test_damping_affects_phase — phase 138° not near -90° (sign convention) _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#560](https://github.com/vamseeachanta/digitalmodel/issues/560) — fix(marine_ops): test_hydro_rao_integration.py::test_coupling_terms_affect_response — needs investigation _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#561](https://github.com/vamseeachanta/digitalmodel/issues/561) — fix(marine_ops): test_ocimf_mooring_integration.py::test_combined_environmental_forces — wrong test premise (current dominates) _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#562](https://github.com/vamseeachanta/digitalmodel/issues/562) — fix(marine_ops): test_marine_eng_performance.py::test_complete_workflow_performance — numpy.bool_ not JSON serializable _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#563](https://github.com/vamseeachanta/digitalmodel/issues/563) — fix(marine_ops): test_marine_eng_performance.py::test_ocimf_database_performance — needs investigation _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#564](https://github.com/vamseeachanta/digitalmodel/issues/564) — fix(marine_ops): test_ocimf_mooring_integration.py::test_environmental_forces_to_mooring_tension — needs investigation _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_
- [digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565) — fix(marine_ops): test_hydro_coefficients.py::TestIntegration::test_csv_to_visualization_workflow — needs investigation _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:plan-approved)_

### Other Status / Triage (0)

_None._

### Planning Needed / Future Backlog (46)

- [digitalmodel#9](https://github.com/vamseeachanta/digitalmodel/issues/9) — OrcaFlex | Installation | Rigging module _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, package, wrk-item)_
- [digitalmodel#13](https://github.com/vamseeachanta/digitalmodel/issues/13) — OrcaFlex | Installation | Modal Analysis  _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, package, wrk-item)_
- [digitalmodel#16](https://github.com/vamseeachanta/digitalmodel/issues/16) — OrcaFlex | SeastateRAOs | Visualizations _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: feature, package, wrk-item)_
- [digitalmodel#18](https://github.com/vamseeachanta/digitalmodel/issues/18) — OrcaFlex | SeastateRAOs | Filtering for analysis _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, package, wrk-item)_
- [digitalmodel#19](https://github.com/vamseeachanta/digitalmodel/issues/19) — OrcaFlex | Postprocess | Visualizations | For a/ QA and b/ Report _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, package, wrk-item)_
- [digitalmodel#40](https://github.com/vamseeachanta/digitalmodel/issues/40) — OrcaFlex | Installation | Batch Files | Reiterate runs and save positions do not fail silently   _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: bug, package, wrk-item)_
- [digitalmodel#41](https://github.com/vamseeachanta/digitalmodel/issues/41) — OrcaFlex | Installation | Implement catenary equations _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, wrk-item)_
- [digitalmodel#62](https://github.com/vamseeachanta/digitalmodel/issues/62) — engg debt | OrcaWave _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: feature, package, wrk-item)_
- [digitalmodel#82](https://github.com/vamseeachanta/digitalmodel/issues/82) — OrcaFlex | Postprocess enhancements _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, package, wrk-item)_
- [digitalmodel#96](https://github.com/vamseeachanta/digitalmodel/issues/96) — OrcaFlex | Iterate to achieve targets _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: wrk-item)_
- [digitalmodel#588](https://github.com/vamseeachanta/digitalmodel/issues/588) — fix(marine_ops): test_find_chain_with_safety_factor needs chain entry ≥78mm R4 _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`)_
- [digitalmodel#589](https://github.com/vamseeachanta/digitalmodel/issues/589) — fix(marine_ops): test_weight_scales_with_diameter_squared queries 20mm not in chain DB array _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`)_
- [digitalmodel#590](https://github.com/vamseeachanta/digitalmodel/issues/590) — fix(marine_ops): test_database_performance has flaky 1ms perf assertion (observed 1–2ms) _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`)_
- [workspace-hub#21](https://github.com/vamseeachanta/workspace-hub/issues/21) — WRK-039: SPM project benchmarking - AQWA vs OrcaFlex _(agent: `agent:claude`, priority: `MEDIUM`, domains: `domain:marine`; labels: enhancement, priority:medium, cat:engineering, domain:marine)_
- [workspace-hub#22](https://github.com/vamseeachanta/workspace-hub/issues/22) — WRK-043: Parametric hull form analysis with RAO generation and client-facing lookup _(agent: `agent:codex`, priority: `LOW`, domains: `domain:marine`; labels: enhancement, priority:low, cat:engineering, domain:marine)_
- [workspace-hub#24](https://github.com/vamseeachanta/workspace-hub/issues/24) — WRK-046: OrcaFlex drilling and completion riser parametric analysis _(agent: `agent:claude`, priority: `MEDIUM`, domains: `domain:marine`; labels: enhancement, priority:medium, cat:engineering, domain:marine)_
- [workspace-hub#28](https://github.com/vamseeachanta/workspace-hub/issues/28) — WRK-075: OFFPIPE Integration Module \u2014 pipelay cross-validation against OrcaFlex _(agent: `agent:claude`, priority: `LOW`, domains: `domain:marine`; labels: enhancement, priority:low, cat:engineering, domain:marine)_
- [workspace-hub#29](https://github.com/vamseeachanta/workspace-hub/issues/29) — WRK-099: Run 3-way benchmark on Unit Box hull _(agent: `agent:claude`, priority: `MEDIUM`, domains: `domain:marine`; labels: enhancement, priority:medium, cat:engineering, domain:marine)_
- [workspace-hub#1586](https://github.com/vamseeachanta/workspace-hub/issues/1586) — Harden solver queue: batch submission, result watcher, auto post-processing _(agent: `agent:claude`, priority: `HIGH`, domains: `domain:marine`; labels: enhancement, priority:high, cat:engineering, domain:marine, machine:licensed-win-1)_
- [workspace-hub#1591](https://github.com/vamseeachanta/workspace-hub/issues/1591) — Seed hull registry with standard hull forms (barge, tanker, semi-sub, spar, FPSO) _(agent: `agent:claude`, priority: `MEDIUM`, domains: `domain:marine`; labels: enhancement, priority:medium, cat:engineering, domain:marine)_
- … 26 more in data artifact / dashboard filters

### Done / Recently Closed (15)

- [digitalmodel#495](https://github.com/vamseeachanta/digitalmodel/issues/495) — OrcaFlex YAML-strict validator — automated load-test for generated files _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#496](https://github.com/vamseeachanta/digitalmodel/issues/496) — OrcaFlex spec schema: multi-wave-train + multi-current-profile support _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#497](https://github.com/vamseeachanta/digitalmodel/issues/497) — OrcaFlex builders: raw_properties round-trip emission + cross-builder validation _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#498](https://github.com/vamseeachanta/digitalmodel/issues/498) — OrcaFlex builder test coverage uplift — missing builder + integration tests _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#499](https://github.com/vamseeachanta/digitalmodel/issues/499) — OrcaFlex model library: upgrade extracted specs from generic to domain-specific sections _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#502](https://github.com/vamseeachanta/digitalmodel/issues/502) — OrcaFlex spec audit: fix remaining 13 failures to reach 100% readiness _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#505](https://github.com/vamseeachanta/digitalmodel/issues/505) — OrcaFlex: emit raw_properties in EnvironmentBuilder for round-trip fidelity _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement)_
- [digitalmodel#510](https://github.com/vamseeachanta/digitalmodel/issues/510) — OrcaFlex: fix 20 pre-existing test failures in orcaflex test suite _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: bug, status:done)_
- [digitalmodel#511](https://github.com/vamseeachanta/digitalmodel/issues/511) — OrcaFlex: campaign spec generation — parametric sweep from spec.yml _(agent: `agent:any`, priority: `Unranked`, domains: `domain:marine`; labels: enhancement, status:done)_
- [digitalmodel#555](https://github.com/vamseeachanta/digitalmodel/issues/555) — fix(marine_ops): _generate_chain_database diameters[:20] excludes 76mm — clears 4 of 77 marine_ops failures _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: status:plan-approved)_
- [workspace-hub#2601](https://github.com/vamseeachanta/workspace-hub/issues/2601) — audit(llm-wiki): marine-engineering wiki gap audit + prioritized backfill sequence (W4-C) _(agent: `agent:claude`, priority: `HIGH`, domains: `domain:marine, domain:knowledge-management`; labels: priority:high, cat:documentation, domain:marine, domain:knowledge-management, status:done)_
- [workspace-hub#2603](https://github.com/vamseeachanta/workspace-hub/issues/2603) — fix(digitalmodel): re-export load_packaged_rudder_stock_torque_yaml from naval_architecture/__init__.py _(agent: `agent:codex`, priority: `MEDIUM`, domains: `domain:marine`; labels: priority:medium, status:plan-approved)_
- [workspace-hub#2605](https://github.com/vamseeachanta/workspace-hub/issues/2605) — chore(digitalmodel): ruff cleanup for naval_architecture/test_vessel_fleet_adapter.py (13 F401) _(agent: `agent:codex`, priority: `LOW`, domains: `domain:marine`; labels: priority:low, status:plan-approved)_
- [workspace-hub#2612](https://github.com/vamseeachanta/workspace-hub/issues/2612) — feat(llm-wiki): lng-projects wiki topical expansion — 8 concept/entity pages (W5-C) _(agent: `agent:claude`, priority: `MEDIUM`, domains: `domain:marine, domain:knowledge-management`; labels: priority:medium, cat:documentation, domain:marine, domain:knowledge-management, status:done)_
- [worldenergydata#327](https://github.com/vamseeachanta/worldenergydata/issues/327) — Test infra: conftest.py blocks pytest collection of tests/unit/marine_safety/ _(agent: `agent:codex`, priority: `Unranked`, domains: `domain:marine`; labels: status:plan-approved)_

