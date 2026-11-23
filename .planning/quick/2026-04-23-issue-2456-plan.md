# Plan for #2456: Extend OrcaFlex semantic proof to lazy/steep-wave riser variants

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2456
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2456-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/spec_to_single.py` (`SpecToSingleConverter`) and `spec_to_modular.py` (`SpecToModularConverter`) — forward canonical generation from `spec.yml` is already implemented.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/single_to_modular.py`, `modular_to_single.py` — format-pair round-trip converters.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/modular_to_spec.py`, `single_to_spec.py` — reverse extraction, explicitly best-effort per roadmap §"Contract boundary".
- Found: `digitalmodel/tests/solvers/orcaflex/format_converter/test_round_trip.py` — proves single↔modular↔single semantic equality on the A01 catenary riser (a01_single_file fixture resolves to `A01 Catenary riser.yml`).
- Found: `digitalmodel/tests/solvers/orcaflex/format_converter/test_spec_conversions.py` — exercises `SpecToSingleConverter`/`SpecToModularConverter` using `spec_file` fixture which resolves to `docs/modules/orcaflex/pipeline/installation/floating/30in_pipeline/spec.yml` (pipeline, not a riser, not lazy-wave).
- Found: `digitalmodel/tests/solvers/orcaflex/reporting/test_riser_fixture_integration.py` and `test_riser_fixture_snapshot.py` — prove reporting-surface stability for fixture `riser_lazy_wave_fpso` (metadata-driven, HTML snapshot regression). These cover reporting, not canonical-spec → native-YAML semantic fidelity.
- Found: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` — canonical pattern for semantic-roundtrip tests in this repo (load spec → backend.generate → reverse-parse → key-field assertions). OrcaWave only; no OrcaFlex analogue using `spec.yml`.
- Found: `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` lines 27–34 define `RiserType.{SCR, LAZY_WAVE, STEEP_WAVE, FREE_HANGING, TTR, HYBRID}` — analytical sizing utility, not semantic-proof surface. Listed to show the library names and confirm lazy-wave / steep-wave are already first-class configuration types.
- Gap: no test forward-generates the A05 lazy-wave `spec.yml` and compares key fields against the committed monolithic `A05 Lazy wave with FPSO.yml` with taxonomy-classified diffs.
- Gap: no OrcaFlex analogue of `test_orcawave_semantic_roundtrip.py` exists — the "semantic roundtrip / semantic diff harness" phrase in issue #2456 currently resolves to OrcaWave + A01 catenary round-trip only.

### Standards

Not applicable — this issue is a harness extension over committed engineering artifacts. The referenced discipline comes from internal taxonomy (to be authored) rather than an external marine/structural standard.

### LLM Wiki pages consulted

No relevant wiki pages — the canonical artifacts live in `digitalmodel/docs/domains/orcaflex/library/model_library/` rather than `knowledge/wikis/`.

### Documents consulted

- Issue #2456 body — "select at least one non-catenary riser family, preference lazy-wave or steep-wave", "reuse or extend the semantic roundtrip / semantic diff harness", "classify with the OrcaFlex taxonomy", "promote at least one additional riser family from partial to ready".
- Issue #2456 owner comment (2026-04-22) — places this after #1652/#1788 in Phase B item 5, guidance to "keep at least one selected family bounded so the issue closes on proof, not on indefinite family expansion".
- Roadmap `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`:
  - §"Contract boundary" (lines 6-10) — "OrcaFlex: treat the forward path (`spec.yml` -> native/modular OrcaFlex input) as the primary contract; reverse extraction (`native` -> `spec.yml`) remains best-effort only."
  - §"Structure readiness snapshot" (lines 109-120) — "Ready now: OrcaFlex catenary riser baseline"; "Partial but high-value next validations: lazy-wave / steep-wave riser".
  - §"Priority 1 — prove forward native fidelity" (lines 28-44) — deliverables call out "semantic diff classification mapped to `SEMANTIC_DIFF_TAXONOMY.md`".
- Related issue #1652 (OPEN) — parent proof track; requires minimal `.sim` fixture (318 KB `minimal_test.sim` is committed), integration test against real OrcFxAPI on licensed-win-1, HTML snapshot, coverage measurement.
- Related issue #1788 (OPEN) — builds snapshot test from `minimal_test.sim`/`minimal_test.dat`; metadata/snapshot fixture pattern established.
- Fixture metadata `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` lines 14-19 — `"Initial stable metadata baseline for #2456 lazy-wave riser proof path"`, `extraction_mode: bounded_static_fixture`, `orcaflex_version: 11.6-reference`.
- Fixture source model `digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/` — `spec.yml`, `monolithic/A05 Lazy wave with FPSO.yml`, `modular/master.yml`, `modular/includes/{01_general.yml, 03_environment.yml, 20_generic_objects.yml}`, `modular/inputs/parameters.yml`.

