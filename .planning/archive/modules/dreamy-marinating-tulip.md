# WRK-1242: Calculation Methodology Skill — Implementation Plan

## Context

Engineering calculations across digitalmodel (CP, fatigue, geotechnical, subsea) are well-implemented
but lack a unified methodology skill that guides the structured analysis workflow from scope definition
through independent verification. The existing `calculation-report` skill covers YAML→HTML rendering
(step 6 of 6) but does not guide steps 1–5. Research across 10+ professional sources (EFCOG, DNV,
Structures Centre, Eng-Tips, Caltrans) identified 16 sections that distinguish best-in-class engineering
calculations from poor ones.

## Deliverables

### Phase 1: Skill + Section Reference Files (core)

**File 1: `.claude/skills/engineering/calculation-methodology/SKILL.md`** (~200 lines)

Orchestrator skill with:
- Frontmatter: name, description, version, category, triggers, related_skills, capabilities
- 6-phase workflow table (Problem Definition → Input Gathering → Method Selection → Computation → Validation → Reporting)
- Section reference table mapping each of 16 sections to its reference file
- Phase-to-section mapping (which sections get populated in which phase)
- Integration point with `calculation-report` skill (Phase 6 triggers report generation)
- Quality checklist summary (the "commonly missed" items from research)

**Files 2–17: `.claude/skills/engineering/calculation-methodology/sections/01-metadata.md` through `16-references.md`**

Each section reference file (~30–60 lines) contains:
- **Purpose**: What this section achieves
- **Schema fields**: Which YAML keys it maps to
- **Required content**: Minimum content for a passing section
- **Quality checklist**: What distinguishes good from poor (3–5 items)
- **Example snippet**: From CALC-007 or another exemplar
- **Common mistakes**: What gets missed (from research)

Section list:
```
01-metadata.md        — doc control, revision, approval workflow
02-scope.md           — objective, inclusions/exclusions, limitations, validity range
03-design-basis.md    — normative codes & editions, design life, safety class, load combinations
04-materials.md       — grades, characteristic/design values, partial factors, certificates
05-inputs.md          — parameters with symbol/value/unit/source, validation ranges
06-assumptions.md     — explicit list with justification, conservative vs best-estimate
07-methodology.md     — standard selection, applicability check, equations (symbolic before numeric)
08-calculations.md    — step-by-step with code clause refs, intermediate results, hand-checks
09-outputs.md         — results summary, pass/fail, utilization ratios, governing cases
10-sensitivity.md     — parameter sweeps, tornado charts, what-if ranges
11-validation.md      — benchmarks, method comparison, test references
12-verification.md    — independent check record, checker name/date, alternative method
13-conclusions.md     — adequacy statement, governing checks, code compliance
14-charts.md          — visualization guidance, chart type selection per data type
15-data-tables.md     — tabular data formatting, column conventions
16-references.md      — citation format, standard editions, normative vs informative separation
```

### Phase 2: Schema Update + Generator Update

**File 18: `config/reporting/calculation-report-schema.yaml`** (update existing)

Add new sections to schema:
- `scope` (new required): `required: [objective, inclusions, exclusions]`, `optional: [limitations, validity_range]`
- `design_basis` (new required): `required: [codes, design_life]`, `optional: [safety_class, load_combinations, environment]`
- `materials` (new optional): `item_required: [name, grade, value, unit]`, `item_optional: [source, partial_factor, certificate]`
- `calculations` (new optional): `item_required: [step, description]`, `item_optional: [detail, code_clause, intermediate_results]`
- `sensitivity` (new optional): `item_required: [parameter, range, result]`
- `validation` (new optional): `required: [method]`, `optional: [test_file, test_count, test_categories, benchmark_source]`
- `verification` (new optional): `required: [checker, date, method]`, `optional: [findings, status]`
- `conclusions` (new optional): `required: [adequacy, governing_check]`, `optional: [recommendations, compliance_statement]`

Backwards compatibility: all new sections are either optional or have defaults that existing files satisfy.
`scope` and `design_basis` become required for NEW reports only — add a `schema_version` field to distinguish.

**File 19: `scripts/reporting/calc_report_html.py`** (update existing)

