# Plan for #2346: Prospect-Data Customized-Demo Pipeline — 48hr Turnaround + Pre-Staged Vessel Templates

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2346
> **Review artifacts (pending):** `scripts/review/results/2026-04-19-plan-2346-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py` (1,257 lines, 680 cases) — loads via `load_pipe_catalog()` (reads `data/pipelines.json`) + `load_jumper_catalog()` (reads `data/rigid_jumpers.json`). CLI surface is `--from-cache` / `--force` only; **no CLI flag to override vessel or structure inputs** — today the parameter matrix is hard-coded at module scope (`WATER_DEPTHS`, `HS_VALUES`, etc.).
- Found: `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` (1,343 lines, 72 cases) — inline `json.load(DATA_DIR / "pipelines.json")` inside `main()`; no separate loader function. Same `--from-cache` / `--force` CLI only.
- Found: `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` (1,223 lines, 180 cases) — `load_vessels()` reads `data/csv_hlv_vessels.json`, `load_structures()` reads `data/mudmat_structures.json`. Hard-coded `WATER_DEPTHS`, `HS_VALUES` at module scope. Same CLI.
- Found: `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py` (1,642 lines, 60 cases) — `load_vessels()` reads `data/pipelay_vessels.json` (different file from demos 3/5), `load_pipes()` reads `data/pipelines.json`. Same CLI.
- Found: `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py` (1,229 lines, 300 cases) — `load_vessel_data()` reads `data/csv_hlv_vessels.json`, `load_jumper_data()` reads `data/rigid_jumpers.json`. Same CLI.
- Found: `digitalmodel/examples/demos/gtm/report_template.py` (620 lines) — `GTMReportBuilder` API already accepts `title`, `subtitle`, `demo_id`, `case_count`, `code_refs`; this is the per-report branding hook. It already emits self-contained HTML reports — the prospect pipeline can reuse it without API changes for the engineering body, and only needs a thin wrapper to inject client header/footer branding.
- Found: `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` — shared by demos 3 + 5. Schema includes `id`, `name`, `representative_class`, `general.{loa_m,beam_m,displacement_te,dp_class,max_water_depth_m}`, `crane_main.{swl_max_te, swl_max_radius_m, crane_capacity_curve[], hoist_speed_m_per_min, main_wire_mbl_te, main_wire_diameter_mm}`, `motion_characteristics.{heave_rao,roll_rao,pitch_rao,natural_periods}`. This is the canonical CSV/HLV vessel shape.
- Found: `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` — **different schema** from `csv_hlv_vessels.json`. Has `pipelay_system.{tensioner, stinger, firing_line}` instead of `crane_main` — demo 4 requires a pipelay-specific vessel shape. **The adapter MUST support two distinct vessel shapes**, not one unified shape.
- Found: `digitalmodel/examples/demos/gtm/data/rigid_jumpers.json` + `pipelines.json` + `mudmat_structures.json` + `freespan_scenarios.json` — four distinct structure schemas. Demo 1 uses pipelines+jumpers+freespan_scenarios; Demo 2 uses pipelines only; Demo 3 uses mudmat_structures; Demo 4 uses pipelines; Demo 5 uses rigid_jumpers.
- Found: `digitalmodel/examples/demos/gtm/data/freespan_scenarios.json` — environment block (`current_velocities_ms`, `turbulence_intensity`, `span_lengths`) is the Demo 1 parametric sweep definition, not a structure. This means the intake schema for Demo 1 must accept *environment* + *structure* + *pipe catalog* — three sub-documents, not two.
- Gap: no CLI flag on any of the 5 demos to point at an alternate data directory (all demos hard-code `DATA_DIR = SCRIPT_DIR / "data"`). Adapter work must add a `--prospect-config` flag to each.
- Gap: no YAML support anywhere in `examples/demos/gtm/` — current data files are JSON. Prospect intake is YAML-first (issue body asks for `docs/gtm/intake/prospect-template.yaml`) so we need a YAML→demo-input translator.
- Gap: no branded-report wrapper — `GTMReportBuilder` emits the digitalmodel brand; there is no hook today for "prospect XYZ Energy" header/footer text.
- Gap: no input-validation harness. Each demo currently `KeyError`s on a missing JSON field rather than refusing with a human-readable error. Under a 48hr SLA the fail mode must be "refuse with line-and-key reference" at intake, not a stack trace after 45 minutes of compute.

