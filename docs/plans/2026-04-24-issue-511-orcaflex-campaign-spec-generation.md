# Plan for #511: OrcaFlex — campaign spec generation (parametric sweep from spec.yml)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/511
> **Review artifacts:** scripts/review/results/2026-04-24-plan-511-claude.md | ...-codex.md | ...-gemini.md

---

## Framing correction (from pod Explorer intel)

The batch-design spec (`docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md:51`) labels #511 as a "greenfield generator". This is incorrect. The core surface ALREADY EXISTS:

- `CampaignSpec`, `CampaignMatrix`, `CampaignGenerator` live in `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py`.
- `CampaignSpec.generate_run_specs()` already performs streaming cartesian-product expansion via `model_copy(deep=True)` + `_apply_overrides`.
- The dotted-path `_set_nested(d, 'a.b.c', value)` helper already exists in the OrcaWave sibling `digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py` (from issue #1596).

This plan therefore reframes #511 as an **extension of the existing OrcaFlex `CampaignMatrix`** with:
1. a generic dotted-path `sweeps:` axis type (porting the `_set_nested` pattern from OrcaWave), and
2. a **spec-only emission mode** on `CampaignGenerator` (write `run_XXX/spec.yml` per combination, no `master.yml`/`includes/`).

Future-tense applies only to the new `ParameterSweep` model, the generic override applier, and the spec-only emission path. The existing `CampaignSpec`/`CampaignMatrix`/`CampaignGenerator` are reused as-is.

**Scope boundary (hard):** Spec generation only. Execution of generated specs against a licensed OrcaFlex, and post-processing of solver outputs, are OUT OF SCOPE for this issue.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py:67-114` — `CampaignMatrix` Pydantic model with fixed typed axes (`water_depths`, `route_lengths`, `tensions`, `environments`, `soils`) and `.combinations()` producing full cartesian product via `itertools.product`. **Primary extension target.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py:117-295` — `CampaignSpec` top-level model with `base: ProjectInputSpec`, `campaign: CampaignMatrix`, `output_naming`, `generate_run_specs()`. **Reuse as-is; add one field to `CampaignMatrix`.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py:298-348` — `_apply_overrides` hand-coded per typed axis. **Will be extended to loop over generic `sweeps:` after the typed axes apply.**
- Found: `digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py:186` — `_set_nested(d, 'a.b.c', value)` helper proven for OrcaWave. **Logic to port; will be re-implemented to re-validate through Pydantic (not raw dict mutation).**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py:362-488` — `CampaignGenerator` with `.preview()` and `.generate(output_dir, force, resume)`. **Will gain a `spec_only: bool=False` path that emits per-combo `spec.yml` only.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/cli.py:293-358` — `cmd_campaign` CLI. **Will gain `--spec-only` flag.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/root.py:21-80` — `ProjectInputSpec` root. **Dotted-path sweep values must round-trip-validate against this model.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py:19-45` — `EnvironmentVariation`, `SoilVariation` structured override blocks. **Conflict surface: dotted sweep targeting `environment.*` must be detectable and warned.**
- Gap: No `ParameterSweep` Pydantic model exists today. Gap: no generic dotted-path applier in the OrcaFlex schema package. Gap: no spec-only emission mode on `CampaignGenerator`.

### Standards

Not applicable — no external standard (DNV/API) governs parametric sweep spec schemas. Internal conventions only (Pydantic v2, `model_copy(deep=True)`, YAML-first IO).

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/workflows/parametric-engineering-reports.md:1-75` — established pattern is "N spec.yml files → solver queue runs of 100-680 cases". This confirms the target output format is **per-combo directory with a single `spec.yml`**, not a single multi-document manifest. No wiki entry exists for "design of experiments" / "Latin hypercube".

### Documents consulted

- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md:242-266` — OrcaWave sibling #1596 produced `solvers/parametric_spec_generator.py` with dataclass sweeps (`FrequencySweep`, `HeadingSweep`, `HullParameterSweep`) and dotted-path UX identical to #511's requested shape.
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md:48-53` — `parametric_hull_analysis/sweep.py` is an execution sweep, NOT a spec-generator. Name collision noted for the plan's terminology section.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md:51` — batch-design spec mislabels #511 as greenfield; this plan corrects that framing.
- Related issue #1596 — sibling OrcaWave parametric generator; terminology source for the `ParameterSweep` shape.
- `docs/plans/_template-issue-plan.md` — template structure followed here.

### Gaps identified

- No `ParameterSweep` Pydantic model exists (dotted `parameter: str`, `values: list[Any]`, optional `alias: str`).
- No generic dotted-path applier that re-validates through Pydantic.
- No spec-only emission mode on `CampaignGenerator`.
- No sweep-parameter resolver (walks `ProjectInputSpec` by dotted path to verify the target field exists before generation begins).
- No combinatorial-explosion preflight warning (issue example already yields 4 × 5 × 3 = 60 combos from three dotted sweeps alone).
- LHS (`latin_hypercube`) and OAAT (`one_at_a_time`) combination modes have no prior art in the repo. Full-factorial is the only mode backed by existing code.

### Evidence (embedded verification)

**Issue status** (intel snapshot 2026-04-24):
- `#511` — OPEN — "OrcaFlex: campaign spec generation — parametric sweep from spec.yml" (labels: enhancement)
- `#1596` — referenced as sibling (OrcaWave parametric generator) — precedent for dotted-path UX

**File existence** (from pod Explorer intel, 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/root.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/cli.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/schema/test_campaign.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_campaign_generator.py`
- EXISTS: `digitalmodel/tests/solver/test_parametric_spec_generator.py`
- MISSING (new — this plan creates): no new top-level modules are required; all changes are in existing files.

**Line excerpts (verbatim from Explorer intel):**
- `CampaignMatrix.combinations()` at `schema/campaign.py:67-114` — typed-axis `itertools.product`.
- `CampaignSpec.generate_run_specs()` at `schema/campaign.py:117-295` — streaming `model_copy(deep=True)` + `_apply_overrides`.
- `_apply_overrides` at `schema/campaign.py:298-348` — hand-coded per typed axis.
- `_set_nested` at `parametric_spec_generator.py:186` — dotted-path dict mutation (to be re-implemented as Pydantic-aware setter).

**Gap proofs (from intel):**
- No `ParameterSweep` class anywhere in `digitalmodel/src/digitalmodel/solvers/orcaflex/` — intel walked `schema/` and none listed.
- No `latin_hypercube` / `lhs` / `qmc` import in repo — LHS would require new dep (`scipy.stats.qmc` or `pyDOE2`) — intel confirms no prior art.
- `knowledge/wikis/` has no page for "design of experiments" or parametric sampling — intel grep yielded nothing.

**Source count: 5** (issue body + 4 distinct file/doc sources) — meets template minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md` |
| Schema extension | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py` (modify) |
| Generic dotted applier helper | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/_overrides.py` (new, small; or inline into `campaign.py`) |
| Generator spec-only path | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py` (modify `CampaignGenerator.generate`) or a new `generate_specs_only()` method |
| CLI flag | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/cli.py` (modify `cmd_campaign`) |
| Schema unit tests | `digitalmodel/tests/solvers/orcaflex/modular_generator/schema/test_campaign.py` (extend) |
| Generator unit tests | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_campaign_generator.py` (extend) |
| Integration test | `digitalmodel/tests/solvers/orcaflex/modular_generator/integration/test_campaign_integration.py` (extend) |
| Plan review — Claude | `scripts/review/results/2026-04-24-plan-511-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-24-plan-511-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-24-plan-511-gemini.md` |
| Docs updates | `docs/plans/README.md` (add this plan to index) |

---

## Deliverable

A generic dotted-path `sweeps:` axis on the existing `CampaignMatrix`, plus a `spec-only` emission mode on `CampaignGenerator`, so a user can write a `campaign_spec.yml` that declares `base: <ProjectInputSpec>` + `sweeps: [{parameter: <dotted>, values: [...]}, ...]` and obtain N per-combo `spec.yml` files without generating full OrcaFlex run directories. OUT OF SCOPE: running the generated specs against licensed OrcaFlex.

---

## Pseudocode

```
class ParameterSweep(BaseModel):           # NEW
    parameter: str                          # dotted path, e.g. "environment.waves.height"
    values: list[Any]                       # non-empty
    alias: Optional[str] = None             # short name for output_naming placeholder

    @field_validator("parameter"):
        must be non-empty, must not contain leading/trailing dots
    @field_validator("values"):
        must be non-empty

# Extend existing CampaignMatrix (reuse — do not replace)
class CampaignMatrix(BaseModel):
    # existing typed axes unchanged: water_depths, route_lengths, tensions, environments, soils
    sweeps: list[ParameterSweep] = []       # NEW — default empty preserves backward compat
    combination: Literal["full_factorial"] = "full_factorial"  # start scoped; see TRADEOFF

    def combinations(self) -> Iterator[dict]:
        # existing typed cartesian product unchanged
        typed_combos = itertools.product(self.water_depths or [None], ...)
        # NEW: cross typed × generic sweeps
        sweep_combos = itertools.product(*(s.values for s in self.sweeps))
        for typed in typed_combos:
            for sweep_vals in sweep_combos:
                yield {**typed_dict(typed), **{s.parameter: v for s, v in zip(self.sweeps, sweep_vals)}}

# NEW helper (port + improve OrcaWave's _set_nested)
def apply_dotted_override(spec: ProjectInputSpec, dotted: str, value: Any) -> ProjectInputSpec:
    # walk Pydantic model by attribute, not dict-mutation
    # use model_copy(update=..., deep=True) at each level to preserve validation
    # on final leaf: assign, then re-validate via model.model_validate(model.model_dump())
    # raise clear error if path doesn't resolve (parameter not found in schema)

# Extend existing _apply_overrides (do NOT replace)
def _apply_overrides(base, combo):
    spec = existing_typed_axis_overrides(base, combo)   # unchanged
    for sweep in matrix.sweeps:                          # NEW loop
        if sweep.parameter in combo:
            spec = apply_dotted_override(spec, sweep.parameter, combo[sweep.parameter])
    return spec

# Extend CampaignGenerator with spec-only emission path
def generate(self, output_dir, force, resume, spec_only=False):   # NEW flag
    for i, run_spec in enumerate(self.campaign.generate_run_specs()):
        run_dir = output_dir / rendered_name(i, run_spec)
        if spec_only:
            write_yaml(run_dir / "spec.yml", run_spec.model_dump())
            continue
        # existing full-run-dir generation path unchanged

# CLI
cmd_campaign: add --spec-only flag → passes through to generate(spec_only=True)

# Preflight guard
if total_combos > 100: log.warning("N combos — consider latin_hypercube or smaller sweeps")
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py` | Add `ParameterSweep`, extend `CampaignMatrix.combinations()`, extend `_apply_overrides`, add `spec_only` path to `CampaignGenerator.generate` |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/_overrides.py` | `apply_dotted_override(spec, dotted, value)` Pydantic-aware setter (or inline into `campaign.py` if small) |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/cli.py` | `--spec-only` flag on `cmd_campaign` |
| Modify | `digitalmodel/tests/solvers/orcaflex/modular_generator/schema/test_campaign.py` | Add `TestParameterSweep`, extend `TestCampaignMatrixCombinations` with dotted-sweep cases |
| Modify | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_campaign_generator.py` | Add `TestCampaignGeneratorSpecOnly`; CLI test for `--spec-only` |
| Modify | `digitalmodel/tests/solvers/orcaflex/modular_generator/integration/test_campaign_integration.py` | End-to-end: campaign.yml with two dotted sweeps → N spec.yml on disk, each validates against `ProjectInputSpec` |
| Update | `docs/plans/README.md` | Index this plan |
| Update | `knowledge/wikis/engineering/wiki/workflows/parametric-engineering-reports.md` | Add OrcaFlex dotted-sweep example alongside existing batch-YAML convention |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_parameter_sweep_empty_values_rejected` | Pydantic rejects empty `values: []` | `ParameterSweep(parameter="a.b", values=[])` | `ValidationError` |
| `test_parameter_sweep_empty_parameter_rejected` | Empty / dot-terminal dotted path rejected | `ParameterSweep(parameter="", values=[1])` | `ValidationError` |
| `test_campaign_matrix_single_sweep_only` | Sweeps-only campaign with no typed axes yields N combos | one sweep, 3 values | iterator yields 3 combos |
| `test_campaign_matrix_sweeps_crossed_with_typed_axis` | Typed × dotted cartesian correct | 2 water_depths × 3 sweep values | 6 combos |
| `test_campaign_matrix_two_sweeps_crossed` | Full-factorial across two dotted sweeps | 2 × 3 sweep values | 6 combos |
| `test_apply_dotted_override_pydantic_validates` | Type-incompatible value surfaces `ValidationError` at generation, not execution | dotted=`environment.waves.height`, value=`"not-a-float"` | `ValidationError` at generate time |
| `test_apply_dotted_override_unresolvable_path` | Unknown dotted path raises clear error with path context | dotted=`not.a.real.field` | `ValueError` citing the path |
| `test_apply_dotted_override_leaf_value_set` | Leaf scalar is set and the spec round-trips via `model_validate(model_dump())` | known valid dotted path | modified spec validates |
| `test_campaign_generator_spec_only_writes_one_yml_per_combo` | Spec-only mode produces exactly N `spec.yml` files | campaign with 4 combos | 4 files on disk, each `ProjectInputSpec`-valid |
| `test_campaign_generator_spec_only_skips_master_and_includes` | Spec-only mode does NOT write `master.yml` / `includes/` | same input | no `master.yml`, no `includes/` under run dirs |
| `test_campaign_generator_full_mode_regression` | Existing full-run-dir mode unchanged when `spec_only=False` | existing integration fixture | byte-identical to pre-change baseline |
| `test_cli_campaign_spec_only_flag` | CLI `--spec-only` propagates to generator | `cmd_campaign(... --spec-only)` | same as programmatic spec-only output |
| `test_sweep_naming_template_with_alias` | `alias:` lets `output_naming` use a short placeholder | sweep with `alias: wave_h` | run-dir names contain `wave_h{value}` |
| `test_sweep_naming_template_without_alias_slug_fallback` | Raw dotted path gets slugged for naming | sweep without alias | run-dir names slugged (e.g. `environment-waves-height-3.5`) |
| `test_preflight_warning_above_threshold` | `combinations()` count > 100 emits WARN log | campaign yielding 150 combos | log captures `WARNING` with combo count |
| `test_backward_compat_no_sweeps_field` | Existing campaign.yml without `sweeps:` still loads and generates | existing fixture `test_campaign_floating.yml` | identical runs to pre-change |
| `test_dotted_sweep_conflict_with_environment_variation_warned` | Sweep targeting `environment.*` while `environments:` axis also set emits WARN | overlapping config | log captures `WARNING` on overlap |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/modular_generator/ -v`
- [ ] No regression: `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/ -q` passes
- [ ] Integration test: a `campaign_spec.yml` with two dotted sweeps (e.g. `environment.waves.height` × `environment.waves.direction`) produces exactly `len(h) * len(d)` `spec.yml` files, each of which loads back as a valid `ProjectInputSpec`.
- [ ] Backward compat: all existing `campaign.yml` fixtures (no `sweeps:` key) still produce byte-identical run directories.
- [ ] Type-safety: setting a dotted value of the wrong type raises `ValidationError` at generate time, not at downstream OrcaFlex ingestion.
- [ ] CLI: `uv run --project digitalmodel python -m digitalmodel.solvers.orcaflex.modular_generator.cli campaign --spec-only <campaign_spec.yml> -o <out>` emits only per-combo `spec.yml` files (no `master.yml`, no `includes/`).
- [ ] Docs: `docs/plans/README.md` lists this plan; `knowledge/wikis/engineering/wiki/workflows/parametric-engineering-reports.md` references OrcaFlex dotted-sweep example.
- [ ] Review artifacts posted to `scripts/review/results/`.
- [ ] Scope boundary respected: no changes that execute OrcaFlex or post-process results.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | TBD |
| Codex | TBD | TBD |
| Gemini | TBD | TBD |

**Overall result:** TBD

Revisions made based on review:
- (to be filled after adversarial review)

---

## Risks and Open Questions

- **[TRADEOFF FOR USER] Sweep dimensionality / combination mode.** Options:
  - **(A) Full-factorial only** (MVP) — reuses existing `itertools.product`; zero new deps; matches issue example; defers `latin_hypercube` + `one_at_a_time` to a follow-up issue. **Recommended for this issue.**
  - **(B) Full-factorial + one-at-a-time** — adds a "baseline + single-axis perturbation" mode. Requires a `baseline:` concept on `CampaignMatrix` that does not exist today. Small schema change; no new deps.
  - **(C) Full-factorial + LHS + OAAT** — issue body lists all three. LHS requires `scipy.stats.qmc` (already in most environments) or `pyDOE2` (new dep), plus a `seed:` field for test determinism. Materially larger surface; recommend as follow-up.
  - **Also: scalar grid syntax** (`start/end/steps`) vs. explicit `values: [...]`. Issue body shows `values:` only. Recommend deferring `start/end/steps` shorthand.

- **[TRADEOFF FOR USER] Output format / manifest.** Options:
  - **(A) Per-combo directory `{output}/run_000/spec.yml`** — matches existing `CampaignGenerator.generate()` layout, aligns with `parametric-engineering-reports.md` convention, and is directly consumable by the solver queue. **Recommended.**
  - **(B) Single multi-document `campaign_runs.yml`** — smaller filesystem footprint but breaks the "one spec.yml per run dir" solver-queue contract.
  - **(C) Per-combo `spec.yml` + a top-level `manifest.yml`** — (A) plus an index file listing every run dir + its parameter combo for traceability. Small delta over (A); worth including as a free addition.
  - Recommended: ship (A) and add (C)'s manifest as a cheap extra.

- **[TRADEOFF FOR USER] Coexistence with typed axes.** `CampaignMatrix` already has `water_depths`, `tensions`, `environments`, `soils`. A dotted sweep on `environment.waves.height` could overlap with an `environments: [EnvironmentVariation(...)]` axis.
  - **(A)** Permit both; emit WARN on detected overlap; dotted applied after typed (dotted wins). **Recommended — lowest breakage.**
  - **(B)** Error on overlap.
  - **(C)** Force users to pick one axis system per campaign.

- **Risk — dotted-path type coercion.** `_set_nested` in the OrcaWave generator mutates a raw dict without re-validating. Porting that naively would let type errors silently reach OrcaFlex. Mitigation: `apply_dotted_override` must walk the Pydantic tree and re-validate via `model_validate(model_dump())` after each leaf assignment. Covered by `test_apply_dotted_override_pydantic_validates`.

- **Risk — combinatorial explosion.** Issue example yields 4 × 5 × 3 = 60 combos from three dotted sweeps. Nothing prevents 10 × 10 × 10 = 1000. Mitigation: preserve existing `CampaignSpec.max_runs` guardrail and add WARN log above a threshold (e.g. 100). Covered by `test_preflight_warning_above_threshold`.

- **Risk — output-naming placeholder compatibility.** Existing templates use `{water_depth}`, `{environment}`, etc. Dotted paths like `environment.waves.height` are invalid `{placeholder}` names. Mitigation: require `alias:` on `ParameterSweep` when the template references the sweep; otherwise slug the dotted path (e.g. `environment-waves-height-3.5`). Covered by two naming tests.

- **Risk — OrcaWave / OrcaFlex sibling drift.** This plan extends the OrcaFlex `CampaignSpec` but does NOT converge the OrcaWave `ParametricSpecGenerator` (dataclass-based). That convergence is a separate refactor (T3-scale) and is deferred to a follow-up issue. Note in plan; do not attempt here.

- **Risk — past-tense artifact-claim trap.** `CampaignSpec`/`CampaignMatrix`/`CampaignGenerator` already exist; `ParameterSweep` and the generic applier do not. This plan uses future tense only for the new work and explicitly marks existing surface as "reuse unchanged". Per `feedback_plan_past_tense_artifact_claims`.

- **Open:** Should `ParameterSweep` support non-scalar values (e.g. a nested dict for `current:`)? Issue body only shows scalars. Default to scalar-only for this issue; flag for user during approval.

- **Open:** Should the spec-only emission also write a top-level `manifest.yml` linking each `run_XXX/spec.yml` to its parameter combo? Covered in the output-format tradeoff above — recommended yes.

- **Open:** Should `combination` literal be defined now as `Literal["full_factorial"]` (MVP, extensible later) or `Literal["full_factorial", "latin_hypercube", "one_at_a_time"]` with the latter two raising `NotImplementedError`? The former is cleaner; the latter is friendlier to future callers. Flag for user.

---

## Complexity: T2

**T2** — extension of an existing multi-file Pydantic schema surface with a new axis type and a new emission mode. The core cartesian-product + `model_copy(deep=True)` machinery already exists; the dotted-path applier pattern already exists on the OrcaWave side. New work is bounded: one new Pydantic model, one new helper function, one new flag on `CampaignGenerator.generate`, one new CLI flag, and ~12-15 new tests. Full TDD required; two existing files modified in `src/`; no new top-level modules.

Downgrade to **T1** possible if LHS / OAAT are explicitly deferred (plan already recommends this). Upgrade to **T3** would apply only if the plan also converged OrcaWave's `ParametricSpecGenerator` into this surface — explicitly out of scope here.
