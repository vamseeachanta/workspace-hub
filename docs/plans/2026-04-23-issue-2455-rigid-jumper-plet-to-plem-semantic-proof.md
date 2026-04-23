# Plan for #2455: Validate rigid jumper family via PLET-to-PLEM semantic proof

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2455
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2455-claude.md | ...-codex.md | ...-gemini.md
> **Worktree HEAD at drafting:** 0e9d6115988e8b7b1a205c4520133b58e23ff1ad
> **Repo under planning:** `digitalmodel/` (submodule under workspace-hub)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` plus `extractor.py`, `schema.py` (`ProjectInputSpec`), `cli.py`, `post_validator.py`, `builders/`, `routers/`, `sections.py`, `templates/` — the forward `spec.yml -> native modular OrcaFlex model` pipeline already exists and is the contract boundary this issue proves for the jumper family.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/` with `spec_to_modular.py`, `spec_to_single.py`, `modular_to_single.py`, `single_to_modular.py`, `modular_to_spec.py`, `single_to_spec.py`, `section_mapping.py`, `protocols.py` — full format-pivot matrix. No jumper-family semantic-equivalence harness consumes it yet.
- Found: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_semantic_roundtrip.py` — generic `extract -> spec -> generate` roundtrip covering 6DBuoy mass/volume, current profile, cross-references, and boolean normalization. **Gap**: no jumper-specific case, no coating/buoyancy/strake coverage, no PLET/PLEM constraint coverage, no PreBendCurvature geometry coverage.
- Found: `digitalmodel/tests/solvers/orcaflex/reporting/test_jumper_fixture_integration.py` + `test_jumper_fixture_snapshot.py` + `digitalmodel/tests/fixtures/reporting/jumper_plet_plem.metadata.json` + `jumper_plet_plem.report.snapshot.html` — existing fixture set tied to #1652/#1788. **Scope mismatch**: reporting-side only, asserts 9 objects at 1200 m water depth; does **not** prove semantic equivalence of the real 1996 m, 21 k-line model.
- Found: `digitalmodel/src/digitalmodel/marine_ops/installation/jumper_lift.py`, `jumper_installation.py`, `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/jumper.py`, and `digitalmodel/src/digitalmodel/solvers/orcaflex/spec_upgrader.py` — jumper domain is a real production surface.
- Gap: no scripted entry point named `jumper_plet_to_plem_semantic_diff` (or equivalent) emitting a classified semantic-diff report.
- Gap: no module named `semantic_diff.py` under `solvers/orcaflex/modular_generator/` — diff classification is implicit in assertion logic of existing tests, not a reusable classifier.

### Standards

| Standard | Status | Source |
|---|---|---|
| API RP 17B (Recommended Practice for Flexible Pipe) | not in ledger as "jumper" row | `data/document-index/standards-transfer-ledger.yaml` |
| DNV-RP-F105 (Free-spanning pipelines) | not applicable — rigid jumper with strakes, not a free-spanning design | — |
| Internal contract | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` line 8: "OrcaFlex: treat the forward path (`spec.yml` -> native/modular OrcaFlex input) as the primary contract; reverse extraction (`native` -> `spec.yml`) remains best-effort only" |

### LLM Wiki pages consulted

- No relevant wiki page located for jumper semantic-equivalence specifically. `knowledge/wikis/marine-engineering/` does not carry a PLET-to-PLEM proof entry at the drafting commit. Treated as a gap; this plan does not author wiki content because the issue is proof/validation, not domain-knowledge capture.

### Documents consulted

- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` (145 lines, updated 2026-04-22): lists "PLET-to-PLEM rigid jumper" under **Partial but high-value next validations** (line 118). Priority 1 cluster is `#1652` + `#1788`. This plan closes the family-level partial-confidence gap.
- Issue #1905 (OPEN) — catalogs `digitalmodel/docs/domains/orcaflex/jumper/{manifold_to_plet,plet_to_plem}/monolithic/SZ.yml` (21 409 lines) and `DZ_AHCoff.yml` (21 557 lines) at 1996 m water depth with line types `10.75"Jumper_wCoat`, `10.75"Jumper_wCoat_wBuoy`, `10.75"Jumper_wCoat_wStrake`; 76.2 mm insulation, 343 mm buoyancy layer, OCS 200-V collet connector, multi-stage simulation structure.
- Issue #1652 (OPEN) — requests a minimal non-proprietary `.sim` fixture and integration tests; parent of #1788.
- Issue #1788 (OPEN) — specifies committed `minimal_test.sim` + snapshot test path in the `digitalmodel` submodule; scaffolding pattern this plan extends from reporting-only into semantic-equivalence.
- Issue #1586 (OPEN) — solver queue hardening (Priority 2 on the roadmap); not a blocker for this plan.
- Issue #1572 (OPEN) — parent capability-roadmap issue; scope is docs/roadmap coverage.
- `digitalmodel/docs/domains/orcaflex/library/templates/jumper_rigid_subsea/spec.yml` (492 lines): human-authored generator-input template — has 17 line segments with `PreBendCurvaturex/y`, three coated/buoyed/straked line types, named constraint expectations. Canonical input to the modular generator.
- `digitalmodel/docs/domains/orcaflex/subsea/jumper/installation/ballymore_plet_plem/spec.yml` (117 lines): installation-calculation spec consumed by `jumper_lift.py`; **different contract, do not conflate**.

