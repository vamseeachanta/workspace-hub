# Plan for #2515: Generate offshore cable umbilical pipeline cross-section reports

> **Status:** plan-review-ready
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2515
> **Review artifacts:** `scripts/review/results/2026-04-27-plan-2515-claude.md` | `scripts/review/results/2026-04-27-plan-2515-codex.md` | `scripts/review/results/2026-04-27-plan-2515-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/subsea/cross_sections/` on `digitalmodel` `origin/main` after #2514. It exports `CrossSectionDefinition`, `RadialLayer`, `PackedComponent`, `Provenance`, `UnitValue`, `ValidationReport`, `validate_cross_section`, `load_cross_section_fixture`, and `dump_cross_section_fixture`.
- Found fixtures in `digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/`: `66kv_inter_array_cable.yml`, `220kv_hvac_export_cable.yml`, `steel_tube_electro_hydraulic_umbilical.yml`, `power_optical_hybrid_umbilical.yml`, and `concrete_coated_pipeline.yml`. These are the authoritative first-pass inputs for this report; do not invent new dimensions in this issue.
- Found tests in `digitalmodel/tests/subsea/cross_sections/`: schema/validation/fixture tests from #2514. New report tests should be additive under `digitalmodel/tests/subsea/cross_sections/test_reporting.py` and should not mutate the schema package behavior.
- Found existing reporting/visualization patterns:
  - `digitalmodel/src/digitalmodel/structural/pipe_cross_section/visualization.py` generates HTML and simple cross-section visuals, but it is pipe-specific and tied to `PipeCrossSection`/`PipeLayer` models.
  - `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_interactive_report.py` shows interactive Plotly report assembly patterns, but #2515 v1 must remain deterministic and browser-free for tests.
  - `digitalmodel/src/digitalmodel/structural/pipe_cross_section/cli.py` demonstrates CLI output flags; #2515 should add one explicit local CLI module rather than leaving entrypoint choice open.
- Gap: no existing `digitalmodel.subsea.cross_sections.reporting` module, report generator, cross-family comparison table, provenance table renderer, or deterministic visual renderer for the #2514 fixtures.

### Standards and source constraints

| Source / constraint | Status | Finding |
|---|---|---|
| #2514 schema implementation | done | Reporting must consume the landed schema/fixtures rather than duplicating parsing or validation logic. Implementation must verify the actual `digitalmodel` worktree contains #2514 before coding. |
| #2513 source catalogue | open follow-up | #2515 may use fixture-level provenance from #2514; it must not claim catalogue completeness or vendor design defaults. |
| #2516 flexible mechanics | open follow-up | #2515 may mention flexible pipe/riser scope as deferred text, but must not implement flexible-pipe mechanics or dynamic riser models. |
| DNV-ST-F101 / pipeline registries | indexed | Useful as provenance/caveat anchors for rigid pipeline terminology, but detailed code-check/reporting remains out of scope. |

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/concepts/subsea-cable-umbilical-cross-sections.md` — taxonomy and family/layer vocabulary for offshore wind cables, O&G umbilicals, rigid pipelines, and deferred flexible pipe mechanics.
- `knowledge/wikis/marine-engineering/wiki/comparisons/offshore-wind-oil-gas-cross-section-assessment.md` — prioritizes table/report needs: layer/component schema, representative examples, provenance, and caveats.
- `knowledge/wikis/marine-engineering/wiki/sources/offshore-cable-umbilical-cross-section-recon-2026-04-26.md` — source-backed reconnaissance; report provenance must link claims back to source IDs/URLs/paths rather than unsupported text.

### Documents and issues consulted

- Issue #2515 — asks for generated Markdown/HTML report comparing offshore wind cable, umbilical, rigid pipeline, and flexible-pipe/riser families. Because #2514 excludes flexible-pipe mechanics, this plan treats flexible pipe as a caveated/deferred comparison note, not a generated fixture visual.
- Issue #2514 — closed/status:done; implementation landed in `vamseeachanta/digitalmodel` commit `e1274b788a18` with cross-section schema, fixtures, validation, and package-data tests.
- Issue #2516 — owns flexible pipe and dynamic riser cross-section mechanics follow-up; #2515 must not absorb that mechanics scope.
- Existing `docs/plans/2026-04-27-issue-2514-subsea-cross-section-schema.md` — upstream schema plan and scope boundary.

### Evidence

**Issue statuses** verified 2026-04-27T09:42:40Z:
- `#2514` — CLOSED, labels include `status:done`; comment records `digitalmodel` commit `e1274b788a18` and `28 passed` for `tests/subsea/cross_sections`.
- `#2515` — OPEN, labels include `enhancement`, `priority:medium`, `cat:engineering`, `domain:pipeline`, `domain:marine`; no status label before this planning pass.
- `#2516` — OPEN follow-up for flexible pipe and dynamic riser mechanics.

