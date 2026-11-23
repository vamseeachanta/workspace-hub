# Phase 2 Architecture Blueprint — Issue #511 (OrcaFlex Campaign Spec Generation)

> **Status:** Phase 2 of 5 per execution handoff `docs/handoffs/2026-04-24-orcaflex-wave-a-issue-511-handoff.md`
> **Synthesizer:** `feature-dev:code-architect` agent, 2026-04-24
> **Inputs:** Plan `docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md`, Adversarial Review `scripts/review/results/2026-04-24-plan-511-adversarial.md`, 3 parallel Phase-1 explorer agents
> **Phase 3 entry:** Pending user sign-off on 3 blocking decisions (see §5)

**Correction to Phase 1 Agent A:** Phase 1 reported `_apply_overrides` had no `matrix` parameter. The actual source at `campaign.py:298-302` shows `_apply_overrides(spec, combo, matrix)` already has a three-argument signature. R3 finding D3 is therefore resolved by the existing code — no signature change needed.

---

## 1. Feature-Slice Ordering (TDD-first)

### Slice 1 — `ParameterSweep` Pydantic model

Intent: Define the new schema model in isolation; no existing code touched.

- Test file: `tests/solvers/orcaflex/modular_generator/schema/test_campaign.py`
- Test class: `TestParameterSweep`
- Test methods: `test_parameter_sweep_valid`, `test_parameter_sweep_empty_values_rejected`, `test_parameter_sweep_empty_parameter_rejected`, `test_parameter_sweep_dot_terminal_rejected`
- Source: `schema/campaign.py` — insert `ParameterSweep` class at line ~47 (after `InstallationSection`, before `CampaignMatrix`)
- Commit: `feat(#511): add ParameterSweep Pydantic model with dotted-path validator`

### Slice 2 — `apply_dotted_override` helper

Intent: Implement the safe dict-dump → mutate → `model_validate` applier as a standalone function; test it in isolation from the campaign machinery.

- Test class: `TestApplyDottedOverride` in `test_campaign.py`
- Test methods: `test_apply_dotted_override_leaf_value_set`, `test_apply_dotted_override_pydantic_validates_type_error`, `test_apply_dotted_override_unresolvable_path_raises`, `test_apply_dotted_override_list_index_raises_not_implemented`
- Source: `schema/_overrides.py` (new file, ~35 lines); `schema/campaign.py` imports it
- Commit: `feat(#511): add apply_dotted_override helper with Pydantic re-validation`

### Slice 3 — `CampaignMatrix.sweeps` field + `combinations()` extension + degenerate-axis guard

Intent: Extend `CampaignMatrix` with `sweeps`, cross-product them into `combinations()`, add the empty-all-axes `@model_validator`, add typed-axis-name collision guard.

- Test class: `TestCampaignMatrixCombinations` in `test_campaign.py`
- Test methods: `test_campaign_matrix_single_sweep_only`, `test_campaign_matrix_sweeps_crossed_with_typed_axis`, `test_campaign_matrix_two_sweeps_crossed`, `test_campaign_matrix_no_axes_and_no_sweeps_rejected`, `test_sweep_parameter_shadowing_typed_axis_rejected`, `test_backward_compat_no_sweeps_field`
- Source: `schema/campaign.py:67-114` — add `sweeps: list[ParameterSweep] = []` after `soils` (line ~80), add `@model_validator(mode='after')` empty-axis guard, extend `combinations()` lines 100-114
- Commit: `feat(#511): extend CampaignMatrix with sweeps field and cartesian product expansion`

### Slice 4 — `_apply_overrides` sweep loop + `validate_output_naming_coverage` extension

Intent: Thread generic sweep overrides through the existing typed-axis applier; extend the naming validator to handle sweep aliases.

- Test class: `TestApplyOverridesWithSweeps` in `test_campaign.py`
- Test methods: `test_apply_overrides_with_sweep_modifies_spec`, `test_dotted_sweep_conflict_emits_warning`, `test_dotted_sweep_conflict_dotted_value_wins`, `test_validate_output_naming_warns_on_sweep_axis_without_alias`
- Source: `schema/campaign.py:298-349` (add sweep loop after line 348); `schema/campaign.py:257-277` (extend `validate_output_naming_coverage` to recognize sweep aliases)
- Commit: `feat(#511): extend _apply_overrides and naming coverage validator for sweep axis`

