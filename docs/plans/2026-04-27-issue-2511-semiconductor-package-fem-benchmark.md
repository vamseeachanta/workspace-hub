# Plan for #2511: Semiconductor package thermal/thermo-mechanical FEM benchmark

> **Status:** draft — r1 adversarial review MAJOR, revised for r2
> **Complexity:** T3
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2511
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2511-claude-r1.md | scripts/review/results/2026-04-26-plan-2511-codex-r1.md | scripts/review/results/2026-04-26-plan-2511-gemini-r1.md | scripts/review/results/2026-04-26-plan-2511-claude.md | scripts/review/results/2026-04-26-plan-2511-codex.md

---

## Resource Intelligence Summary

### Existing repo code
- `tests/docs/test_semiconductor_kb.py` exists from #2508 and validates the research/taxonomy foundation for the semiconductor lane. It does not implement any FEM benchmark.
- `docs/reports/semiconductor-cad-fem-knowledge-base.md` exists and explicitly recommends #2511 as the first practical portfolio benchmark: a simple die/substrate/package thermal and thermal-stress model with assumptions and no proprietary standards claims.
- `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` exists and maps `ic-packaging-simulation`, `semiconductor-mechanical-thermal-engineer`, and `advanced-packaging-engineer` to #2511.
- Gap: no `scripts/semiconductor/`, no `tests/semiconductor/`, no `data/semiconductor/`, and no `docs/reports/semiconductor-package-fem-benchmark.md` exist yet.

### Standards and source limits
| Source / standard family | Status | Finding |
|---|---|---|
| JEDEC reliability concepts / JESD22 family | restricted or not locally ingested | #2508 taxonomy permits vocabulary only; this issue must not claim JEDEC compliance or extract proprietary requirements. |
| IPC electronics packaging terminology | restricted or not locally ingested | #2508 taxonomy permits vocabulary only; this issue must not claim IPC compliance. |
| `data/document-index/standards-transfer-ledger.yaml` | exists | Ledger is offshore/mechanical heavy; no local semiconductor packaging standards were found as implementation requirements for #2511. |
| `data/document-index/online-resource-registry.yaml` | exists | General engineering/solver resources are registered; #2511 should cite open solver documentation and local research, not restricted standards. |
| `data/design-codes/code-registry.yaml` | exists | Canonical design-code registry per `docs/document-intelligence/data-intelligence-map.md`; entries are DNV/API/ASTM/ISO/BS offshore/mechanical codes, with no semiconductor package standards entry. Consulted to satisfy the engineering retrieval bundle and confirm no hidden JEDEC/IPC implementation source exists locally. |
| `data/document-index/code-registry.yaml` | missing legacy/wrong path | This path is not the canonical registry; the canonical registry is `data/design-codes/code-registry.yaml`. |

### LLM wiki / knowledge pages consulted
- `docs/reports/semiconductor-cad-fem-knowledge-base.md` — identifies package FEM / thermal-mechanical analysis as the strongest near-term bridge from existing engineering experience.
- `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` — identifies CalculiX, FEniCSx, Elmer, scikit-fem, ParaView, and Python as relevant tools for package FEM.
- `docs/document-intelligence/data-intelligence-map.md` — identifies `data/design-codes/code-registry.yaml` as the design-code registry; this corrected the r1 review finding that the draft checked the wrong `data/document-index/code-registry.yaml` path.
- `knowledge/wikis/engineering/wiki/sources/2026-04-17-hn-cadquery.md` — confirms Python CAD/STEP/mesh pipeline vocabulary and the geometry → mesh → solver input pattern, but #2511 should not wait on #2510 layout/CAD geometry.

