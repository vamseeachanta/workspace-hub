# Plan for #2474: feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2474
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2474-claude.md | ...-codex.md | ...-gemini.md (TBD)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` (784 lines) — defines `OrcaWaveInputParser.parse(yml_path) -> DiffractionSpec`. This is the **OrcaWave reverse-parser baseline pattern** that #2474 will mirror for OrcaFlex. Class begins at line 387; covers single-body and multi-body cases, environment, frequencies, headings, solver options, mesh format/symmetry reverse-mapping.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/single_to_spec.py` (92 lines) — already implements a chained `single OrcaFlex YAML -> modular -> spec.yml` converter via `SingleToSpecConverter.convert()`. Returns a `ConversionReport` with `confidence`, `is_best_effort`, `expected_gaps`, `actionable_gaps`. **This is a best-effort converter, not a strict semantic-equivalence proof harness.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/modular_to_spec.py` (301 lines) — `ModularToSpecConverter` does the modular-YAML-to-spec leg. Already returns gap-tracking metadata.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/{spec_to_modular.py,spec_to_single.py,single_to_modular.py,modular_to_single.py}` — the **forward** generation chain (`spec.yml -> native OrcaFlex YAML`) used by PR #528 semantic proofs.
- Found: `digitalmodel/src/digitalmodel/marine_ops/marine_analysis/parsers/orcaflex_yml_parser.py` (335 lines) — `OrcaFlexYMLParser` ONLY extracts displacement RAOs from `VesselTypes` blocks. **It is NOT a general OrcaFlex reverse parser** despite the name; it is RAO-scoped only.
- Found: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py` and `test_riser_variant_semantic_proof.py` — PR #528 semantic-proof tests, **forward only** (`spec -> generated native YAML` assertions). These are the tests #2474 must extend with the reverse leg.
- Found: `digitalmodel/tests/solvers/orcaflex/format_converter/test_round_trip.py` — round-trips `single -> modular -> single`, semantic-equality on top-level keys. **Exists for the format-conversion chain; does NOT cover spec-canonical-intent equivalence after a round-trip.**
- Gap: No `OrcaFlexInputParser` symmetric to `OrcaWaveInputParser`. No test asserts `spec -> native -> reverse-parse -> spec'` equivalence at the canonical-intent level for OrcaFlex.
- Gap: No catalog of "intentionally ignored OrcaFlex native defaults" so reviewers can distinguish cosmetic divergence from semantic loss.

### Standards