### Gaps identified

- No jumper-family semantic-equivalence test exists — family currently rides on the generic roundtrip test plus reporting snapshots only.
- No reusable semantic-diff classifier emitting a structured classification of residual differences.
- `SEMANTIC_DIFF_TAXONOMY.md` is cited by the roadmap (line 40) but **does not exist** in the repo at the drafting SHA. Plan chooses to create it (alternative of silently pinning categories in code would keep the roadmap reference dangling).
- No scripted CLI entry point for "run PLET-to-PLEM semantic-equivalence proof end-to-end and emit a classified report". Existing `modular_generator/cli.py` stops at `generate` / `validate`; there is no `compare` / `diff` verb.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23T09:04:40Z via `gh issue view`):
- `#2455` — OPEN — "feat(canonical-spec): validate rigid jumper family via PLET-to-PLEM semantic proof" — labels: `enhancement`, `priority:high`, `cat:engineering`, `domain:marine`, `machine:dev-primary`
- `#1905` — OPEN — "DATA: Rigid jumper OrcaFlex model + input workbook for model generation"
- `#1572` — OPEN — "Domain-specific capability roadmaps — OrcaWave/OrcaFlex, structural, hydrodynamics, pipeline"
- `#1652` — OPEN — "OrcaFlex reporting: integration test with real .sim fixture + HTML snapshot testing"
- `#1788` — OPEN — "OrcaFlex .sim snapshot testing: HTML report from minimal_test.sim fixture"
- `#1586` — OPEN — "Harden solver queue: batch submission, result watcher, auto post-processing"