### Gaps identified

1. No OrcaFlex-side analogue of `test_orcawave_semantic_roundtrip.py` grounded in a riser-family spec — must be authored.
2. `SEMANTIC_DIFF_TAXONOMY.md` is cited by the canonical-spec roadmap but does not exist anywhere in `workspace-hub` or `digitalmodel` (verified below). Must be created before classification claims are testable.
3. No semantic-diff helper exists to classify `dict` differences between canonical-generated and committed-native YAML under explicit categories — must be authored.
4. Steep-wave riser has no committed `spec.yml` / monolithic pair under `digitalmodel/docs/domains/orcaflex/library/model_library/` (only `a05_lazy_wave_with_fpso/` is the lazy-wave directory). Without a fixture, steep-wave proof is not tractable in this plan — explicit deferral with a scoping note.
5. Drilling-riser has no semantic fixture; out-of-scope per roadmap and issue guidance.
6. Roadmap "Structure readiness snapshot" does not promote lazy-wave to "Ready now" until a forward-fidelity test lands — readiness promotion is part of this plan's deliverable.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2456` — OPEN — "feat(canonical-spec): extend OrcaFlex semantic proof to lazy/steep-wave riser variants"
- `#1572` — OPEN — "Domain-specific capability roadmaps — OrcaWave/OrcaFlex, structural, hydrodynamics, pipeline"
- `#1652` — OPEN — "OrcaFlex reporting: integration test with real .sim fixture + HTML snapshot testing"
- `#1788` — OPEN — "OrcaFlex .sim snapshot testing: HTML report from minimal_test.sim fixture"

**File existence** (verified 2026-04-23 via Glob/Read):
- EXISTS: `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/spec.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/monolithic/A05 Lazy wave with FPSO.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/modular/master.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/modular/includes/{01_general.yml, 03_environment.yml, 20_generic_objects.yml}`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/modular/inputs/parameters.yml`
- EXISTS: `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json`
- EXISTS: `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.report.snapshot.html`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/format_converter/test_spec_conversions.py`, `test_round_trip.py`, `conftest.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/reporting/test_riser_fixture_integration.py`, `test_riser_fixture_snapshot.py`, `fixture_helpers.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/{spec_to_single.py, spec_to_modular.py, modular_to_spec.py, single_to_spec.py, single_to_modular.py, modular_to_single.py}`
- MISSING (new — this plan creates): `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/semantic_diff.py`
- MISSING (new — this plan creates): `digitalmodel/tests/solvers/orcaflex/format_converter/test_lazy_wave_semantic_fidelity.py`

**Line excerpts:**

Roadmap contract boundary (`docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` lines 6-10):
```
- OrcaWave: treat the current claim as near-equivalent for key engineering inputs and tested pathways, not strict identity across every native YAML field.
- OrcaFlex: treat the forward path (`spec.yml` -> native/modular OrcaFlex input) as the primary contract; reverse extraction (`native` -> `spec.yml`) remains best-effort only.
- Therefore the roadmap focuses on forward-generation proof, repeatability, and coverage expansion.
```

Fixture metadata notes (`digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` lines 14-19):
```
"notes": [
  "Initial stable metadata baseline for #2456 lazy-wave riser proof path",
  "Counts and names are intentionally bounded for reporting regression tests"
]
```

A05 spec source (`digitalmodel/docs/domains/orcaflex/library/model_library/a05_lazy_wave_with_fpso/spec.yml` lines 7-23):
```
environment:
  water:
    depth: 2950
    density: 64
  seabed:
    slope: 0
    stiffness:
      normal: 25
      shear: 3.5
  waves:
    type: Dean stream
    height: 25
    period: 18
    direction: 180
```

**Gap proofs:**
- `Grep "SEMANTIC_DIFF_TAXONOMY"` across workspace-hub returns exactly one match — the roadmap doc itself. No taxonomy file exists. Confirmed 2026-04-23.
- `Glob digitalmodel/docs/domains/orcaflex/library/model_library/*/spec.yml` returns only the a05 entry checked above; no `steep_wave_*` or `drilling_riser_*` directory with a `spec.yml` exists.
- `Grep "a05_lazy_wave|riser_lazy_wave"` inside `digitalmodel/tests/solvers/orcaflex/format_converter/` returns zero — the forward-fidelity test for A05 has not been written yet.

