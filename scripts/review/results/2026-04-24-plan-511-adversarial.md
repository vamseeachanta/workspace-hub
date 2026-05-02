# Adversarial Review — Plan for Issue #511 (OrcaFlex campaign spec generation)

**Reviewer stance:** Defect-hunter. Charitable reading forbidden.
**Plan under review:** `docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md`
**Intel:** `/tmp/orca-batch-2026-04-24/intel-511.md`
**Date:** 2026-04-24

---

## Verdict

**MINOR** — plan is structurally sound (correct reframe from "greenfield" to extension; correct citations of `CampaignMatrix`, `CampaignGenerator`, `_apply_overrides`, and OrcaWave `_set_nested`; honest tradeoff surfacing), but contains several concrete correctness defects in the pseudocode, a missing existing-file citation (`extractor.py` BOM-safe YAML loader), and an under-specified sweep cross-product that will produce wrong combo counts when `sweeps` is empty.

Not MAJOR because no defect invalidates the plan's core approach or its scope boundary. All defects are localized edits to the pseudocode, acceptance criteria, or the TRADEOFF blocks.

Not APPROVE because the `itertools.product(*())` edge case (D1) and the `{**typed_dict, **{...}}` key-clash hazard (D2) are genuine implementation traps that a downstream agent will hit, and the `_set_nested`→Pydantic-aware-setter port (D5) is under-specified in a way that lets frozen/validator-coupled models silently corrupt state.

---

## Full defect checklist

| # | Check | Status | Notes |
|---|---|---|---|
| C1 | Plan reframes from "greenfield" to extension | PASS | Framing correction at lines 11-26 is explicit and correct. |
| C2 | Plan cites `schema/campaign.py` | PASS | Cited with line ranges `67-114`, `117-295`, `298-348`, `362-488`. |
| C3 | Plan cites `_set_nested` in `parametric_spec_generator.py` | PASS | Cited at line 186 as pattern to port. |
| C4 | Plan addresses sweep-dimensionality tradeoffs (full-factorial, LHS, OAAT, scalar grid) | PASS | TRADEOFF block at lines 257-262 covers (A)/(B)/(C) + scalar-grid explicitly. |
| C5 | Scope boundary (spec-only, no execution) stated | PASS | Hard scope line at 25; reinforced in acceptance criteria. |
| C6 | Future tense only for new artifacts | PASS | Line 23 explicit; passes past-tense trap check. |
| C7 | Backward compat called out | PASS | `sweeps: list[...] = []` default + regression test `test_campaign_generator_full_mode_regression`. |
| C8 | Pseudocode is internally consistent | **FAIL** | See D1, D2, D3. |
| C9 | YAML loader robustness addressed | **FAIL** | Intel cites `extractor.py:119-163` BOM/latin-1 fallback. Plan does not mention reusing it for the new `campaign_spec.yml` path. See D4. |
| C10 | Pydantic-aware setter fully specified | **FAIL** | Plan says "walk Pydantic tree and re-validate" but the dump/revalidate strategy has holes for `model_config = ConfigDict(frozen=True)` and for path-walk past `Optional[...]` / `Union` fields. See D5. |
| C11 | Source count ≥ 3 | PASS | Five distinct sources (issue + 4 repo refs). |
| C12 | Test list maps to acceptance criteria | PASS | 17 tests; all ACs have corresponding tests. |
| C13 | Complexity justified | PASS | T2 rationale at 292-296 is coherent. |
| C14 | No self-approval / no past-tense claims | PASS | Adversarial Review section is explicitly TBD. |
| C15 | `test_dotted_sweep_conflict_with_environment_variation_warned` matches the chosen overlap policy | PARTIAL | Plan picks option (A) — WARN + dotted-wins — but the test name only asserts WARN; it does not assert "dotted wins". See D6. |
| C16 | Combinatorial-explosion preflight threshold is sensible | PARTIAL | 100 is arbitrary and not aligned with existing `max_runs` guardrail on `CampaignSpec`. See D7. |
| C17 | `alias:` slug fallback covers dotted-path collisions | PARTIAL | `environment.waves.height` and `environment.current.height` both slug to `environment-*-height` patterns distinct, but two sweeps under the same parent segment with same leaf produce identical slugs. See D8. |
| C18 | Manifest.yml emission is decided | PARTIAL | Listed as "recommended yes" in tradeoff (line 267) but NOT in the Files-to-Change table, NOT in the test list, NOT in acceptance criteria. See D9. |
| C19 | `combination: Literal[...]` decision is made | PARTIAL | Line 141 scopes to `Literal["full_factorial"]` but line 288 reopens the decision. Pick one. See D10. |