**File existence / upstream dependency proof**:

```text
git -C digitalmodel ls-tree -r --name-only origin/main -- src/digitalmodel/subsea/cross_sections tests/subsea/cross_sections
→ src/digitalmodel/subsea/cross_sections/{__init__.py,io.py,schema.py,validation.py,fixtures/*.yml}
→ tests/subsea/cross_sections/{test_fixtures.py,test_schema.py,test_validation.py}
```

**Public API excerpt**:

```text
src/digitalmodel/subsea/cross_sections/__init__.py exports:
CrossSectionDefinition, RadialLayer, PackedComponent, Provenance, UnitValue,
ValidationIssue, ValidationReport, validate_cross_section,
load_cross_section_fixture, dump_cross_section_fixture
```

### Gaps identified

- Build deterministic report data extraction from `CrossSectionDefinition` fixtures.
- Build deterministic Markdown and HTML renderers for cross-family comparison tables, provenance/caveats, and per-fixture visuals.
- Build simple cross-section visuals for radial-layer fixtures and packed-component fixtures without solving packing layout optimization.
- Add report-generation tests that assert required sections, fixture coverage, provenance, units, caveats, and visual anchors.
- Add one explicit CLI module so the report can be regenerated, not hand-edited.

---

## Pre-Implementation Prerequisite Gate

Before writing any #2515 tests or implementation in `digitalmodel`, the executor must run this gate in the actual implementation worktree:

```bash
git fetch origin main
git merge-base --is-ancestor e1274b788a18396908e25674c56b74e69dbd3067 origin/main
test -f src/digitalmodel/subsea/cross_sections/schema.py
test -f src/digitalmodel/subsea/cross_sections/fixtures/66kv_inter_array_cable.yml
PYTHONPATH=src ./.venv/bin/python -m pytest tests/subsea/cross_sections -q
```

If #2514 files are missing or the tests fail for dependency reasons, stop and post a blocker/update rather than backfilling #2514 inside #2515. Use a clean `digitalmodel` worktree from `origin/main`; do not implement from a stale local feature branch.

---

## Deterministic Output Contract

#2515 implementation must lock these rules before rendering any artifact:

- Fixture order: stable sorted order by `(family, id)` after loading, not filesystem traversal order.
- Layer order: preserve schema order for radial layers; visual rendering must use inner-to-outer order from the fixture.
- Component order: stable sorted order by `(component_type, service_role, name)` for packed-component schematics unless fixture order is explicitly required; document the choice in code.
- Provenance order: stable sorted order by `(source_id, source_type, citation or "", url_or_path or "")`, de-duplicated by full record content.
- Caveat order: fixed constant order: cable duty, umbilical schematic, pipeline route/coating, flexible-pipe deferred.
- Numeric formatting: one helper controls float rendering, with fixed precision and trimmed trailing zeros where specified; tests cover representative `mm`, `kV`, `bar/MPa`, and density values.
- SVG/HTML IDs: deterministic slug IDs derived from fixture IDs; no random UUIDs.
- Generated metadata: no timestamps, absolute machine paths, Python versions, or host-specific strings in committed generated artifacts.
- HTML policy: self-contained HTML with inline CSS/SVG and no external network assets.
- Markdown policy: inline SVG or deterministic fenced HTML blocks only; no linked generated assets in v1.