### Slice 5 — Output naming slug + alias resolution + collision detection

Intent: Implement alias-required-when-referenced and full-path-slug fallback, with dir-name collision detection.

- Test class: `TestSweepNaming` in `test_campaign.py`
- Test methods: `test_sweep_naming_template_with_alias`, `test_sweep_naming_template_without_alias_slug_fallback`, `test_two_alias_less_sweeps_distinct_leaf_names_produce_distinct_dirs`, `test_duplicate_slug_collision_detected_at_generation`
- Source: `schema/campaign.py:292-295` (`generate_run_specs` naming line); `CampaignGenerator.validate()` at lines 383-405 (add collision detection)
- Commit: `feat(#511): add sweep alias resolution and slug fallback for output naming`

### Slice 6 — `CampaignGenerator.generate()` spec-only path + resume sentinel fix

Intent: Add `spec_only: bool = False` to `CampaignGenerator.generate()`, wire it through `generate_run_specs`, fix resume sentinel to check `spec.yml` in spec-only mode, add `max_runs`-relative explosion warning.

- Test class: `TestCampaignGeneratorSpecOnly` in `test_campaign_generator.py`
- Test methods: `test_campaign_generator_spec_only_writes_one_yml_per_combo`, `test_campaign_generator_spec_only_skips_master_and_includes`, `test_campaign_generator_full_mode_regression`, `test_preflight_warning_above_max_runs_threshold`, `test_spec_only_writes_top_level_manifest_with_combo_index`
- Source: `schema/campaign.py:407-487` (add `spec_only` parameter, branch body, write per-combo `spec.yml` + top-level `manifest.yml`, fix resume at line 436)
- Commit: `feat(#511): add spec_only emission path to CampaignGenerator`

### Slice 7 — CLI `--spec-only` flag + sweep preview display

Intent: Surface the new flag on `cmd_campaign`; extend the preview block to include sweep axis counts.

- Test class: `TestCampaignCLI` in `test_campaign_generator.py`
- Test methods: `test_cli_campaign_spec_only_flag`, `test_cli_preview_shows_sweep_counts`
- Source: `cli.py:293-358` — add `--spec-only` to argument parser, plumb through `gen.generate(..., spec_only=args.spec_only)`, extend preview block lines 320-330
- Commit: `feat(#511): add --spec-only CLI flag and sweep count in preview`

### Slice 8 — End-to-end integration

Intent: Campaign YAML with two dotted sweeps → N `spec.yml` on disk, each validates against `ProjectInputSpec`; BOM-encoded input handled; backward compat asserted.

- Test class: `TestSweepCampaignE2E` in `tests/solvers/orcaflex/modular_generator/integration/test_campaign_integration.py`
- Test methods: `test_e2e_two_dotted_sweeps_produce_n_spec_ymls`, `test_e2e_each_spec_yml_validates_as_project_input_spec`, `test_e2e_manifest_yml_combo_index_correct`, `test_e2e_backward_compat_no_sweeps_key`, `test_campaign_loader_handles_bom_encoded_yaml`
- Source: `schema/campaign.py:369-372` — replace `yaml.safe_load` with BOM-safe loader from `extractor.py:119-163`; add `tests/solvers/orcaflex/modular_generator/integration/` fixtures
- Commit: `test(#511): end-to-end sweep campaign generates and validates all spec.yml files`

---

## 2. Key Design Decisions

### (a) LHS sampler dependency

**Alternative A:** `Literal["full_factorial"]` only — zero new deps, matches all examples in issue body, defers LHS/OAAT.

**Alternative B:** Pre-declare `Literal["full_factorial", "latin_hypercube", "one_at_a_time"]` with `NotImplementedError` for the latter two.

Trade-offs: B invites accidental invocation and creates dead code. A is cleanest. The OrcaWave sibling uses no LHS; no wiki page covers LHS; no issue example requests it.

**Recommendation: A.** Lock to `Literal["full_factorial"]` at the field declaration. Do not pre-declare LHS/OAAT. Close the plan's Open Question at line 288.

Affects `schema/campaign.py` at the `CampaignMatrix.combination` field (insert after `sweeps`). The R3 review (D10) agrees: "lock to `Literal['full_factorial']` only (line 141 is right)."