---

## Specific defects

### D1 — `itertools.product(*(s.values for s in self.sweeps))` yields `[()]` when `sweeps == []`, multiplying the typed product by 1 (benign) OR `[]` when a single sweep has empty `values` (would short-circuit to zero combos silently)

**Location:** plan line 147.

```
sweep_combos = itertools.product(*(s.values for s in self.sweeps))
```

- If `self.sweeps == []`: `itertools.product()` yields `[()]` (single empty tuple) — benign, multiplies typed_combos by 1. OK.
- If any `ParameterSweep.values == []`: validator rejects (test `test_parameter_sweep_empty_values_rejected` covers it). OK at load time.
- **But:** if `self.sweeps == []` AND typed axes are also all empty (`water_depths=[]`, `route_lengths=[]`, etc.), existing `combinations()` already yields `itertools.product([None], [None], ...)` = one combo of all-Nones. The new code's `{**typed_dict(typed), **{s.parameter: v for s, v in zip(self.sweeps, sweep_vals)}}` then yields a single empty-ish combo that `_apply_overrides` must handle.

**Why this is a defect:** the pseudocode does not guard or test the "zero typed axes + zero sweeps" degenerate case. `CampaignMatrix()` with all defaults will now validate (no `sweeps:` required) and `combinations()` will yield one bogus combo. Add `test_campaign_matrix_no_axes_and_no_sweeps_rejected` (or explicit model-level `@model_validator` that at least one axis must be set).

**Fix:** add a `@model_validator(mode='after')` on `CampaignMatrix` asserting `any([water_depths, route_lengths, tensions, environments, soils, sweeps])`. Add test.

---

### D2 — `{**typed_dict(typed), **{s.parameter: v for ...}}` key-clash hazard when a dotted sweep key collides with a typed-axis key

**Location:** plan line 150.

The combo dict merge uses `**` spread. If a user writes `sweeps: [{parameter: "water_depth", values: [...]}]` (a dotted path that happens to match the name used in `typed_dict(typed)`), the dotted version silently overwrites the typed version. The plan's overlap guard (TRADEOFF C) only covers `environment.*` overlap with `EnvironmentVariation`; it does not cover top-level axis-name collision.

**Why this is a defect:** The failure mode is silent — user expects 2 × 3 = 6 runs from typed `water_depths=[100, 200]` × dotted `parameter="water_depth", values=[10, 20, 30]`, but gets 2 × 3 = 6 combos where typed's water_depth is overwritten every time. No warning.

**Fix:** in `combinations()`, detect `sweep.parameter in typed_combo_keys()` and raise `ValueError` with the conflicting name at model-validation time (preferably in a `@model_validator`, not at generation time). Add test `test_sweep_parameter_shadowing_typed_axis_rejected`.

---

### D3 — Pseudocode `_apply_overrides(base, combo)` has no access to `matrix.sweeps` in its current signature

**Location:** plan lines 160-165.

```
def _apply_overrides(base, combo):
    spec = existing_typed_axis_overrides(base, combo)   # unchanged
    for sweep in matrix.sweeps:                          # NEW loop
```

The existing `_apply_overrides` at `schema/campaign.py:298-348` is a module-level function called from `CampaignSpec.generate_run_specs()`. It has no `matrix` parameter today — it works off the `combo` dict alone and the typed keys it contains. The plan's new loop references `matrix.sweeps` without showing how it is plumbed through. The real implementation must either:

1. Change the signature to `_apply_overrides(base, combo, sweeps)` and thread it from `generate_run_specs`, or
2. Move the generic loop into `CampaignSpec.generate_run_specs()` before/after calling `_apply_overrides`, or
3. Encode enough metadata in `combo` so `_apply_overrides` can detect dotted keys heuristically (fragile — dotted-path key contains `.`, typed key does not).

**Why this is a defect:** downstream implementer will either hack option (3) or silently break the existing signature. Plan should pick option (1) or (2) explicitly and note it in Files-to-Change.