---

## Report Output Contract

### Committed/generated artifacts

Implementation must produce and commit both generated artifacts from the same report model:

- `digitalmodel/docs/subsea/cross_sections/offshore_cross_section_report.md`
- `digitalmodel/docs/subsea/cross_sections/offshore_cross_section_report.html`

No JSON summary is required in v1; removing JSON avoids expanding the contract surface. If a future implementation wants machine-readable summaries, create a follow-up issue.

### Required Markdown/HTML sections

Both formats must contain the same fixture IDs and section content:

1. `Offshore Cable, Umbilical, and Pipeline Cross-Section Report`
2. `Regeneration`
3. `Fixture Inventory`
4. `Cross-Family Comparison`
5. `Cross-Section Visuals`
6. `Provenance`
7. `Engineering Caveats`
8. `Deferred Scope and Follow-Ups`

### Required comparison-table columns

Use a curated, non-misleading table rather than a huge sparse schema dump:

| Column | Source |
|---|---|
| Fixture ID | `CrossSectionDefinition.id` |
| Name | `CrossSectionDefinition.name` |
| Family | `family` |
| Duty | `design_metadata.duty` if available |
| Overall OD / envelope | explicit outer diameter where available; otherwise `not specified` |
| Radial layer count | `len(radial_layers)` |
| Packed component count | `len(packed_components)` |
| Key ratings | voltage/pressure/temperature fields where present; otherwise `not specified` |
| Primary source IDs | de-duplicated source IDs |
| Caveat tags | derived deterministic caveat tags |

Do not compute or claim derived mechanical capacities, weights, bending stiffness, thermal ratings, or fatigue properties in #2515.

### CLI contract

Implementation must create `digitalmodel/src/digitalmodel/subsea/cross_sections/cli.py` with a module entrypoint:

```bash
PYTHONPATH=src ./.venv/bin/python -m digitalmodel.subsea.cross_sections.cli \
  --output-dir docs/subsea/cross_sections \
  --format all
```

Required behavior:
- `--format md|html|all`, default `all`.
- `--output-dir PATH`, default `docs/subsea/cross_sections`.
- Exit code `0` on success; non-zero on validation/report-generation failure.
- Failure must not leave partial output files; write to temporary files and atomically replace on success.
- stdout lists generated relative paths; stderr contains validation errors on failure.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2515-cross-section-reporting-demo.md` |
| Plan index row | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-04-27-plan-2515-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-27-plan-2515-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-27-plan-2515-gemini.md` |
| Plan review synthesis | `scripts/review/results/2026-04-27-plan-2515-disagreement.md` |
| Reporting implementation | `digitalmodel/src/digitalmodel/subsea/cross_sections/reporting.py` |
| Visual rendering implementation | `digitalmodel/src/digitalmodel/subsea/cross_sections/visualization.py` |
| CLI entrypoint | `digitalmodel/src/digitalmodel/subsea/cross_sections/cli.py` |
| Public exports | `digitalmodel/src/digitalmodel/subsea/cross_sections/__init__.py` |
| Tests | `digitalmodel/tests/subsea/cross_sections/test_reporting.py` |
| Generated Markdown report | `digitalmodel/docs/subsea/cross_sections/offshore_cross_section_report.md` |
| Generated HTML report | `digitalmodel/docs/subsea/cross_sections/offshore_cross_section_report.html` |

---

## Deliverable

A deterministic `digitalmodel.subsea.cross_sections` reporting/demo workflow that regenerates Markdown and self-contained HTML comparison reports and simple visuals from the #2514 fixtures, including units, provenance, caveats, and tests/snapshot checks.

---

## Scope Boundaries

### In scope

- Consume existing #2514 fixture YAML files through `load_cross_section_fixture()`.
- Generate a curated comparison table across all available fixture families.
- Generate a provenance table using `Provenance.source_id`, `source_type`, `citation`, `url_or_path`, `note`, and `derived_from` fields.
- Generate deterministic visuals:
  - radial layer annulus-style SVG/HTML for cable and pipeline fixtures with radial layers;
  - packed-component schematic SVG/HTML for umbilical fixtures with components, clearly marked schematic/not-to-scale when exact packing coordinates are unavailable.