### Documents consulted
- Issue #2511 body — requires simplified package stackup, material properties with CTE/thermal assumptions, local solver path preferably CalculiX first, plots, and an engineering report.
- Parent issue #2507 — open umbrella for the semiconductor chip-design CAD/FEM career lane.
- Sibling issues #2510, #2509, #2512 — remain open; #2511 must not mutate them or depend on their implementation.
- `docs/research/open-source-fea-survey.md` — ranks CalculiX first for Linux engineering assignments; notes CalculiX supports structural, thermal, and thermo-mechanical workflows and integrates with Gmsh/ParaView.
- `docs/research/scikit-fem-eval.md` — scikit-fem is useful for Python-native prototypes and mesh I/O but has no shell elements or built-in post-processor; use it as optional follow-up, not as the first solver target.
- `docs/resources/structural-resources.md` — lists CalculiX, Gmsh, FEniCSx, FreeCAD, Elmer, ParaView, SciPy, SfePy, and SALib as structural/FEA resources.
- External probes on 2026-04-27 returned HTTP 200 for CalculiX, Gmsh docs, CalculiX PDF, scikit-fem docs, and FEniCS project; Elmer docs probe returned 403 and is therefore not a first-wave dependency.

### Environment findings
- `ccx` exists at `/home/vamsee/.local/bin/ccx` in the planning worktree host.
- `gmsh` exists at `/home/vamsee/.local/bin/gmsh` in the planning worktree host.
- Fresh `uv run` environment currently contains `yaml` but not `numpy`, `scipy`, `matplotlib`, `plotly`, `gmsh`, `meshio`, or `skfem`. Therefore the first implementation should use Python stdlib for generation/validation/reporting and treat external solver execution as optional/gated unless the command is available.

### Gaps identified
- No implemented package stackup geometry/mesh generator.
- No solver-ready CalculiX input deck for semiconductor package thermal or thermal-stress benchmark.
- No deterministic post-processing parser/summary/report for benchmark artifacts.
- No tests covering mesh/input generation, materials/units/provenance, solver-output parsing/smoke status, result-plot artifact generation, report limitations, or standards-claim guardrails.
- No committed report explaining boundary conditions, loads, materials, units, convergence/limitations, and portfolio framing.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27T01:56:51Z via `gh issue view`):
- `#2507` — OPEN — Feature: semiconductor chip-design CAD/FEM career lane
- `#2508` — CLOSED — research(semiconductor): build chip-design CAD/FEM knowledge base and job taxonomy
- `#2509` — OPEN — feat(eda): create reproducible OpenLane/OpenROAD RTL-to-GDS demo report
- `#2510` — OPEN — feat(cad): build Python layout/CAD automation demo for chip/package geometries
- `#2511` — OPEN — feat(fem): create semiconductor package thermal/thermo-mechanical benchmark
- `#2512` — OPEN — feat(career): build semiconductor CAD/FEM portfolio and job-application packet

**File existence** (verified 2026-04-27T01:56:51Z):
- EXISTS: `tests/docs/test_semiconductor_kb.py`
- EXISTS: `docs/reports/semiconductor-cad-fem-knowledge-base.md`
- EXISTS: `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml`
- MISSING (new): `scripts/semiconductor/package_fem_benchmark.py`
- MISSING (new): `tests/semiconductor/test_package_fem_benchmark.py`
- MISSING (new): `data/semiconductor/package_fem_benchmark/`
- MISSING (new): `data/semiconductor/package_fem_benchmark/temperature_profile.svg`
- MISSING (new): `data/semiconductor/package_fem_benchmark/stress_warpage_estimates.svg`
- MISSING (new): `docs/reports/semiconductor-package-fem-benchmark.md`

**Tool availability** (verified 2026-04-27T01:56:51Z):
```text
ccx: /home/vamsee/.local/bin/ccx
gmsh: /home/vamsee/.local/bin/gmsh
uv: /home/vamsee/.local/bin/uv
python: /home/vamsee/miniforge3/bin/python
```

**Fresh uv package availability** (verified 2026-04-27T01:56:51Z):
```text
numpy: False
scipy: False
matplotlib: False
plotly: False
yaml: True
gmsh: False
meshio: False
skfem: False
```