**Fix:** add to Files-to-Change row for `campaign.py`: "thread `sweeps` into `_apply_overrides` OR handle dotted overrides in `generate_run_specs` directly (decide during implementation)."

---

### D4 — `extractor.py:119-163` BOM/latin-1 fallback YAML loader is cited in intel but NOT in the plan

**Location:** intel line 19 (file reference table) — plan does not cite it.

Intel explicitly flags: *"The campaign loader in the new code should reuse this robustness instead of plain `yaml.safe_load`."* This is a direct instruction from resource intel that the plan ignored.

**Why this is a defect:** `CampaignGenerator` today uses `yaml.safe_load` (plan implies continuation). A Windows-authored `campaign_spec.yml` with BOM will fail silently on some loaders or surface cryptic `yaml.scanner.ScannerError` instead of the existing extractor's user-friendly fallback. Cross-platform regressions are expensive.

**Fix:** add a Files-to-Change row for `CampaignGenerator._load_yaml` (or similar) to route through the same BOM/latin-1 fallback helper. Add test `test_campaign_loader_handles_bom_encoded_yaml`.

---

### D5 — "walk Pydantic tree and re-validate via `model_validate(model_dump())`" is under-specified for frozen models, `Union` fields, and computed-validator dependencies

**Location:** plan lines 153-158.

```
# walk Pydantic model by attribute, not dict-mutation
# use model_copy(update=..., deep=True) at each level to preserve validation
# on final leaf: assign, then re-validate via model.model_validate(model.model_dump())
```

Three concrete gaps:

1. **`model_copy(update=...)` does NOT revalidate by default** in Pydantic v2. You must pass `deep=True` AND the caller must re-run `.model_validate(...)` on the result if type coercion is desired — `model_copy(update=...)` only *assigns*. The pseudocode says "model_copy(update=..., deep=True) at each level" — but `update=` is a flat-dict arg for the top-level model, not "at each level."

2. **`Union[WaveA, WaveB]` discriminated unions**: setting `environment.waves.height=3.5` when `environment.waves` is a discriminated union picks the *current* discriminator; if the dotted value changes the discriminator field, the walk must re-discriminate. The plan does not address this.

3. **`ConfigDict(frozen=True)`**: if any intermediate Pydantic model in the `ProjectInputSpec` tree is frozen, `setattr` fails. Plan says "assign, then re-validate" — assignment fails first.

**Why this is a defect:** the port of `_set_nested` is the load-bearing technical move. Intel specifically warns *"`_set_nested` in `parametric_spec_generator.py` skips validation — setting a sweep value must re-validate via Pydantic to catch type errors at generation, not execution"* (intel line 56). The plan acknowledges the requirement but under-specifies the mechanism.

**Fix:** pick a strategy and state it. Recommended: *dump whole `base` to `dict`, walk dict by dotted path (like `_set_nested`), then `ProjectInputSpec.model_validate(full_dict)` to re-hydrate. This sidesteps frozen/Union/validator-ordering issues in one pass and preserves validation.* Test coverage: add `test_apply_dotted_override_to_frozen_submodel` and `test_apply_dotted_override_crossing_discriminated_union`.

---

### D6 — `test_dotted_sweep_conflict_with_environment_variation_warned` asserts WARN but not the chosen "dotted wins" semantic

**Location:** plan lines 220, 270.

TRADEOFF (A) picks "dotted applied after typed (dotted wins)." The test name only guarantees a WARN is logged. It does not pin down the resolution order.

**Why this is a defect:** a downstream implementer could emit the WARN but apply typed-after-dotted (typed wins) and the test still passes. User approval of tradeoff (A) becomes unbinding.

**Fix:** rename / split into `test_dotted_sweep_conflict_emits_warning` + `test_dotted_sweep_conflict_dotted_value_wins`. Add the second test to the TDD list.

---

### D7 — Combinatorial-explosion WARN threshold (100) is arbitrary and not aligned with existing `CampaignSpec.max_runs`

**Location:** plan lines 180, 276.

`CampaignSpec.max_runs` already exists as a hard guardrail (intel line 58, plan line 276 acknowledges). Adding a *separate* WARN threshold at 100 creates two independent knobs with no documented relationship. If `max_runs=500` and threshold=100, users see WARN for anything >100 even when explicitly permitted.