**USER DECISION REQUIRED before Phase 3 if user has strong preference for Alternative B.**

### (b) Dotted-path validation strategy

**Alternative A:** Full `model_dump()` → `_set_nested()` → `ProjectInputSpec.model_validate(full_dict)` in one pass.

**Alternative B:** Walk Pydantic tree attribute by attribute with `model_copy(update=..., deep=True)` at each level.

Trade-offs: B fails silently for frozen sub-models (see R3/D5), cannot discriminate `Union` fields correctly on path traversal, and `model_copy` does not re-validate by default. A sidesteps all three issues: dict mutation is type-agnostic, and the single `model_validate` at the end catches every type error in one shot.

**Recommendation: A.** The `_set_nested` in `parametric_spec_generator.py:186-191` is the right structural template, but must guard against missing intermediate keys (raise `KeyError` with path context, do NOT use `setdefault` which silently creates nodes). List-index paths (`foo.items[0].bar`) must raise `NotImplementedError`.

Affects `schema/_overrides.py` (new), imported at `schema/campaign.py` top-level.

**No user decision needed — A is unambiguously correct.**

### (c) `validate_output_naming_coverage` extension strategy

**Alternative A:** Extend to recognize sweep `.alias` as a valid placeholder (WARN instead of raise for alias-less sweeps).

**Alternative B:** Relax to WARN across the board for sweep-only axes.

**Alternative C:** Leave unchanged; runtime `KeyError` in `generate_run_specs` at `output_naming.format(**combo)` surfaces the gap.

Trade-offs: C allows the failure to propagate to generation-time string formatting where dotted keys cause `KeyError` immediately, which is worse UX. B loses the guarantee that users get warned about named axes missing from templates. A is correct: if a sweep has an `alias`, treat the alias as the placeholder key; if no alias, emit WARN but do not raise (the slug fallback provides the naming).

**Recommendation: A.** Extend `validate_output_naming_coverage` (lines 257-277) to iterate `self.campaign.sweeps` and for each sweep: if `alias` is set, check `{alias}` in template (raise if absent); if no alias, emit `logger.warning` only.

Affects `schema/campaign.py:257-277`.

**No user decision needed — A resolves all three validator failure modes.**

### (d) Output-naming slug strategy for dotted keys

**Alternative A:** Require explicit `alias` when the template references the sweep; use full-path slug (`environment-waves-height`) as fallback when no alias.

**Alternative B:** Auto-slug always (no alias required; dotted path is always slugged by replacing `.` with `-`).

**Alternative C:** `str.format_map` with a custom mapping that ignores extra keys.

Trade-offs: B causes ambiguity when two sweeps share a leaf segment name (R3/D8: `vessel.inertia.mass` vs `vessel.drag.mass` both produce `*-mass-*`). C masks missing aliases silently. A is explicit: full-path slug ensures uniqueness across all dotted paths in the sweep set; alias gives user control of short names in templates.

**Recommendation: A.** Slug = `parameter.replace(".", "-")` (full path, not just leaf). Collision detection added to `CampaignGenerator.validate()`.

Affects `schema/campaign.py:292-295` (naming line in `generate_run_specs`), `schema/campaign.py:383-405` (`CampaignGenerator.validate`).

**No user decision needed.**

---

## 3. Files-to-Touch Checklist

### Schema layer — `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/`

- `campaign.py:47` — insert `ParameterSweep` class (Slice 1)
- `campaign.py:67-114` (`CampaignMatrix`) — add `sweeps` field ~line 80, add `@model_validator` empty-axis guard, add typed-axis-shadowing guard in same validator, extend `combinations()` lines 100-114 to cross-product sweep values (Slice 3)
- `campaign.py:257-277` (`validate_output_naming_coverage`) — extend to alias/warning logic for sweeps (Slice 4)
- `campaign.py:279-295` (`generate_run_specs`) — replace `output_naming.format(**combo)` with alias-aware slug resolution; do not use `model_copy(deep=True)` alone — the sweep path must re-validate via `apply_dotted_override` (Slice 4/5)
- `campaign.py:298-349` (`_apply_overrides`) — add sweep loop after line 348 calling `apply_dotted_override` (Slice 4)
- `campaign.py:369-372` (`CampaignGenerator.__init__`) — replace `yaml.safe_load` with BOM-safe loader from `extractor.py:119-163` (Slice 8)
- `campaign.py:407-487` (`CampaignGenerator.generate`) — add `spec_only: bool = False` parameter, branch body for spec-only path, write `spec.yml` + `manifest.yml`, fix resume sentinel at line 436 (Slice 6)
- `_overrides.py` (new, ~35 lines) — `apply_dotted_override(spec, dotted, value)` + `_set_nested_safe(d, path, value)` that raises `KeyError` on missing intermediates and `NotImplementedError` on list-index segments (Slice 2)

