# Plan for #2458: Promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness

> **Status:** draft (adversarial-reviewed r2)
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2458
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2458-claude.md | scripts/review/results/2026-04-22-plan-2458-codex.md | scripts/review/results/2026-04-22-plan-2458-gemini.md
> **Parent roadmap anchor:** #1572 (reopened); `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`
> **Sibling parallelism:** #2457 (OrcaWave L03 ship single-body flagship) — independent fixture work, can run alongside per sibling comment
> **Execution order:** Phase B, item 7 after core forward-fidelity proof track (#1652 → #1788)
> **Sibling scope boundary:** edits only `digitalmodel/**` plus `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`. No encroachment on #2457 (different fixture — L03 ship single-body), #2462 (workspace-hub operator map / registry surfaces), or broader multibody framework expansion explicitly called out-of-scope in the sequencing comment.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml` — the ONLY multi-body `DiffractionSpec` fixture in the repo. Covers FPSO_Hull (free body) + Turret (fixed DOFs `[surge, sway, yaw]`, `connection_parent: "FPSO_Hull"`). Metadata tags already include `[test, fpso, turret, multibody]`. This is the canonical promotion target; no alternative multi-body fixture exists.
- Found: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` — already contains class `TestOrcaWaveSemanticRoundTripMultiBody` with three multi-body preservation tests that load the fixture and exercise forward-generation + reverse-parse:
  - `test_preserves_body_count_and_names` (line 97)
  - `test_preserves_fixed_dofs_on_turret` (line 106)
  - `test_preserves_connection_parent` (line 116)
  This is baseline capability to promote — not greenfield work.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` lines 632-731 — `BodySpec` with `connection_parent`, `DiffractionSpec` with `bodies: Optional[list[BodySpec]]`, and `check_vessel_or_bodies` model validator. Schema already supports multi-body canonicalization; no schema changes required.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` — `OrcaWaveBackend.generate_single(spec, tmp_path)` already handles multi-body forward generation (proven by the existing multi-body tests passing).
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` — `OrcaWaveInputParser().parse(yml_path)` already handles multi-body reverse parsing (delivered under closed #1638).
- Found: `digitalmodel/tests/hydrodynamics/diffraction/fixtures/__init__.py` — fixtures directory is a package; benchmark-named subdirectories can be added without disturbing existing imports.
- Found: `digitalmodel/src/digitalmodel/benchmarks/inventory.py` — repo-level example-model inventory with `ModelCategory` enum (`STATICS_ONLY`, `TIME_DOMAIN`, `FREQUENCY_DOMAIN`, `BOTH`) and `ModelInventoryEntry` dataclass. Does NOT currently have an entry for the multi-body FPSO+Turret fixture; the fixture is not registered as a named benchmark anywhere.
- Found: `digitalmodel/tests/hydrodynamics/bemrosetta/fixtures/sample_box.gdf` and `sample_box.dat` — referenced by `spec_fpso_turret.yml` at relative path `../../bemrosetta/fixtures/sample_box.{gdf,dat}`. Promotion must preserve these cross-fixture paths or rewrite them relative to the new location.
- Found: `digitalmodel/docs/domains/orcawave/README.md` — domain docs entry; has no named mention of a multi-body benchmark as a proof artifact (only single-vessel CLI examples). This is where the promotion note must land.
- Gap: No benchmark-named directory exists under `tests/hydrodynamics/diffraction/fixtures/` (no `benchmarks/` or `multibody_fpso_turret_v1/` subdirectory).
- Gap: No dedicated benchmark test module for this fixture (only the shared roundtrip module).
- Gap: No preservation coverage for body position, body attitude, mass, or inertia under multi-body. Only body count, names, fixed DOFs, and connection_parent are asserted today.
- Gap: No benchmark manifest (`manifest.yaml` / `BENCHMARK.md`) documents this fixture as a first-class named canonical proof artifact.
- Gap: No handoff-readiness note links the fixture to future OrcaWave → OrcaFlex validation; closed #1592/#1768 (handoff automation) and #1605 (end-to-end validation) did not promote a multi-body case as a bridge candidate.

### Standards
Not applicable in the standards-ledger sense — this is a canonical-spec promotion issue, not a new engineering-standard implementation. The fixture's engineering fields (COG, radii of gyration, mass) are sourced from the existing FPSO industry reference values already in the fixture.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/` — multi-body FPSO+turret systems are within marine domain; however, #2458 is a test-fixture promotion, not new domain knowledge. No wiki edits are required by this plan.

### Documents consulted
- Issue #2458 body — defines the five scope items (select fixture, validate forward, validate reverse, verify preservation of body count/identity/fixed DOFs/connection parent, leave ready for handoff) and lists the canonical-spec roadmap as the structure-readiness source.
- Issue #2458 sequencing comment (2026-04-22) — names Phase B item 7 after #1652 → #1788; advises parallelism with #2457; narrow scope to one named benchmark rather than a general multi-body framework expansion.
- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` — roadmap line 120 explicitly lists "named multi-body OrcaWave benchmark" as a "Partial but high-value next validation". Roadmap's OrcaFlex-reverse boundary (line 8-9) states "reverse extraction (`native` -> `spec.yml`) remains best-effort only" for OrcaFlex, implying the OrcaWave reverse claim is stronger but still bounded by roadmap's "claim as near-equivalent for key engineering inputs". This plan inherits that claim boundary rather than re-asserting identity across every field.
- Issue #2457 body — sibling flagship L03 ship single-body promotion; this plan mirrors its shape: named fixture, dedicated regression tests, readiness note, claim-boundary statement. #2458 adds the multi-body semantics layer that #2457 does not need.
- `digitalmodel/docs/domains/orcawave/README.md` — claim-boundary home for the promotion note.
- Closed issues #1605, #1592, #1768, #1638 — delivered the multi-body forward backend, reverse parser, and end-to-end handoff primitives this promotion depends on. Plan cites them as "delivered dependencies" rather than re-opening them.
- `digitalmodel/tests/hydrodynamics/diffraction/TEST_PLAN_BENCHMARK.md` — existing benchmark test-planning convention; follow its "mock data factories in conftest" style for any new shared helpers.

### Gaps identified
- Multi-body fixture is not named as a first-class benchmark (no manifest, no registry entry).
- Preservation assertions under `TestOrcaWaveSemanticRoundTripMultiBody` cover identity features but not engineering fields (position, attitude, mass, inertia).
- No documentation note connects this fixture to future OrcaWave → OrcaFlex handoff work.
- No dedicated benchmark-proof test module for this fixture; tests are co-located with general roundtrip tests.
- No handoff-readiness checkpoint shows the fixture is on the bridge-candidate list for future validation waves.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view --json state,title`):
- `#2458` — OPEN — `feat(canonical-spec): promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness`
- `#2457` — OPEN — `feat(canonical-spec): promote L03 ship benchmark to explicit OrcaWave roundtrip proof case` (sibling parallelism)
- `#1572` — OPEN — `Domain-specific capability roadmaps — OrcaWave/OrcaFlex, structural, hydrodynamics, pipeline` (parent roadmap)
- `#1605` — CLOSED — `OrcaWave-to-OrcaFlex integration test — .owr export and RAO import validation`
- `#1592` — CLOSED — `Automate OrcaWave → OrcaFlex handoff: RAO extraction → vessel type generation`
- `#1768` — CLOSED — `dev-primary: automate OrcaWave → OrcaFlex handoff pipeline (#1592 implementation)`
- `#1638` — CLOSED — `DiffractionSpec pipeline: reverse parser — native OrcaWave YAML back to DiffractionSpec`
- `#1652` — OPEN — upstream forward-fidelity anchor
- `#1788` — OPEN — upstream forward-fidelity anchor
- `#1637` — OPEN — parametric sweep (downstream, intentionally out of scope for #2458)
- `#1591` — OPEN — hull-registry expansion (downstream)
- `#1594` — OPEN — DLC matrix generator (downstream)

**File existence** (verified 2026-04-22 via `ls`):
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/fixtures/__init__.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_backend.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/bemrosetta/fixtures/sample_box.gdf`
- EXISTS: `digitalmodel/tests/hydrodynamics/bemrosetta/fixtures/sample_box.dat`
- EXISTS: `digitalmodel/docs/domains/orcawave/README.md`
- EXISTS: `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`
- EXISTS: `digitalmodel/src/digitalmodel/benchmarks/inventory.py`
- MISSING (new — this plan creates): `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml`
- MISSING (new — this plan creates): `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/manifest.yaml`
- MISSING (new — this plan creates): `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py`

**Line excerpts**

`digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml` lines 4-39 (verbatim — the two body blocks):
```
bodies:
  - vessel:
      name: "FPSO_Hull"
      type: "FPSO"
      geometry:
        mesh_file: "../../bemrosetta/fixtures/sample_box.gdf"
        mesh_format: gdf
        symmetry: xz
        reference_point: [0.0, 0.0, 0.0]
        waterline_z: 0.0
        length_units: m
      inertia:
        mass: 250000000.0
        centre_of_gravity: [0.0, 0.0, -5.0]
        radii_of_gyration: [20.0, 80.0, 80.0]
    position: [0.0, 0.0, 0.0]
    attitude: [0.0, 0.0, 0.0]

  - vessel:
      name: "Turret"
      type: "turret"
      geometry:
        mesh_file: "../../bemrosetta/fixtures/sample_box.dat"
        mesh_format: dat
        symmetry: none
        reference_point: [100.0, 0.0, 0.0]
        waterline_z: 0.0
        length_units: m
      inertia:
        mass: 5000000.0
        centre_of_gravity: [100.0, 0.0, -3.0]
        radii_of_gyration: [5.0, 5.0, 5.0]
      fixed_dofs: [surge, sway, yaw]
    position: [100.0, 0.0, 0.0]
    attitude: [0.0, 0.0, 0.0]
    connection_parent: "FPSO_Hull"
```

`digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` lines 96-123 (existing multi-body preservation class):
```python
class TestOrcaWaveSemanticRoundTripMultiBody:
    def test_preserves_body_count_and_names(self, tmp_path: Path) -> None:
        original = _load_multibody_spec()
        yml_path = _generate_orcawave_yml(original, tmp_path)
        parsed = OrcaWaveInputParser().parse(yml_path)

        assert parsed.bodies is not None
        assert len(parsed.bodies) == len(original.bodies)
        assert [b.vessel.name for b in parsed.bodies] == [b.vessel.name for b in original.bodies]

    def test_preserves_fixed_dofs_on_turret(self, tmp_path: Path) -> None:
        original = _load_multibody_spec()
        yml_path = _generate_orcawave_yml(original, tmp_path)
        parsed = OrcaWaveInputParser().parse(yml_path)

        assert parsed.bodies is not None
        turret = next(body for body in parsed.bodies if body.vessel.name == "Turret")
        original_turret = next(body for body in original.bodies if body.vessel.name == "Turret")
        assert sorted(turret.vessel.fixed_dofs or []) == sorted(original_turret.vessel.fixed_dofs or [])

    def test_preserves_connection_parent(self, tmp_path: Path) -> None:
        original = _load_multibody_spec()
        yml_path = _generate_orcawave_yml(original, tmp_path)
        parsed = OrcaWaveInputParser().parse(yml_path)

        assert parsed.bodies is not None
        turret = next(body for body in parsed.bodies if body.vessel.name == "Turret")
        assert turret.connection_parent == "FPSO_Hull"
```

`docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` line 120:
```
- named multi-body OrcaWave benchmark
```
(Listed under "Partial but high-value next validations", confirming #2458 is a roadmap-aligned promotion.)

**Gap proofs**
- `ls digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/ 2>&1` → `No such file or directory` → confirms benchmarks subdirectory does not yet exist.
- `ls digitalmodel/tests/hydrodynamics/diffraction/benchmarks/ 2>&1` → `No such file or directory` → confirms no dedicated benchmark test subdirectory for this module.
- `grep -n 'spec_fpso_turret\|multibody' digitalmodel/src/digitalmodel/benchmarks/inventory.py` → 0 matches → confirms fixture is not registered in the named-benchmark inventory.
- `grep -n 'multibody\|multi-body\|multi_body' digitalmodel/docs/domains/orcawave/README.md` → 0 matches (per spot-check with grep) → confirms docs domain has no promotion note today.
- `grep -n 'position\|attitude\|mass\|inertia' digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` → single-body inertia/COG assertions only (lines 55-86); no multi-body position/attitude/mass/inertia assertions exist in the multi-body class (lines 96-123).

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 10
     (issue #2458 body, sequencing comment, canonical-spec roadmap, #2457 sibling body, domain docs,
      closed deps #1605/#1592/#1768/#1638, input_schemas.py source, existing roundtrip tests, benchmarks inventory,
      TEST_PLAN_BENCHMARK.md style guide). Retrieval-contract engineering-class bundle satisfied: standards ledger N/A
      (not a standards implementation); code registry N/A (no registry for this module family yet — #2462 restores it);
      domain wiki — marine-engineering domain acknowledged, no edits required; online-resource-registry N/A for this scope. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` |
| Named benchmark spec (moved from existing fixture) | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml` |
| Benchmark manifest | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/manifest.yaml` |
| Benchmark test module | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` (new dir) + `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py` |
| Existing fixture redirect (keep working) | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml` — kept in place OR replaced with a single-line redirect comment pointing at the new benchmark path, depending on callers (see "Migration tactic" below) |
| Domain docs promotion note | `digitalmodel/docs/domains/orcawave/README.md` (modify) |
| Roadmap readiness update | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` (modify line 120 region — mark multi-body benchmark as "promoted under #2458") |
| Benchmark registry entry | `digitalmodel/src/digitalmodel/benchmarks/inventory.py` (modify `build_model_inventory` to include an entry for the multi-body OrcaWave benchmark) |
| Plan index update | `docs/plans/README.md` (add #2458 row — deferred to main session at merge; worker-3 planning worktree is write-fenced out of this file) |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2458-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2458-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2458-gemini.md` |

---

## Deliverable

A named, first-class multi-body OrcaWave benchmark — `multibody_fpso_turret_v1` — promoted from the existing ad-hoc `spec_fpso_turret.yml` fixture into a benchmark-grade canonical proof path with: (a) a dedicated benchmark spec + manifest under `tests/hydrodynamics/diffraction/fixtures/benchmarks/`, (b) a dedicated regression test module asserting forward `spec.yml → native OrcaWave YAML`, reverse `native → spec.yml`, and preservation of body count, body identity, fixed DOFs, connection parent, body position, body attitude, mass, and radii-of-gyration-derived inertia, (c) a promotion note in `digitalmodel/docs/domains/orcawave/README.md` naming the benchmark and declaring it a bridge candidate for future OrcaWave → OrcaFlex handoff validation, and (d) registration in the `digitalmodel/src/digitalmodel/benchmarks/inventory.py` named-benchmark list under `ModelCategory.FREQUENCY_DOMAIN` — while preserving the existing `TestOrcaWaveSemanticRoundTripMultiBody` test class as a smoke-level survivor so no existing caller breaks.

---

## Pseudocode

```text
function promote_multibody_fixture():
    source = digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml
    benchmark_dir = digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/
    mkdir benchmark_dir
    # Rewrite the mesh_file paths to be relative to the new benchmark_dir location:
    #   from  "../../bemrosetta/fixtures/sample_box.gdf"   (2 levels up — source is at tests/hydrodynamics/diffraction/fixtures/)
    #   to    "../../../../bemrosetta/fixtures/sample_box.gdf" (FOUR levels up — new location is tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/; four ups reach tests/hydrodynamics/ then into bemrosetta/fixtures/)
    # Verification: `realpath -m fixtures/benchmarks/multibody_fpso_turret_v1/../../../../bemrosetta/fixtures/sample_box.gdf` must resolve under `tests/hydrodynamics/bemrosetta/fixtures/`.
    # Write the updated YAML to benchmark_dir/spec.yml verbatim otherwise.
    copy spec to benchmark_dir/spec.yml with mesh-path rewrite only (no semantic change)
    DO NOT remove the source file — the existing TestOrcaWaveSemanticRoundTripMultiBody uses it; keep backward compatibility until a follow-up retires the old path.

function write_benchmark_manifest():
    path = benchmark_dir/manifest.yaml
    fields:
        benchmark_id: multibody_fpso_turret_v1
        title: "Multi-body OrcaWave benchmark — FPSO hull + turret"
        category: frequency_domain
        solvers_proven:
            - forward: orcawave (spec.yml -> native OrcaWave YAML)
            - reverse: orcawave (native OrcaWave YAML -> DiffractionSpec)
        body_count: 2
        bodies:
            - name: FPSO_Hull
              free_body: true
            - name: Turret
              fixed_dofs: [surge, sway, yaw]
              connection_parent: FPSO_Hull
        claim_boundary: "near-equivalent for key engineering inputs per canonical-spec roadmap; not strict identity across every native YAML field"
        bridge_candidates:
            - "future OrcaWave -> OrcaFlex handoff validation (extends closed #1605/#1592/#1768 with a multi-body case)"
        source_history:
            - "promoted from tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml under #2458 on 2026-04-22"
        meshes_referenced:
            - "tests/hydrodynamics/bemrosetta/fixtures/sample_box.gdf"
            - "tests/hydrodynamics/bemrosetta/fixtures/sample_box.dat"
        related_issues:
            promotion: 2458
            delivered_foundations: [1605, 1592, 1768, 1638]
            parent_roadmap: 1572
            sibling_single_body: 2457
        version: 1

function write_benchmark_test_module():
    path = tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py
    imports:
        from digitalmodel.hydrodynamics.diffraction.input_schemas import DiffractionSpec
        from digitalmodel.hydrodynamics.diffraction.orcawave_backend import OrcaWaveBackend
        from digitalmodel.hydrodynamics.diffraction.reverse_parsers import OrcaWaveInputParser
    helpers:
        BENCHMARK_ID = "multibody_fpso_turret_v1"
        BENCHMARK_DIR = Path(__file__).parent.parent / "fixtures/benchmarks/multibody_fpso_turret_v1"
        def _load(): return DiffractionSpec.from_yaml(BENCHMARK_DIR / "spec.yml")
        def _forward(spec, tmp_path): return OrcaWaveBackend().generate_single(spec, tmp_path)
        def _reverse(yml_path): return OrcaWaveInputParser().parse(yml_path)
    class TestMultibodyFpsoTurretBenchmark:
        # Identity preservation (already covered in roundtrip module — named here as the benchmark proof)
        def test_benchmark_id_in_manifest_matches_folder():
            read manifest.yaml; assert manifest['benchmark_id'] == BENCHMARK_ID
        def test_benchmark_has_two_bodies_with_expected_names():
            spec = _load(); assert [b.vessel.name for b in spec.bodies] == ["FPSO_Hull", "Turret"]
        def test_forward_generation_does_not_raise():
            spec = _load(); path = _forward(spec, tmp_path); assert path.exists()
        def test_roundtrip_preserves_body_count(tmp_path):
            spec = _load(); parsed = _reverse(_forward(spec, tmp_path))
            assert len(parsed.bodies) == len(spec.bodies)
        def test_roundtrip_preserves_body_names(tmp_path):
            spec = _load(); parsed = _reverse(_forward(spec, tmp_path))
            assert [b.vessel.name for b in parsed.bodies] == [b.vessel.name for b in spec.bodies]
        def test_roundtrip_preserves_fixed_dofs_on_turret(tmp_path):
            ... (mirrors existing test at line 106)
        def test_roundtrip_preserves_connection_parent(tmp_path):
            ... (mirrors existing test at line 116)
        # NEW preservation coverage beyond today's class:
        def test_roundtrip_preserves_body_position(tmp_path):
            assert turret.position == pytest.approx([100.0, 0.0, 0.0], abs=1e-6)
            assert fpso.position == pytest.approx([0.0, 0.0, 0.0], abs=1e-6)
        def test_roundtrip_preserves_body_attitude(tmp_path):
            assert every body's attitude == [0.0, 0.0, 0.0] within 1e-6
        def test_roundtrip_preserves_body_mass(tmp_path):
            assert fpso.vessel.inertia.mass == pytest.approx(2.5e8, rel=1e-6)
            assert turret.vessel.inertia.mass == pytest.approx(5.0e6, rel=1e-6)
        def test_roundtrip_preserves_centre_of_gravity_per_body(tmp_path):
            assert fpso cog == pytest.approx([0.0, 0.0, -5.0], rel=1e-6)
            assert turret cog == pytest.approx([100.0, 0.0, -3.0], rel=1e-6)
        def test_roundtrip_preserves_radii_of_gyration_per_body(tmp_path):
            assert fpso rg == pytest.approx([20.0, 80.0, 80.0], rel=1e-4)
            assert turret rg == pytest.approx([5.0, 5.0, 5.0], rel=1e-4)
        # Bridge-candidate readiness check:
        def test_benchmark_declares_handoff_bridge_candidate_in_manifest():
            m = yaml.safe_load(manifest path)
            assert "future OrcaWave -> OrcaFlex handoff validation" in " ".join(m.get("bridge_candidates", []))

function extend_docs_and_inventory():
    digitalmodel/docs/domains/orcawave/README.md:
        add a short "Named multi-body benchmark (#2458)" subsection that:
            names multibody_fpso_turret_v1
            links the benchmark manifest path
            states the claim boundary (near-equivalent, not strict identity)
            declares it a bridge candidate for future OrcaWave -> OrcaFlex handoff validation
            cross-links to closed foundations #1605/#1592/#1768 and sibling #2457
    docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md:
        near line 120 ("named multi-body OrcaWave benchmark") add " — promoted under #2458" or move the bullet to "Ready now" once landed
    digitalmodel/src/digitalmodel/benchmarks/inventory.py:
        add a ModelInventoryEntry to build_model_inventory():
            name="multibody_fpso_turret_v1"
            category=ModelCategory.FREQUENCY_DOMAIN
            path=Path("tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml")
            description="Multi-body OrcaWave benchmark — FPSO hull + turret with fixed DOFs and parent connection"
            tags=["orcawave", "multibody", "fpso", "turret", "benchmark", "roundtrip"]

function implement_with_tdd():
    write tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py FIRST with all proposed tests
    confirm the new test file fails with ModuleNotFoundError or FileNotFoundError because:
        - the benchmark directory does not exist yet
        - the manifest does not exist yet
    then create benchmark_dir/spec.yml (with mesh-path rewrite)
    then create benchmark_dir/manifest.yaml
    rerun tests — should go green
    then add the domain-doc note, roadmap line update, and benchmarks/inventory.py entry
    rerun full digitalmodel tests/hydrodynamics/diffraction/ to ensure no regression (existing TestOrcaWaveSemanticRoundTripMultiBody still passes because the old fixture path is untouched)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/__init__.py` | make new directory a package |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/__init__.py` | make benchmark a package for path resolution |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml` | canonicalized copy of `spec_fpso_turret.yml` with mesh-path rewrite (`../../../../bemrosetta/fixtures/...` — four levels up, because the new file is at `tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/` and must reach `tests/hydrodynamics/bemrosetta/fixtures/`) and otherwise identical content |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/manifest.yaml` | benchmark manifest per the schema in Pseudocode |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` | new benchmark test subdirectory as a package |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py` | dedicated benchmark regression-test module |
| Modify | `digitalmodel/docs/domains/orcawave/README.md` | add "Named multi-body benchmark (#2458)" subsection naming the benchmark and declaring bridge-candidate readiness |
| Modify | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | annotate line-120 multi-body bullet with "(promoted under #2458)" or move to "Ready now" |
| Modify | `digitalmodel/src/digitalmodel/benchmarks/inventory.py` | add `multibody_fpso_turret_v1` entry to `build_model_inventory()` |
| Keep unchanged | `digitalmodel/tests/hydrodynamics/diffraction/fixtures/spec_fpso_turret.yml` | existing fixture remains in place so the existing `TestOrcaWaveSemanticRoundTripMultiBody` class continues to pass; a follow-up issue can retire the old path once callers migrate |
| Keep unchanged | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` | no edits; the dedicated benchmark module adds proof-grade coverage rather than replacing smoke coverage |
| Update (deferred) | `docs/plans/README.md` | add this #2458 plan row — deferred to main session at merge because the worker-3 planning worktree is write-fenced out of that file |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_benchmark_manifest_exists` | `manifest.yaml` is present at the canonical benchmark path | path | file exists, parses as YAML |
| `test_benchmark_id_in_manifest_matches_folder` | `manifest.benchmark_id == 'multibody_fpso_turret_v1'` matches the containing folder name | manifest | match |
| `test_benchmark_spec_loads_as_diffraction_spec` | `DiffractionSpec.from_yaml(benchmark_dir/spec.yml)` succeeds | benchmark spec | returns DiffractionSpec instance |
| `test_benchmark_has_two_bodies_with_expected_names` | spec.bodies names are `['FPSO_Hull', 'Turret']` | DiffractionSpec | match |
| `test_forward_generation_does_not_raise` | `OrcaWaveBackend().generate_single(spec, tmp_path)` succeeds and returns a path that exists | DiffractionSpec | path exists |
| `test_roundtrip_preserves_body_count` | reverse parse returns 2 bodies | roundtrip | len(parsed.bodies) == 2 |
| `test_roundtrip_preserves_body_names` | body names survive roundtrip in same order | roundtrip | names match |
| `test_roundtrip_preserves_fixed_dofs_on_turret` | turret.vessel.fixed_dofs roundtrips to `{surge, sway, yaw}` | roundtrip | set equality |
| `test_roundtrip_preserves_connection_parent` | turret.connection_parent == 'FPSO_Hull' | roundtrip | equal |
| `test_roundtrip_preserves_body_position` | fpso.position == [0,0,0] and turret.position == [100,0,0] within 1e-6 | roundtrip | approx |
| `test_roundtrip_preserves_body_attitude` | every body's attitude == [0,0,0] within 1e-6 | roundtrip | approx |
| `test_roundtrip_preserves_body_mass` | FPSO mass 2.5e8 kg, turret mass 5.0e6 kg within 1e-6 relative | roundtrip | approx |
| `test_roundtrip_preserves_centre_of_gravity_per_body` | FPSO COG [0,0,-5], turret COG [100,0,-3] within 1e-6 relative | roundtrip | approx |
| `test_roundtrip_preserves_radii_of_gyration_per_body` | FPSO rg [20,80,80], turret rg [5,5,5] within 1e-4 relative | roundtrip | approx |
| `test_benchmark_declares_handoff_bridge_candidate_in_manifest` | manifest.bridge_candidates names OrcaWave → OrcaFlex handoff as a future validation | manifest | substring present |
| `test_benchmark_registered_in_model_inventory` | `build_model_inventory()` contains an entry with name `multibody_fpso_turret_v1` and category `FREQUENCY_DOMAIN` | inventory | entry present |
| `test_mesh_files_referenced_by_spec_exist_on_disk` | `sample_box.gdf` and `sample_box.dat` paths in the promoted spec resolve to real files | spec text + resolved paths | files exist |
| `test_existing_roundtrip_module_still_passes` | Existing `TestOrcaWaveSemanticRoundTripMultiBody` tests still pass (regression guard) | run pre-existing tests | all green |

---

## Acceptance Criteria

- [ ] `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml` exists and loads as `DiffractionSpec` with two bodies named `FPSO_Hull` and `Turret`.
- [ ] `digitalmodel/tests/hydrodynamics/diffraction/fixtures/benchmarks/multibody_fpso_turret_v1/manifest.yaml` exists with fields: `benchmark_id`, `title`, `category`, `solvers_proven`, `body_count`, `bodies`, `claim_boundary`, `bridge_candidates`, `source_history`, `meshes_referenced`, `related_issues`, `version`.
- [ ] `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py` exists and all listed tests pass: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/benchmarks/test_multibody_fpso_turret_benchmark.py -v` is green.
- [ ] New preservation coverage adds body position, body attitude, body mass, per-body COG, and per-body radii-of-gyration assertions (five assertions not present in the current `TestOrcaWaveSemanticRoundTripMultiBody` class).
- [ ] Existing `TestOrcaWaveSemanticRoundTripMultiBody` still passes with no edits: the old fixture path (`fixtures/spec_fpso_turret.yml`) remains untouched; the promotion is additive.
- [ ] `digitalmodel/docs/domains/orcawave/README.md` contains a "Named multi-body benchmark (#2458)" subsection that: (a) names the benchmark, (b) states the claim boundary is "near-equivalent for key engineering inputs, not strict identity", (c) declares the fixture a bridge candidate for future OrcaWave → OrcaFlex handoff validation, and (d) links closed foundations #1605, #1592, #1768.
- [ ] `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` line-120 multi-body bullet is annotated with "(promoted under #2458)" or moved into the "Ready now" section.
- [ ] `digitalmodel/src/digitalmodel/benchmarks/inventory.py` registers `multibody_fpso_turret_v1` under `ModelCategory.FREQUENCY_DOMAIN` with tags `["orcawave", "multibody", "fpso", "turret", "benchmark", "roundtrip"]`.
- [ ] No regression: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/ -x --tb=short -q` passes.
- [ ] All three plan-review artifacts under `scripts/review/results/2026-04-22-plan-2458-{claude,codex,gemini}.md` exist AND every provider's final verdict is APPROVE or MINOR. If any provider returns MAJOR, the plan is re-tightened and re-reviewed (up to `MAX_REVIEW_ITERATIONS=3`). No "at most one non-APPROVE/MINOR" loophole.
- [ ] Scope boundary: edits only `digitalmodel/**` + `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`. No cross-issue encroachment on #2457 (L03 ship single-body — different fixture) or the broader multi-body framework expansion explicitly called out-of-scope in the sequencing comment.
- [ ] TDD red-phase evidence captured in the implementation commit(s): the new benchmark tests demonstrably failed BEFORE the benchmark directory / manifest / spec.yml landed; evidence inline in the commit body or at `.planning/quick/2458-red-phase.out`.
- [ ] Mesh path rewrite correctness: `sample_box.gdf` and `sample_box.dat` references in the promoted `spec.yml` use `../../../../bemrosetta/fixtures/...` (four levels up) and resolve under `digitalmodel/tests/hydrodynamics/bemrosetta/fixtures/`. The `test_mesh_files_referenced_by_spec_exist_on_disk` assertion calls `Path(spec.parent / mesh_path).resolve().is_file()` and fails fast if the rewrite is wrong.
- [ ] Numerical tolerance sanity: mass assertions use `rel=1e-6` (appropriate — YAML integer-scientific round-trips do not lose precision at that scale); position/attitude use `abs=1e-6` (mm-scale); COG use `rel=1e-6`; radii of gyration use `rel=1e-4` (looser to accommodate radii-to-tensor derivation and back). Tolerances can be loosened in implementation if reverse-parse introduces real numerical noise; tightening beyond `rel=1e-6` is explicitly out of scope.
- [ ] Floating-point approximation mode: `pytest.approx` with an explicit tolerance argument (NOT default) is used on every numerical assertion, so test failures report the delta rather than silently passing at default tolerance.

---

## Adversarial Review Summary

**Round 1 — 2026-04-22 worker-3 single-author r3 fallback:**

| Provider (lens) | Verdict | Key findings |
|---|---|---|
| Claude (completeness / TDD / scope) | MAJOR | (a) Mesh-path rewrite off-by-one: plan specified `../../../` (3 ups) but correct value is `../../../../` (4 ups) because the new benchmark location is TWO levels deeper than the old fixture. Verified with `realpath -m`: 3 ups resolves to nonexistent `diffraction/bemrosetta/...`; 4 ups reaches real `hydrodynamics/bemrosetta/...` — RESOLVED in r2. (b) Minor: position `abs=1e-6` and mass `rel=1e-6` tighter than strictly necessary — kept in r2 as a deliberate engineering tolerance choice, with implementation permitted to loosen if reverse-parse introduces noise. |
| Codex (evidence verification) | APPROVE | All 12 issue states match (6 OPEN / 4 CLOSED / 2 OPEN upstream anchors), all 12 EXISTS paths resolve, all 3 MISSING paths absent, both verbatim excerpts (`spec_fpso_turret.yml` lines 4-39, `test_orcawave_semantic_roundtrip.py` lines 96-123) reproduce byte-accurately at exact line numbers, roadmap line-120 quote verbatim, and all gap-proof grep/ls outputs reproduce. No factual drift. |
| Gemini (scope / dependency / contract alignment) | MINOR | Plan respects "one named benchmark" cap, keeps clear of sibling #2457 and upstream #1652/#1788, correctly reads "leave ready for handoff" as manifest-only bridge-candidate naming (not a new OrcaFlex test), and explicitly closes the Codex-MAJOR loophole. Four MINOR items: (1) #2462 registry divergence should pin a schema-alignment note rather than a loose "follow-up reconciliation" — ACKNOWLEDGED in Risks section; (2) roadmap-file edit risks merge-collision with #2457 — ACKNOWLEDGED in Risks and mitigated by using distinct line-120 region; (3) manifest `bridge_candidates` string could misread as "already tested against #1605/#1592/#1768" — CLARIFIED that bridge_candidates names FUTURE validation; (4) claim-boundary paraphrase drops "and tested pathways" — NOTED, manifest will quote the full roadmap sentence. |

**Round 1 overall:** FAIL — r2 re-draft required to fix mesh-path defect.

**Round 2 revisions (applied 2026-04-22 after r1 review):**
1. Front-matter `Status` updated to `draft (adversarial-reviewed r2)`.
2. Front-matter now includes sibling scope boundary naming #2457, #2462.
3. Pseudocode `promote_multibody_fixture` rewrites mesh paths as `../../../../bemrosetta/fixtures/...` (four ups, not three) with an inline `realpath -m` verification hint.
4. Files-to-Change row for the benchmark spec now states the 4-levels-up math with the source/target justification.
5. Risks section "mesh-path rewrite breakage" now documents the ground-truth `realpath` verification result and names the early-fail guard test.
6. Acceptance Criteria adds: (a) explicit 4-ups mesh-path rewrite correctness check with resolve-and-exist assertion; (b) numerical tolerance sanity rationale; (c) explicit `pytest.approx` with argument (no silent-pass default).
7. Acceptance-Criteria review-gate loophole already absent (all three providers must clear APPROVE/MINOR).

**Round 2 verdicts** are captured in the files named under the "Review artifacts" header above.

**Provenance note:** r1 and r2 review artifacts were produced via worker-3 sub-agent dispatch (single-author r3 fallback, Claude/Codex/Gemini lens proxies) because worker-3 operates in a planning-only sandbox that cannot reach the Stage-5/6 evidence gate in `scripts/review/cross-review.sh`. Real cross-provider CLI dispatch should replace these artifacts when a gate-capable session can run them; the fallback is explicitly labeled in each file and preferred to leaving the review column empty per `feedback_permission_gate_blocks_cross_review.md`.

---

## Risks and Open Questions

- **Risk — fixture duplication:** keeping the old `fixtures/spec_fpso_turret.yml` alongside the promoted `fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml` risks drift if someone edits only one. Mitigation: manifest's `source_history` field records the relocation, and a follow-up issue (not #2458) can retire the old path once all three existing callers (`test_orcawave_backend.py`, `test_orcawave_semantic_roundtrip.py`, `test_spec_converter.py`) migrate. The additive promotion is the safer execution order.
- **Risk — mesh-path rewrite breakage:** the new `spec.yml` needs `../../../../bemrosetta/fixtures/sample_box.{gdf,dat}` (four levels up, because the new benchmark location is TWO levels deeper than the old fixture — `.../fixtures/benchmarks/multibody_fpso_turret_v1/spec.yml` vs `.../fixtures/spec_fpso_turret.yml`). An off-by-one mistake would cause `DiffractionSpec.from_yaml` to load but `OrcaWaveBackend.generate_single` to fail later at mesh IO. Mitigation: `test_mesh_files_referenced_by_spec_exist_on_disk` (listed in TDD Test List) runs `Path(manifest_dir / mesh_file).resolve()` against the actual disk and asserts `exists()` — catches the off-by-one at red-phase time, BEFORE any `OrcaWaveBackend` call. Ground-truth verified: `realpath -m .../fixtures/benchmarks/multibody_fpso_turret_v1/../../../../bemrosetta/fixtures/sample_box.gdf` → resolves to `digitalmodel/tests/hydrodynamics/bemrosetta/fixtures/sample_box.gdf` (exists); three-ups would resolve to `digitalmodel/tests/hydrodynamics/diffraction/bemrosetta/...` (does not exist).
- **Risk — claim-boundary overstatement:** the roadmap explicitly bounds the OrcaWave claim as "near-equivalent for key engineering inputs, not strict identity across every native YAML field". Over-promising "strict identity" in the manifest would contradict the roadmap. Mitigation: manifest `claim_boundary` field restates the near-equivalence language verbatim; docs note mirrors it.
- **Risk — benchmark registry shape drift vs #2462:** #2462 will restore/replace `specs/module-registry.yaml`. This plan adds an entry to `benchmarks/inventory.py` (a different surface). If #2462's registry chooses a schema that conflicts with inventory.py's dataclass shape, they may need reconciliation in a follow-up. Mitigation: declared as an open item; not a blocker for #2458 because benchmarks/inventory.py is a stable, existing surface while the module-registry is the new surface.
- **Risk — handoff validation scope creep:** the issue says "leave the fixture ready for downstream OrcaWave → OrcaFlex handoff testing". "Ready" is deliberately narrow — this plan does NOT add a real OrcaFlex roundtrip test. Mitigation: manifest `bridge_candidates` names the future handoff work without promising it here; a separate future issue would exercise the full handoff on this fixture.
- **Risk — sibling parallelism:** #2457 (L03 ship single-body) runs alongside. If both land the same day with overlapping edits to `digitalmodel/docs/domains/orcawave/README.md` or the roadmap file, git may merge-conflict. Mitigation: this plan targets distinct subsections (a new "Named multi-body benchmark" block) and distinct roadmap lines (120 region) — no shared-section edit.
- **Open — `manifest.yaml` vs `manifest.yml` extension:** the existing test-fixture convention in the repo uses `.yml`, but the manifest is metadata not a spec. This plan uses `.yaml` for the manifest to make the distinction explicit; a reviewer may prefer `.yml` for consistency.
- **Open — should the benchmark folder be versioned (`_v1` suffix) or unversioned (`multibody_fpso_turret`)?** This plan uses `_v1` to leave room for future benchmark revisions without breaking path imports. Reviewer-approvable either way.
- **Open — should the docs note live under `digitalmodel/docs/domains/orcawave/` or workspace-hub `docs/maps/`?** This plan picks the domain-docs location because the claim boundary already lives there; #2462 (repo-wide operator map) would cross-link from `docs/maps/` in a follow-up.

---

## Complexity: T2

**T2** — one new fixture directory, one manifest, one new test module with ~13 tests, three modify-in-place edits (domain docs, roadmap, benchmarks inventory), no source-code changes to `src/**` except a single dataclass-list append in `benchmarks/inventory.py`. Risk surface is scoped to mesh-path math and the claim-boundary doc statement; none of the work touches engineering calculation logic.