### Standards

Not applicable — this is a GTM infrastructure / pipeline issue, not new engineering calculation code. (The underlying engineering codes are already cited inside each demo: DNV-RP-H103, DNV-ST-F101, API 5L, etc.)

### LLM Wiki pages consulted

No relevant wiki pages — this is a sales/ops pipeline, not a domain-knowledge question.

### Documents consulted

- `docs/gtm/gtm-plan-30day.md` lines 125-138 (Week 4 "Demo Customization — The Real Sales Event") — explicit claim: "The free demo-with-their-data is the **highest-conversion sales tool** — prioritize this over everything else." 48hr turnaround is set at line 135 ("Run parametric demo with THEIR data within 48 hours"). Risk mitigation quoted in issue body: "Always keep a clean demo environment ready; pre-stage common vessel types."
- `digitalmodel/examples/demos/gtm/README.md` lines 7-25 (Quick Start + Demos) + lines 117-125 (Common Flags) — confirms the 5 demos each emit one HTML report + one JSON result file. Lines 129-142 document the 7 data files. Confirms **only** `--from-cache` / `--force` exist on the CLI today; there is no prospect-override path.
- Issue #2342+#2343 plan `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — v4-lite self-approved 2026-04-19. Defines the published aceengineer-website detail-page shape (branded `<title>A&CE — ...</title>`, `partials/head-common.html` + `nav.html` + `footer.html` includes, vendored Plotly). Each prospect-demo report can be rendered as a one-off derivative page on the same template, posted to a private URL (see "Branded Report" below) — **no need to invent a new branded HTML skeleton**.
- Issue #2016 (umbrella "client conversion pipeline") — lines 25-31 identify parametric demo reports as a top gap; line 133 ("Demo Customization — The Real Sales Event") in the 30-day plan is the named Week 4 deliverable. This plan is the concrete execution of #2016's line-item "demo materials ready for outreach" for the *prospect-specific* case.
- Issue body #2346 — names the four concrete deliverables: (1) intake schema at `docs/gtm/intake/`, (2) 3 canonical vessel profiles pre-staged, (3) SOP at `docs/gtm/prospect-demo-sop.md`, (4) shared input adapter across 5 demos. Acceptance criteria include "Dry-run end-to-end <48 hr from dummy intake."
- Memory `feedback_adversarial_review_stance.md` — every plan must be defect-hunted, not charitably read. Informs the Risks section below (in particular the "48hr burnout" and "schema-drift" risks are flagged intentionally).
- Memory `feedback_queue_git_tracked.md` — any pre-staged vessel profile must be committed to git before it is referenced from the SOP (no floating local-only files).

### Gaps identified

1. No YAML intake schema exists at `docs/gtm/intake/` — the directory itself doesn't exist today.
2. No pre-staged "canonical" vessel profiles exist at a stable path — `data/csv_hlv_vessels.json` has two vessels, but they're demo fixtures, not prospect-intake defaults.
3. No shared input-adapter module — each demo ships its own bespoke `load_*()` functions against hard-coded JSON paths.
4. No branded-output wrapper on `GTMReportBuilder` — today all reports say "digitalmodel" in the footer.
5. No SOP document — the 48hr runbook does not exist in any form.
6. No schema-validation + refuse-vs-fix decision tree for malformed prospect input.
7. No test coverage for the end-to-end intake→demo→report path.