### CLI layer

- `cli.py:293-358` (`cmd_campaign`) — add `--spec-only` to subparser args; extend preview block lines 320-330 to show sweep axis counts; plumb `spec_only=args.spec_only` into `gen.generate(...)` at line 354 (Slice 7)

### Test files

- `tests/solvers/orcaflex/modular_generator/schema/test_campaign.py` — extend with `TestParameterSweep`, `TestApplyDottedOverride`, extended `TestCampaignMatrixCombinations`, `TestApplyOverridesWithSweeps`, `TestSweepNaming` (Slices 1-5)
- `tests/solvers/orcaflex/modular_generator/test_campaign_generator.py` — extend with `TestCampaignGeneratorSpecOnly`, `TestCampaignCLI` (Slices 6-7)
- `tests/solvers/orcaflex/modular_generator/integration/test_campaign_integration.py` — new or extend with `TestSweepCampaignE2E` (Slice 8)

### Fixtures (YAML)

- `tests/solvers/orcaflex/modular_generator/fixtures/campaign_two_sweeps.yml` (new) — `base:` with known field values, two dotted sweeps (`environment.waves.height` × `environment.waves.direction`), `output_naming` with aliases
- `tests/solvers/orcaflex/modular_generator/fixtures/campaign_two_sweeps_bom.yml` (new, BOM-prefixed copy for Slice 8 BOM test)
- Existing `test_campaign_floating.yml` — do not modify; used only in backward-compat regression test

---

## 4. Risks the Implementer Must Not Miss

**R1 — `model_copy(deep=True)` at `campaign.py:290` skips Pydantic v2 validation.**
The existing `generate_run_specs` uses `model_copy(deep=True)` for base spec cloning, which is fine for the typed axes (those mutate well-typed fields directly). But the sweep path must go through `apply_dotted_override` which dumps to dict and re-validates, not through `model_copy`. Do not call `model_copy` anywhere in the sweep loop. The final returned spec from `apply_dotted_override` is already validated — do not `model_copy` it again afterward.

**R2 — `str.format(**combo)` at `campaign.py:292-294` KeyErrors on dotted keys.**
After Slice 3, the combo dict will contain keys like `"environment.waves.height"`. Python's `str.format` cannot accept dotted keys as placeholders. The naming line must map each sweep to its alias (if set) or full-path-slug before calling `format`. This is not a nice-to-have; it is a hard crash path.

**R3 — `validate_output_naming_coverage` raises `ValueError` on sweep axes (`campaign.py:271-276`).**
The existing validator raises if any varying parameter is absent from the template. After adding sweeps to `combinations()`, dotted-path keys will be in `combo` and will trip the validator on every sweep-only campaign. Slice 4 must extend the validator before Slice 3's changes are tested end-to-end, or the `CampaignSpec` constructor itself will raise during the fixture load.

**R4 — `setdefault` silent key creation (from OrcaWave `parametric_spec_generator.py:190`).**
Do not inherit this behavior. `_set_nested_safe` in `_overrides.py` must raise `KeyError` with the full attempted path when an intermediate key does not exist in the dict. `setdefault` would silently graft a new branch onto the dict, then `model_validate` would see an unrecognized field and either strip it (extra='ignore') or raise an opaque error. Explicit `KeyError` gives a clear user message: "path segment 'foo' not found under 'environment'."

**R5 — List-index dotted paths silently create string keys.**
`_set_nested_safe` must detect segments that look like integers (e.g. `"0"`, `"1"`) when the target at that level is a `list` and raise `NotImplementedError("List-index paths are not supported: <path>")`. Without this guard, `_set_nested_safe` would set `d["0"] = value` on a list, which either silently fails or corrupts the dict in unpredictable ways.