Add builder functions:
- `build_scope_card(scope)` — objective + inclusions/exclusions list + limitations
- `build_design_basis_card(design_basis)` — codes table + design life + safety class + load combos
- `build_materials_card(materials)` — materials table with grades/values/partial factors
- `build_calculations_card(calculations)` — numbered steps with detail blocks and code clause refs
- `build_sensitivity_card(sensitivity)` — parameter sweep table
- `build_validation_card(validation)` — test summary with categories
- `build_verification_card(verification)` — checker record with findings
- `build_conclusions_card(conclusions)` — adequacy statement + governing checks

**File 20: `scripts/reporting/generate-calc-report.py`** (update existing)

- Add validation constants for new sections
- Update `load_and_validate()` to check new required/optional fields
- Update `render_markdown()` to include new sections
- Update `render_html()` to call new builder functions
- Add `schema_version` handling (v1 = current, v2 = with new sections)

### Phase 3: Gap Audit + Exemplar Upgrades

**File 21: `specs/wrk/WRK-1242/calc-report-gap-audit.yaml`**

Audit all 12 existing examples against 16-section checklist:
- Matrix: example × section → present/absent/partial
- Summary: which sections are most commonly missing
- Priority list for exemplar upgrades

**Files 22–24: Upgrade 2–3 exemplar reports** (update existing)

- `examples/reporting/spectral-fatigue-dnv-rp-c203.yaml` — already has calculations/validation; add scope, design_basis, materials, verification, conclusions
- `examples/reporting/geotechnical-pile-axial-capacity.yaml` — add scope, design_basis, materials, calculations, conclusions
- `examples/reporting/resource-estimation-monte-carlo.yaml` — add scope, design_basis, sensitivity, conclusions

### Phase 4: Tests

**File 25: `tests/reporting/test_calc_report_schema_v2.py`**

- Test new sections validate correctly
- Test backwards compatibility (v1 examples still pass)
- Test HTML generation includes new section cards
- Test each new builder function produces valid HTML

## Critical Files to Modify

| File | Action | Lines affected |
|------|--------|---------------|
| `config/reporting/calculation-report-schema.yaml` | Edit | Add ~40 lines for 8 new sections |
| `scripts/reporting/calc_report_html.py` | Edit | Add ~200 lines (8 new builder functions) |
| `scripts/reporting/generate-calc-report.py` | Edit | Add ~80 lines (validation + rendering) |
| `examples/reporting/spectral-fatigue-dnv-rp-c203.yaml` | Edit | Add ~30 lines (new sections) |
| `examples/reporting/geotechnical-pile-axial-capacity.yaml` | Edit | Add ~40 lines |
| `examples/reporting/resource-estimation-monte-carlo.yaml` | Edit | Add ~35 lines |

## Files to Create

| File | Size |
|------|------|
| `.claude/skills/engineering/calculation-methodology/SKILL.md` | ~200 lines |
| `.claude/skills/engineering/calculation-methodology/sections/01..16-*.md` | ~40 lines each (640 total) |
| `specs/wrk/WRK-1242/calc-report-gap-audit.yaml` | ~60 lines |
| `tests/reporting/test_calc_report_schema_v2.py` | ~120 lines |

## Reuse Points

- **Existing builders**: Follow exact pattern of `build_inputs_card()` / `build_outputs_card()` in `calc_report_html.py`
- **Existing schema**: Extend `calculation-report-schema.yaml` format (required/optional/item_required/item_optional)
- **Existing validation**: Reuse `load_and_validate()` pattern in `generate-calc-report.py`
- **Existing CSS**: Reuse `.card`, `.badge`, table styling from `calc_report_css.py` (no CSS changes needed)
- **Existing examples**: CALC-007 spectral fatigue already demonstrates `calculations` and `validation` sections

## Execution Order

1. Create SKILL.md + 16 section files (no dependencies)
2. Update schema (foundation for everything else)
3. Update HTML builders (depends on schema)
4. Update generator (depends on builders)
5. Run gap audit on existing 12 examples
6. Upgrade 2–3 exemplars to v2 schema
7. Write and run tests

## Verification

```bash
# Schema validation on existing examples (backwards compat)
for f in examples/reporting/*.yaml; do
  uv run --no-project python scripts/reporting/generate-calc-report.py "$f" --format html
done

# Schema validation on upgraded exemplars
uv run --no-project python scripts/reporting/generate-calc-report.py examples/reporting/spectral-fatigue-dnv-rp-c203.yaml

# Run tests
uv run --no-project python -m pytest tests/reporting/test_calc_report_schema_v2.py -v

# Visual check — open generated HTML
xdg-open examples/reporting/spectral-fatigue-dnv-rp-c203.html
```