(14 distinct sources above: issue body, issue-owner comment, roadmap, #1572, #1652, #1788, fixture metadata, a05 spec, a05 monolithic, a05 modular master+includes, riser_config.py, test_orcawave_semantic_roundtrip.py, test_round_trip.py, test_riser_fixture_*. Minimum 3 required — 14 present.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-23-issue-2456-lazy-wave-riser-semantic-proof.md |
| Taxonomy doc (new) | digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md |
| Semantic-diff helper (new) | digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/semantic_diff.py |
| Forward-fidelity tests (new) | digitalmodel/tests/solvers/orcaflex/format_converter/test_lazy_wave_semantic_fidelity.py |
| Fixture additions | digitalmodel/tests/solvers/orcaflex/format_converter/conftest.py |
| Roadmap readiness promotion | docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md |
| Plan index row (main session, NOT this worker) | docs/plans/README.md |
| Plan review — Claude | scripts/review/results/2026-04-23-plan-2456-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-23-plan-2456-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-23-plan-2456-gemini.md |

Note: this worker's write boundary forbids editing `docs/plans/README.md`; the plan index row will be added by the main overnight session or by the user on approval, per the worker write-only pattern (feedback_parallel_agent_write_only_pattern).

---

## Deliverable

A forward-fidelity regression test for the A05 lazy-wave riser (`a05_lazy_wave_with_fpso/spec.yml` → `SpecToSingleConverter` → compared against the committed `A05 Lazy wave with FPSO.yml`) that classifies every structural diff under an explicit OrcaFlex `SEMANTIC_DIFF_TAXONOMY.md` (Categories A/B/C/D) and blocks only on Category D defects, with the roadmap readiness matrix promoting the lazy-wave riser family from "Partial but high-value" to "Ready now".

Scope is intentionally bounded to lazy-wave only. Steep-wave and drilling-riser are deferred (see Risks).

---

## Pseudocode

```
# --- taxonomy doc (SEMANTIC_DIFF_TAXONOMY.md) ---
Category A (cosmetic, always allowed):
  - YAML flow vs block style
  - key ordering within a mapping
  - quoted vs unquoted scalars with identical value

Category B (derived/generated, allowed when convention holds):
  - auto-generated object IDs, display/Pen colours, cosmetic comment blocks
  - raw_properties fields that are OrcaFlex defaults for an unset value
  - fields produced by OrcaFlex 11.6-reference conventions

Category C (numeric drift, conditional, allowed within tolerance):
  - float representation drift within relative tolerance 1e-6
  - integer/float coercion where value preserved
  - conditional: abs tolerance 1e-9 only for physical-zero fields

Category D (structural/semantic, blocking):
  - missing or extra top-level OrcaFlex sections
  - changed object counts by type
  - renamed or missing named objects (Vessels, Lines, LineTypes, VesselTypes)
  - changed Line end-connections, fixed-DOF patterns, or vessel coupling
  - changed LineType physical properties beyond Category C tolerance
  - environment (water depth, wave train identity, current-profile point count) mismatch

# --- semantic_diff.py helper ---
@dataclass
class Diff:  path, left_value, right_value, category (A|B|C|D)

function classify_diff(path, left, right, taxonomy_rules) -> Category
function semantic_diff(left_dict, right_dict, taxonomy_rules) -> list[Diff]
function classification_summary(diffs) -> mapping_of_category_to_diff_list

# --- test_lazy_wave_semantic_fidelity.py ---
fixture a05_spec_file       = model_library/a05_lazy_wave_with_fpso/spec.yml
fixture a05_monolithic_file = model_library/a05_lazy_wave_with_fpso/monolithic/A05 Lazy wave with FPSO.yml

def test_a05_spec_generates_valid_single(a05_spec_file, tmp_path):
    report = SpecToSingleConverter().convert(a05_spec_file, tmp_path / "out.yml")
    assert report.success and (tmp_path / "out.yml").exists()
    data = yaml.safe_load((tmp_path / "out.yml").read_text())
    assert "General" in data and "Environment" in data

def test_a05_line_type_names_preserved(...):
    names = set of lt["Name"] for lt in generated["LineTypes"]
    assert {"Flex joint", "Lazy Straked", "Lazy Bare", "Lazy Buoyed"} is subset of names

def test_a05_buoyed_section_properties(...):
    buoyed = first lt in generated["LineTypes"] where lt["Name"] == "Lazy Buoyed"
    assert buoyed["OuterDiameter"] == approx(2.22863108489382, rel=1e-5)
    assert buoyed["InnerDiameter"] == approx(0.813333333333333, rel=1e-5)
    assert buoyed["MassPerUnitLength"] == approx(198.623920105366, rel=1e-5)

def test_a05_environment_coupling(...):
    env = generated["Environment"]
    assert env["WaterDepth"] == 2950
    wave = env["WaveTrains"][0]
    assert wave["WaveType"] == "Dean stream"
    assert wave["WaveHeight"] == 25 and wave["WavePeriod"] == 18
    assert wave["WaveDirection"] == 180
    # 13-point profile from spec.yml (0…2950 m)
    assert len(env["CurrentProfile"]) == 13

def test_a05_line_connectivity(...):
    lines = generated["Lines"]
    assert len(lines) == 1
    assert lines[0]["Name"] == "Riser with Flexjoint"
    assert lines[0]["EndAConnection"] == "FPSO"
    assert lines[0]["EndBConnection"] in {"Anchored", "Fixed"}

def test_a05_semantic_diff_no_blocking(...):
    generated = yaml.safe_load(generated_path.read_text())
    committed = yaml.safe_load(a05_monolithic_file.read_text())
    diffs = semantic_diff(generated, committed, default_orcaflex_taxonomy())
    summary = classification_summary(diffs)
    # record categorised diffs to a JSON artifact for review
    (tmp_path / "a05_diff_report.json").write_text(json.dumps(summary, indent=2))
    assert summary["D"] == [] — message: blocking diffs must be empty

def test_semantic_diff_categorises_numeric_drift_as_C(...):
    # helper unit test: 1.0 vs 1.0 + 1e-9 under default taxonomy → Category C

def test_semantic_diff_flags_missing_line_type_as_D(...):
    # helper unit test: drop a LineType → exactly one Category D diff with that path
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` | Author the taxonomy the roadmap already references. |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/semantic_diff.py` | Helper to produce classified diffs; consumed by the new test and reusable for drilling/steep-wave follow-ons. |
| Create | `digitalmodel/tests/solvers/orcaflex/format_converter/test_lazy_wave_semantic_fidelity.py` | New TDD test module that proves the A05 lazy-wave forward-fidelity claim. |
| Modify | `digitalmodel/tests/solvers/orcaflex/format_converter/conftest.py` | Add `a05_spec_file`, `a05_monolithic_file`, `a05_modular_dir` fixtures pointing at the committed `a05_lazy_wave_with_fpso/` tree. |
| Update | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | Move "lazy-wave / steep-wave riser" out of "Partial but high-value" into "Ready now" for the lazy-wave sub-item and leave a bullet noting steep-wave still partial, once test lands. |
| (Not touched by this worker) | `docs/plans/README.md` | Forbidden in this worker's write boundary; main session / user will add the plan-index row. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_a05_spec_generates_valid_single | forward generation succeeds from A05 spec.yml | a05_spec_file | `report.success is True`; output file exists; parsed YAML has both `General` and `Environment` sections |
| test_a05_line_type_names_preserved | line-type naming semantic fidelity | a05_spec_file | set of LineType names includes "Flex joint", "Lazy Straked", "Lazy Bare", "Lazy Buoyed" |
| test_a05_buoyed_section_properties | critical lazy-wave buoyancy section values | a05_spec_file | OD ≈ 2.22863108, ID ≈ 0.81333333, mass ≈ 198.624 kg/m (rel tol 1e-5) |
| test_a05_environment_coupling | environment block preserved | a05_spec_file | WaterDepth=2950; Dean-stream H=25, T=18, dir=180; CurrentProfile has 13 points |
| test_a05_line_connectivity | riser end connections | a05_spec_file | 1 Line, name `"Riser with Flexjoint"`, EndA=FPSO, EndB in set of Anchored/Fixed |
| test_a05_seabed_model_preserved | seabed coupling matches spec | a05_spec_file | SeabedModel=Elastic; normal stiffness=25; shear stiffness=3.5; slope=0 |
| test_a05_stage_durations_preserved | simulation stages | a05_spec_file | StageDuration == [18, 144] (+/- float tolerance) |
| test_a05_semantic_diff_no_blocking | taxonomy gate for full-YAML diff | generated single vs committed monolithic | Category-D list empty; Categories A/B/C populated and written to `tmp_path/a05_diff_report.json` |
| test_semantic_diff_categorises_numeric_drift_as_C | helper unit test | mapping `x: 1.0` vs `x: 1.0+1e-9` under default taxonomy | exactly one Diff with category C on path `x` |
| test_semantic_diff_flags_missing_line_type_as_D | helper unit test | dict dropping one LineType by name | exactly one Diff with category D on a path containing that LineType name |
| test_semantic_diff_allows_key_order_as_A | helper unit test | same mapping with reordered keys | zero diffs (or all category A) after order-normalised comparison |

---

## Acceptance Criteria

- [ ] New test module passes on ubuntu without OrcFxAPI: `uv run pytest digitalmodel/tests/solvers/orcaflex/format_converter/test_lazy_wave_semantic_fidelity.py -v`
- [ ] No regression in existing format_converter tests: `uv run pytest digitalmodel/tests/solvers/orcaflex/format_converter/ -v`
- [ ] `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` exists and explicitly names Categories A, B, C, D with at least one example per category.
- [ ] `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/semantic_diff.py` exposes `semantic_diff(...)`, `classify_diff(...)`, `classification_summary(...)` and is imported by the new test module.
- [ ] Roadmap `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` diff shows lazy-wave riser moved from "Partial but high-value next validations" into "Ready now", with steep-wave explicitly retained as "partial".
- [ ] `a05_diff_report.json` artifact contract verified in at least one test assertion so that Category A/B/C counts are reviewable.
- [ ] Review artifacts posted to `scripts/review/results/2026-04-23-plan-2456-{claude,codex,gemini}.md`; plan not surfaced as approval-ready until at least two non-blocking verdicts exist.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | to be filled after Step 4 |
| Codex | PENDING | to be filled after Step 4 |
| Gemini | PENDING | to be filled after Step 4 |

**Overall result:** PENDING

Revisions made based on review:
- (to be filled)

---

## Risks and Open Questions

- **Risk:** `SpecToSingleConverter` may not currently generate every `raw_properties` field present in the committed monolithic `A05 Lazy wave with FPSO.yml`. The taxonomy **intentionally** allows this under Category B (defaults/derived) — but first real run may surface Category-D diffs we expected to be Category B. Mitigation: run `semantic_diff` on the real a05 pair at plan-approved time, update `SEMANTIC_DIFF_TAXONOMY.md` with the observed Category-B default-field list before freezing tests. This may require a second adversarial-review wave if the taxonomy needs expansion.
- **Risk:** Steep-wave has no committed `spec.yml`/monolithic pair in `model_library/`. Building one is a separate scope (fixture authoring, model-library curation, licensed-machine extraction). This plan **defers** steep-wave explicitly. Acceptance criterion for roadmap promotion applies only to lazy-wave; steep-wave stays "partial".
- **Risk:** Drilling-riser is out-of-scope per roadmap ("optional if tractable"); deferred to a follow-on issue if/when a drilling-riser model-library entry is curated.
- **Risk:** The A05 monolithic file includes `raw_properties` blocks copied verbatim from a licensed OrcaFlex export. If the forward converter emits different cosmetic defaults (for example `SeaSurfacePen` as `[1, Solid, $FCFC54]` vs `~`), naive equality comparison would break. The taxonomy's Category A (cosmetic) and Category B (defaults) guard this, but the first real diff may surface edge cases the taxonomy did not anticipate.
- **Risk:** Roadmap readiness promotion is a claim that implies CI passes on both ubuntu and licensed-win-1. The new test is YAML-only and runs on both; we are **not** making a new `.sim`-level claim for lazy-wave — that remains #1652/#1788's territory. The promotion is at the "forward canonical YAML → native YAML" level, which the roadmap §"Contract boundary" defines as the OrcaFlex primary contract.
- **Risk:** Worker write boundary forbids `docs/plans/README.md` edits. The plan-index row must be added by the main overnight session or the user at approval time. Without that row, the #2456 plan may not be picked up by README-driven audits. Mitigation: GH summary comment on #2456 links the plan file directly so readers are not dependent on the README.
- **Open:** Should `SemanticDiff` live under `format_converter/` or a new `validation/` subpackage? Current plan puts it next to the converters for colocation; a follow-on refactor can extract it if steep-wave / drilling land their own test modules.
- **Open:** Should the taxonomy doc live under `digitalmodel/docs/domains/orcaflex/` or at workspace-hub `docs/roadmaps/`? Plan places it next to OrcaFlex domain docs so the converter code and taxonomy co-locate. User to confirm at approval.
- **Open:** What numerical tolerances are appropriate for Category C per-field? The plan proposes relative 1e-6 and absolute 1e-9 as defaults; real A05 values suggest this survives (values like 198.623920105366 have ≥12 significant figures preserved). User to confirm or override at approval.

---

## Complexity: T3

**T3** — new taxonomy document, new helper module, new test module, modifications to conftest, and roadmap update. Multiple files, TDD required, crosses `digitalmodel/` submodule and `workspace-hub/` roadmap doc. Not trivial; not a pure-addition single-module change.