- Emit Markdown and HTML from one report model so content does not drift.
- Add required caveats: static vs dynamic cable duty, customer-specific umbilical packing, route-specific concrete coating design, and flexible pipe/riser mechanics deferred to #2516.
- Add tests/snapshot checks for required sections, fixture coverage, provenance, units, caveats, visual markers, determinism, CLI behavior, and regeneration-clean behavior.

### Out of scope

- Full flexible pipe mechanics, carcass/pressure armor/tensile armor calculations, dynamic riser stress/fatigue, or packing optimization; #2516 owns these.
- OrcaFlex export, production client-report styling, interactive Plotly dashboards, GTM website integration, or machine-readable JSON summaries.
- Adding new vendor dimensions or declaring design defaults beyond the landed fixtures and their provenance.
- Refactoring existing `digitalmodel.structural.pipe_cross_section` modules.

---

## Pseudocode

```text
function load_default_cross_section_fixtures(fixtures_dir=None):
    resolve fixtures_dir to package fixture directory unless explicitly provided
    iterate *.yml but sort loaded definitions by (family, id)
    load each fixture via load_cross_section_fixture(path)
    return list[CrossSectionDefinition]
```

```text
function build_report_model(definitions):
    validate each definition with validate_cross_section
    if any invalid, collect validation report and raise ReportGenerationError
    for each definition in deterministic order:
        extract comparison row using the locked table columns
        collect provenance records from definition, layers, components, and metadata
        de-duplicate and sort provenance rows by Deterministic Output Contract
        derive caveat tags in fixed caveat order
        render or prepare visual model using family/geometry type
    return CrossSectionReportModel(definitions, comparison_rows, provenance_rows, caveats, visuals)
```

```text
function render_radial_layers_svg(definition):
    for each radial layer in fixture order:
        use derived ID/OD from schema; schema validates length units
        map OD to deterministic radius scale
        render concentric annulus/circle elements with deterministic colors and slug IDs
        include concise layer legend/caption with name, role, material, dimensions, units, source IDs
    return SVG string with normalized whitespace and numeric formatting
```

```text
function render_packed_components_svg(definition):
    create schematic bundle outline using overall diameter when available, otherwise schematic bounding circle
    place components in deterministic sorted order on a simple fixed ring/grid layout
    do not optimize packing, detect collisions, or imply manufacturing layout
    add explicit text: schematic only / not to scale / not packing optimization
    include component counts, service roles, ratings, and source IDs in caption/legend
    return SVG string with normalized whitespace and numeric formatting
```

```text
function render_markdown_report(model):
    emit required sections in locked order
    render comparison/provenance tables with deterministic formatting
    embed inline SVG/fenced HTML blocks for visuals
    include regeneration command and caveats/follow-up text
    return markdown string
```

```text
function render_html_report(model):
    reuse same model rows and SVG strings as Markdown renderer
    emit self-contained HTML with inline CSS and no network assets
    include same section IDs and fixture IDs as Markdown
    return html string
```