| Standard | Status | Source |
|---|---|---|
| Not applicable — this is a software/parser-symmetry issue, not a standards-derived calc | n/a | This issue does NOT introduce standards-derived numerical constants. The calc-citation contract (`.claude/rules/calc-citation-contract.md`) will not apply unless review surfaces a code-derived field that warrants citation. |

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/` — to be confirmed during implementation; no canonical spec equivalence contract page exists yet per handoff line 174-187 ("YAML canonical-contract documentation" is a noted llm-wiki gap).
- `digitalmodel/docs/domains/orcaflex/library/templates/{riser_lazy_wave,riser_steep_wave}/spec.yml` — existing fixture templates that the reverse-parser tests will round-trip.
- `digitalmodel/docs/domains/orcaflex/jumper/plet_to_plem/spec.yml` — PLET-to-PLEM jumper canonical fixture, mandatory round-trip target per issue body.

### Documents consulted

- `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` — explicitly identifies "Bidirectional OrcaFlex reverse parsing" as gap #2 (lines 136-139); says: "OrcaFlex proof is mostly canonical spec -> generated native YAML assertions. Need stronger OrcaFlex native YAML -> canonical semantic extraction / equivalence checks." This issue **is** that gap.
- digitalmodel PR #528 (MERGED, commit `f956f51209503a1fca457c5cac3ec9c098e2bea9`) — established `OrcaWaveInputParser` reverse-parser pattern AND deterministic forward OrcaFlex semantic tests. #2474 extends parity by adding the reverse leg for OrcaFlex.
- digitalmodel commit `63c1cbdd feat(orcaflex): clarify reverse extraction limits (#520)` — most-recent prior work that **already documented** reverse-extraction limits in the format_converter chain. The plan must not duplicate #520; it must build on top of it.
- Closed sibling #2455 (PLET-to-PLEM semantic proof, forward), #2456 (lazy/steep-wave riser semantic proof, forward), #2457 (L03 OrcaWave roundtrip — already bidirectional) — establish the fixtures to be reused.
- Open sibling #1652 — real licensed `.sim` fixture / OrcFxAPI integration. **Out of scope for #2474.** That issue covers binary-file parsing on a licensed machine; this issue stops at YAML.
- Open sibling #2473 (OrcaWave-to-OrcaFlex hydrodynamic handoff) and #2472 (CALM/SPM buoy proof) — peer next-wave issues spawned from the same handoff. **Coordinate to avoid touching the same fixtures concurrently** but this issue's surface (reverse parser module + reverse-direction tests) does not collide with #2473/#2472 surfaces (forward fixtures + RAO database integration).

### Gaps identified

- No `OrcaFlexInputParser` class that maps native OrcaFlex YAML back to the canonical `ProjectInputSpec` / `spec.yml` intent. Symmetric to `OrcaWaveInputParser` at `reverse_parsers.py:387`.
- No test fixture asserting that `spec -> generated native -> reverse-parse -> spec'` produces canonical-intent equivalence (not byte equivalence) for PLET-to-PLEM, lazy-wave, or steep-wave fixtures.
- No declared "ignored-fields registry" so a reviewer can tell which native-YAML keys are intentionally dropped (formatting, OrcaFlex defaults, telemetry-only fields) versus which represent a semantic regression.
- No documented schema-version pinning convention for the OrcaFlex YAML format the parser targets — required so an upstream OrcaFlex format change can be detected as a test failure rather than a silent drift.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2474` — OPEN — feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof
- `#2455` — CLOSED — feat(canonical-spec): validate rigid jumper family via PLET-to-PLEM semantic proof
- `#2456` — CLOSED — feat(canonical-spec): extend OrcaFlex semantic proof to lazy/steep-wave riser variants
- `#2457` — CLOSED — feat(canonical-spec): promote L03 ship benchmark to explicit OrcaWave roundtrip proof case
- `#1652` — OPEN — OrcaFlex reporting: integration test with real .sim fixture + HTML snapshot testing
- `#2473` — OPEN — feat(canonical-spec): prove OrcaWave-to-OrcaFlex hydrodynamic handoff semantics
- `#2472` — OPEN — feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof

**File existence** (verified 2026-04-26):
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` (784 lines; `OrcaWaveInputParser` at line 387)
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/single_to_spec.py` (92 lines)
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/modular_to_spec.py` (301 lines)
- EXISTS: `digitalmodel/src/digitalmodel/marine_ops/marine_analysis/parsers/orcaflex_yml_parser.py` (335 lines; RAO-scoped only)
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_riser_variant_semantic_proof.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/format_converter/test_round_trip.py`
- EXISTS: `digitalmodel/docs/domains/orcaflex/jumper/plet_to_plem/spec.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a01_lazy_wave_riser/spec.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/a01_steep_wave_riser/spec.yml`
- EXISTS: `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md`
- MISSING (this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser.py` (or extend format_converter)
- MISSING (this plan creates): `digitalmodel/tests/solvers/orcaflex/modular_generator/test_orcaflex_reverse_parser_equivalence.py`
- MISSING (this plan creates): `digitalmodel/docs/domains/orcaflex/canonical-spec-equivalence-contract.md`

**Source count for retrieval contract:** issue body (1) + handoff (2) + PR #528 (3) + sibling issues #2455/#2456/#2457/#2473/#2472/#1652 (4) + repo code: `reverse_parsers.py`, `single_to_spec.py`, `modular_to_spec.py`, `orcaflex_yml_parser.py` (5+). Minimum of 3 satisfied.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser-proof.md |
| Reverse parser implementation | `digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser.py` (new module — alternative: extend `format_converter/`) |
| Equivalence-contract doc | `digitalmodel/docs/domains/orcaflex/canonical-spec-equivalence-contract.md` |
| Ignored-fields registry | `digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser_ignored_fields.py` |
| Tests — equivalence proof | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_orcaflex_reverse_parser_equivalence.py` |
| Tests — ignored-fields registry | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_reverse_parser_ignored_fields.py` |
| Tests — schema-version drift detection | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_reverse_parser_schema_pinning.py` |
| Plan review — Claude | scripts/review/results/2026-04-26-plan-2474-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-26-plan-2474-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-26-plan-2474-gemini.md |
| Wiki updates | knowledge/wikis/marine-engineering/wiki/concepts/orcaflex-canonical-spec-equivalence.md (TBD if applicable) |
| Docs updates | `digitalmodel/docs/domains/orcaflex/README.md` (claim-boundary update) |

---

## Deliverable

A deterministic, license-free `OrcaFlexInputParser` module + ignored-fields registry + canonical-equivalence test harness that proves canonical `spec.yml -> native OrcaFlex YAML -> reverse-parse -> spec'` round-trips with semantic equivalence on PLET-to-PLEM, lazy-wave, and steep-wave fixtures, with intentionally-ignored OrcaFlex defaults explicitly enumerated and any unenumerated divergence failing the test.

---

## Pseudocode

```
# digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser.py

class OrcaFlexInputParser:
    """Reverse parser: native OrcaFlex YAML -> canonical ProjectInputSpec.

    Symmetric to OrcaWaveInputParser at reverse_parsers.py:387.
    Operates on YAML only — does NOT load .sim/.dat binary or call OrcFxAPI.
    """

    SCHEMA_VERSION_PINNED = "..."  # from a known-good OrcaFlex YAML header
    IGNORED_NATIVE_KEYS = load_from(reverse_parser_ignored_fields.py)

    def parse(yml_path) -> ProjectInputSpec:
        data = yaml.safe_load(yml_path)
        assert_schema_version_compatible(data)            # raises if unknown
        environment = parse_environment(data)             # waves/currents/wind
        line_types = parse_line_types(data)               # geometry, mass, stiffness
        objects = parse_objects(data)                     # vessels, lines, buoys, supports
        load_cases = parse_load_cases(data)               # stages, durations, seeds
        solver_options = parse_general(data)              # time-step, integrator, units
        return ProjectInputSpec(
            environment, line_types, objects, load_cases, solver_options
        )

    def parse_with_diff(yml_path, expected_spec) -> SemanticDiff:
        actual = parse(yml_path)
        return semantic_diff(actual, expected_spec, IGNORED_NATIVE_KEYS)

# Equivalence-proof test pattern (per fixture)

def test_<fixture>_reverse_round_trip_preserves_canonical_intent(tmp_path):
    spec_in = load_spec("docs/domains/orcaflex/<fixture>/spec.yml")
    native_yaml = ModularModelGenerator(spec_in).generate(tmp_path)
    spec_out = OrcaFlexInputParser().parse(native_yaml)
    diff = semantic_diff(spec_in, spec_out, ignored=IGNORED_NATIVE_KEYS)
    assert diff.is_empty, f"Semantic divergence: {diff.unexpected_differences}"

# Ignored-fields contract

IGNORED_NATIVE_KEYS = {
    "General.LastModifiedDate",                # timestamp churn
    "General.Comments",                        # human annotation
    "Lines.*.LogPrecision",                    # output formatting
    # ... each entry MUST cite why-ignored
}
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser.py` | New `OrcaFlexInputParser` class; symmetric to `OrcaWaveInputParser` |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser_ignored_fields.py` | Ignored-fields registry — separates intentional drops from semantic loss |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/_semantic_diff.py` | Helper: compare two `ProjectInputSpec` instances modulo ignored keys |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_orcaflex_reverse_parser_equivalence.py` | TDD round-trip equivalence tests, three fixtures |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_reverse_parser_ignored_fields.py` | Pin and document ignored-fields registry |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_reverse_parser_schema_pinning.py` | Detect upstream OrcaFlex schema-version drift as a fail rather than silent miss |
| Create | `digitalmodel/docs/domains/orcaflex/canonical-spec-equivalence-contract.md` | Author the equivalence contract referenced as llm-wiki gap #1 in the handoff |
| Modify | `digitalmodel/docs/domains/orcaflex/README.md` | Add reverse-parser claim-boundary section parallel to OrcaWave |
| Modify (potential) | `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/single_to_spec.py` | Optionally route through new parser for spec-extraction parity (or leave best-effort and use new parser only for proof-test surface) — decide at implementation review |
| Update | docs/plans/README.md | Add this plan to index |
| Update (workspace-hub) | docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md | Mark gap #2 (Bidirectional OrcaFlex reverse parsing) as addressed once merged |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_plet_to_plem_reverse_round_trip_preserves_canonical_intent | PLET-to-PLEM jumper spec round-trips through generation+reverse-parse with no semantic divergence | `docs/domains/orcaflex/jumper/plet_to_plem/spec.yml` | `semantic_diff(spec_in, spec_out).is_empty` |
| test_lazy_wave_riser_reverse_round_trip_preserves_canonical_intent | Lazy-wave riser fixture round-trips | `docs/domains/orcaflex/library/model_library/a01_lazy_wave_riser/spec.yml` | empty diff |
| test_steep_wave_riser_reverse_round_trip_preserves_canonical_intent | Steep-wave riser fixture round-trips, including stage durations and time-step | `docs/domains/orcaflex/library/model_library/a01_steep_wave_riser/spec.yml` | empty diff |
| test_reverse_parser_preserves_line_type_mass_stiffness_drag | Mass/EI/EA/drag survive native-YAML emission and reverse-parse | line_type with non-default mass=...kg/m, EI=..., drag=... | values equal within float tolerance |
| test_reverse_parser_preserves_environment_waves_currents_wind | Environment block fully reversible | spec with regular wave + current profile + steady wind | exact reverse-extraction |
| test_reverse_parser_preserves_load_case_stage_durations | Stage and time-step intent reversed | steep-wave fixture stages | exact stage list, durations, seeds |
| test_reverse_parser_preserves_vessel_floater_connections | Object-graph (vessel/line attach points, supports) reversed | lazy-wave fixture | object IDs and parent refs match |
| test_reverse_parser_raises_on_unknown_schema_version | Upstream OrcaFlex YAML schema bump fails loud | YAML with unrecognized `OrcaFlexVersion` header | `OrcaFlexSchemaVersionError` |
| test_reverse_parser_distinguishes_ignored_default_from_divergence | Ignored-fields registry classifies correctly | native YAML mutated by adding ignored field + adding tracked field | only the tracked-field mutation surfaces in diff |
| test_reverse_parser_rejects_binary_sim_file | Hard-fail boundary: parser refuses `.sim` / `.dat` | `.sim` path | `OrcaFlexBinaryNotSupportedError` (license-free policy) |
| test_reverse_parser_no_orcfxapi_import | License-free guarantee | `import OrcaFlexInputParser` | no `OrcFxAPI` import in module dependency graph |
| test_reverse_parser_handles_multi_document_yaml | OrcaFlex YAML can be multi-doc (per existing `OrcaFlexYMLParser`) | multi-doc YAML | parser merges or selects correctly |
| test_ignored_fields_registry_each_entry_has_justification | Every ignored key has documented why-ignored | the registry | every entry has `reason` field non-empty |
| test_ignored_fields_registry_no_silent_growth | Registry size is regression-tracked | post-merge | registry size matches snapshot |

---

## Equivalence Criteria

A canonical-YAML round-trip is **semantically equivalent** if and only if:

1. **Object identity preserved.** Every object in `spec_in.objects` has a one-to-one match in `spec_out.objects` by canonical name and type.
2. **Numeric fields equal within tolerance.** Floats compared at `rtol=1e-9`, `atol=0` unless a field documents a coarser tolerance (e.g., logged precision-limited natives).
3. **Enum/categorical fields exact-equal.** Wave model, line type model, integrator type — exact string match after normalization.
4. **Reference graph preserved.** Every `LineType` / `VesselType` / `Constraint` reference resolved in `spec_in` resolves to the same target in `spec_out`.
5. **Ignored fields enumerated.** Every native-YAML key not lifted into the canonical spec must appear in `IGNORED_NATIVE_KEYS` with a stated reason. Unenumerated divergence is a failure.
6. **Units preserved.** Canonical unit on emit equals canonical unit on reverse-parse; native-YAML unit conventions are normalized at parser boundary.
7. **No information added.** Reverse-parsed spec must not contain canonical fields that were not present in the input spec (no defaults injection that would silently mask omissions).

---

## Explicit Binary / Licensed-Machine Boundaries

This issue stops strictly at YAML. The following are **out of scope** and must surface as explicit refusal in the parser:

- `.sim` binary file parsing — covered by #1652 on a licensed machine.
- `.dat` legacy OrcaFlex format — separate licensed-proof issue if needed.
- Calling `OrcFxAPI` — the parser MUST NOT import or invoke OrcFxAPI; tests assert this.
- Round-tripping through an actual OrcaFlex application solve — covered by the licensed-machine load/run protocol gap (handoff line 131-134).

These boundaries match the issue body's "Out of scope" clause and the handoff's gap #1 (Licensed solver load/run proof).

---

## Acceptance Criteria

- [ ] All new tests pass: `cd digitalmodel && PYTHONPATH=src ./.venv/bin/python -m pytest tests/solvers/orcaflex/modular_generator/test_orcaflex_reverse_parser_equivalence.py tests/solvers/orcaflex/modular_generator/test_reverse_parser_ignored_fields.py tests/solvers/orcaflex/modular_generator/test_reverse_parser_schema_pinning.py -v`
- [ ] No regression: existing PR #528 semantic-proof tests still pass: `pytest tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py tests/solvers/orcaflex/modular_generator/test_riser_variant_semantic_proof.py -q`
- [ ] No regression in format_converter round-trip suite: `pytest tests/solvers/orcaflex/format_converter/ -q`
- [ ] `OrcaFlexInputParser` parses all three flagship fixtures (PLET-to-PLEM, lazy-wave, steep-wave) and produces empty `semantic_diff` against the source `spec.yml`.
- [ ] Ignored-fields registry has at least one documented entry per category (timestamp/comment/format-only/precision-only) with stated reason.
- [ ] Schema-version pinning test fails loud on injected unknown `OrcaFlexVersion`.
- [ ] License-free guarantee verified: `grep -r OrcFxAPI digitalmodel/src/digitalmodel/solvers/orcaflex/reverse_parser.py` returns empty.
- [ ] `digitalmodel/docs/domains/orcaflex/canonical-spec-equivalence-contract.md` written and references this issue.
- [ ] `digitalmodel/docs/domains/orcaflex/README.md` claim-boundary section updated to mention reverse-parser parity.
- [ ] Adversarial review artifacts posted under `scripts/review/results/2026-04-26-plan-2474-{claude,codex,gemini}.md` per cross-review policy.
- [ ] Handoff line 136-139 (gap #2) marked addressed in a follow-up handoff or in the readiness matrix.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | TBD |
| Codex | TBD | TBD |
| Gemini | TBD | TBD |

**Overall result:** PENDING — to be filled after Step 4 cross-review.

Pre-emptive defenses to common adversarial critiques:

- **"What if OrcaFlex YAML format changes upstream?"** — addressed by `test_reverse_parser_raises_on_unknown_schema_version` (fail-loud on schema drift) and the pinned `SCHEMA_VERSION_PINNED` in the parser. Plan calls out this risk in Risks below.
- **"How do you tell intentionally-ignored defaults from semantic divergence?"** — addressed by the explicit `reverse_parser_ignored_fields.py` registry where every entry must carry a `reason`. The `test_ignored_fields_registry_each_entry_has_justification` and `test_ignored_fields_registry_no_silent_growth` tests gate this. The semantic_diff helper consults the registry.
- **"Is this just a duplicate of `single_to_spec.py`?"** — no. `single_to_spec.py` is best-effort with `is_best_effort=True` and `actionable_gaps`. This issue's `OrcaFlexInputParser` is **strict** (no `actionable_gaps` allowed for the proof-test fixtures) and is the test-side oracle. Plan's "Files to Change" leaves the option of internally reusing `single_to_spec.py` plumbing but the proof harness is independent.
- **"Why a new module instead of extending `OrcaFlexYMLParser` in `marine_ops/.../parsers/`?"** — `OrcaFlexYMLParser` is RAO-only (lines 27-40) and lives under `marine_ops`, not `solvers/orcaflex`. Its scope is hardwired to `VesselTypes/Draughts/DisplacementRAOs`. Extending it would conflate RAO extraction with full-spec reverse parsing. New module under `solvers/orcaflex/` keeps cohesion.
- **"Could OrcFxAPI sneak in?"** — `test_reverse_parser_no_orcfxapi_import` asserts the module dependency graph excludes `OrcFxAPI`.
- **"What about multi-document YAML and BOM-encoded files?"** — `test_reverse_parser_handles_multi_document_yaml` and pattern from existing `OrcaFlexYMLParser._find_vessel_types_document` will be reused.
- **"Is the round-trip provably empty, or just empty for the chosen fixtures?"** — explicitly acknowledged: this issue proves equivalence for **three named fixtures**. Generalization to all OrcaFlex fixtures is out of scope and would chain into #2472 (CALM/SPM), #2473 (RAO handoff), and family-coverage gaps in the handoff matrix.
- **"PR #520 already clarified reverse-extraction limits — does this contradict?"** — no. #520 set boundary expectations on the format_converter best-effort path. #2474 adds a strict proof harness on top. The plan must read #520's commit message and not weaken its declared limits.

---

## Risks and Open Questions

- **Risk:** OrcaFlex native YAML uses many native-side conveniences (computed defaults, polymorphic key shapes, multi-doc YAML, BOM-encoded files) that PR #528 forward generation hides. Reverse parsing surfaces them. Mitigation: schema-version pin + ignored-fields registry + parser raises on unknown keys outside the registry.
- **Risk:** Upstream OrcaFlex format change silently breaks reverse parsing. Mitigation: schema-version pinning test; CI fail-loud rather than silent skip.
- **Risk:** Selected fixtures may already happen to round-trip due to PR #528 forward generator covering only fields present in the spec. The proof is fixture-bound. Open question: does Codex/Gemini want a `test_reverse_parser_fails_on_silent_field_drop` failure-injection test? Plan currently includes `test_reverse_parser_distinguishes_ignored_default_from_divergence` which mutates the native YAML; a stronger negative test could be added if reviewers flag.
- **Risk:** "Semantic equivalence" is undefined absent the canonical-spec equivalence contract document. Mitigation: write `canonical-spec-equivalence-contract.md` **before** writing parser code (in TDD spirit, contract first).
- **Risk:** `single_to_spec.py` already exists with `confidence < 1.0` semantics. Reviewers may push to consolidate. Open question for user approval: should `OrcaFlexInputParser.parse()` route through `SingleToSpecConverter` internally, or remain independent? Recommend **independent** for proof-test isolation; converter remains best-effort production path.
- **Risk:** Three fixtures is a narrow proof. The handoff's gap #3 (broader structural family coverage) and gap #4 (environmental and load-case equivalence) remain open after this issue. Acknowledged; this issue is intentionally scoped to the three PR #528 fixtures, not all families.
- **Risk:** The plan-approval gate requires `status:plan-approved` on workspace-hub before any digitalmodel implementation commits. Hermes/parallel-agent workflow must respect that boundary.
- **Open:** Should the parser emit a structured `SemanticDiff` even on empty diff (for downstream tooling) or only on non-empty? Defer to user during approval.
- **Open:** Should the equivalence-contract doc live at `digitalmodel/docs/domains/orcaflex/` (cohesion with claim-boundary doc) or under `knowledge/wikis/marine-engineering/` (per llm-wiki gap callout in handoff line 174-187)? Defer to user.
- **Open:** Multi-body OrcaFlex YAML (e.g., dual-body installation scenarios) is not in the three flagship fixtures; do reviewers want at least one multi-body smoke test in scope? If yes, scope creeps toward #2472/#2473 territory.

---

## Complexity: T3

**T3** — new module + new test surface + new contract document, three fixture round-trips, schema-version pinning, ignored-fields registry, three cross-provider reviews required, and the issue is `cat:engineering` + `domain:marine` so the engineering-issue-workflow gates apply (cross-review after implementation per `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`).