**R6 — D1 from R3: `CampaignMatrix()` with all defaults is valid but produces one degenerate combo.**
The actual source code (`campaign.py:70`) uses `Field(..., min_length=1)` on `water_depths` (required). This means the all-empty case cannot be constructed without sweeps — but after making `water_depths` optional (which Slice 3 may require for sweep-only campaigns), the degenerate case becomes live. Add `@model_validator(mode='after')` asserting `any([self.water_depths, self.route_lengths, self.tensions, self.environments, self.soils, self.sweeps])`. This is load-bearing: without it, `CampaignMatrix(sweeps=[])` would produce one empty combo.

**R7 — D7 from R3: separate WARN threshold at 100 drifts from `max_runs`.**
Derive the explosion warning from `max_runs` if set (warn if `combos > max_runs * 0.5` or simply `combos >= max_runs`), or use a module-level constant (default 100) only when `max_runs` is `None`. Document the chosen relationship. Do not add a separate uncoupled constant.

**R8 — D4 from R3: BOM-encoded `campaign_spec.yml` from Windows authoring tools.**
`CampaignGenerator.__init__` at `campaign.py:371` calls `yaml.safe_load(self.campaign_file.read_text())` — no encoding fallback. Replace with the BOM/latin-1 fallback loader used by `src/digitalmodel/solvers/orcaflex/modular_generator/extractor.py:119-163`. Failure mode is `yaml.scanner.ScannerError` on BOM byte `\xef\xbb\xbf`, which is a cross-platform regression.

**R9 — D9 from R3: manifest.yml is "recommended yes" in the plan but untracked.**
The blueprint commits to writing a `manifest.yml` in spec-only mode (Slice 6). This must appear in `CampaignResult` (add `manifest_path: Path | None` field to the dataclass at line 351), in the test list, and in the acceptance criteria. If the user decides to defer it, the test `test_spec_only_writes_top_level_manifest_with_combo_index` should be explicitly skipped with a `pytest.mark.skip` and a comment referencing the follow-up issue number.

---

## 5. Phase 3 Entry Conditions

### Blocks Phase 3 start (user sign-off required)

1. **LHS decision (Decision a):** Confirm `Literal["full_factorial"]` only for v1. Blueprint recommends yes; user must confirm before implementer writes the `CampaignMatrix.combination` field.
2. **`water_depths` optionality:** The current `CampaignMatrix.water_depths` has `Field(..., min_length=1)` — it is required. For sweep-only campaigns (no typed axes), this field must become optional. Confirm whether to make `water_depths: list[float] | None = None` and rely on the `@model_validator` to enforce at-least-one-axis. Schema-level backward-compat decision.
3. **Manifest decision:** Confirm whether `manifest.yml` is in scope for this issue. Blueprint includes it in Slice 6; if deferred, remove `test_spec_only_writes_top_level_manifest_with_combo_index` from the acceptance criteria and file a follow-up.

### Can be decided during Phase 3 (non-blocking)

- Whether `ParameterSweep` supports non-scalar `values` entries (nested dicts). Default: allow `list[Any]` as specified; non-scalar values round-trip through `model_validate`.
- Exact `max_runs`-relative threshold constant value for explosion warning.
- Whether to put `apply_dotted_override` in `_overrides.py` (new file) or inline into `campaign.py`. Either is acceptable; `_overrides.py` is preferred for testability.

### Pre-work checklist for Phase 3 implementer

- Branch `issue-511-campaign-spec-generation` from `origin/main` of the digitalmodel git repo at `/mnt/local-analysis/workspace-hub/digitalmodel`
- Confirm baseline passes: `uv run --project digitalmodel pytest tests/solvers/orcaflex/modular_generator/schema/ -q` — all green before first edit
- Read this blueprint and the adversarial review `scripts/review/results/2026-04-24-plan-511-adversarial.md` in full
- Confirm `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py` exists and matches the line ranges cited here (key anchors: `CampaignMatrix` at line 67, `_apply_overrides` at line 298, `CampaignGenerator.generate` at line 407)
- Confirm `extractor.py` BOM loader location: `src/digitalmodel/solvers/orcaflex/modular_generator/extractor.py:119-163`
- Implement slice-by-slice in order 1 → 8; run tests after each slice before proceeding
- Do NOT run any slice's tests under `tests/solver/` (OrcFxAPI-gated); all new tests belong under `tests/solvers/orcaflex/modular_generator/`