```text
function cli_main(argv):
    parse --output-dir and --format
    generate requested artifacts into temp files
    on success atomically replace final report files and print relative paths
    on failure remove temp files, print validation/report errors to stderr, return non-zero
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/subsea/cross_sections/reporting.py` | Report model, comparison/provenance rows, Markdown/HTML rendering, generation function |
| Create | `digitalmodel/src/digitalmodel/subsea/cross_sections/visualization.py` | Deterministic SVG/HTML visual helpers for radial and packed-component fixtures |
| Create | `digitalmodel/src/digitalmodel/subsea/cross_sections/cli.py` | Regeneration entrypoint with output directory and format flags |
| Modify | `digitalmodel/src/digitalmodel/subsea/cross_sections/__init__.py` | Export stable report-generation API only after tests define it |
| Create | `digitalmodel/tests/subsea/cross_sections/test_reporting.py` | TDD test suite for report model, required sections, provenance, caveats, visuals, determinism, and CLI |
| Create | `digitalmodel/docs/subsea/cross_sections/offshore_cross_section_report.md` | Checked-in generated demo Markdown artifact |
| Create | `digitalmodel/docs/subsea/cross_sections/offshore_cross_section_report.html` | Checked-in generated self-contained HTML artifact |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_prerequisite_fixtures_available_on_implementation_branch` | implementation checkout has #2514 package/fixtures | actual worktree | required files exist and #2514 tests pass before #2515 code |
| `test_load_default_report_fixtures_covers_all_landed_fixtures` | fixture inventory includes all five #2514 fixtures | default fixture directory | IDs/families for 66 kV cable, 220 kV export cable, steel-tube umbilical, power/optical umbilical, concrete-coated pipeline |
| `test_build_report_model_contains_locked_comparison_columns` | report model uses curated table contract | loaded fixtures | one comparison row per fixture with locked columns and no derived mechanical capacity fields |
| `test_provenance_rows_are_deduplicated_and_stably_sorted` | provenance is deterministic and linked | loaded fixtures | sorted unique provenance rows with source IDs and references |
| `test_markdown_report_contains_required_sections_and_caveats` | Markdown has issue-required sections and caveats | report model | all required headings and caveat text including #2516 deferred note |
| `test_html_report_is_self_contained_and_has_visuals_for_each_fixture` | HTML has inline SVG/HTML visuals and no external assets | report model | one visual container per fixture, `<svg` present, no external network dependency |
| `test_markdown_and_html_share_fixture_ids_and_sections` | no drift between formats | report model | both formats contain identical required section IDs and fixture IDs |
| `test_radial_visual_preserves_layer_order_units_and_source_ids` | radial visual uses inner-to-outer layer order and unit labels | radial-layer fixture | SVG/legend includes layer names, OD/thickness values, units, source IDs |
| `test_packed_component_visual_is_schematic_not_to_scale` | umbilical visual does not overclaim exact packing | packed-component fixture | contains `schematic`, `not to scale`, component counts/service roles/ratings |
| `test_report_generation_is_byte_stable_across_two_runs` | deterministic output | same fixtures, temp output dirs | Markdown/HTML bytes match exactly across two runs |
| `test_cli_writes_requested_artifacts_and_reports_paths` | CLI success contract | temp output dir, `--format all` | exit 0, writes `.md` and `.html`, stdout lists relative paths |
| `test_cli_failure_leaves_no_partial_artifacts` | invalid input fails safely | invalid fixture dir or monkeypatched invalid loader | non-zero exit, stderr errors, no final partial report files |
| `test_generated_artifacts_match_regenerated_output` | committed docs are not stale | run generator to temp output | generated bytes match committed Markdown/HTML artifacts |
| `test_report_escapes_markup_sensitive_provenance_text` | generated HTML/Markdown cannot be broken by source strings | artificial definition/provenance with `<`, `&`, quotes | escaped output; no raw unsafe HTML from data fields |

---

## Acceptance Criteria

- [ ] Pre-implementation prerequisite gate confirms #2514 package/fixtures are present in the actual `digitalmodel` implementation worktree; otherwise #2515 stops as blocked instead of backfilling #2514.
- [ ] Report generation consumes #2514 fixtures via `load_cross_section_fixture()`; no duplicated parser or hand-edited table source of truth.
- [ ] Generated report includes the five landed #2514 fixtures.
- [ ] Markdown and HTML outputs contain the locked required sections, fixture inventory, curated comparison table, per-fixture visual section, provenance table, engineering caveats, and follow-up/deferred-scope section.
- [ ] Every numeric/example claim in generated tables/visual captions carries units and source/provenance linkage.
- [ ] Visuals are deterministic and testable without a browser; HTML is self-contained and has no external network assets.
- [ ] Umbilical packed-component visuals are explicitly schematic/not-to-scale and avoid packing optimization or collision-solving scope.
- [ ] Flexible-pipe/riser mechanics are not implemented; report clearly defers them to #2516.
- [ ] CLI contract is implemented by `python -m digitalmodel.subsea.cross_sections.cli --output-dir docs/subsea/cross_sections --format all`.
- [ ] Tests run from `digitalmodel/` and pass: `PYTHONPATH=src ./.venv/bin/python -m pytest tests/subsea/cross_sections/test_reporting.py -q` or, in an isolated worktree, `PYTHONPATH=src /mnt/local-analysis/workspace-hub/digitalmodel/.venv/bin/python -m pytest tests/subsea/cross_sections/test_reporting.py -q`.
- [ ] Nearby regression passes: `PYTHONPATH=src ./.venv/bin/python -m pytest tests/subsea/cross_sections -q`.
- [ ] Regeneration check proves committed Markdown/HTML artifacts match generator output.
- [ ] `git diff --check` passes for owned digitalmodel paths.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Needed prerequisite gate for #2514 availability, deterministic ordering/format contract, resolved artifact policy, concrete CLI, installed/source fixture access checks, and regeneration-clean tests. |
| Codex | MAJOR | Needed concrete report schema/output contract, deterministic SVG/HTML formatting rules, CLI failure behavior, committed artifact policy, mixed-family comparison columns, and no optional JSON scope. |
| Gemini | APPROVE | Supported deterministic browser-free SVG direction and scope boundaries; requested cross-platform formatting stability and guardrails against packed-component layout scope creep. |

**Overall result:** PASS after revision; ready for approval gate.

Revisions made based on review:
- Added explicit pre-implementation prerequisite gate verifying #2514 is present in the actual `digitalmodel` implementation worktree.
- Added deterministic output contract for ordering, numeric formatting, IDs, metadata, HTML/Markdown policy, and no external assets.
- Added report output contract: committed Markdown and HTML only; removed optional JSON summary from v1.
- Fixed CLI choice to `digitalmodel.subsea.cross_sections.cli` with exact command, flags, exit codes, stdout/stderr, and no-partial-output behavior.
- Added curated comparison-table columns to avoid sparse/misleading cross-family schema dumps.
- Added TDD cases for determinism, CLI behavior, markup escaping, regeneration-clean artifacts, and Markdown/HTML parity.
- Preserved #2516 boundary and explicitly forbade packing optimization/collision-solving scope.

---

## Risks and Open Questions

- **Risk: Visual overclaiming.** Packed-component umbilical visuals can imply exact manufacturing layout. Mitigation: label as schematic/not-to-scale and avoid layout optimization/collision-solving.
- **Risk: Provenance loss.** A report renderer could summarize values without source IDs. Mitigation: report model requires provenance rows and tests assert source IDs appear in tables/captions.
- **Risk: Artifact churn.** Generated docs can drift from code. Mitigation: deterministic output contract plus regeneration-clean test.
- **Risk: Dependency drift.** Plotly/matplotlib could create brittle artifacts. Mitigation: v1 uses deterministic inline SVG/string rendering; interactive dashboards can be a future issue.
- **Risk: Scope creep into #2516.** Flexible-pipe/riser mechanics are deferred; #2515 includes text-only caveat but no mechanics model.
- **Open: Installed-mode fixture access.** #2514 already tested package data; #2515 should add only a report-level smoke test if needed, not rework packaging.

---

## Follow-up Issues

- Existing #2516 remains the flexible pipe and dynamic riser mechanics follow-up.
- Candidate future issue after #2515: interactive Plotly/GTM-grade dashboard or website demo integration after deterministic Markdown/HTML generation is landed and tested.
- Candidate future issue after #2515: richer packed-component layout/coordinate model if exact coordinates or bundle-envelope metadata are later added.

---

## Complexity: T2

**T2** — bounded additive reporting/visualization workflow on top of the already-landed #2514 schema, with new tests and generated artifacts. It remains T2 because no schema redesign, mechanics solver, OrcaFlex integration, or multi-agent workstream split is required.
