# Plan for #515: Clarify and close semantic-equivalence gaps between spec/LLM-friendly YAML and OrcaFlex strict YAML

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/515
> **Review artifacts:** scripts/review/results/2026-04-24-plan-515-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This is a parent/contract issue in the OrcaFlex YAML semantic-equivalence cluster (parent of #517 taxonomy, #518 model-library regression tests, #519 General/Environment/Groups fidelity). The intel pod confirmed that most of the implementation substrate already exists — the work is to formalize a claim boundary, reconcile scattered sources of truth, and resolve four Open Questions (OQ-1..OQ-4) that the existing taxonomy draft flagged. This plan describes the DELTA from current state (skip-lists, best-effort reverse extractor, draft taxonomy, per-family proofs) to the contract-level artifacts #515 requires — it is not a greenfield plan.

### Existing repo code (per intel)
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py:115-149` — `_SKIP_GENERAL_KEYS` (34 view/display keys) and `:160-165` `_SKIP_OBJECT_KEYS` (2 dormant-mode props). Core intentional-omission policy #515 must formally enumerate.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/environment_builder.py:49-159` — `_DEFAULTS` (21 hardcoded env defaults), `_SAFE_RAW_OVERLAY_KEYS` whitelist, `_WIND_SPEED_DORMANT` list. Source of the OQ-3 silent-substitution risk.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/groups_builder.py:27-29` — `GroupsBuilder.should_generate()` returns `spec.is_pipeline() or spec.is_riser()`, so Groups are intentionally suppressed for generic track. Explains the a01 "Groups present in original, omitted in generated" finding.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/modular_to_spec.py:20-85` — `EXTRACTION_MAP` (17 fields), `EXPECTED_UNMAPPED_SECTIONS` (20), `ACTIONABLE_UNMAPPED_SECTIONS` (Lines, LineTypes), confidence = extracted_count/17. Reverse extraction is explicitly best-effort (confidence 0.88 on a01).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/yaml_utils.py:17-40` — `OrcaFlexDumper` emits `None→~`, `bool→Yes/No`, `sort_keys=False`. Source of the OQ-4 Yes/No ↔ true/false C2 normalization asymmetry.
- Found: `digitalmodel/scripts/semantic_validate.py:101-108` — `Significance` enum (`match|cosmetic|minor|significant|type_mismatch|missing|extra`) and `:117-200+` `ALLOWED_DIFF_PROPS` (50+ cosmetic-downgraded properties, superset of `_SKIP_GENERAL_KEYS`). Mechanism-level diff engine; currently coupled to taxonomy via string names only.
- Found: `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` (413 lines) — draft C1..C6 taxonomy, L1/L2/L3 claim levels, four Open Questions. Already labeled under "#517 (parent: #515)".
- Found: `digitalmodel/docs/domains/orcaflex/SECTION_FIDELITY_ANALYSIS.md` (196 lines) — builder track matrix, per-section coverage percentages.
- Gap: No single authoritative claim-boundary doc. Per-family claim-level registry does not exist.
- Gap: Skip-list sources of truth (`ALLOWED_DIFF_PROPS`, `_SKIP_GENERAL_KEYS`, `_SKIP_OBJECT_KEYS`, `_WIND_SPEED_DORMANT`) are not reconciled by any test.
- Gap: OQ-4 `values_equal()` does not equate `Yes↔true`/`No↔false`, producing false-positive SIGNIFICANT diffs misclassified as C6.

### Standards
Not standards-driven. Equivalence classes, cosmetic property lists, and claim levels are defined entirely by repo-internal artifacts (`semantic_validate.py`, builders, `SEMANTIC_DIFF_TAXONOMY.md`). `data/document-index/online-resource-registry.yaml` only references Orcina/DNV at solver level, not at YAML-equivalence level.

| Standard | Status | Source |
|---|---|---|
| (none applicable) | n/a | internal only |

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/entities/orcaflex-viv-analysis.md` — VIV-specific, not equivalence.
- `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` — solver entity page; no equivalence contract.
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` — handoff flow; narrower than #515's contract scope.
- Future (per approved #2476): `knowledge/wikis/engineering/wiki/concepts/semantic-equivalence-contract.md` — **#515 outputs MUST harmonize with this contract**, not duplicate or contradict it.

### Documents consulted
- `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` — already-drafted C1..C6 + L1/L2/L3 + OQ-1..OQ-4. Attribution: "#517 (parent: #515)".
- `digitalmodel/docs/domains/orcaflex/SECTION_FIDELITY_ANALYSIS.md` — per-section coverage baseline to cite.
- `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md` — flagship generic-track FPSO semantic proof; already references SEMANTIC_DIFF_TAXONOMY.md as authoritative; claims L1 only.
- `docs/plans/2026-04-23-issue-2455-rigid-jumper-plet-to-plem-semantic-proof.md` — per-family semantic-proof pattern #515 generalizes.
- `docs/plans/2026-04-23-issue-2456-lazy-wave-riser-semantic-proof.md` — closed; complementary per-family proof.
- `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md` — OrcaWave side of the same story.
- `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` — **APPROVED**; cross-solver equivalence contract. #515's taxonomy is the OrcaFlex-strict instantiation and MUST slot into it.
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — established `ProjectInputSpec` canonical-spec pattern.
- Related issues: #517 (taxonomy), #518 (model-library regression tests), #519 (General/Environment/Groups fidelity), #2454/#2455/#2456/#2457 (per-family proofs), #2476 (wiki contract).

### Gaps identified
1. No single authoritative claim-boundary doc; SEMANTIC_DIFF_TAXONOMY.md is labeled "#517 work" and does not itself state what the repo is allowed to claim today.
2. Taxonomy → code coupling is implicit across four separate string sets (`ALLOWED_DIFF_PROPS`, `_SKIP_GENERAL_KEYS`, `_SKIP_OBJECT_KEYS`, `_WIND_SPEED_DORMANT`) with no reconciliation test.
3. OQ-1 `VerticalWindVariationFactor` unresolved (C3 vs C6 classification pending).
4. OQ-2 Groups generated-vs-monolithic gap unmeasured for pipeline/riser tracks.
5. OQ-3 `_DEFAULTS` (21 env defaults) never verified against OrcaFlex's own defaults on a blank model.
6. OQ-4 `values_equal()` treats Yes ≠ true, producing false-positive SIGNIFICANT diffs.
7. Reverse extraction is hardcoded at 17 fields with no roadmap or scope-boundary statement.
8. No per-family claim-level registry listing which model in `library/model_library/` is validated at which L-level by which test.

### Evidence (embedded verification)

**Issue statuses** (per intel pod recon):
- `#515` — OPEN — Clarify and close semantic-equivalence gaps between spec/LLM-friendly YAML and OrcaFlex strict YAML — status:pending, priority:high, route:B
- `#517` — OPEN — Taxonomy child (per SEMANTIC_DIFF_TAXONOMY.md attribution)
- `#518` — OPEN — Model-library regression tests child
- `#519` — OPEN — General/Environment/Groups fidelity closure child
- `#2476` — APPROVED plan — llm-wiki semantic-equivalence contract (cross-solver)
- `#2454` / `#2455` / `#2456` / `#2457` — per-family proof plans

**File existence** (per intel pod `ls`-verified paths):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py` (343 lines)
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/environment_builder.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/groups_builder.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/modular_to_spec.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/single_to_spec.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/yaml_utils.py`
- EXISTS: `digitalmodel/scripts/semantic_validate.py` (2108 lines)
- EXISTS: `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` (413 lines)
- EXISTS: `digitalmodel/docs/domains/orcaflex/SECTION_FIDELITY_ANALYSIS.md` (196 lines)
- MISSING (new — this plan creates): `digitalmodel/docs/domains/orcaflex/SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` (contract statement)
- MISSING (new — this plan creates): `digitalmodel/docs/domains/orcaflex/MODEL_CLAIM_REGISTRY.yaml` (per-family L-level registry)
- MISSING (new — this plan creates): `digitalmodel/tests/solvers/orcaflex/test_skip_list_reconciliation.py`
- MISSING (new — only if Approach A: OQ-4 fix): test + patch in `yaml_utils.py` / `semantic_validate.py` bool normalization

**Line excerpts** (from intel pod citations):
```
# generic_builder.py:115-149 (_SKIP_GENERAL_KEYS — 34 keys including:)
DefaultViewMode, DefaultShadedFillMode, DefaultShadedProjectionMode,
DefaultViewSize, DefaultViewCentre, DefaultViewAzimuth, DefaultViewElevation,
BackgroundColour, SeaSurfaceTranslucency, ModelState, TemperatureUnits,
ImplicitVariableMaxTimeStep, ...
```
```
# semantic_validate.py:101-108 (Significance enum)
class Significance(Enum):
    match | cosmetic | minor | significant | type_mismatch | missing | extra
```
```
# modular_to_spec.py:20-85
EXTRACTION_MAP = {...17 entries...}
EXPECTED_UNMAPPED_SECTIONS = [VesselTypes, LineTypes, Vessels, Lines, Groups, ...]
confidence = extracted_count / len(EXTRACTION_MAP)  # => 0.88 on a01
```

**Gap proofs** (intel-verified):
- `ls digitalmodel/docs/domains/orcaflex/SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` → missing → confirms no single claim-boundary doc exists.
- `ls digitalmodel/docs/domains/orcaflex/MODEL_CLAIM_REGISTRY.yaml` → missing → confirms no per-family L-level registry.
- Reverse extractor uses `len(EXTRACTION_MAP) == 17`, hardcoded → confirms scope is implicit, not documented.

<!-- Source count: issue body (1) + SEMANTIC_DIFF_TAXONOMY.md (2) + SECTION_FIDELITY_ANALYSIS.md (3) + semantic_validate.py (4) + 6 related plans (5-10) + 3 wiki pages (11-13) + intel pod (14). Well above the 3-source minimum. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-515-semantic-equivalence-yaml-strict.md` |
| Claim-boundary contract (new) | `digitalmodel/docs/domains/orcaflex/SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` |
| Per-family claim registry (new) | `digitalmodel/docs/domains/orcaflex/MODEL_CLAIM_REGISTRY.yaml` |
| Skip-list reconciliation test (new) | `digitalmodel/tests/solvers/orcaflex/test_skip_list_reconciliation.py` |
| OQ-4 bool-normalization fix test (Approach A only) | `digitalmodel/tests/solvers/orcaflex/test_values_equal_bool_normalization.py` |
| Taxonomy adoption amendment (Approach A only) | `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` (re-attribute) |
| Plan review — Claude | `scripts/review/results/2026-04-24-plan-515-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-24-plan-515-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-24-plan-515-gemini.md` |
| Wiki cross-reference | `knowledge/wikis/engineering/wiki/concepts/semantic-equivalence-contract.md` (#2476 output, consumed here) |

---

## Deliverable

A formally-ratified semantic-equivalence claim-boundary contract for OrcaFlex YAML (taxonomy + L1/L2/L3 claim levels + per-family claim registry + reconciled skip-list sources of truth) that locks the decisions children #517/#518/#519 will implement, with a single failing-on-drift test guaranteeing the four code-level skip sets stay consistent with the taxonomy document.

---

## Pseudocode

```
# test_skip_list_reconciliation.py (T2 — new)
function test_skip_lists_reconciled_with_taxonomy:
    parse SEMANTIC_DIFF_TAXONOMY.md section "C3 intentional omissions"
    load _SKIP_GENERAL_KEYS from generic_builder
    load _SKIP_OBJECT_KEYS from generic_builder
    load _WIND_SPEED_DORMANT from environment_builder
    load ALLOWED_DIFF_PROPS from semantic_validate
    assert every key in _SKIP_GENERAL_KEYS is listed under a C3 bucket in taxonomy doc
    assert every key in ALLOWED_DIFF_PROPS ∩ General is either in _SKIP_GENERAL_KEYS or has C1/C2 marker in taxonomy
    assert _SKIP_OBJECT_KEYS ⊆ ALLOWED_DIFF_PROPS OR each documented as C3 in taxonomy
    emit human-readable diff if any reconciliation fails

# MODEL_CLAIM_REGISTRY.yaml schema (new)
models:
  - name: a01_catenary_riser
    family: riser
    builder_track: generic
    highest_validated_level: L1
    test_enforcing: tests/.../test_roundtrip_fidelity.py::test_a01_generic_merge
    known_diffs: [C3:General.view_keys, C2:Environment.bool_normalization, OQ-1:VerticalWindVariationFactor]
  - name: c03_fpso
    family: fpso
    builder_track: generic
    highest_validated_level: L1
    test_enforcing: tests/.../test_c03_fpso_semantic.py  # from #2454
    ...

# SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md structure (new)
Section 1: What the repo IS allowed to claim (per family × per L-level)
Section 2: What the repo is NOT allowed to claim (strict round-trip, L3 on generic)
Section 3: How claims are enforced (test paths → registry → CI gate)
Section 4: How to raise a claim level (add fixture → run proof → update registry → PR review)
Section 5: Deferred work (link to #517 taxonomy, #518 fixtures, #519 OQ closures)

# OQ-4 bool-normalization fix (Approach A only)
function values_equal(a, b):
    if isinstance(a, bool) and isinstance(b, str) and b in {'Yes','No'}:
        return a == (b == 'Yes')
    # symmetric case
    # existing numeric/string logic
    return a == b
```

---

## Files to Change

### Path-Common (both approaches)
| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/docs/domains/orcaflex/SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` | Claim-boundary contract — single authoritative doc (closes Gap #1) |
| Create | `digitalmodel/docs/domains/orcaflex/MODEL_CLAIM_REGISTRY.yaml` | Per-family L-level registry (closes Gap #8) |
| Create | `digitalmodel/tests/solvers/orcaflex/test_skip_list_reconciliation.py` | Enforces taxonomy ↔ code coupling (closes Gap #2) |
| Update | `docs/plans/README.md` | Add this plan to index |
| Update | `knowledge/wikis/engineering/wiki/concepts/semantic-equivalence-contract.md` | Cross-link #2476 wiki contract to OrcaFlex claim-boundary doc |

### Approach-A-only (broad — adopts taxonomy + closes OQs in-scope)
| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` | Re-attribute under #515 (ratified) or add "Adopted by #515 YYYY-MM-DD" header; resolve OQ-1..OQ-4 inline |
| Modify | `digitalmodel/scripts/semantic_validate.py` (~line of `values_equal`) | OQ-4: treat `Yes↔true`, `No↔false` as equal at value-equality layer |
| Create | `digitalmodel/tests/solvers/orcaflex/test_values_equal_bool_normalization.py` | OQ-4 regression test |
| Create | `digitalmodel/tests/solvers/orcaflex/test_environment_defaults_vs_orcfxapi.py` | OQ-3 verification (marked `licensed-win-1`) |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/environment_builder.py` | OQ-1 classification: add `VerticalWindVariationFactor` to documented-omission list or fix generator |

### Approach-B-only (narrow — meta-contract only, defers OQ resolution)
| Action | Path | Reason |
|---|---|---|
| (no extra files) | — | OQ-1/2/3/4 remain open; referenced by claim-boundary doc as "tracked in #517/#518/#519" |

---

## TDD Test List

### Path-common tests
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_skip_general_keys_documented_in_taxonomy | every `_SKIP_GENERAL_KEYS` entry is listed under a C3 bucket in `SEMANTIC_DIFF_TAXONOMY.md` | parsed taxonomy doc + module constant | all 34 keys present in taxonomy; 0 unlisted |
| test_skip_object_keys_documented_in_taxonomy | every `_SKIP_OBJECT_KEYS` entry has a taxonomy classification | parsed taxonomy + module constant | both 2 keys classified |
| test_allowed_diff_props_superset_of_skip_general | `ALLOWED_DIFF_PROPS ⊇ _SKIP_GENERAL_KEYS` semantically (not just names) | both sets | set inclusion holds; if violation, name a counterexample key |
| test_wind_speed_dormant_classified | `_WIND_SPEED_DORMANT` entries appear under Environment/C3 in taxonomy | both sources | all classified |
| test_model_claim_registry_schema_valid | `MODEL_CLAIM_REGISTRY.yaml` parses, every entry has required keys (name, family, builder_track, highest_validated_level, test_enforcing) | registry file | schema-valid; no orphan test paths |
| test_model_claim_registry_tests_exist | every `test_enforcing` path in registry resolves to a real test module | registry + fs | all paths exist |
| test_claim_boundary_doc_cross_links_wiki_2476 | `SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` links the #2476 wiki page | doc content | link present |

### Approach-A-only tests
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_values_equal_yes_true | `values_equal(True, 'Yes')` and `values_equal('Yes', True)` return True | bool ↔ string fixture | equal |
| test_values_equal_no_false | `values_equal(False, 'No')` and `values_equal('No', False)` return True | bool ↔ string fixture | equal |
| test_values_equal_rejects_unrelated_strings | `values_equal(True, 'maybe')` returns False | bool + random string | not equal |
| test_environment_only_bool_fixture_zero_significant | a fixture with only bool-representation differences yields zero SIGNIFICANT diffs end-to-end | minimal env-only YAML pair | 0 SIGNIFICANT diffs; ≥1 COSMETIC |
| test_environment_defaults_match_orcfxapi_blank_model (licensed-win-1) | each of the 21 `_DEFAULTS` matches OrcFxAPI-exported blank-model default (or is documented as deliberate override) | blank .dat + `_DEFAULTS` | all 21 match OR have a deliberate-override annotation |
| test_vertical_wind_variation_factor_classified | OQ-1 key is either in a documented-omission list (C3) or generator emits it | generator output on a01 | one or the other holds |

---

## Acceptance Criteria

### Path-common
- [ ] `SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` exists and enumerates: (a) per-family claim level, (b) list of legitimate claims, (c) list of forbidden claims, (d) how claims are enforced.
- [ ] `MODEL_CLAIM_REGISTRY.yaml` exists with ≥3 real models (including `a01_catenary_riser`, `c03_fpso`, rigid jumper from #2455); each has `highest_validated_level` and a resolvable `test_enforcing` path.
- [ ] `test_skip_list_reconciliation.py` passes: the 4 code-level skip sets are reconciled with the taxonomy doc.
- [ ] #2476 wiki contract cross-referenced both ways (wiki page links to claim-boundary doc; claim-boundary doc links to wiki page).
- [ ] Plan and outputs do NOT re-invent SEMANTIC_DIFF_TAXONOMY.md — either ratified in place (Approach A) or explicitly deferred to #517 (Approach B).
- [ ] All new tests pass on dev-primary (L1 gate): `uv run pytest digitalmodel/tests/solvers/orcaflex/test_skip_list_reconciliation.py -v`.
- [ ] No regression: `uv run pytest digitalmodel/tests/solvers/orcaflex/` passes.
- [ ] Review artifacts posted to `scripts/review/results/`.

### Approach-A-only (additional)
- [ ] OQ-4: `values_equal(True, 'Yes') == True` and bool-only fixture produces 0 SIGNIFICANT diffs.
- [ ] OQ-3: licensed-win-1 test comparing `_DEFAULTS` to OrcFxAPI blank-model export passes (or each deviation is documented).
- [ ] OQ-1: `VerticalWindVariationFactor` either classified C3 with test, or generator emits it.
- [ ] OQ-2: measured Groups gap for at least one pipeline + one riser model, recorded in registry `known_diffs`.
- [ ] SEMANTIC_DIFF_TAXONOMY.md re-attribution preserves original author history (no force-rewrite).

### L-level split
- [ ] L1 (YAML-loadable + schema-valid) claims: fully dev-primary-runnable.
- [ ] L2 (behavioral parity via OrcFxAPI statics) claims: gated to `licensed-win-1`, marked with pytest marker.
- [ ] L3 (strict round-trip) claims: explicitly called out as NOT supported for generic-track models.

---

## Adversarial Review Summary

<!-- Filled in after Wave 3 adversarial review. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | (placeholder) |
| Codex | APPROVE / MINOR / MAJOR | (placeholder) |
| Gemini | APPROVE / MINOR / MAJOR | (placeholder) |

**Overall result:** PENDING

Revisions made based on review:
- (placeholder — Wave 3 fills)

---

## Risks and Open Questions

### [TRADEOFF FOR USER] — Primary scope decision (MUST decide before implementation)

Explorer recon found `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` (413 lines, C1..C6 categories, L1/L2/L3 claim levels, OQ-1..OQ-4) **already exists** under attribution "#517 work (parent: #515)". This invalidates the default "#515 = taxonomy authoring" framing and creates two viable paths. Present both — do NOT silently pick.

- **Approach A (broad) — #515 adopts/ratifies the existing taxonomy and resolves the four OQs in-scope.**
  - Scope: adopt SEMANTIC_DIFF_TAXONOMY.md (re-attribute or add "Adopted by #515" header), resolve OQ-1 (VerticalWindVariationFactor classification), OQ-2 (measure Groups gap), OQ-3 (verify `_DEFAULTS` against OrcFxAPI — licensed-win-1 gated), OQ-4 (fix bool-normalization in `values_equal`), write claim-boundary doc + registry + reconciliation test.
  - Pros: #515 closes as a meaningful deliverable (not just paperwork); children #517/#518/#519 shrink to implementation-only; prevents re-litigation of taxonomy.
  - Cons: larger plan; L2 OQ-3 needs licensed-win-1; OQ-4 touches `semantic_validate.py` (2108 lines) and may re-classify existing test-run verdicts; bumps complexity toward T3.
  - Complexity: T2-high (potentially T3 if all four OQs close in one pass).

- **Approach B (narrow) — #515 writes only the meta-contract and defers everything else to children.**
  - Scope: write `SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` + `MODEL_CLAIM_REGISTRY.yaml` + `test_skip_list_reconciliation.py`. Reference SEMANTIC_DIFF_TAXONOMY.md as "provisional, ratification tracked in #517"; defer OQ-1/2/3/4 to #517/#518/#519.
  - Pros: clean separation of concerns; #515 closes fast; preserves original cluster shape; L2 licensed-win-1 work stays out of #515; lowest-risk to existing test verdicts.
  - Cons: #515 feels paperwork-only; OQ-4 false-positive SIGNIFICANT diffs persist until #518 lands; OQ-1/2/3 stay unresolved; some reviewers may view this as "scope dodging".
  - Complexity: T2 (clean).

**Decision required from user before Wave 3 review.** Planner recommends Approach B only if user wants strict per-issue scope hygiene; Approach A if user values single-issue closure over cluster shape.

### [TRADEOFF FOR USER] — Secondary: OQ-4 fix location (only if Approach A)

`values_equal()` in `semantic_validate.py` vs `OrcaFlexDumper` in `yaml_utils.py`.
- Fix-at-compare (in `values_equal`): narrower blast radius; only the diff engine treats Yes≡true; existing YAML output unchanged.
- Fix-at-dump (in `yaml_utils.py`): widens blast radius; changes YAML emit convention, risks OrcaFlex load-side regressions (OrcaFlex expects Yes/No).
- Planner recommends fix-at-compare.

### [TRADEOFF FOR USER] — Tertiary: Registry format (both approaches)

- YAML registry (`MODEL_CLAIM_REGISTRY.yaml`) — machine-readable, assertable in tests. Recommended.
- Markdown table — human-readable, harder to assert. Needed if non-engineer stakeholders read it.

### Other risks
- **Risk:** `semantic_validate.py` (2108 lines) is highly coupled — any `values_equal` change may re-classify previous test-run verdicts (2454/2455/2456/2457 proofs already on file). Adversarial review must force a back-compat story (re-run all prior proofs, diff verdicts).
- **Risk:** `generic_builder.py` (343 lines) — `_SKIP_GENERAL_KEYS` expansions (if any OQ resolution adds keys) require re-running all per-family proofs. Scope any skip-list change to "documentation-only unless user explicitly approves expansion".
- **Risk:** Evidence is `a01_catenary_riser`-scoped; claims must specify evidence scope per family. Planner enforces via registry `known_diffs` field.
- **Risk:** `#2476 wiki contract` is approved and cross-solver; #515 is OrcaFlex-specific. If wording diverges, the wiki contract wins. Planner should treat #2476 as a constraint, not a collaborator.
- **Risk:** L2 validation requires OrcFxAPI + licensed-win-1. OQ-3 test must be marked `pytest.mark.licensed_win_1` or equivalent; cannot run on dev-primary.
- **Risk:** SEMANTIC_DIFF_TAXONOMY.md re-attribution (Approach A) may create git-blame churn. Preferred: add an "Adopted by #515 on YYYY-MM-DD" header without moving line numbers.

### Open questions (independent of approach)
- **Open:** Should `test_skip_list_reconciliation.py` be a unit test or a CI-gate-only check? (Recommend unit + pre-commit hook at Level-2 enforcement.)
- **Open:** Does the registry enumerate every model in `library/model_library/` or only those with at-least-L1 claims? (Recommend: only claimed models; unclaimed models silently excluded but inventoried in a sibling file.)

---

## Complexity: T2

**T2** — scope-and-contract issue with mostly-existing substrate. Approach B is unambiguously T2 (3 new files: 1 doc, 1 registry YAML, 1 reconciliation test; no source-code changes). Approach A is T2-high (adds OQ-4 fix in `values_equal`, 1 licensed-win-1 test, 1 builder modification) but not T3 because changes are narrow-touch (≤5 source files) and each OQ has a clear existing landing site. Promote to T3 only if user requests Approach A AND wants all four OQs closed in a single PR rather than split across children.