**Line excerpts:**
```text
# docs/reports/semiconductor-cad-fem-knowledge-base.md
15: 2. #2511 — create a semiconductor package thermal/thermo-mechanical FEM benchmark.
87: The package FEM lane is the strongest near-term bridge from existing engineering experience. The #2511 benchmark should start with simple, traceable assumptions: material stack, package/die/substrate abstraction, thermal load or temperature delta, constraints, mesh notes, and stress/warpage/temperature interpretation.
110: #2511: prioritize the first benchmark as a simple die/substrate/package thermal and thermal-stress model with a short verification report and no proprietary standards claims.

# docs/research/open-source-fea-survey.md
51: CalculiX is a mature, lightweight structural FEA solver with Abaqus-compatible input format...
53: Its solver (CCX) handles linear/nonlinear static, dynamic, thermal, and coupled thermo-mechanical problems.
139: Rank 1: CalculiX (with FreeCAD FEM Workbench + Gmsh + ParaView)

# docs/research/scikit-fem-eval.md
67: Zero-compilation install — pip install scikit-fem; works on any Python 3.10+ environment with no MPI, no Docker
74-79: limitations include no shell elements, no built-in contact/nonlinear material, no integrated post-processor
```

Source count: 8+ distinct sources (issue body, parent/sibling issues, #2508 report, #2508 taxonomy, open-source FEA survey, scikit-fem evaluation, structural resources, external tool probes).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2511-semiconductor-package-fem-benchmark.md` |
| Tests | `tests/semiconductor/test_package_fem_benchmark.py` |
| Implementation | `scripts/semiconductor/package_fem_benchmark.py` |
| Generated benchmark artifacts | `data/semiconductor/package_fem_benchmark/` |
| Report | `docs/reports/semiconductor-package-fem-benchmark.md` |
| Plan review — Claude r1 | `scripts/review/results/2026-04-26-plan-2511-claude-r1.md` |
| Plan review — Codex r1 | `scripts/review/results/2026-04-26-plan-2511-codex-r1.md` |
| Plan review — Gemini r1 | `scripts/review/results/2026-04-26-plan-2511-gemini-r1.md` |
| Plan review — Claude r2 | `scripts/review/results/2026-04-26-plan-2511-claude.md` |
| Plan review — Codex r2 | `scripts/review/results/2026-04-26-plan-2511-codex.md` |
| Plan review — Gemini r2 | `scripts/review/results/2026-04-26-plan-2511-gemini.md` |
| Plan review disagreement/synthesis | `scripts/review/results/2026-04-26-plan-2511-disagreement.md` |
| Artifact-map note | Review artifact filenames use the local review-execution date (`date +%F`), which may differ from the plan-publication date in the plan filename. |
| Implementation review | `scripts/review/results/2026-04-27-issue-2511-implementation-review.md` |

---

## Deliverable

A reproducible, stdlib-first semiconductor package FEM benchmark generator that emits a simplified multilayer package mesh/input deck, gated CalculiX smoke/run artifacts when `ccx` is available, deterministic summary data, temperature/stress/warpage-style SVG result plots, per-material provenance, and a portfolio-safe engineering report documenting assumptions, boundary conditions, units, convergence checks, and limitations.

---

## Scope Boundaries

### In scope now
- Simplified rectangular package stackup: substrate, die, mold/underfill abstraction, and simplified solder/interconnect representation as zones or lumped support features.
- Deterministic structured hexahedral mesh generator suitable for small CI/test cases and portfolio demonstration.
- Material table with SI units plus per-material `source` / `source_note`: elastic modulus, Poisson ratio, CTE, thermal conductivity, and representative temperature/load assumptions.
- CalculiX `.inp` writer for two solver decks:
  1. thermal deck / thermal-field setup where practical;
  2. thermo-mechanical deck or static mechanical deck with thermal-expansion loads represented in a traceable way.
- `ccx` execution wrapper guarded by `shutil.which("ccx")`: tests must not require solver availability, but the implementation/closeout must run a local CalculiX smoke path when `ccx` is present. `--no-solver` is only for deterministic artifact regeneration and is mutually exclusive with `--require-solver-smoke`; the CLI must reject both flags together. Solver rejection fails the issue closeout unless the user explicitly re-scopes #2511.
- Deterministic post-processing from generated input/summary artifacts; if real FRD parsing is too brittle for first wave, include a bounded parser for a small committed fixture plus analytical no-solver summary path.
- Markdown report with tables plus temperature profile and stress/warpage-style SVG result plots generated without non-stdlib plotting dependencies.
- Clear statement: portfolio benchmark only; not production-certified; no JEDEC/IPC compliance claim.
- Material values are representative educational handbook-style values with `source`/`source_note` provenance; the strict design-code citation schema in `.claude/rules/calc-citation-contract.md` is out of scope because this benchmark does not derive constants from controlled design codes or standards requirements.

### Out of scope now
- Full semiconductor package certification, JEDEC/IPC compliance, fatigue life prediction, nonlinear/contact solder fatigue, and production signoff.
- Dependence on proprietary foundry/package data.
- FEniCSx, Elmer, scikit-fem, FreeCAD, ParaView, or pyvista implementation beyond future issue notes.
- Mutating #2509, #2510, or #2512 issue bodies/labels.
- Requiring heavy Python packages not already present in the workspace-hub `uv run` environment.

---

## Pseudocode

```text
PackageLayer dataclass:
    store name, thickness_m, material_id, mesh_divisions_z
    validate positive thickness and integer divisions

Material dataclass:
    store name, E_Pa, nu, cte_per_K, k_W_m_K, density_kg_m3 optional, source, source_note
    validate engineering units, reasonable positive values, and non-empty provenance fields

BenchmarkSpec dataclass:
    define package length/width, layers, grid counts nx/ny, temperatures, heat flux/power, constraints
    compute total thickness and layer z offsets
    validate mesh resolution and unit consistency

build_default_spec():
    return a small benchmark: substrate + die + mold + solder-zone simplification
    use representative educational material values, not proprietary data

structured_hex_mesh(spec):
    create nodes on regular x/y grid and nonuniform z levels from each layer mesh_divisions_z
    assign elements to layer/material based on explicit layer z interval
    create named node/element sets for bottom, top, die, substrate, symmetry/reference surfaces
    return MeshModel(nodes, elements, sets, material assignment)

write_calculix_inputs(spec, mesh, output_dir):
    write common node/element/material sections
    write thermal .inp with material conductivity and temperature/flux boundary placeholders
    write mechanical .inp with elastic/expansion material data and simple constraints/load step
    include comments explaining simplifications and units

run_calculix_if_available(input_path, output_dir, require_solver_smoke=False, no_solver=False):
    if no_solver and require_solver_smoke: raise ValueError("--no-solver and --require-solver-smoke are mutually exclusive")
    if no_solver: return skipped status with reason no_solver_requested
    if ccx missing: return skipped status; if require_solver_smoke then raise a clear error
    run ccx in artifact directory with timeout
    capture stdout/stderr/status and expected artifact presence
    expected CalculiX smoke artifact is a non-empty .dat or .frd file with the same job basename; record .cvg/.sta when present as diagnostics
    if ccx exists and returns nonzero or no expected artifact, record failed; raise when require_solver_smoke=True

summarize_benchmark(spec, mesh, solver_status):
    compute mesh counts, element counts by material/layer, package dimensions, aspect-ratio checks
    compute simple analytical/sanity checks: layer thermal resistance per area, delta-T estimate from heat flux, free thermal strain estimate from CTE mismatch, curvature/warpage-style educational estimate
    write JSON and CSV summaries with units, material provenance, solver status, and artifact hashes

render_result_plots(spec, summary, output_dir):
    write temperature_profile.svg showing through-thickness temperature estimate
    write stress_warpage_estimates.svg showing layer CTE mismatch / normalized stress and warpage-style estimates
    write result_profiles.csv with plotted data and units

render_report(spec, summary, output_dir):
    create Markdown report at docs/reports/semiconductor-package-fem-benchmark.md
    embed generated tables, stackup schematic, temperature plot, and stress/warpage-style plot
    document boundary conditions, loads, materials, units, solver status, convergence notes, limitations, portfolio framing
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/semiconductor/test_package_fem_benchmark.py` | TDD suite for mesh generation, input deck generation, summary/report content, and standards guardrails |
| Create | `scripts/semiconductor/package_fem_benchmark.py` | Main stdlib-first benchmark generator, optional solver wrapper, post-processing, and report renderer |
| Create | `data/semiconductor/package_fem_benchmark/README.md` | Describes generated artifact directory, regeneration command, and artifact policy |
| Create | `data/semiconductor/package_fem_benchmark/package_thermal.inp` | Generated CalculiX thermal input deck fixture/artifact |
| Create | `data/semiconductor/package_fem_benchmark/package_thermomechanical.inp` | Generated CalculiX thermo-mechanical/static input deck fixture/artifact |
| Create | `data/semiconductor/package_fem_benchmark/mesh_summary.csv` | Generated mesh/material summary used by report/tests |
| Create | `data/semiconductor/package_fem_benchmark/result_profiles.csv` | Generated plotted temperature/stress/warpage-style profile data with units |
| Create | `data/semiconductor/package_fem_benchmark/benchmark_summary.json` | Generated benchmark metadata, units, assumptions, material provenance, solver status, and artifact hashes |
| Create | `data/semiconductor/package_fem_benchmark/artifact_manifest.sha256` | Regeneration/drift manifest for committed artifacts |
| Create | `data/semiconductor/package_fem_benchmark/package_stackup.svg` | Generated simple stackup schematic for report |
| Create | `data/semiconductor/package_fem_benchmark/temperature_profile.svg` | Generated temperature-result plot from analytical/smoke summary |
| Create | `data/semiconductor/package_fem_benchmark/stress_warpage_estimates.svg` | Generated stress/warpage-style plot from CTE mismatch sanity estimates |
| Create | `docs/reports/semiconductor-package-fem-benchmark.md` | Portfolio-safe engineering report |
| Update | `docs/plans/README.md` | Add #2511 plan row |
| Create | `.planning/plan-approved/2511.md` | Only after explicit user approval, before implementation commit |
| Create | `scripts/review/results/2026-04-27-issue-2511-implementation-review.md` | Post-implementation adversarial review artifact |

---

## TDD Test List

Write these tests before implementation.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_default_spec_uses_si_units_sources_and_required_layers` | default stackup has substrate/die/mold/solder abstraction, positive dimensions, SI unit fields, and per-material provenance | `build_default_spec()` | required layer/material names, positive unit-bearing values, and non-empty source fields |
| `test_structured_hex_mesh_counts_and_sets` | mesh generator produces deterministic node/element counts and boundary sets | small default spec | expected counts and sets: top, bottom, die, substrate |
| `test_package_stackup_svg_is_generated_and_nonempty` | stackup schematic required by report is generated and non-empty | generated artifacts | `package_stackup.svg` exists, contains `<svg`, and includes layer labels |
| `test_material_assignment_spans_all_layers` | each generated layer has elements and material IDs | default mesh | non-empty element count for each material/layer |
| `test_calculix_input_decks_include_materials_steps_units_and_solver_names` | `.inp` writer includes nodes/elements/materials, expansion/conductivity data, step blocks, units comments, compatible element/material keywords, and documented solver smoke status | generated mesh | thermal and thermomechanical `.inp` files contain required sections/strings and summary can record smoke result |
| `test_summary_contains_sanity_checks_sources_manifest_and_solver_status` | summary JSON records mesh counts, thermal resistance estimate, CTE mismatch/warpage estimate, material sources, units, artifact hashes, and solver skipped/run/failed status | generated artifacts | required JSON keys and numeric values in plausible ranges |
| `test_result_plots_and_report_documents_engineering_assumptions_and_limitations` | temperature/stress/warpage-style SVGs exist and report includes BCs, loads, materials, units, convergence/mesh note, result-plot references, and portfolio-only limitation | generated artifacts/report | required SVGs and headings/phrases present |
| `test_report_does_not_claim_jedec_or_ipc_compliance` | standards guardrail prevents overclaiming with case-insensitive regex | generated report | no phrases matching hyphenated or non-hyphenated `JEDEC[- ]?compliant`, `IPC[- ]?compliant`, `meets JESD22`, `per IPC`, `validated to JEDEC`, `certified`, or `production signoff` |
| `test_cli_regenerates_expected_artifacts_and_manifest_is_stable` | CLI can regenerate all committed artifacts in a temp output directory and compare manifest/schema invariants against the committed artifact set | `uv run python scripts/semiconductor/package_fem_benchmark.py --output <tmp> --report <tmp>/report.md --no-solver` | expected files exist, manifest lists all artifacts, and stable schema/mesh/material hashes match committed invariants |
| `test_solver_wrapper_skips_cleanly_when_ccx_missing_without_require_flag` | solver execution is skip-safe in tests when unavailable | monkeypatch `shutil.which` to None | status `skipped` with reason `ccx not found` |
| `test_solver_wrapper_requires_smoke_when_flag_is_set` | implementation has an enforceable solver-smoke mode instead of an unfalsifiable suitability claim | monkeypatch `shutil.which` to None and call with `require_solver_smoke=True` | clear RuntimeError / failure status |
| `test_solver_flags_are_mutually_exclusive` | `--no-solver` cannot silently override `--require-solver-smoke` | call CLI/parser or wrapper with both flags | clear ValueError / CLI nonzero error |
| `test_solver_wrapper_records_failure_without_crashing_report` | failed solver call records failure metadata and report still renders unless `--require-solver-smoke` is set | monkeypatch subprocess failure | status `failed` with stdout/stderr captured |

---

## Acceptance Criteria

- [ ] Canonical plan and review artifacts exist and #2511 is explicitly approved before implementation begins.
- [ ] Tests are written first and the initial focused test run fails for missing implementation/artifacts.
- [ ] `uv run pytest tests/semiconductor/test_package_fem_benchmark.py -q` passes after implementation.
- [ ] `uv run python scripts/semiconductor/package_fem_benchmark.py --output data/semiconductor/package_fem_benchmark --report docs/reports/semiconductor-package-fem-benchmark.md --no-solver` regenerates the committed deterministic benchmark artifacts.
- [ ] `--no-solver` and `--require-solver-smoke` are mutually exclusive and covered by tests.
- [ ] If `ccx` is available on the implementation machine, `uv run python scripts/semiconductor/package_fem_benchmark.py --output /tmp/package-fem-smoke --report /tmp/package-fem-smoke/report.md --require-solver-smoke` must pass before #2511 closeout; if it fails, fix the deck or stop for explicit user-approved re-scope/blocker conversion.
- [ ] Generated `.inp` files document units and contain mesh/material/step sections; when `ccx` is present, solver-smoke status proves whether they are accepted by CalculiX on this machine.
- [ ] `benchmark_summary.json` records geometry, materials, per-material sources, mesh counts, sanity checks, solver status, command/version when available, artifact hashes, and limitations.
- [ ] `package_stackup.svg`, `temperature_profile.svg`, `stress_warpage_estimates.svg`, and `result_profiles.csv` are generated, non-empty, and referenced by the report.
- [ ] Report explicitly documents boundary conditions, loads, materials/provenance, units, mesh/convergence notes, solver status, result-plot interpretation, and limitations.
- [ ] Report frames the result as a portfolio benchmark, not a production-certified semiconductor model.
- [ ] Report and generated artifacts do not claim JEDEC/IPC compliance or proprietary source extraction.
- [ ] Post-implementation adversarial review is run; any MAJOR findings are fixed before closeout.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | Found review-state/path drift, missing result plots, wrong code-registry path, unfalsifiable CalculiX suitability AC, mesh z-grid inconsistency, weak regeneration invariant, and missing material provenance. |
| Codex r1 | MAJOR | Found missing temperature/stress/warpage plot coverage, wrong code-registry path, and insufficient CalculiX deck validation. |
| Gemini r1 | UNAVAILABLE | CLI trust failure before retrieval; no review signal. |
| Claude r2 | MINOR | All r1 blockers resolved; requested tightening around stackup SVG test, solver flag precedence, citation-contract boundary, artifact-date convention, Hermes preflight, and expected CalculiX artifacts. |
| Codex r2 | MAJOR | Provider could not retrieve the local uncommitted plan and flagged solver-downgrade risk plus standards-regex guardrail; solver/regex findings were folded into this revision, retrieval concern is resolved by committing/pushing the plan before approval request. |
| Gemini r2 | NOT RUN | r1 trust failure; no additional signal required before approval if Claude/Codex issues are addressed and artifacts are committed. |

**Overall result:** r1 FAIL / r2 CONDITIONAL — do not implement yet; ready for plan-review posting after this revision is committed/pushed and user explicitly approves.

Revisions made based on r1 review:
- Added temperature profile and stress/warpage-style SVG/CSV result artifacts and tests.
- Corrected engineering retrieval to consult canonical `data/design-codes/code-registry.yaml` and retained `data/document-index/code-registry.yaml` only as a wrong/missing path note.
- Replaced unfalsifiable CalculiX "suitable" criterion with guarded `--require-solver-smoke` behavior when `ccx` is available.
- Clarified mesh uses regular x/y and nonuniform per-layer z divisions.
- Added artifact manifest/regeneration invariants.
- Added per-material source/provenance fields and tests.
- Corrected review artifact bookkeeping to preserve r1 artifacts and note review-execution-date naming.
- Added stackup SVG test/AC, solver flag mutual exclusion, stricter standards-overclaim regex, explicit CalculiX smoke artifact contract, Hermes preflight risk, and mandatory local solver smoke closeout when `ccx` is present.

---

## Risks and Open Questions

- **Risk: CalculiX input semantics.** A generated `.inp` can be solver-ready in structure but still need iterative solver-specific fixes. Mitigation: tests verify deck structure; deterministic regeneration may use `--no-solver`; issue closeout must run `--require-solver-smoke` when local `ccx` exists and must stop for fixes/re-scope if the local solver rejects the deck; report must clearly state whether real solver execution succeeded, skipped, or failed.
- **Risk: solver availability differs by machine.** Mitigation: implementation must not require `ccx` in CI/test; command availability is recorded in summary.
- **Risk: stdlib-only plotting limits visual quality.** Mitigation: generate simple but explicit SVG temperature and stress/warpage-style plots plus tables first; richer Plotly/ParaView visuals become follow-up work if needed.
- **Risk: standards overclaiming.** Mitigation: tests forbid JEDEC/IPC compliance phrases and report includes explicit source limitations.
- **Risk: package model oversimplification.** Mitigation: report labels stackup/materials as educational assumptions and includes convergence/limitations notes.
- **Open:** If user wants higher visual polish or a real coupled solve beyond the first CalculiX smoke/deck benchmark, create a follow-up issue after this first portfolio-safe benchmark lands.

---

## Follow-up Issue Candidates

- Candidate: `feat(fem): add real CalculiX FRD parser and ParaView/PyVista figures for semiconductor package benchmark` — only if first benchmark lands and solver artifacts are stable.
- Candidate: `research(semiconductor): ingest legally accessible electronics packaging reliability references` — needed before making any JEDEC/IPC-derived requirements claims.
- Candidate: `feat(cad-fem): connect #2510 generated package layout geometry into #2511 FEM stackup` — after #2510 exists.

No follow-up issue should be created during #2511 unless adversarial review says the current scope is still too broad and must be decomposed.

---

## Complexity: T3

**T3** — engineering-critical FEM benchmark with multiple generated artifacts, solver-input semantics, optional external solver behavior, TDD requirements, standards-claim guardrails, and post-implementation adversarial review. The implementation remains bounded to one script, one test file, one generated artifact directory, and one report.