**Why this is a defect:** drift between two guardrails. User approves `max_runs=500` but keeps seeing WARN noise.

**Fix:** derive threshold from `max_runs` (e.g. `WARN if combos > max_runs * 0.5`) OR fold into `max_runs` itself (WARN if `combos > max_runs` and `allow_large=True`). Document which. Update test `test_preflight_warning_above_threshold` to reflect chosen semantic.

---

### D8 — `alias:` slug fallback risks identical slugs for distinct dotted paths under the same alias-less sweep set

**Location:** plan line 217.

`test_sweep_naming_template_without_alias_slug_fallback` only covers one sweep. If a user declares two alias-less sweeps `vessel.inertia.mass` and `vessel.drag.mass`, both slug containing `-mass-{value}`. Run-dir names become ambiguous.

**Why this is a defect:** silent dir-name collision overwrites previous combo's `spec.yml` or `run_000`/`run_001` mapping depends on iteration order. User gets fewer output files than combos.

**Fix:** require full-path slug (join all segments, not just the leaf), and add `test_two_alias_less_sweeps_distinct_leaf_names_produce_distinct_dirs` + collision detection at generation time (`FileExistsError` if a run dir's slug collides with a prior one).

---

### D9 — Manifest.yml emission is "recommended yes" in tradeoff but not in Files-to-Change, TDD list, or acceptance criteria

**Location:** plan line 267 (tradeoff) vs. lines 187-196 (Files-to-Change) vs. 200-221 (TDD) vs. 224-234 (acceptance).

Tradeoff block recommends shipping both per-combo `spec.yml` AND a top-level `manifest.yml`. The rest of the plan does not reflect the recommendation.

**Why this is a defect:** a reader following only the Files-to-Change + TDD will not build the manifest. Recommendation is non-binding.

**Fix:** either (a) commit to the recommendation — add `manifest.yml` to Files-to-Change, add `test_spec_only_writes_top_level_manifest_with_combo_index`, add an acceptance criterion; or (b) drop the recommendation and move to Open Questions.

---

### D10 — `combination: Literal["full_factorial"]` is locked at line 141 but reopened at line 288

**Location:** plan lines 141 vs. 288.

Line 141: `combination: Literal["full_factorial"] = "full_factorial"` — locked.
Line 288: Open question whether to lock or pre-declare `Literal["full_factorial", "latin_hypercube", "one_at_a_time"]` with `NotImplementedError`.

**Why this is a defect:** inconsistent self-commitment. Downstream implementer does not know which shape to build.

**Fix:** pick one. Recommended: lock to `Literal["full_factorial"]` only (line 141 is right). Remove the line-288 Open Question. Rationale: pre-declaring LHS/OAAT with `NotImplementedError` invites accidental invocation and creates a dead-code smell.

---

## Justification

Verdict is **MINOR** because:

- The reframe (intel C1) is correct and the plan's primary technical approach (extend `CampaignMatrix` with `sweeps:`, port `_set_nested`, add `spec_only` path) matches intel's "cheapest path" recommendation line-for-line.
- All four required intel-driven checks (C1–C4) pass.
- Ten concrete defects are bounded edits: three pseudocode clarifications (D1, D2, D3), one missing citation (D4), one strategy pick (D5), four acceptance/test refinements (D6, D7, D8, D9), one consistency fix (D10). None require reworking the scope boundary or changing the target file.

Defects would become **MAJOR** if any of the following were also true:
- Plan claimed `CampaignSpec` was greenfield (past-tense trap) — it does not.
- Plan proposed executing specs — it explicitly excludes this.
- Plan ignored the OrcaWave precedent — it cites and ports it.
- Plan proposed a new top-level `CampaignSpec2` class — it does not.

**Recommended gate:** request revision addressing D1–D5 before `status:plan-approved`. D6–D10 can be resolved inline in the same revision pass.

---

## Hard forbiddens check

- [x] Did NOT self-label `status:plan-approved`.
- [x] Did NOT offer to approve on user's behalf.
- [x] Did NOT read the plan charitably — specifically hunted for defects.
- [x] Did NOT cite external/training knowledge — only this repo's intel, plan, and issue body.
- [x] Did NOT skip the intel's flagged items (extractor.py BOM loader was the one that was missing — flagged as D4).
