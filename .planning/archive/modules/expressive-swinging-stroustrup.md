# WRK-1242 Fix: Align Section Schemas with Renderer Contract

## Context

Codex cross-review (hard gate) returned REQUEST_CHANGES on WRK-1242. The 16 calculation methodology section reference files define YAML schemas incompatible with the actual `calculation-report` renderer (`scripts/reporting/generate-calc-report.py` + `calc_report_html.py`). An agent following these section guides would produce YAML that fails validation or silently drops content.

## Approach

Update the **Schema Fields** and **Example Snippet** sections in each of the 16 markdown files to match the renderer contract. Preserve all methodology guidance (Purpose, Required Content, Quality Checklist, Common Mistakes). Add a "Renderer Mapping Note" where the methodology documents richer concepts than the renderer supports.

## Changes Per File

All files in `.claude/skills/engineering/calculation-methodology/sections/`:

| File | Severity | Key Changes |
|------|----------|-------------|
| 01-metadata.md | moderate | `doc_number`→`doc_id`, `authors[]`→`author`(scalar), `revision_history`→`change_log`, status enum fix |
| 02-scope.md | minor | `limitations` list→string, `validity_range` nested→scalar |
| 03-design-basis.md | significant | `codes[].standard`→`.code`, remove `.title/.role`, `load_combinations` dicts→strings, `design_life` nested→scalar |
| 04-materials.md | complete | Replace nested `properties/partial_factors/certificates` with flat `{name,grade,value,unit,source?,partial_factor?,certificate?}` |
| 05-inputs.md | minor | Remove `category`, `validation{min,max,note}` |
| 06-assumptions.md | complete | Structured dicts→simple list of strings |
| 07-methodology.md | significant | Remove `method_name/applicability/alternative_methods`, `.symbolic`→`.latex`, add `.name` |
| 08-calculations.md | significant | `id`→`step`, `reference`→`code_clause`, `formula+substitution`→`detail`, remove `result/hand_check` |
| 09-outputs.md | complete | Replace `summary[]` with flat `{name,symbol,value,unit,pass_fail?,limit?,notes?}` |
| 10-sensitivity.md | complete | Replace complex `parameters[]/tornado/conclusions` with flat `{parameter,range,result}` |
| 11-validation.md | complete | Replace `methods[]` with flat `{method?,test_file?,test_count?,test_categories[]?,benchmark_source?}` |
| 12-verification.md | significant | Flatten `checker{name,qual,date}` to scalar fields, `findings[]`→scalar string |
| 13-conclusions.md | significant | `adequacy_statement`→`adequacy`, `governing_checks[]`→`governing_check`(scalar), `code_compliance[]`→`compliance_statement` |
| 14-charts.md | complete | Replace `axes/series/annotations` with `x_label/y_label/datasets[]`, type enum to `line|bar|scatter|log_log` |
| 15-data-tables.md | minor | `columns[].header`→`.name`, remove `format/alignment/description/source/notes` |
| 16-references.md | complete | Categorized `normative/informative/project_documents` → simple list of strings |

## Ground Truth References

- `scripts/reporting/generate-calc-report.py` — validation constants + `load_and_validate()`
- `scripts/reporting/calc_report_html.py` — HTML builder functions with exact field access
- `examples/reporting/cp-anode-design-dnv-rp-b401.yaml` — working example
- `examples/reporting/fatigue-pipeline-girth-weld.yaml` — working example with charts

## Verification

1. Every example YAML snippet should pass `load_and_validate()` if embedded in a complete calc file
2. Every Schema Fields entry consumed by at least one renderer function
3. Cross-check against `examples/reporting/` for consistency
4. Re-run Codex cross-review to confirm APPROVE
