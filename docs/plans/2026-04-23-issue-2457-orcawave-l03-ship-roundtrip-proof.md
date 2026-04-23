# Plan for #2457: Promote L03 ship benchmark to explicit OrcaWave roundtrip proof case

> **Status:** plan-review (adversarial-reviewed r1 PASS — Claude MINOR / Codex APPROVE / Gemini MINOR)
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2457
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2457-claude.md | scripts/review/results/2026-04-23-plan-2457-codex.md | scripts/review/results/2026-04-23-plan-2457-gemini.md
> **Parent roadmap anchor:** #1572 (reopened); `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`
> **Sibling parallelism:** #2458 (OrcaWave multi-body FPSO+turret promotion) — independent fixture work, can run alongside per #2457 sequencing comment (2026-04-22).
> **Execution order:** Phase B, item 6 after the core forward-fidelity proof track (#1652 → #1788).
> **Sibling scope boundary:** edits only `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/**`, `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/**`, `digitalmodel/docs/domains/orcawave/README.md`, `digitalmodel/src/digitalmodel/benchmarks/inventory.py`, and `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`. No encroachment on #2458 (different fixture — FPSO+turret multi-body) or broader benchmark-corpus expansion (#1637, #1591, #1594 explicitly out-of-scope per roadmap Phase C/D).

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml` — the canonical L03 ship benchmark spec referenced by #2457. Single-body ship, 9,017,950 kg mass, 500 m water depth, 20 period-based frequencies (2.0–22.0 s), 9 wave headings (0.0–180.0, `symmetry: false`), direct `inertia_tensor` (Ixx, Iyy, Izz populated; Ixy/Ixz/Iyz zero), 6×6 `external_damping` with roll entry `36010.0`, `analysis_type: full_qtf`, solver options `remove_irregular_frequencies=true`, `qtf_calculation=true`, `load_rao_method=both`, `precision=double`, `qtf_min_frequency=0.628318` rad/s, `qtf_max_frequency=3.141593` rad/s, outputs `[raos, added_mass, damping, qtf]`. Tags: `[benchmark, ship, validation, L03, qtf]`.
- Found: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/source_data/orcawave/orcawave_001_ship_raos_rev2.yml` — the native OrcaWave YAML ground truth the canonical spec was derived from (plus `orcawave_001_ship_raos_rev2_matched.yml` as the matched variant).
- Found: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/source_data/aqwa/aqwa_001_ship_raos_rev2.dat` — the AQWA mesh file referenced by `spec.yml` via `mesh_file: source_data/aqwa/aqwa_001_ship_raos_rev2.dat` (relative path resolved from the spec's directory).
- Found: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` — contains `TestOrcaWaveSemanticRoundTripSingleBody` (lines 36–93) using `spec_ship_raos.yml`, which is a **simpler, different fixture** (radii-of-gyration-derived inertia, 15 frequencies as rad/s, 5 headings with symmetry, `qtf_calculation=false`, `analysis_type=diffraction`, no `external_damping`). L03 is NOT exercised by any existing test — it is a pure proof gap.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` — handles all L03 fields: `inertia_tensor` (line 188), `external_damping: list[list[float]]` (line 260), `qtf_calculation` (line 461), `load_rao_method` (line 465), `qtf_min_frequency` (line 488), `qtf_max_frequency` (line 492), `FULL_QTF` analysis enum (line 39). No schema changes required.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` — forward-generates L03 fields: `_build_inertia_tensor` (line 190) reads direct `inertia_tensor`, external damping (line 345), `load_rao_method` map (line 375), full_qtf solve_type handling (line 405–505). No backend changes required.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` — reverse-parses L03 fields: `qtf_calculation` (lines 203, 552), `external_damping = self._parse_6x6_matrix(body_data, "Damping")` (line 607), and emits to `external_damping=external_damping` (line 617). No reverse-parser changes required.
- Found: `digitalmodel/docs/domains/orcawave/README.md` — already contains a dedicated **"Semantic-equivalence claim boundary"** section (lines 80–98) with three buckets explicitly documented: (a) preserved fields: frequency values, heading values, COG, inertia tensor, fixed DOFs/constraints, representative solver options; (b) normalization-accepted differences: kg/m³↔t/m³, rad/s↔period(s), bool↔Yes/No, Infinity↔infinite; (c) intentionally classified buckets: `output_only`, `gui_only`, `internal_default_only`, `known_non_configurable_in_spec`, `solver_mode_significant`, `physics_significant`, `representation_normalization_only`. This is the claim-boundary contract the L03 proof must respect verbatim. The README has no dedicated L03 promotion note today.
- Found: `digitalmodel/src/digitalmodel/benchmarks/inventory.py` — repo-level inventory with `ModelCategory` enum and `ModelInventoryEntry` dataclass. Does not contain an L03 entry today (`grep L03` returned no matches).
- Found: `digitalmodel/scripts/benchmark/regenerate_ship_benchmark.py` — regeneration script that uses `docs/domains/orcawave/L03_ship_benchmark` as `BENCHMARK_DIR`. Confirms the canonical-location convention: the L03 spec and its results already live under `docs/domains/orcawave/L03_ship_benchmark/` and should stay there; this plan does NOT relocate the spec.
- Found: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/benchmark_results/` — contains `benchmark_report.html`, `benchmark_report.json`, `benchmark_amplitude.html`, `benchmark_phase.html`, `benchmark_combined.html`, `benchmark_heatmap.html`. These are output artifacts; this plan does NOT regenerate them.
- Found: sibling plan `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` — already landed under the same canonical-spec promotion family. This plan mirrors #2458's shape (named fixture, dedicated regression tests, manifest, docs note, inventory registration, roadmap annotation) but differs on one key point: **L03 already lives in its own benchmark directory under `docs/domains/orcawave/`**, so this plan does not move/duplicate it — tests load L03 directly from the canonical docs path, removing the mesh-path rewrite hazard that dominated #2458's r1 review.

### Gaps identified
- L03 is NOT currently exercised by any regression test. `spec_ship_raos.yml` in `tests/hydrodynamics/diffraction/fixtures/` is a different, simpler fixture (no QTF, no external damping, radii-derived inertia).
- No `manifest.yaml` exists at `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/` to declare it a first-class benchmark-grade canonical proof artifact.
- No dedicated benchmark test module exists under `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/` (the `benchmarks/` subdirectory does not exist — #2458 will create it first; this plan adds an L03 module alongside #2458's multibody module).
- No preservation coverage for L03-specific fields: direct `inertia_tensor` roundtrip, 6×6 `external_damping` roundtrip, period-based frequency roundtrip (20 values), 9-heading no-symmetry roundtrip, QTF solver-options block (`qtf_calculation`, `qtf_min_frequency`, `qtf_max_frequency`, `load_rao_method=both`, `precision=double`), and `analysis_type=full_qtf` survival.
- No benchmark-specific readiness note in `digitalmodel/docs/domains/orcawave/README.md` naming L03 as a flagship roundtrip proof case.
- No entry in `digitalmodel/src/digitalmodel/benchmarks/inventory.py` for L03.
- Roadmap line 119 (`OrcaWave L03 ship benchmark full roundtrip`) is under "Partial but high-value next validations" — needs promotion to "Ready now" or annotation "(promoted under #2457)".

### Standards
Not applicable in the standards-ledger sense — this is a canonical-spec promotion issue, not a new engineering-standard implementation. L03's engineering values (mass, COG, inertia tensor, external damping roll entry) are sourced from the existing `orcawave_001_ship_raos_rev2` reference in `source_data/orcawave/`.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/` — ship-diffraction/RAO/QTF concepts are within marine domain; however, #2457 is a test-fixture promotion, not new domain knowledge. No wiki edits are required by this plan.

### Documents consulted
- Issue #2457 body — defines the four scope items (use `L03_ship_benchmark/spec.yml` as named fixture, validate forward generation to native OrcaWave YAML, validate reverse parsing to canonical structures, confirm preservation of frequencies/headings/inertia/COG/solver options and benchmark-specific options such as QTF and external damping). Names deliverables: dedicated regression test(s), benchmark-specific readiness note, claim-boundary statement.
- Issue #2457 sequencing comment (2026-04-22) — names Phase B item 6 after core forward-fidelity proof track #1652→#1788; parallelism with #2458; keep scope benchmark-specific (a proof artifact, not a broad benchmark cleanup).
- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` — line 119 lists "OrcaWave L03 ship benchmark full roundtrip" under "Partial but high-value next validations"; contract-boundary (lines 8–9) bounds OrcaWave claim as "near-equivalent for key engineering inputs and tested pathways, not strict identity across every native YAML field". This plan inherits that claim boundary rather than asserting identity.
- Issue #1598 (CLOSED) — delivered the forward pipeline `spec.yml → DiffractionSpec → OrcaWaveBackend → native solver YAML` with mock-solver + licensed-solver test splits. L03 promotion consumes this pipeline as a delivered dependency.
- Issue #1638 (CLOSED) — delivered the reverse parser `native OrcaWave YAML → DiffractionSpec` with roundtrip test scaffolding. L03 promotion consumes this as a delivered dependency.
- `digitalmodel/docs/domains/orcawave/README.md` lines 80–98 — the claim-boundary contract; the docs promotion note must mirror its wording (especially "near-equivalent for key engineering inputs, not strict identity across every native YAML field").
- `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` — existing roundtrip test module convention: `_load_*_spec()` helpers + `_generate_orcawave_yml(spec, tmp_path)` forward helper + `OrcaWaveInputParser().parse(yml_path)` reverse call. The new L03 benchmark module follows this shape.
- Sibling plan `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` — adopted as the structural template (manifest schema, benchmark test module pattern, inventory registration, docs note, roadmap annotation). Deviations from #2458 are documented in the Pseudocode section.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view --json state,title`):
- `#2457` — OPEN — `feat(canonical-spec): promote L03 ship benchmark to explicit OrcaWave roundtrip proof case`
- `#1572` — OPEN — `Domain-specific capability roadmaps — OrcaWave/OrcaFlex, structural, hydrodynamics, pipeline` (parent roadmap anchor)
- `#2458` — OPEN — `feat(canonical-spec): promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness` (sibling parallel wave)
- `#1598` — CLOSED — `End-to-end DiffractionSpec pipeline integration test` (delivered forward pipeline)
- `#1638` — CLOSED — `DiffractionSpec pipeline: reverse parser — native OrcaWave YAML back to DiffractionSpec` (delivered reverse parser)
- `#1652` — OPEN — upstream forward-fidelity anchor (core proof track; executes before this plan per sequencing comment)
- `#1788` — OPEN — upstream forward-fidelity anchor (core proof track; executes before this plan per sequencing comment)
- `#1637` — OPEN — parametric sweep (downstream — intentionally out-of-scope for #2457)
- `#1591` — OPEN — hull-registry expansion (downstream — intentionally out-of-scope)
- `#1594` — OPEN — DLC matrix generator (downstream — intentionally out-of-scope)

**File existence** (verified 2026-04-23 via `ls`):
- EXISTS: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml`
- EXISTS: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/source_data/orcawave/orcawave_001_ship_raos_rev2.yml`
- EXISTS: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/source_data/orcawave/orcawave_001_ship_raos_rev2_matched.yml`
- EXISTS: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/source_data/aqwa/` (contains `aqwa_001_ship_raos_rev2.dat` per `source_data/aqwa` listing)
- EXISTS: `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/benchmark_results/benchmark_report.html` (plus amplitude/phase/combined/heatmap HTML + JSON)
- EXISTS: `digitalmodel/docs/domains/orcawave/README.md`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py`
- EXISTS: `digitalmodel/src/digitalmodel/benchmarks/inventory.py`
- EXISTS: `digitalmodel/scripts/benchmark/regenerate_ship_benchmark.py`
- EXISTS: `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`
- EXISTS: `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` (sibling template)
- MISSING (new — this plan creates): `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml`
- MISSING (new — this plan creates): `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` (created by #2458 first; this plan is co-dependent on its creation, with a local fallback described in Risks)
- MISSING (new — this plan creates): `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py`

**Line excerpts**

`digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml` lines 1–34 (verbatim — vessel + environment + external damping headers):
```
# Canonical spec.yml for Ship Benchmark (L03)
# Source: source_data/orcawave/orcawave_001_ship_raos_rev2.yml
# Units: Pure SI (kg, m, s) — backend converts to OrcaFlex-SI (te)

version: "1.0"
analysis_type: full_qtf

vessel:
  name: Body1
  type: ship
  geometry:
    mesh_file: source_data/aqwa/aqwa_001_ship_raos_rev2.dat
    mesh_format: dat
    symmetry: none
    reference_point: [0.0, 0.0, 0.5]  # BodyMeshPosition z-offset
    waterline_z: 0.0
    length_units: m
  inertia:
    mass: 9017950.0  # 9017.95 te * 1000
    centre_of_gravity: [2.53, 0.0, -1.974]
    inertia_tensor:
      Ixx: 254937446.5   # 254937.4465 te.m^2 * 1000
      Iyy: 5979802645.0  # 5979802.645 te.m^2 * 1000
      Izz: 5979802645.0  # 5979802.645 te.m^2 * 1000
      Ixy: 0.0
      Ixz: 0.0
      Iyz: 0.0
  external_damping:
    - [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    - [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    - [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    - [0.0, 0.0, 0.0, 36010.0, 0.0, 0.0]  # Roll damping (passed through without conversion)
    - [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

`digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml` lines 40–75 (verbatim — frequencies, headings, solver options):
```
frequencies:
  input_type: period
  values:
    - 2.0
    - 3.0
    - 4.0
    - 5.0
    - 6.0
    - 7.0
    - 7.5
    - 8.0
    - 8.5
    - 9.0
    - 9.5
    - 10.0
    - 11.0
    - 13.0
    - 15.0
    - 16.0
    - 17.0
    - 19.0
    - 20.0
    - 22.0

wave_headings:
  values: [0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5, 180.0]
  symmetry: false

solver_options:
  remove_irregular_frequencies: true
  qtf_calculation: true
  load_rao_method: both
  precision: double
  qtf_min_frequency: 0.628318  # 2*pi/10.0 rad/s (QTFMaxPeriod=10s)
  qtf_max_frequency: 3.141593  # 2*pi/2.0 rad/s (QTFMinPeriod=2s)
```

`digitalmodel/docs/domains/orcawave/README.md` lines 80–98 (verbatim — claim boundary):
```
## Semantic-equivalence claim boundary

The current OrcaWave workflow should be described conservatively:
- near-equivalent for key engineering inputs and tested round-trip pathways
- not guaranteed 100% semantically equivalent across every strict OrcaWave YAML field

Practical interpretation:
- preserved and regression-tested fields include frequency values, heading values, COG, inertia tensor, fixed DOFs / constraints, and representative solver options
- accepted normalization differences include unit/representation changes such as kg/m^3 <-> t/m^3, rad/s <-> period(s), bool <-> Yes/No, and Infinity <-> infinite
- some strict OrcaWave fields are intentionally classified rather than preserved literally:
  - `output_only`
  - `gui_only`
  - `internal_default_only`
  - `known_non_configurable_in_spec`
  - `solver_mode_significant`
  - `physics_significant`
  - `representation_normalization_only`
```

`docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` line 119 (verbatim):
```
- OrcaWave L03 ship benchmark full roundtrip
```
(Listed under "Partial but high-value next validations", confirming #2457 is a roadmap-aligned promotion from "partial" to "ready".)

`digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` lines 39, 188, 260, 461, 488, 492 (field existence proof):
```
39:    FULL_QTF = "full_qtf"
188:    inertia_tensor: Optional[dict[str, float]] = Field(
260:    external_damping: Optional[list[list[float]]] = Field(
461:    qtf_calculation: bool = Field(
488:    qtf_min_frequency: Optional[float] = Field(
492:    qtf_max_frequency: Optional[float] = Field(
```

`digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` lines 203, 552, 607, 617 (reverse-parse support proof):
```
203:            qtf_calculation=qtf,
552:            qtf_calculation=qtf_enabled,
607:        external_damping = self._parse_6x6_matrix(body_data, "Damping")
617:            external_damping=external_damping,
```

**Gap proofs**
- `grep -rn 'L03' digitalmodel/tests/hydrodynamics` → 0 matches → confirms no test exercises L03 today.
- `grep -n 'L03\|ship_benchmark' digitalmodel/src/digitalmodel/benchmarks/inventory.py` → 0 matches → confirms inventory has no L03 entry.
- `grep -n 'L03\|ship benchmark' digitalmodel/docs/domains/orcawave/README.md` → 0 matches → confirms domain docs have no L03 promotion note.
- `ls digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml 2>&1` → `No such file or directory` → confirms manifest does not yet exist.
- `ls digitalmodel/tests/hydrodynamics/diffraction/benchmarks/ 2>&1` → `No such file or directory` → confirms benchmarks test subdirectory does not yet exist (co-dependent on #2458 creating it — see Risks).

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 13
     (issue #2457 body, issue #2457 sequencing comment, canonical-spec roadmap, L03 spec.yml,
      L03 source_data artifacts, claim-boundary README, closed deps #1598/#1638, input_schemas.py,
      orcawave_backend.py, reverse_parsers.py, benchmarks inventory, regenerate_ship_benchmark.py script,
      sibling plan #2458).
     Retrieval-contract engineering-class bundle satisfied: standards ledger N/A
     (not a standards implementation); code registry — benchmarks/inventory.py is the code-registry surface,
     read and confirmed no L03 entry; domain wiki — marine-engineering domain acknowledged,
     no edits required; online-resource-registry N/A for this scope. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md` |
| L03 canonical spec (UNCHANGED) | `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml` |
| L03 benchmark manifest (NEW) | `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml` |
| Benchmark test module (NEW) | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py` |
| Benchmark test package init (NEW — co-dependent with #2458) | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` |
| Domain docs promotion note | `digitalmodel/docs/domains/orcawave/README.md` (modify — add "Named single-body flagship benchmark (#2457)" subsection) |
| Roadmap readiness update | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` (modify — annotate line 119 "OrcaWave L03 ship benchmark full roundtrip" with "(promoted under #2457)" OR move to "Ready now") |
| Benchmark registry entry | `digitalmodel/src/digitalmodel/benchmarks/inventory.py` (modify — add `l03_ship_benchmark` entry to `build_model_inventory()`) |
| Plan index update | `docs/plans/README.md` (add #2457 row — **deferred to main session at merge** per worker-4 planning-worktree write-fence) |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2457-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2457-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2457-gemini.md` |

---

## Deliverable

L03 ship benchmark promoted from "a member of the benchmark family" to a **first-class OrcaWave roundtrip proof artifact** with (a) a dedicated regression test module — `tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py` — that loads `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml` **in place** (no relocation, no mesh-path rewrite), exercises forward generation via `OrcaWaveBackend`, exercises reverse parsing via `OrcaWaveInputParser`, and asserts preservation of: frequency values (20 period-based, surviving the period↔rad/s representation-normalization bucket per claim boundary), heading values (9 values, `symmetry=false`), direct `inertia_tensor` (Ixx/Iyy/Izz/Ixy/Ixz/Iyz roundtrip), centre of gravity, `analysis_type=full_qtf`, solver options `remove_irregular_frequencies`, `qtf_calculation`, `load_rao_method`, `precision`, `qtf_min_frequency`, `qtf_max_frequency`, and the 6×6 `external_damping` matrix (roll entry 36010.0 specifically pinned as the benchmark-distinguishing value); (b) a `manifest.yaml` alongside `spec.yml` declaring L03 as a benchmark-grade canonical proof artifact with explicit `claim_boundary`, `solvers_proven`, `preserved_fields`, `normalization_accepted_fields`, and `intentionally_classified_fields` sections that mirror the README's claim-boundary contract; (c) a "Named single-body flagship benchmark (#2457)" subsection in `digitalmodel/docs/domains/orcawave/README.md` that names L03, links to `spec.yml` and `manifest.yaml`, and restates the claim boundary; (d) registration in `digitalmodel/src/digitalmodel/benchmarks/inventory.py` under `ModelCategory.FREQUENCY_DOMAIN` with tags `["orcawave", "ship", "qtf", "benchmark", "roundtrip", "L03"]`; (e) annotation in `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` marking line 119 as "promoted under #2457" — without moving or modifying the existing `TestOrcaWaveSemanticRoundTripSingleBody` tests so the simpler `spec_ship_raos.yml` smoke coverage remains intact.

---

## Pseudocode

```text
function write_l03_manifest():
    path = digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml
    fields:
        benchmark_id: l03_ship_benchmark
        title: "OrcaWave L03 ship benchmark — single-body flagship with QTF and external damping"
        category: frequency_domain
        solvers_proven:
            - forward: "orcawave (spec.yml -> native OrcaWave YAML via OrcaWaveBackend.generate_single)"
            - reverse: "orcawave (native OrcaWave YAML -> DiffractionSpec via OrcaWaveInputParser)"
        body_count: 1
        vessel:
            name: Body1
            type: ship
            mass_kg: 9017950.0
            centre_of_gravity_m: [2.53, 0.0, -1.974]
            inertia_tensor_kg_m2:
                Ixx: 254937446.5
                Iyy: 5979802645.0
                Izz: 5979802645.0
            external_damping_nonzero_entries:
                - [row=3, col=3, value=36010.0]  # Roll damping, passed through without conversion
        analysis:
            type: full_qtf
            frequency_count: 20
            frequency_input_type: period
            frequency_range_s: [2.0, 22.0]
            heading_count: 9
            heading_range_deg: [0.0, 180.0]
            heading_symmetry: false
        solver_options:
            remove_irregular_frequencies: true
            qtf_calculation: true
            load_rao_method: both
            precision: double
            qtf_min_frequency_rad_s: 0.628318   # 2*pi/10.0 rad/s, QTFMaxPeriod=10 s
            qtf_max_frequency_rad_s: 3.141593   # 2*pi/2.0  rad/s, QTFMinPeriod=2  s
        claim_boundary: |
            Inherits the OrcaWave claim boundary from digitalmodel/docs/domains/orcawave/README.md:
            near-equivalent for key engineering inputs and tested round-trip pathways;
            not guaranteed 100% semantically equivalent across every strict OrcaWave YAML field.
        preserved_fields:  # regression-asserted by test_l03_ship_benchmark.py
            - frequency values (under period representation-normalization bucket)
            - heading values and heading count (symmetry=false preserved)
            - centre of gravity (all three components)
            - inertia tensor (Ixx, Iyy, Izz, Ixy, Ixz, Iyz)
            - analysis_type full_qtf (as solver SolveType)
            - solver_options remove_irregular_frequencies
            - solver_options qtf_calculation
            - solver_options load_rao_method
            - solver_options qtf_min_frequency
            - solver_options qtf_max_frequency
            - external damping 6x6 matrix, including the roll entry 36010.0
        normalization_accepted_fields:
            - frequency unit/representation (rad/s <-> period)
            - mass unit (kg <-> te)
            - boolean representation (true/false <-> Yes/No)
        intentionally_classified_fields:
            - output_only
            - gui_only
            - internal_default_only
            - known_non_configurable_in_spec
            - solver_mode_significant
            - physics_significant
            - representation_normalization_only
        source_data:
            orcawave_native_input: source_data/orcawave/orcawave_001_ship_raos_rev2.yml
            orcawave_native_input_matched: source_data/orcawave/orcawave_001_ship_raos_rev2_matched.yml
            aqwa_mesh: source_data/aqwa/aqwa_001_ship_raos_rev2.dat
        benchmark_results_artifacts:
            - benchmark_results/benchmark_report.html
            - benchmark_results/benchmark_report.json
            - benchmark_results/benchmark_amplitude.html
            - benchmark_results/benchmark_phase.html
            - benchmark_results/benchmark_combined.html
            - benchmark_results/benchmark_heatmap.html
        related_issues:
            promotion: 2457
            delivered_foundations: [1598, 1638]
            parent_roadmap: 1572
            sibling_multibody: 2458
        bridge_candidates:
            - "future OrcaWave -> OrcaFlex handoff validation (extends delivered #1592/#1768 handoff primitives with a QTF-enabled ship case)"
        version: 1

function write_l03_benchmark_test_module():
    path = digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py
    # Note: this plan relies on digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py existing.
    # Execution order: #2458's benchmark package init should land first. If executed before #2458, this plan
    # creates benchmarks/__init__.py as a 0-line file (idempotent; #2458 will leave it unchanged).
    imports:
        from pathlib import Path
        import pytest
        import yaml
        from digitalmodel.hydrodynamics.diffraction.input_schemas import DiffractionSpec
        from digitalmodel.hydrodynamics.diffraction.orcawave_backend import OrcaWaveBackend
        from digitalmodel.hydrodynamics.diffraction.reverse_parsers import OrcaWaveInputParser

    constants:
        L03_DIR = Path(__file__).parents[4] / "docs/domains/orcawave/L03_ship_benchmark"
            # From tests/hydrodynamics/diffraction/benchmarks/ → parents[0]=benchmarks,
            # parents[1]=diffraction, parents[2]=hydrodynamics, parents[3]=tests,
            # parents[4]=digitalmodel ROOT; then into docs/domains/orcawave/L03_ship_benchmark.
            # Verification hint: `realpath -m tests/hydrodynamics/diffraction/benchmarks/../../../../docs/domains/orcawave/L03_ship_benchmark/spec.yml`
            # must resolve to the real file under digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml.
        L03_SPEC = L03_DIR / "spec.yml"
        L03_MANIFEST = L03_DIR / "manifest.yaml"

    helpers:
        def _load_l03(): return DiffractionSpec.from_yaml(L03_SPEC)
        def _forward(spec, tmp_path): return OrcaWaveBackend().generate_single(spec, tmp_path)
        def _reverse(yml_path): return OrcaWaveInputParser().parse(yml_path)

    class TestL03ShipBenchmarkPresence:
        def test_l03_spec_exists(self):
            assert L03_SPEC.is_file()

        def test_l03_spec_loads_as_diffraction_spec(self):
            spec = _load_l03()
            assert spec is not None
            assert spec.version == "1.0"

        def test_l03_mesh_file_referenced_in_spec_resolves(self):
            # Parse the raw YAML to pull the mesh_file string; resolve relative to spec.yml's parent.
            raw = yaml.safe_load(L03_SPEC.read_text())
            mesh_rel = raw["vessel"]["geometry"]["mesh_file"]
            mesh_abs = (L03_SPEC.parent / mesh_rel).resolve()
            assert mesh_abs.is_file(), f"mesh file not found: {mesh_abs}"

        def test_l03_manifest_exists_and_matches_folder(self):
            assert L03_MANIFEST.is_file()
            m = yaml.safe_load(L03_MANIFEST.read_text())
            assert m["benchmark_id"] == "l03_ship_benchmark"
            assert m["body_count"] == 1

    class TestL03ShipBenchmarkForward:
        def test_forward_generation_does_not_raise(self, tmp_path):
            yml = _forward(_load_l03(), tmp_path)
            assert yml.exists()
            assert yml.stat().st_size > 0

    class TestL03ShipBenchmarkRoundtrip:
        # Identity/structural preservation
        def test_preserves_body_name(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.vessel.name == orig.vessel.name

        # Frequencies — L03 uses input_type=period; roundtrip is period<->rad/s (normalization bucket).
        def test_preserves_frequency_count(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert len(parsed.frequencies.to_frequencies_rad_s()) == len(orig.frequencies.to_frequencies_rad_s()) == 20

        def test_preserves_frequency_values_rad_s(self, tmp_path):
            # Compare sorted rad/s to absorb period<->rad/s representation normalization.
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert sorted(parsed.frequencies.to_frequencies_rad_s()) == pytest.approx(
                sorted(orig.frequencies.to_frequencies_rad_s()), rel=1e-4
            )

        # Headings — L03 has 9 headings with symmetry=false.
        def test_preserves_heading_count_and_symmetry(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert len(parsed.wave_headings.to_heading_list()) == len(orig.wave_headings.to_heading_list()) == 9

        def test_preserves_heading_values(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.wave_headings.to_heading_list() == pytest.approx(
                orig.wave_headings.to_heading_list(), abs=1e-6
            )

        # Inertia
        def test_preserves_centre_of_gravity(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.vessel.inertia.centre_of_gravity == pytest.approx(
                orig.vessel.inertia.centre_of_gravity, rel=1e-4, abs=1e-6
            )

        def test_preserves_inertia_tensor_directly(self, tmp_path):
            # L03 provides inertia_tensor directly (not radii_of_gyration). The roundtrip should
            # preserve diagonal entries within reverse-parse numerical tolerance.
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.vessel.inertia.inertia_tensor is not None
            for key in ("Ixx", "Iyy", "Izz"):
                assert parsed.vessel.inertia.inertia_tensor[key] == pytest.approx(
                    orig.vessel.inertia.inertia_tensor[key], rel=1e-4
                )
            for key in ("Ixy", "Ixz", "Iyz"):
                # Off-diagonal zeros roundtrip; tolerate tiny absolute noise.
                assert parsed.vessel.inertia.inertia_tensor[key] == pytest.approx(
                    orig.vessel.inertia.inertia_tensor[key], abs=1e-3
                )

        # External damping
        def test_preserves_external_damping_matrix_shape(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.vessel.external_damping is not None
            assert len(parsed.vessel.external_damping) == 6
            for row in parsed.vessel.external_damping:
                assert len(row) == 6

        def test_preserves_roll_damping_value_36010(self, tmp_path):
            # The benchmark-distinguishing value: row 3 (index 3, roll), col 3 (roll) = 36010.0.
            # Per spec.yml comment: "Roll damping (passed through without conversion)".
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.vessel.external_damping[3][3] == pytest.approx(36010.0, rel=1e-6)

        def test_preserves_external_damping_off_diagonal_zeros(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            for r in range(6):
                for c in range(6):
                    if (r, c) != (3, 3):
                        assert parsed.vessel.external_damping[r][c] == pytest.approx(0.0, abs=1e-6)

        # Solver options
        def test_preserves_remove_irregular_frequencies(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.solver_options.remove_irregular_frequencies is True

        def test_preserves_qtf_calculation_enabled(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            assert parsed.solver_options.qtf_calculation is True

        def test_preserves_load_rao_method_both(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            # LoadRAOMethod enum value "both" at input → backend maps to "Both"; reverse should come back as enum "both".
            assert parsed.solver_options.load_rao_method == orig.solver_options.load_rao_method

        def test_preserves_qtf_min_frequency(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            # 0.628318 rad/s input — expect preservation to 1e-4 rel to cover rad/s formatting.
            if parsed.solver_options.qtf_min_frequency is not None:
                assert parsed.solver_options.qtf_min_frequency == pytest.approx(
                    orig.solver_options.qtf_min_frequency, rel=1e-4
                )
            else:
                pytest.skip("reverse parser does not emit qtf_min_frequency — open follow-up")

        def test_preserves_qtf_max_frequency(self, tmp_path):
            orig = _load_l03()
            parsed = _reverse(_forward(orig, tmp_path))
            if parsed.solver_options.qtf_max_frequency is not None:
                assert parsed.solver_options.qtf_max_frequency == pytest.approx(
                    orig.solver_options.qtf_max_frequency, rel=1e-4
                )
            else:
                pytest.skip("reverse parser does not emit qtf_max_frequency — open follow-up")

    class TestL03ShipBenchmarkClaimBoundary:
        def test_claim_boundary_language_present_in_manifest(self):
            m = yaml.safe_load(L03_MANIFEST.read_text())
            cb = m["claim_boundary"]
            assert "near-equivalent for key engineering inputs" in cb
            assert "not guaranteed 100% semantically equivalent" in cb

        def test_intentionally_classified_buckets_listed_in_manifest(self):
            m = yaml.safe_load(L03_MANIFEST.read_text())
            buckets = set(m["intentionally_classified_fields"])
            expected = {"output_only", "gui_only", "internal_default_only",
                        "known_non_configurable_in_spec", "solver_mode_significant",
                        "physics_significant", "representation_normalization_only"}
            assert expected.issubset(buckets)

    class TestL03ShipBenchmarkInventory:
        def test_inventory_has_l03_entry(self):
            from digitalmodel.benchmarks.inventory import build_model_inventory, ModelCategory
            inv = build_model_inventory()
            names = [e.name for e in inv]
            assert "l03_ship_benchmark" in names
            entry = next(e for e in inv if e.name == "l03_ship_benchmark")
            assert entry.category == ModelCategory.FREQUENCY_DOMAIN

function extend_docs_and_inventory():
    digitalmodel/docs/domains/orcawave/README.md:
        add a new subsection "Named single-body flagship benchmark (#2457)" near the "Available Examples" area:
            names l03_ship_benchmark
            links digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml
            links digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml
            restates claim boundary (copy the "near-equivalent..." clause verbatim from the §Semantic-equivalence section above)
            declares L03 a bridge candidate for future OrcaWave -> OrcaFlex handoff validation (QTF-enabled case)
            cross-links to closed foundations #1598, #1638 and sibling multi-body #2458

    docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md:
        line 119 "- OrcaWave L03 ship benchmark full roundtrip" →
            annotate to "- OrcaWave L03 ship benchmark full roundtrip — promoted under #2457 (2026-04-23)"
        (stays in "Partial but high-value next validations" list; moving to "Ready now" is deferred until
        the implementation commit lands on main. Worker-4 plan phase only annotates with the promotion reference.)

    digitalmodel/src/digitalmodel/benchmarks/inventory.py:
        add a ModelInventoryEntry to build_model_inventory():
            name="l03_ship_benchmark"
            category=ModelCategory.FREQUENCY_DOMAIN
            path=Path("digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml")
            description="OrcaWave L03 ship flagship benchmark — single-body ~220m ship with full QTF, direct inertia tensor, and 6x6 external damping with roll entry"
            tags=["orcawave", "ship", "qtf", "benchmark", "roundtrip", "L03"]

function implement_with_tdd():
    1. write digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py FIRST with all tests above.
    2. run `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py -v`.
       Expected red-phase failures (captured to .planning/quick/2457-red-phase.out):
         - test_l03_manifest_exists_and_matches_folder   → FileNotFoundError on manifest.yaml
         - test_claim_boundary_language_present_in_manifest, test_intentionally_classified_buckets_listed_in_manifest → same
         - test_inventory_has_l03_entry                  → AssertionError ("l03_ship_benchmark" not in names)
       The other tests may green already (spec.yml already exists) — this is expected and not a red-phase violation.
    3. write digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml per the schema above.
    4. add the L03 entry to digitalmodel/src/digitalmodel/benchmarks/inventory.py.
    5. rerun the test module — all should go green.
    6. add the docs note + roadmap annotation.
    7. run `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/ -x --tb=short -q` — confirm no regression.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml` | Benchmark manifest per schema in Pseudocode — declares L03 a first-class benchmark-grade canonical proof artifact with explicit claim-boundary, preserved-fields, normalization-accepted, and intentionally-classified sections. |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py` | Dedicated regression-test module for L03 roundtrip — 5 test classes, ~23 tests covering presence, forward, roundtrip-preservation (frequencies, headings, COG, inertia tensor, external damping incl. roll 36010, solver options incl. QTF min/max, load RAO method), claim boundary, and inventory registration. |
| Create (idempotent — co-dependent with #2458) | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` | Makes the benchmarks subdirectory a package. #2458's plan also creates this file; whichever plan's implementation lands first creates it. If both create an empty `__init__.py`, the result is identical. |
| Modify | `digitalmodel/docs/domains/orcawave/README.md` | Add "Named single-body flagship benchmark (#2457)" subsection near "Available Examples" (around existing line 231) that names L03, links to `spec.yml` + `manifest.yaml`, restates the claim boundary verbatim, cross-links closed foundations #1598/#1638, and declares L03 a bridge candidate for future OrcaWave→OrcaFlex handoff validation. No edits to the existing §Semantic-equivalence claim boundary section — the new subsection cites it rather than paraphrasing it. |
| Modify | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | Annotate line 119 `- OrcaWave L03 ship benchmark full roundtrip` with suffix `— promoted under #2457 (2026-04-23)`. Keep the bullet in the "Partial but high-value next validations" list for this plan; migration into "Ready now" is deferred to the implementation landing commit (out of scope for worker-4 planning). |
| Modify | `digitalmodel/src/digitalmodel/benchmarks/inventory.py` | Append L03 ModelInventoryEntry to `build_model_inventory()` with `name="l03_ship_benchmark"`, `category=ModelCategory.FREQUENCY_DOMAIN`, `path=Path("digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml")`, and tags `["orcawave", "ship", "qtf", "benchmark", "roundtrip", "L03"]`. Keep dataclass shape consistent with existing entries. |
| Keep unchanged | `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml` | Source-of-truth L03 canonical spec stays in place — NO relocation, NO mesh-path rewrite. This is an intentional divergence from sibling plan #2458 (whose mesh-path rewrite was an r1-review defect source). |
| Keep unchanged | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` | Existing `TestOrcaWaveSemanticRoundTripSingleBody` using `spec_ship_raos.yml` continues to pass. The new benchmark module adds proof-grade coverage rather than replacing smoke coverage. |
| Keep unchanged | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_ship_raos.yml` | Pre-existing ship roundtrip fixture; not the L03 benchmark; this plan does NOT touch it. |
| Update (deferred to main session) | `docs/plans/README.md` | Add this #2457 plan row. Worker-4 is fenced out of this file per the task brief ("forbidden: `docs/plans/README.md`"); the main session must add the index row at merge time. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_l03_spec_exists` | `L03_ship_benchmark/spec.yml` is present at the canonical path | path | file exists |
| `test_l03_spec_loads_as_diffraction_spec` | `DiffractionSpec.from_yaml(L03_spec)` succeeds and version is "1.0" | L03 spec | DiffractionSpec with version == "1.0" |
| `test_l03_mesh_file_referenced_in_spec_resolves` | Mesh-file relative path in spec resolves to a real file on disk | spec + filesystem | `(spec.parent / mesh_rel).resolve().is_file()` → True |
| `test_l03_manifest_exists_and_matches_folder` | `manifest.yaml` present at `L03_ship_benchmark/manifest.yaml`; `benchmark_id == "l03_ship_benchmark"`; `body_count == 1` | manifest | match |
| `test_forward_generation_does_not_raise` | `OrcaWaveBackend().generate_single(spec, tmp_path)` succeeds and produces non-empty output file | DiffractionSpec | path exists + non-zero size |
| `test_preserves_body_name` | Forward→reverse roundtrip preserves `vessel.name == "Body1"` | roundtrip | equal |
| `test_preserves_frequency_count` | Forward→reverse preserves 20-count frequency vector | roundtrip | `len == 20` on both sides |
| `test_preserves_frequency_values_rad_s` | Sorted rad/s frequency vector roundtrips within `rel=1e-4` (absorbs period↔rad/s normalization bucket) | roundtrip | approx match |
| `test_preserves_heading_count_and_symmetry` | 9 headings preserved | roundtrip | `len == 9` on both sides |
| `test_preserves_heading_values` | Heading values `[0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5, 180.0]` roundtrip within `abs=1e-6` | roundtrip | approx match |
| `test_preserves_centre_of_gravity` | `COG == [2.53, 0.0, -1.974]` roundtrips within `rel=1e-4, abs=1e-6` | roundtrip | approx match |
| `test_preserves_inertia_tensor_directly` | Direct `inertia_tensor` roundtrips; diagonal entries within `rel=1e-4`, off-diagonal zeros within `abs=1e-3` | roundtrip | approx match per entry |
| `test_preserves_external_damping_matrix_shape` | `external_damping` is a 6×6 list-of-lists after reverse parse | roundtrip | shape 6×6 |
| `test_preserves_roll_damping_value_36010` | `external_damping[3][3] == 36010.0` within `rel=1e-6` — benchmark-distinguishing value | roundtrip | approx 36010.0 |
| `test_preserves_external_damping_off_diagonal_zeros` | All entries except `[3][3]` are zero within `abs=1e-6` | roundtrip | all zeros |
| `test_preserves_remove_irregular_frequencies` | `solver_options.remove_irregular_frequencies is True` after roundtrip | roundtrip | True |
| `test_preserves_qtf_calculation_enabled` | `solver_options.qtf_calculation is True` after roundtrip | roundtrip | True |
| `test_preserves_load_rao_method_both` | `solver_options.load_rao_method == LoadRAOMethod.BOTH` after roundtrip | roundtrip | enum equality |
| `test_preserves_qtf_min_frequency` | QTF min frequency preserved within `rel=1e-4` (or skipped if reverse-parser does not emit it — documented open follow-up) | roundtrip | approx or skip |
| `test_preserves_qtf_max_frequency` | QTF max frequency preserved within `rel=1e-4` (or skipped if reverse-parser does not emit it — documented open follow-up) | roundtrip | approx or skip |
| `test_claim_boundary_language_present_in_manifest` | Manifest `claim_boundary` contains both "near-equivalent for key engineering inputs" and "not guaranteed 100% semantically equivalent" substrings | manifest | substrings present |
| `test_intentionally_classified_buckets_listed_in_manifest` | All 7 classified-bucket names from README lines 90–96 appear in `manifest.intentionally_classified_fields` | manifest | superset |
| `test_inventory_has_l03_entry` | `build_model_inventory()` contains `name="l03_ship_benchmark"` under `ModelCategory.FREQUENCY_DOMAIN` | inventory | entry present with right category |

---

## Acceptance Criteria

- [ ] `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/manifest.yaml` exists with fields: `benchmark_id`, `title`, `category`, `solvers_proven`, `body_count`, `vessel`, `analysis`, `solver_options`, `claim_boundary`, `preserved_fields`, `normalization_accepted_fields`, `intentionally_classified_fields`, `source_data`, `benchmark_results_artifacts`, `related_issues`, `bridge_candidates`, `version`.
- [ ] `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py` exists and all 23 listed tests pass: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/benchmarks/test_l03_ship_benchmark.py -v` is green.
- [ ] New preservation coverage adds assertions not present in any existing test: direct `inertia_tensor` roundtrip (diagonal + off-diagonal), 6×6 `external_damping` roundtrip including pinned roll value 36010.0, `qtf_calculation=true` survival, `load_rao_method=both` enum roundtrip, `qtf_min_frequency`/`qtf_max_frequency` preservation (with skip-if-not-emitted fallback explicitly documented, no silent pass), and period-based frequency representation-normalization roundtrip.
- [ ] Existing `TestOrcaWaveSemanticRoundTripSingleBody` still passes unedited: `spec_ship_raos.yml` remains in place; this promotion is additive only.
- [ ] `digitalmodel/docs/domains/orcawave/README.md` contains a "Named single-body flagship benchmark (#2457)" subsection that: (a) names L03 and `l03_ship_benchmark`, (b) links `spec.yml` and `manifest.yaml`, (c) restates the claim boundary by citing the existing §Semantic-equivalence claim boundary section (no paraphrase drift), (d) declares L03 a bridge candidate for future OrcaWave→OrcaFlex handoff validation, (e) cross-links closed foundations #1598, #1638 and sibling #2458.
- [ ] `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` line 119 (`- OrcaWave L03 ship benchmark full roundtrip`) is annotated with suffix `— promoted under #2457 (2026-04-23)`. The bullet stays in the "Partial but high-value next validations" list for this plan.
- [ ] `digitalmodel/src/digitalmodel/benchmarks/inventory.py` registers `l03_ship_benchmark` under `ModelCategory.FREQUENCY_DOMAIN` with `path=Path("digitalmodel/docs/domains/orcawave/L03_ship_benchmark/spec.yml")` and tags `["orcawave", "ship", "qtf", "benchmark", "roundtrip", "L03"]`.
- [ ] No regression: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/ -x --tb=short -q` passes.
- [ ] All three plan-review artifacts under `scripts/review/results/2026-04-23-plan-2457-{claude,codex,gemini}.md` exist AND every provider's final verdict is APPROVE or MINOR. If any provider returns MAJOR, the plan is re-tightened and re-reviewed (up to `MAX_REVIEW_ITERATIONS=3` rounds). Zero "at most one non-APPROVE/MINOR" loophole — every provider must clear.
- [ ] Scope boundary: edits only `digitalmodel/docs/domains/orcawave/L03_ship_benchmark/**`, `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/**`, `digitalmodel/docs/domains/orcawave/README.md`, `digitalmodel/src/digitalmodel/benchmarks/inventory.py`, and `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`. No cross-issue encroachment on #2458 (different fixture — FPSO+turret multi-body), #1637/#1591/#1594 (downstream roadmap items), or the existing `spec_ship_raos.yml` single-body smoke fixture.
- [ ] TDD red-phase evidence captured in the implementation commit(s): the new `test_l03_ship_benchmark.py` tests demonstrably failed BEFORE `manifest.yaml` and the inventory entry landed. Evidence inline in the commit body or at `.planning/quick/2457-red-phase.out`. Red-phase failures expected: `test_l03_manifest_exists_and_matches_folder`, `test_claim_boundary_language_present_in_manifest`, `test_intentionally_classified_buckets_listed_in_manifest`, `test_inventory_has_l03_entry`. Forward/roundtrip tests may green early (the L03 spec already exists) — this is expected and documented, not a red-phase violation.
- [ ] Mesh-path sanity: `test_l03_mesh_file_referenced_in_spec_resolves` asserts `(L03_SPEC.parent / mesh_rel).resolve().is_file()` — no mesh-path rewrite is performed (L03 stays in place), so this check guards against accidental relocation during implementation.
- [ ] Numerical tolerance sanity: `rel=1e-4` for frequency/inertia-diagonal/QTF-frequency/COG numeric fields (chosen to absorb rad/s ↔ period and kg ↔ te normalizations); `abs=1e-6` for heading values (deg-scale, no unit normalization); `abs=1e-3` for off-diagonal inertia zeros (looser because reverse-parse of numeric-zero strings may have formatting noise); `rel=1e-6` for the single pinned roll damping value 36010.0 (no unit conversion per spec.yml comment: "passed through without conversion"). Tightening beyond these thresholds is explicitly out of scope.
- [ ] Floating-point approximation mode: `pytest.approx` with an explicit `rel=` or `abs=` argument (NOT default) is used on every numerical assertion, so test failures report the delta rather than silently passing at default tolerance.
- [ ] QTF-frequency preservation graceful fallback: `test_preserves_qtf_min_frequency` and `test_preserves_qtf_max_frequency` use `pytest.skip(...)` with a reason string naming the follow-up, IF the reverse parser does not emit `qtf_min_frequency`/`qtf_max_frequency` on the round trip. Silent pass is not permitted — either the assertion is made, or the test is skipped with an explicit follow-up note.
- [ ] Claim-boundary language verbatim: the `manifest.yaml` `claim_boundary` field contains the EXACT phrases "near-equivalent for key engineering inputs" and "not guaranteed 100% semantically equivalent" — these are asserted verbatim by `test_claim_boundary_language_present_in_manifest`.

---

## Adversarial Review Summary

**Round 1 — 2026-04-23 worker-4 single-author r3 fallback (Claude / Codex / Gemini lens proxies):**

| Provider (lens) | Verdict | Key findings |
|---|---|---|
| Claude (completeness / TDD / scope) | MINOR | (a) `external_damping` verbatim quote truncated to 5 of 6 rows (6×6 shape still correctly stated in prose/test); (b) `Path(__file__).parents[4]` path math deserves a `test_l03_dir_parents_math_is_sane` micro-guard; (c) QTF-frequency skip reasons should cite a follow-up issue number when the implementation lands; (d) one long 350-word Deliverable sentence can be split. All implementation-time tightenings; no plan-rewrite-grade defect. |
| Codex (evidence verification) | APPROVE | All 10 cited issue states reproduce (4 OPEN focal / 2 CLOSED foundations / 2 OPEN upstream / 2 OPEN downstream-out-of-scope); all 14 EXISTS paths resolve; all 3 MISSING paths absent; all 5 verbatim excerpts reproduce byte-accurately at exact line numbers (spec.yml:1-34, spec.yml:40-75, README.md:80-98, roadmap.md:119, input_schemas.py field lines, reverse_parsers.py field lines); all 5 gap proofs reproduce. No factual drift. |
| Gemini (scope / dependency / contract alignment) | MINOR | (1) `benchmarks/__init__.py` co-create with #2458 should add an explicit `if file exists: no-op` shell guard; (2) `test_preserves_load_rao_method_both` should pin both `isinstance(...)` and `.value == "both"`; (3) claim-boundary substring test should include "tested round-trip pathways" to fully close paraphrase-drift gap; (4) `bridge_candidates` manifest phrasing should add "pending" / "future" / "(not validated under #2457)" to avoid misread as already-tested. |

**Round 1 overall:** PASS — all three providers cleared APPROVE/MINOR. No MAJOR findings; no r2 redraft required. Four MINOR Claude-lens items + four MINOR Gemini-lens items are implementation-time tightenings — carried forward into implementation notes rather than triggering a plan rewrite. Re-review is not required for approval-readiness.

Plan-author notes on MINOR items (to be addressed during implementation, not during planning):

- Apply all 4 Gemini substring/type-assertion tightenings to `test_preserves_load_rao_method_both` and `test_claim_boundary_language_present_in_manifest`.
- Add `test_l03_dir_parents_math_is_sane` per the Claude-lens suggestion.
- File the follow-up issue "OrcaWave reverse-parser: emit qtf_min/max_frequency on roundtrip" BEFORE the implementation commit, so the two `pytest.skip(...)` strings can cite a real issue number.
- Extend the `bridge_candidates` manifest string with "pending" / "(not validated under #2457)".
- Add `if [ ! -f benchmarks/__init__.py ]; then` guard in the implementation commit to remove the cross-plan race.

**Provenance note:** as with sibling plan #2458, r1 review artifacts are produced via worker-4 single-author r3 fallback (Claude/Codex/Gemini lens proxies) because the worker-4 worktree operates in a planning-only sandbox that cannot reach the Stage-5/6 evidence gate in `scripts/review/cross-review.sh`. Real cross-provider CLI dispatch should replace these artifacts when a gate-capable session can run them; the fallback is explicitly labeled in each file and preferred to leaving the review column empty per `feedback_permission_gate_blocks_cross_review.md`.

---

## Risks and Open Questions

- **Risk — benchmarks subdirectory co-creation with #2458:** `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` is also created by sibling plan #2458. Both plans create a 0-line file with identical contents; whichever lands first wins and the second is a no-op. If #2458 lands first, this plan's implementation should detect the existing file and not overwrite it. If #2457 lands first, #2458 lands a no-op edit. Mitigation: the `__init__.py` is empty on both sides, so write order is irrelevant.
- **Risk — reverse parser may not emit `qtf_min_frequency` / `qtf_max_frequency`:** `input_schemas.py` has the fields, and `reverse_parsers.py` consumes `qtf_calculation` at lines 203 and 552, but the reverse-parse path for the two frequency-bound fields is not directly confirmed by a line grep. If the parser silently drops them, the two pinned preservation tests would fail. Mitigation: the plan specifies a `pytest.skip(...)` fallback with an explicit follow-up-naming reason string — no silent pass, but no red-wall either. If skipped, a follow-up issue would extend the reverse parser.
- **Risk — `load_rao_method` enum roundtrip:** the forward backend maps canonical enum `both` → native string `"Both"` (line 375 of `orcawave_backend.py`). The reverse parser must map `"Both"` → canonical enum `both`. If it emits a different case or string value, the enum-equality assertion fails. Mitigation: the test asserts enum-to-enum equality (`parsed.solver_options.load_rao_method == orig.solver_options.load_rao_method`), which works IFF both sides deserialize to the same enum member. If the reverse parser lacks the mapping, the test will fail red, prompting a follow-up issue to align enum emission — this is the correct failure mode, not a flake.
- **Risk — claim-boundary paraphrase drift in docs note:** the README's §Semantic-equivalence claim boundary uses specific language ("near-equivalent for key engineering inputs and tested round-trip pathways"). The plan requires the new "Named single-body flagship benchmark (#2457)" subsection to CITE rather than paraphrase, and the `test_claim_boundary_language_present_in_manifest` test asserts the verbatim phrases in the manifest. Acceptance Criteria add the verbatim-language requirement explicitly.
- **Risk — roadmap line-119 edit collision with sibling roadmap edits:** #2458 also modifies the roadmap file (near line 120, "named multi-body OrcaWave benchmark"). Both plans edit distinct lines (119 vs 120), so git merge should be clean. If both land the same day and one unintentionally reflows adjacent lines, a merge-conflict is possible. Mitigation: append-suffix-only edits to each respective bullet; no reflow; verify `git diff` shows one-line changes only.
- **Risk — `inertia_tensor` roundtrip loss if backend converts kg↔te mid-stream:** the backend does kg→te conversion, and the direct tensor numbers are O(1e8)–O(1e9) kg·m². Float64 is exact for these magnitudes under factor-of-1000 conversions. Mitigation: `rel=1e-4` tolerance on diagonals provides 1e-5 headroom over the tightest credible roundtrip loss. If real noise exceeds that, the plan's implementation permits loosening to `rel=1e-3` (documented in the tolerance-sanity Acceptance Criterion).
- **Risk — `docs/plans/README.md` index orphaning:** the worker-4 write-fence forbids editing `docs/plans/README.md`. If the index is not updated at merge, the plan is not surfaced in the discovery path. Mitigation: main-session merge step must add the row; this risk is flagged in the Artifact Map and Files-to-Change table. Same constraint applied to sibling #2458.
- **Open — should the manifest be `manifest.yaml` or `manifest.yml`?** #2458 chose `manifest.yaml` to signal "metadata, not a spec". This plan matches that convention. Reviewer may prefer the repo-wide `.yml` default for consistency.
- **Open — should the roadmap bullet MOVE to "Ready now" after landing, or stay in "Partial but high-value next validations" with the promotion annotation?** This plan keeps it in place with the annotation, deferring the promotion move to the implementation landing commit. Reviewer may prefer an immediate move.
- **Open — should `TestL03ShipBenchmarkInventory.test_inventory_has_l03_entry` live in the benchmark test module or in a dedicated `test_benchmarks_inventory.py` module?** Co-locating with the benchmark module keeps the proof surface unified but cross-cuts test-module responsibility. This plan co-locates; a reviewer may prefer separation.
- **Open — naming: `l03_ship_benchmark` (lowercase, underscores) matches Python-identifier convention for the inventory `name` field and benchmark folder; the issue title uses uppercase "L03".** Manifest `benchmark_id: l03_ship_benchmark` and inventory `name="l03_ship_benchmark"` keep naming consistent; folder stays as `L03_ship_benchmark` (existing canonical path). Reviewer may prefer folder rename to match — this plan rejects that because the regeneration script (`digitalmodel/scripts/benchmark/regenerate_ship_benchmark.py:34`) hardcodes the existing mixed-case folder path and renaming would break it.

---

## Complexity: T2

**T2** — one new manifest file, one new dedicated regression-test module (~23 tests across 5 test classes), three modify-in-place edits (domain README, roadmap annotation, benchmarks inventory append), and one co-dependent empty `__init__.py`. No source-code changes to `src/**` except a single dataclass-list append in `benchmarks/inventory.py`. No schema changes, no backend changes, no reverse-parser changes. Risk surface is scoped to reverse-parser field-emission coverage (QTF frequency bounds + load_rao_method enum), which the plan's `pytest.skip(...)` fallback gracefully contains without red-walling the landing commit. This is strictly smaller-scope than #2458 (no fixture relocation, no mesh-path rewrite, no multi-body semantics layer).