**File existence** (verified 2026-04-23T09:04:40Z):
- EXISTS: `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` (145 lines)
- EXISTS: `digitalmodel/docs/domains/orcaflex/jumper/plet_to_plem/spec.yml` (68 253 lines)
- EXISTS: `digitalmodel/docs/domains/orcaflex/jumper/plet_to_plem/monolithic/` (21 k-line SZ.yml and DZ_AHCoff.yml per #1905)
- EXISTS: `digitalmodel/docs/domains/orcaflex/jumper/manifold_to_plet/spec.yml` (68 340 lines)
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/templates/jumper_rigid_subsea/spec.yml` (492 lines)
- EXISTS: `digitalmodel/docs/domains/orcaflex/subsea/jumper/installation/ballymore_plet_plem/spec.yml` (117 lines)
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/{extractor.py,schema.py,cli.py,post_validator.py,sections.py,__main__.py}`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/{spec_to_modular.py,spec_to_single.py,modular_to_spec.py,single_to_spec.py,modular_to_single.py,single_to_modular.py,section_mapping.py,protocols.py}`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_semantic_roundtrip.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/reporting/test_jumper_fixture_integration.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/reporting/test_jumper_fixture_snapshot.py`
- EXISTS: `digitalmodel/tests/fixtures/reporting/jumper_plet_plem.metadata.json`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/semantic_diff.py`
- MISSING (new — this plan creates): `digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py`
- MISSING (new — this plan creates): `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/`
- MISSING (new — this plan creates): `digitalmodel/scripts/validation/jumper_plet_to_plem_semantic_diff.py`
- MISSING (new — this plan creates): `docs/standards/SEMANTIC_DIFF_TAXONOMY.md`

**Line excerpts**

Template spec (`digitalmodel/docs/domains/orcaflex/library/templates/jumper_rigid_subsea/spec.yml` lines 58-76):

```
generic:
  line_types:
  - name: 10.75"Jumper_wCoat              # Bare coated rigid jumper pipe
    category: Homogeneous pipe
    outer_diameter: 0.27305                # OD including coating (m)
    inner_diameter: 0.18212                # Steel ID (m)
    properties:
      MaterialDensity: 7.85               # Steel density (te/m3)
      E: 212e6                            # Young's modulus (kN/m2)
      PoissonRatio: 0.293
      ...
      CoatingThickness: 0.0762            # Insulation thickness (m)
      CoatingMaterialDensity: 0.97873     # Insulation density (te/m3)
```

Roadmap anchor (`docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` lines 8-10):

```
- OrcaWave: treat the current claim as near-equivalent for key engineering inputs and tested pathways, not strict identity across every native YAML field.
- OrcaFlex: treat the forward path (`spec.yml` -> native/modular OrcaFlex input) as the primary contract; reverse extraction (`native` -> `spec.yml`) remains best-effort only.
```

Roadmap readiness snapshot (lines 115-120):

```
Partial but high-value next validations:
- turret-moored FPSO
- PLET-to-PLEM rigid jumper
- lazy-wave / steep-wave riser
- OrcaWave L03 ship benchmark full roundtrip
- named multi-body OrcaWave benchmark
```

**Gap proofs**:
- `find workspace-hub -maxdepth 10 -iname 'SEMANTIC_DIFF*'` → empty → confirms roadmap-cited taxonomy doc is absent at drafting SHA.
- `grep -rln 'semantic_diff' digitalmodel/src/digitalmodel/solvers/orcaflex` → empty → no existing classifier module.
- `find digitalmodel/tests -name '*jumper*' -path '*modular_generator*'` → empty → no jumper test under `modular_generator/`.

<!-- Source count: issue body + roadmap + 5 related issues + template spec + installation spec + generic roundtrip test + reporting fixture + standards ledger = 11 distinct sources. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2455-rigid-jumper-plet-to-plem-semantic-proof.md` |
| Tests | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py` |
| Classifier module | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/semantic_diff.py` |
| CLI driver | `digitalmodel/scripts/validation/jumper_plet_to_plem_semantic_diff.py` |
| Proof fixture | `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/spec.yml` |
| Expected-artifact snapshot | `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/expected_native.snapshot.yml` |
| Classified diff report | `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/expected_diff_report.json` |
| Taxonomy legend | `docs/standards/SEMANTIC_DIFF_TAXONOMY.md` |
| Roadmap readiness update | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2455-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2455-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2455-gemini.md` |

---

## Deliverable

A committed PLET-to-PLEM rigid jumper semantic-equivalence harness — a trimmed non-proprietary fixture `spec.yml`, a pytest-executable semantic test suite, a classifier module emitting diffs categorised against a checked-in taxonomy doc, a CLI driver producing a structured report, and a roadmap readiness update — proving the forward path `jumper/plet_to_plem/spec.yml -> modular-generator native YAML` preserves analysis-significant jumper properties (pipe/coating/buoyancy/strake line types, OCS 200-V connector LineType, PLET/PLEM constraints, cross-references, PreBendCurvature M-profile geometry, multi-stage simulation durations) such that any residual difference is classified and bounded.

---

## Pseudocode

Classifier module (`semantic_diff.py`):

```
class SemanticDiffCategory(Enum):
    IGNORABLE       # whitespace / key-ordering / comment-only
    ALLOWED         # template defaults filled in by generator, matches spec via lookup
    NORMALIZED      # "Yes"/"No" -> True/False, aliases from sections.py
    REFERENCE_SAFE  # cross-ref target exists even if path changed
    BLOCKING        # analysis-significant value drift or missing field

function classify_diff(mono_doc, modular_doc, structure_type, taxonomy_rules):
    normalize both docs (units, booleans, case)
    resolve cross-references by name
    for each section in OBJECT_SECTIONS:
        for each object, compare field-by-field
        apply taxonomy_rules[structure_type=jumper] for allowed tolerances
    return list[DiffFinding(category, section, object_name, field, expected, actual)]

function proof_passes(findings) -> bool:
    return not any(f.category == BLOCKING for f in findings)
```

Test module (`test_jumper_plet_to_plem_semantic.py`):

```
FIXTURE_SPEC = fixtures/orcaflex/jumper/plet_to_plem_proof/spec.yml

class TestPletToPlemSemanticEquivalence:
    def test_line_types_three_variants_survive_generation
    def test_wCoat_coating_thickness_preserved           # 0.0762 m
    def test_wCoat_coating_density_preserved             # 0.97873 te/m3
    def test_wBuoy_buoyancy_layer_present_with_density   # 694 kg/m3
    def test_wStrake_strake_layer_present
    def test_OCS_200V_collet_linetype_ea_te_per_m        # 2.514 te/m
    def test_constraints_PLET_and_PLEM_present_anchored
    def test_line_references_linetypes_by_name_only
    def test_prebend_curvature_segment_count_matches     # 17 segments
    def test_prebend_curvature_values_match_per_segment
    def test_stage_durations_preserved
    def test_classifier_returns_no_blocking_findings     # overall proof
```

CLI driver (`scripts/validation/jumper_plet_to_plem_semantic_diff.py`):

```
parser = argparse.ArgumentParser()
parser.add_argument("--spec", default=FIXTURE_SPEC_PATH)
parser.add_argument("--report", type=Path, required=False)
args = parser.parse_args()
spec_dict = yaml.safe_load(args.spec.read_text())
proj = ProjectInputSpec(**spec_dict)
with tempfile.TemporaryDirectory() as tmp:
    gen = ModularModelGenerator.from_spec(proj); gen.generate(tmp)
    modular = merge_yaml_includes(Path(tmp)/"includes")
mono = load_monolithic_yaml(REFERENCE_MONO_PATH)
findings = classify_diff(mono, modular, structure_type="jumper",
                         taxonomy_rules=load_taxonomy())
emit_markdown_and_json(findings, args.report)
sys.exit(0 if proof_passes(findings) else 2)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/semantic_diff.py` | Classifier emitting `DiffFinding` list against `SemanticDiffCategory` taxonomy |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py` | TDD test suite per table below |
| Create | `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/spec.yml` | Trimmed non-proprietary PLET-to-PLEM spec |
| Create | `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/expected_native.snapshot.yml` | Committed generator output at a pinned commit |
| Create | `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/expected_diff_report.json` | Pinned-expected classified diff for regression |
| Create | `digitalmodel/scripts/validation/jumper_plet_to_plem_semantic_diff.py` | CLI driver; exits non-zero on any BLOCKING finding |
| Create | `docs/standards/SEMANTIC_DIFF_TAXONOMY.md` | Roadmap-cited taxonomy legend |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` | Re-export `classify_diff`, `SemanticDiffCategory`, `DiffFinding` |
| Modify | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | Move PLET-to-PLEM rigid jumper from "Partial" to "Ready now" |

**Explicitly out-of-scope** for this plan (defer to follow-up issues):
- Extension of the harness to `manifold_to_plet` companion.
- Licensed-machine `.sim` re-ingestion loop (belongs to #1586 and licensed-win-1).
- Reverse-path (`native -> spec.yml`) roundtrip — roadmap explicitly defines reverse as best-effort only.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_line_types_three_variants_survive_generation` | Generator preserves three line-type names | fixture | all three names present in `LineTypes` section |
| `test_wCoat_coating_thickness_preserved` | `CoatingThickness` not rounded/dropped/aliased | fixture | exact value `0.0762` (m) |
| `test_wCoat_coating_density_preserved` | `CoatingMaterialDensity` roundtrips identically | fixture | exact value `0.97873` (te/m3) |
| `test_wBuoy_buoyancy_layer_present_with_density` | Distributed buoyancy layer density preserved (#1905: 694 kg/m3) | fixture | `0.694` te/m3 on `..._wBuoy` |
| `test_wStrake_strake_layer_present` | Strake layer exists on `..._wStrake` | fixture | strake section present |
| `test_OCS_200V_collet_linetype_ea_te_per_m` | Collet connector mass/length per #1905 | fixture | mass-per-length `2.514` te/m preserved |
| `test_constraints_PLET_and_PLEM_present_anchored` | Named PLET/PLEM constraints with `Anchored` | fixture | both names + connection type present |
| `test_line_references_linetypes_by_name_only` | Line refs LineTypes by name string | fixture | every `LineType` token resolves |
| `test_prebend_curvature_segment_count_matches` | 17-segment M-profile count preserved | fixture | exactly 17 segments |
| `test_prebend_curvature_values_match_per_segment` | Per-segment `PreBendCurvaturex/y` values survive | fixture | per-segment tuple equality |
| `test_stage_durations_preserved` | Multi-stage `[10, 300]` durations not flattened | fixture | exact list equality |
| `test_classifier_returns_no_blocking_findings` | Overall proof — zero BLOCKING findings | fixture | `proof_passes(findings) is True` |
| `test_classifier_detects_injected_blocking_drift` | Negative control — mutation raises BLOCKING | mutated fixture | >=1 BLOCKING finding |
| `test_classifier_keeps_ignorable_whitespace_off_blocking_list` | Whitespace diff is IGNORABLE | mono with added comment | zero BLOCKING |
| `test_cli_exits_zero_on_passing_proof` | CLI exit code contract | invoke on fixture | exit code `0` |
| `test_cli_exits_nonzero_on_blocking_finding` | CLI exit code contract | invoke with mutated fixture | exit code `2` |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py -v`
- [ ] No regression: `uv run pytest digitalmodel/tests/solvers/orcaflex/ -q` still green
- [ ] CLI driver exits `0` on the committed fixture
- [ ] `semantic_diff.py` produces a JSON report matching `expected_diff_report.json`
- [ ] `docs/standards/SEMANTIC_DIFF_TAXONOMY.md` exists with five defined categories and one worked jumper-family example per category
- [ ] Roadmap promotes PLET-to-PLEM rigid jumper from "Partial" to "Ready now" with a dated note referencing this plan
- [ ] Fixture `spec.yml` is non-proprietary: `grep -iE 'ballymore|acma|ansys|saipem'` returns empty on the committed fixture copy
- [ ] Fixture size is reviewable: target `spec.yml` <= 2 000 lines; justify in revision wave if infeasible
- [ ] Review artifacts posted under `scripts/review/results/` for Claude, Codex, Gemini at `-plan-2455-*.md`

---

## Adversarial Review Summary

_To be filled in after Step 4 (adversarial review) completes._

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | TBD |
| Codex | TBD | TBD |
| Gemini | TBD | TBD |

**Overall result:** TBD

Revisions made based on review:
- (list any changes made after adversarial review)

---

## Risks and Open Questions

- **Risk — spec pedigree vs fixture committability:** the 68 253-line `plet_to_plem/spec.yml` is an extraction of proprietary-adjacent material (ACMA-ANSYS05 export per #1905; the word "ballymore" appears in the reporting-side fixture metadata). Committing unchanged would leak client/source identifiers. Mitigation: author a trimmed fixture under `digitalmodel/tests/fixtures/orcaflex/jumper/plet_to_plem_proof/` with scrubbed names, keeping only analysis-critical line types, segment count, constraints, and connector.
- **Risk — template vs extract mismatch:** two distinct PLET-to-PLEM specs already exist (`library/templates/jumper_rigid_subsea/spec.yml` at 492 lines vs `jumper/plet_to_plem/spec.yml` at 68 253 lines). The issue says "preferably `jumper/plet_to_plem/spec.yml`"; this plan uses the template-shaped spec as the generator input and the monolithic artifacts in `jumper/plet_to_plem/monolithic/` as the ground-truth reference. The split is made explicit above.
- **Risk — roadmap-cited taxonomy is vaporware:** `SEMANTIC_DIFF_TAXONOMY.md` is referenced by the roadmap (line 40) but absent from the tree. Creating it here is the lowest-surface-area remedy.
- **Risk — negative-control coverage:** a proof that only asserts "no blocking findings" on a good input is weak. Plan includes `test_classifier_detects_injected_blocking_drift` and `test_classifier_keeps_ignorable_whitespace_off_blocking_list` so the classifier itself is tested.
- **Risk — `spec_upgrader.py` interaction:** may normalise specs before generation in some entry points. Plan pins a single entry path (`ProjectInputSpec(**data) -> ModularModelGenerator.from_spec(spec) -> generate`) and explicitly does not exercise the upgrader.
- **Risk — OrcFxAPI unavailability on planning/dev machines:** all assertions are YAML-level; no licensed OrcaFlex runtime required. Intentional; the forward-generation contract is structural, not solver-runtime. Runtime validation is already covered by #1652/#1788 on licensed-win-1.
- **Open question for user approval:** the plan assumes a single representative case (PLET-to-PLEM) is sufficient to satisfy the issue's "family" claim; issue body allows either, so `manifold_to_plet` is deferred unless user wants parity.
- **Open question for user approval:** whether the roadmap readiness edit lands in this plan's PR or in a separate docs-only PR (plan assumes same-PR for atomicity).

---

## Complexity: T3

**T3** — multiple new source files, new fixture subtree, new CLI, new taxonomy doc, negative-control coverage, and a roadmap-readiness edit; cross-boundary changes across the `digitalmodel/` submodule and `docs/` at workspace-hub level. Decomposable into TDD-ordered slices (taxonomy doc -> classifier with unit tests -> fixture authoring -> integration tests -> CLI -> snapshot -> roadmap edit), but end-to-end correctness is non-trivial and requires the adversarial review wave before implementation begins.