Distinct sources consulted: 11 (issue body + 30-day plan + 5 demo scripts + README + report_template.py + 4 data files + #2016 body + #2342/#2343 plan + 2 memory feedback entries). Exceeds minimum 3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` |
| YAML intake schema (template) | `docs/gtm/intake/prospect-template.yaml` |
| YAML intake schema (JSON-Schema validator) | `docs/gtm/intake/prospect-schema.json` |
| Pre-staged canonical vessel — pipelay barge | `docs/gtm/intake/canonical-vessels/pipelay-barge.yaml` |
| Pre-staged canonical vessel — heavy-lift CSV | `docs/gtm/intake/canonical-vessels/heavy-lift-csv.yaml` |
| Pre-staged canonical vessel — PLSV | `docs/gtm/intake/canonical-vessels/plsv.yaml` |
| SOP runbook | `docs/gtm/prospect-demo-sop.md` |
| Shared input adapter (module) | `digitalmodel/examples/demos/gtm/prospect_adapter.py` |
| Branded-report wrapper | `digitalmodel/examples/demos/gtm/branded_report.py` |
| Golden regression test | `digitalmodel/examples/demos/gtm/tests/test_prospect_adapter.py` |
| Dry-run end-to-end test | `digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py` |
| Plan index row | `docs/plans/README.md` (one new row) |
| Plan review — Claude | `scripts/review/results/2026-04-19-plan-2346-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-19-plan-2346-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-19-plan-2346-gemini.md` |

---

## Deliverable

A repeatable pipeline that ingests one prospect YAML file (vessel specs + target structure + project conditions), validates it against a JSON-Schema, maps it through a shared `prospect_adapter` to any of the 5 existing GTM demos, runs the demo in under the existing wall-clock budget, and emits a client-branded HTML report — all driven by a single SOP runbook that guarantees ≤48 hr end-to-end delivery, with three pre-staged canonical vessel templates (pipelay barge, heavy-lift CSV, PLSV) for scenarios where prospect data is incomplete.

---

## Pseudocode

### A. YAML intake schema (`prospect-template.yaml`)

```yaml
# Top-level shape — all fields required unless noted "optional"
prospect:
  company: "Acme Marine Contractors"        # required, string
  contact: "jane.doe@acme.example"          # required, for report cover
  nda_in_place: true                        # required bool — gates report distribution
  target_demo: "demo_05"                    # required enum: demo_01..demo_05
  delivery_deadline_utc: "2026-04-21T17:00Z"  # required ISO8601

vessel:
  shape: "csv_hlv"                          # required enum: csv_hlv | pipelay
  source: "prospect_provided"               # required enum: prospect_provided | canonical_ref
  canonical_ref: null                       # required-if source==canonical_ref, string id
  # Body omitted here when source==canonical_ref; otherwise inline body
  # must match the schema fragment csv_hlv_vessel_schema OR pipelay_vessel_schema
  body: { ... }                             # required-if source==prospect_provided

structure:
  kind: "rigid_jumper"                      # required enum matching demo
  # body shape selected by kind: rigid_jumper, pipeline, mudmat, freespan
  body: { ... }

environment:
  water_depths_m: [1500, 2000, 2500]        # optional — overrides demo default sweep
  hs_values_m: [1.5, 2.0, 2.5]              # optional
  current_velocity_ms: 0.5                  # optional
  # If absent, demo uses its module-level defaults

output:
  brand_header: "Prepared for Acme Marine"  # required string — report cover
  brand_footer: "Confidential — NDA"        # required string
  # Optional prospect logo (inline SVG or path under docs/gtm/intake/logos/)
  logo_inline_svg: null
```

### B. JSON-Schema validator (`prospect-schema.json`)

```
JSON-Schema draft-07 describing:
  - required top-level blocks: prospect, vessel, structure, output
  - enum constraints on target_demo, vessel.shape, vessel.source, structure.kind
  - conditional "required": if source==prospect_provided then body required;
    if source==canonical_ref then canonical_ref required
  - numeric bounds: water_depth >=0 && <=4000 m, hs_m >=0 && <=8 m
  - format: date-time on delivery_deadline_utc
  - additionalProperties: false on every object to refuse unknown keys
    (guards against silent typos like "target_dmo" — the 48hr SLA will not
     allow a 30-min post-mortem on a misspelling)
```

### C. Shared input adapter (`prospect_adapter.py`)

```
MODULE prospect_adapter

CONSTANTS:
    SCHEMA_PATH = docs/gtm/intake/prospect-schema.json
    CANONICAL_DIR = docs/gtm/intake/canonical-vessels/
    DEMO_TO_VESSEL_SHAPE = {
        "demo_01": None,                    # no vessel, just pipe + environment
        "demo_02": None,                    # no vessel, just pipe + codes
        "demo_03": "csv_hlv",               # mudmat → CSV
        "demo_04": "pipelay",               # S-lay → PLV
        "demo_05": "csv_hlv",               # jumper → CSV
    }
    DEMO_TO_STRUCTURE_KIND = {
        "demo_01": ["pipeline", "jumper_and_freespan"],
        "demo_02": ["pipeline"],
        "demo_03": ["mudmat"],
        "demo_04": ["pipeline"],
        "demo_05": ["rigid_jumper"],
    }

function load_and_validate(yaml_path):
    intake = yaml.safe_load(yaml_path)
    schema = json.load(SCHEMA_PATH)
    jsonschema.validate(intake, schema)              # first gate: structural
    # Second gate: cross-field consistency (not expressible in JSON-Schema)
    verify intake.vessel.shape matches DEMO_TO_VESSEL_SHAPE[intake.prospect.target_demo]
    verify intake.structure.kind in DEMO_TO_STRUCTURE_KIND[intake.prospect.target_demo]
    if intake.vessel.source == "canonical_ref":
        canonical_path = CANONICAL_DIR / f"{intake.vessel.canonical_ref}.yaml"
        must exist, else raise ProspectIntakeError with refuse-message
        inline_body = yaml.safe_load(canonical_path)
        intake.vessel.body = inline_body
    # Third gate: numeric sanity — depth within vessel's max_water_depth_m
    if vessel shape is csv_hlv:
        if any(d > intake.vessel.body.general.max_water_depth_m for d in intake.environment.water_depths_m):
            raise ProspectIntakeError("prospect requested deeper water than vessel rating")
    return intake

function materialize_demo_inputs(intake, tmpdir):
    # Rewrites intake.vessel + intake.structure into the JSON shapes the
    # existing demo scripts already expect — emits files into tmpdir/data/
    if intake.prospect.target_demo in ("demo_03", "demo_05"):
        write tmpdir/data/csv_hlv_vessels.json from intake.vessel.body
    elif intake.prospect.target_demo == "demo_04":
        write tmpdir/data/pipelay_vessels.json from intake.vessel.body
    write tmpdir/data/<structure_file>.json from intake.structure.body
    # Environment overrides are materialized as a separate env-override JSON
    # that each demo main() reads via the new --prospect-env flag (see patch D)
    if intake.environment:
        write tmpdir/data/prospect_env.json from intake.environment
    return tmpdir

function run_demo(intake, materialized_dir):
    demo = intake.prospect.target_demo
    script = f"digitalmodel/examples/demos/gtm/{demo}_*.py"    # glob-resolved
    subprocess: PYTHONPATH=... uv run python <script> \
        --prospect-data-dir <materialized_dir>/data \
        --prospect-env <materialized_dir>/data/prospect_env.json  (if env present)
    return path to generated output/*.html
```

### D. Per-demo CLI patches (5 scripts — smallest possible diffs)

Each demo gets a `--prospect-data-dir PATH` argparse flag that, when set, overrides the module-level `DATA_DIR` constant **for loaders only**. This is the **only** change to demo 01-05 scripts — no refactoring of the sweep logic, no change to existing `--from-cache`/`--force` behavior.

```python
# Added to each parse_args():
parser.add_argument("--prospect-data-dir", type=Path, default=None,
                    help="Override DATA_DIR for prospect-customized runs")
parser.add_argument("--prospect-env", type=Path, default=None,
                    help="Override module-level parameter sweep (WATER_DEPTHS etc) from JSON")
parser.add_argument("--brand-header", type=str, default=None)
parser.add_argument("--brand-footer", type=str, default=None)

# In main() after args parsed:
if args.prospect_data_dir:
    global DATA_DIR; DATA_DIR = args.prospect_data_dir
if args.prospect_env:
    override_constants_from(args.prospect_env)  # mutates WATER_DEPTHS, HS_VALUES in-module
```

### E. Branded-report wrapper (`branded_report.py`)

```
function wrap_with_client_branding(report_html_path, brand_header, brand_footer, nda_watermark):
    # Post-processes the GTMReportBuilder output — injects <div class="client-header"> and
    # <div class="client-footer"> plus a fixed-position "CONFIDENTIAL — <NDA>" watermark
    # if nda_watermark truthy. Uses BeautifulSoup to parse; writes back in-place.
    # The existing #2342+#2343 detail-page styling is preserved — this only overlays, never
    # replaces, the engineering body.
```

### F. SOP runbook (`prospect-demo-sop.md`) — 48hr decision tree

```
Hour 0-2: Receive prospect data (email, LinkedIn, form). File as docs/gtm/intake/received/YYYY-MM-DD-<company>.yaml
Hour 2-6: Run prospect_adapter.load_and_validate()
  - PASS → proceed to Hour 6-24
  - FAIL schema → email prospect back within 2hrs with specific line/key reference
    asking for the missing field. Do NOT invent defaults. Do NOT silently fill.
    EXCEPTION: if vessel block is missing AND prospect said "use your closest vessel",
    swap to canonical_ref pointing at one of the 3 pre-staged profiles; log the
    substitution on the report cover page.
  - FAIL cross-field (e.g. depth > vessel rating) → email prospect: "you asked for 3500m
    on a vessel rated 3000m — confirm you want us to flag this as NO_GO, or provide
    revised vessel spec."
Hour 6-24: Run demo via prospect_adapter.run_demo()
  - On numerical failure (NaN / exception) → flag specific phase, fall back to canonical
    vessel ONLY if prospect pre-authorized it in step 1. Otherwise refuse and email.
Hour 24-36: Render branded report, spot-check all 5 charts render, open in 2 browsers.
Hour 36-44: Internal review — 1 engineer reads the whole report; if any flag, fix or escalate.
Hour 44-48: Deliver — email prospect the HTML + PDF, log to docs/gtm/deliveries-log.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/gtm/intake/prospect-template.yaml` | Copy-paste starting point for prospect (and for our own data entry on their behalf) |
| Create | `docs/gtm/intake/prospect-schema.json` | Machine-checkable validation contract |
| Create | `docs/gtm/intake/canonical-vessels/pipelay-barge.yaml` | Pre-staged fallback (Demo 4 vessel shape) |
| Create | `docs/gtm/intake/canonical-vessels/heavy-lift-csv.yaml` | Pre-staged fallback (Demo 3+5 vessel shape) |
| Create | `docs/gtm/intake/canonical-vessels/plsv.yaml` | Pre-staged fallback (Pipe-Lay Support Vessel) |
| Create | `docs/gtm/intake/README.md` | Short index describing what each file is for |
| Create | `docs/gtm/prospect-demo-sop.md` | 48hr runbook (section F pseudocode, expanded) |
| Create | `docs/gtm/deliveries-log.md` | Empty table header for future delivery records |
| Create | `digitalmodel/examples/demos/gtm/prospect_adapter.py` | load_and_validate + materialize_demo_inputs + run_demo |
| Create | `digitalmodel/examples/demos/gtm/branded_report.py` | wrap_with_client_branding helper |
| Create | `digitalmodel/examples/demos/gtm/tests/test_prospect_adapter.py` | TDD suite |
| Create | `digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py` | End-to-end golden-output regression test |
| Create | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-valid.yaml` | Valid fixture for tests |
| Create | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-missing-vessel.yaml` | Invalid fixture (schema-fail case) |
| Create | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-depth-exceeds.yaml` | Invalid fixture (cross-field-fail case) |
| Modify | `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py` | Add `--prospect-data-dir` / `--prospect-env` / `--brand-*` flags; swap `DATA_DIR` if set |
| Modify | `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/README.md` | Add "Prospect-customized runs" section with flag docs |
| Modify | `docs/plans/README.md` | Register this plan (status: draft) |

**Note on `.gitignore`:** `docs/gtm/intake/received/` should be created but be in `.gitignore` — prospect data is potentially NDA-covered and must NEVER be committed to the public repo. The SOP will explicitly instruct that. (See Risks below for the PII/NDA treatment.)

---

## TDD Test List

Tests written against `pytest` with `uv run pytest digitalmodel/examples/demos/gtm/tests/ -v`.

### Schema validation tests (`test_prospect_adapter.py`)

| Test name | What it verifies | Input | Expected |
|---|---|---|---|
| test_valid_yaml_passes_schema | Happy path: valid YAML passes both JSON-Schema and cross-field check | `fixtures/prospect-valid.yaml` | no exception, returns dict |
| test_missing_vessel_body_fails | Missing required `vessel.body` when source=prospect_provided | `fixtures/prospect-missing-vessel.yaml` | raises `ProspectIntakeError` with "vessel.body required" in msg |
| test_unknown_top_level_key_fails | Typo like `prospct:` triggers additionalProperties=false | mutated fixture | raises `ProspectIntakeError` |
| test_wrong_demo_vessel_shape_mismatch | Demo 4 asked with shape=csv_hlv (mismatch) | mutated fixture | raises `ProspectIntakeError` with "demo_04 requires pipelay shape" |
| test_depth_exceeds_vessel_rating | `environment.water_depths_m` max > `vessel.body.general.max_water_depth_m` | `fixtures/prospect-depth-exceeds.yaml` | raises `ProspectIntakeError` with both numbers in msg |
| test_canonical_ref_loads_inline | `vessel.source=canonical_ref` with `canonical_ref=heavy-lift-csv` | fixture | returned dict has `vessel.body` inline-populated from canonical YAML |
| test_canonical_ref_unknown_id_fails | `canonical_ref=does-not-exist` | fixture | raises `ProspectIntakeError` |
| test_enum_target_demo_rejects_demo_99 | `prospect.target_demo=demo_99` | mutated fixture | raises `ProspectIntakeError` |

### Adapter materialization tests

| Test name | What it verifies |
|---|---|
| test_materialize_csv_hlv_writes_correct_file | Demo 3 or 5 target → `csv_hlv_vessels.json` exists in tmpdir with expected schema |
| test_materialize_pipelay_writes_correct_file | Demo 4 target → `pipelay_vessels.json` exists in tmpdir |
| test_materialize_env_override | `environment.water_depths_m=[500,1000]` → `prospect_env.json` contains same |

### Pre-staged canonical vessel tests

| Test name | What it verifies |
|---|---|
| test_each_canonical_vessel_validates_against_schema | All 3 canonical YAMLs pass `load_and_validate` as bodies (with wrapper prospect-stub) |
| test_canonical_coverage_spans_three_vessel_shapes | Pipelay + heavy-lift + PLSV cover the two schemas (csv_hlv × 2, pipelay × 1) |

### End-to-end tests (`test_prospect_pipeline_e2e.py`)

| Test name | What it verifies | Performance gate |
|---|---|---|
| test_e2e_demo_05_with_canonical_vessel | Full run: valid YAML → adapter → demo_05 → HTML report → branded output exists | Full run completes < 90 s (well within 48hr SLA — this is the dry-run budget) |
| test_e2e_report_contains_brand_strings | Generated HTML contains `brand_header` + `brand_footer` literals | n/a |
| test_e2e_report_has_nda_watermark_when_requested | `nda_in_place=true` → watermark div present in HTML | n/a |
| test_e2e_golden_regression_demo_05 | Canonical "heavy-lift-csv" vessel + fixture structure → charts' underlying JSON payload matches committed golden file byte-for-byte (modulo timestamps) | n/a — regression guard |
| test_e2e_refuse_on_malformed_yaml | Invalid YAML → pipeline exits non-zero before any compute | < 5 s — must fail fast |

### SOP tests (trivial — markdown link-checks)

| Test name | What it verifies |
|---|---|
| test_sop_references_exist | Every path referenced in `prospect-demo-sop.md` (adapter, schema, canonical-vessels dir) resolves on disk |

---

## Acceptance Criteria

- [ ] `docs/gtm/intake/prospect-template.yaml` exists, validates against `prospect-schema.json`, and contains inline comments explaining each field
- [ ] `docs/gtm/intake/prospect-schema.json` is draft-07 JSON-Schema with `additionalProperties: false` on every object
- [ ] Three canonical vessel files exist at `docs/gtm/intake/canonical-vessels/{pipelay-barge,heavy-lift-csv,plsv}.yaml` and each validates standalone
- [ ] `digitalmodel/examples/demos/gtm/prospect_adapter.py` exposes `load_and_validate`, `materialize_demo_inputs`, `run_demo` per pseudocode
- [ ] `digitalmodel/examples/demos/gtm/branded_report.py` exposes `wrap_with_client_branding` per pseudocode
- [ ] All 5 demo scripts accept `--prospect-data-dir`, `--prospect-env`, `--brand-header`, `--brand-footer` flags; behavior unchanged when flags absent (regression-protected)
- [ ] `docs/gtm/prospect-demo-sop.md` exists with the 48hr decision tree AND explicit "refuse vs fix" rules for schema-fail and cross-field-fail cases
- [ ] `docs/gtm/deliveries-log.md` exists (empty table header)
- [ ] `docs/gtm/intake/received/` appears in `.gitignore` (NDA / PII isolation)
- [ ] `.gitignore` entry verified with `git check-ignore docs/gtm/intake/received/sample.yaml` returning exit 0
- [ ] `uv run pytest digitalmodel/examples/demos/gtm/tests/ -v` passes — all schema, materialization, e2e, golden, SOP tests green
- [ ] `test_e2e_demo_05_with_canonical_vessel` completes in < 90 s (dry-run budget proves 48hr SLA is achievable with 100× headroom for manual review)
- [ ] `test_e2e_refuse_on_malformed_yaml` completes in < 5 s (fail-fast verified)
- [ ] Golden regression test committed with a canonical golden JSON output file
- [ ] `docs/plans/README.md` has a new row for #2346 in the index
- [ ] No regression in existing demos: `uv run python digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py --from-cache` still produces identical HTML when no prospect flags are passed
- [ ] Review artifacts posted to `scripts/review/results/` from at least 2 providers (Claude + Codex) before any implementation

---

## Adversarial Review Summary

<!-- To be filled in after Step 4. Not yet dispatched. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Gemini | TBD | — |

**Overall result:** TBD

---

## Risks and Open Questions

### Risks

- **Risk: prospect data leakage (PII / NDA).** Prospect vessel specs, project coordinates, and contact information are commercial-sensitive and may be covered under NDA. Mitigation: (1) `docs/gtm/intake/received/` is `.gitignore`d and verified by test; (2) SOP mandates explicit NDA check before any report leaves ACE; (3) `nda_in_place: true` gates watermark application; (4) deliveries-log.md records prospect + date + demo but NOT vessel specs. **Residual risk:** a human forgetting to add `.gitignore` entry for a new subfolder — mitigation is the git-check-ignore acceptance test.
- **Risk: turnaround burnout under 48hr SLA.** A single engineer running this on nights/weekends will degrade quality after week 1. Mitigation: the SOP's explicit refuse-rather-than-guess rule is the burnout backstop — if schema fails, the clock resets at prospect's end, not ACE's. Plan explicitly rejects "silently fill defaults" as a failure mode.
- **Risk: quality drift under pressure.** Under time pressure an engineer might skip the Hour 36-44 internal review. Mitigation: the golden-regression test + the in-report NDA watermark are both CI-enforced artifacts that cannot be faked; they don't eliminate the risk but make violations auditable after the fact.
- **Risk: vessel-shape mismatch not caught pre-run.** If a prospect submits a pipelay vessel shape for a demo_05 jumper analysis, the engineering output would be nonsense. Mitigation: `DEMO_TO_VESSEL_SHAPE` + cross-field validation gate; TDD test `test_wrong_demo_vessel_shape_mismatch` locks this.
- **Risk: 5-demo CLI-patch blast radius.** Touching all 5 demos risks a regression in an already-working sweep. Mitigation: the patches are the minimal possible diff (2 lines of argparse + 2 lines in main() per demo); regression acceptance criterion explicitly includes running `--from-cache` on demo_05 and comparing HTML byte-level.
- **Risk: YAML injection / file-read attacks in canonical_ref.** If prospect supplies `canonical_ref: "../../../etc/passwd"`, the adapter should refuse. Mitigation: adapter must sanitize `canonical_ref` against an allowlist constructed at module load by `glob(CANONICAL_DIR / "*.yaml")`, not by string concat. Acceptance test `test_canonical_ref_unknown_id_fails` + a new `test_canonical_ref_traversal_rejected` must both pass.
- **Risk: schema drift between YAML intake and existing JSON data files.** Demo data files may evolve; the adapter's materialization step could silently break. Mitigation: the golden regression test re-materializes and compares against committed golden output — drift surfaces as a failing test, not a silent malformed report delivered to a prospect.
- **Risk: Demo 1 intake is 3-document (environment + structure + pipe catalog).** More complex than other demos' intake. Mitigation: schema uses `oneOf` per `structure.kind`; Demo 1 fixture committed and test-covered.

### Open questions for user (FLAG before adversarial review)

1. **Q1 — branded-report path:** Should branded prospect reports be published to the live `aceengineer-website` (on a private URL like `/demos/prospect-<slug>.html` with crawler-block) or delivered purely over email? The #2342+#2343 plan builds the public-page infrastructure; this plan assumes **email-only delivery** (no public URL, not even private-by-obscurity) to minimize NDA exposure. **CONFIRM** before implementation.
2. **Q2 — canonical vessel realism:** Should the 3 canonical vessels be derived from public vessel specs (Heerema / Saipem / Subsea 7 publicly disclosed class data) or purely synthetic? Synthetic is safer against claims of misrepresentation; public-class-derived is more credible to prospects. **Suggest synthetic-but-plausible**, with a data dictionary note that they're representative, not named.
3. **Q3 — demo_01 + demo_02 have no vessel.** The intake schema's `vessel:` block becomes optional in those cases. Plan currently marks `vessel` as required across all intakes; should it be conditional on `target_demo`? **Suggest conditional-required** (matches the `DEMO_TO_VESSEL_SHAPE[demo]==None` cases); change is localized to the JSON-Schema `if/then` blocks.
4. **Q4 — SOP Hour 2-6 refuse-vs-fix policy.** On schema fail, plan says "email prospect with line/key reference; do NOT invent defaults." Is this too strict for a high-value lead where ACE has a strong canonical default? Current plan leaves one explicit exception: if prospect pre-authorized "use your closest vessel", swap to canonical_ref. **Confirm this is the ONLY exception** and that it must be logged on the report cover.
5. **Q5 — test runtime budget.** Plan sets e2e < 90 s. Demo 5's 300-case sweep is ~30 s today; demo 1 is 680 cases. Should the e2e golden test use demo_05 (smallest footprint with a vessel) or run all 5? **Suggest demo_05 only** for CI speed, with the other 4 covered by unit-level materialization tests.

---

## Complexity: T2

**T2** — new module (adapter + branded-report wrapper), new docs (schema + template + SOP + 3 canonical vessels), minimum-diff modifications to 5 existing demo scripts, full TDD coverage including a golden-regression test. No new engineering calculations, no standards gap work, no cross-machine infrastructure. Blast radius is contained to `docs/gtm/intake/` + `digitalmodel/examples/demos/gtm/` + one README row. Not T3 (no architectural decisions, no new subsystem) and not T1 (multi-file, multi-module, schema design).
