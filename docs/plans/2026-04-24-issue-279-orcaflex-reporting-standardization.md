# Plan for #279: Standardize analysis reporting for each OrcaFlex structure type (WRK-129)

> **Status:** draft
> **Complexity:** T2-large (re-evaluated — see Complexity section)
> **Date:** 2026-04-24 (r2)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/279
> **Review artifacts:** scripts/review/results/2026-04-24-plan-279-claude.md | ...-codex.md | ...-gemini.md | ...-adversarial.md (r1)

---

## Revision Notes (r2)

This revision addresses the Wave 3 adversarial review verdict (`REQUEST_CHANGES`, 3 MAJOR + 5 MINOR defects) filed at `scripts/review/results/2026-04-24-plan-279-adversarial.md`. Residual r1-Claude findings (from `...-plan-279-claude.md`, MAJOR verdict with 12 findings, 5 additional blockers + 5 cleanup items) are merged into the same revision pass since they overlap heavily.

### MAJOR defects addressed

| # | Defect (source) | Resolution |
|---|---|---|
| MAJOR-1 | `docs/modules/` → `docs/domains/` rename-risk ignored (adversarial) — same failure mode as #510. Issue body hard-codes `docs/modules/orcaflex/reporting/examples/` 5x. `docs/modules/orcaflex/` does NOT currently exist; `docs/domains/` does NOT currently exist. Rename decision is unresolved. | Added **§ Docs Path Binding (Rename-Risk Lock)** below; bound the examples path to a single canonical variable `$EXAMPLES_DIR`; added Risk bullet; Acceptance Criteria now predicates path on rename-decision lookup. Plan must NOT race `docs/modules/` vs. `docs/domains/`. |
| MAJOR-2 | Spec-mandated golden HTML examples (issue body line 945: *"≥ 2 example HTML reports committed to `docs/modules/orcaflex/reporting/examples/`"*) missing from Artifact Map, Files to Change, Acceptance Criteria. These are committed user-facing deliverables, distinct from pytest-snapshot fixtures. | Added 2 golden HTML artifacts to Artifact Map (riser + mooring at minimum); added Files to Change rows; added 2 acceptance-criteria checkboxes; linked path to $EXAMPLES_DIR from MAJOR-1. |
| MAJOR-3 | Fabricated TDD test `test_boundary_conditions_wired_in_aggregator` — r1 listed it as a gap, but `aggregator.py:24` already imports `extract_boundary_conditions` and `aggregator.py:68` calls it via `_safe_extract`. Spurious green test on false-premise gap. | Removed the fabricated test from TDD Test List; removed Gap #8 from Gaps; removed the "verify wiring" clause from the aggregator Files-to-Change row; replaced with 3 genuinely-needed tests: (a) existing-fpso-fixture vessel-renderer migration test, (b) OrcFxAPI-free `from_dict()` roundtrip across all 11 Pydantic models, (c) dispatch-map vs. renderer-registry parity test. |

### MINOR defects addressed (adversarial r1)

| # | Defect | Resolution |
|---|---|---|
| MINOR-1 | Dispatch pseudocode shows `renderer_map = {...}` but live `report_generator.py:60-74` uses `if/elif` ladder. Plan doesn't commit to append-elif vs. dict-rewrite. | Pseudocode now commits explicitly to **append-elif** (preserves per-branch kwargs surface); refactor-to-dict deferred; added `test_dispatch_ladder_parity` to catch regression. |
| MINOR-2 | `from_dict()` offline construction buried in a Risk bullet; spec P-requirement applies to all 11 Pydantic models, not just vessel. | Promoted to Acceptance Criteria as dedicated checkbox + added `test_from_dict_all_models_offline` parameterised over `models/*.py`. |
| MINOR-3 | Source-count footnote claimed 5 sources but body cites ≥ 6 (incl. #282 + WRK cluster). | Updated footnote; now honest count. |
| MINOR-4 | `check-plotly-sri-pin.sh` only guards `PLOTLY_JS_VERSION` vs. wheel, not `PLOTLY_JS_SRI` vs. declared version. Version-bump without SRI-bump passes silently. | Script pseudocode extended: also recompute SRI-384 of pinned CDN URL and compare against `PLOTLY_JS_SRI` constant. |
| MINOR-5 | Codex-iter-14 APPROVE / Gemini NO_OUTPUT x14 lineage acknowledged as "prudent" but not gated. | Re-cross-review against as-shipped code wired into Acceptance Criteria as an explicit blocker. Added Gemini NO_OUTPUT fallback: consensus moves forward on Claude+Codex if Gemini NO_OUTPUTs ≥ 2 attempts with captured stderr. |

### r1-Claude blockers additionally addressed (overlap with adversarial)

- **Finding 2 (FPSO snapshot silent regression):** Added explicit § FPSO Snapshot Re-baseline Protocol — FPSO is a vessel; adding `VesselRenderer` will change `test_fpso_report_matches_snapshot` output. Re-baseline step + before/after commit required.
- **Finding 4 (Vessel-as-primary vs. vessel-as-subcomponent):** Added Pseudocode section for `VesselExtract.to_other_structures_dict()` adapter so the same vessel renders consistently whether it's a top-level `structure_type="vessel"` report OR nested in a mooring/riser report via `OtherStructures.vessels[]`.
- **Finding 5 (fixtures/ directory doesn't exist):** Added `fixture_helpers.py` refactor as its own Files-to-Change row + sub-step; FPSO/mooring fixture migration called out.
- **Finding 6 (extractor count 7 vs. 8):** Corrected to 8.
- **Finding 7 (`css.py` omitted):** Added to inventory.
- **Finding 8 (`test_report_generator.py:112` already tests dispatch):** `test_vessel_renderer_dispatched` now **extends** the existing file, not a new file.
- **Finding 9 (17 section modules for 16 sections):** Clarified: `utils.py` is the 17th (shared `_escape`), not a section — "16 sections + 1 utils".
- **Finding 10 (TRADEOFF-gated Acceptance):** Locked defaults: Legacy=Option A (Deprecate), Vessel=Option A (Minimum-viable), structure_types=Option A (Remove). User can still override, but plan no longer starves on unresolved tradeoffs.
- **Finding 12 (deprecation comment self-contradicts):** Aligned — "non-removal" removed; warning now reads "will be removed in v<N+2>"; Acceptance Criterion #7 wording matches.

### Residual concerns (not silenced)

- r2 is **not** adversarially reviewed — Wave 3 reviewed r1. Per the r2 Acceptance Criteria, r2 must run its own Claude+Codex (+Gemini if available) cross-review before leaving `draft`.
- The docs-rename decision itself (`docs/modules/` vs. `docs/domains/`) is **not** resolved here. Plan binds path via variable + risk-notes the unknown; implementer halts if the resolution tracking issue (TBD — flagged to user) is not closed.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py` (107 lines) — `generate_orcaflex_report()` entry point, Plotly 2.26.0 CDN pinning + SRI (`PLOTLY_JS_VERSION` and `PLOTLY_JS_SRI` both declared), `_escape()` XSS guard integration. **Dispatch is an `if/elif` ladder at lines 60-74** (verified r1-Claude), not a dict.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/css.py` (213 lines) — holds the `#2c3e50` theme (contrast to legacy `builder.py:31`'s Bootstrap `#0d6efd`). Previously omitted in r1.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/` — 5 of 6 renderers (`pipeline.py`, `riser.py`, `jumper.py`, `mooring.py`, `installation.py`) plus `base.py`. **Missing: `vessel.py`.** `BaseRenderer` is the fallback for `structure_type="vessel"` today — which is what the existing `test_fpso_fixture_snapshot.py` baseline currently captures.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/` — **16 section modules + `utils.py`** (17 files total): `header, executive_summary, model_overview, geometry, materials, boundary_conditions, mesh, other_structures, loads, analysis_setup, results_static, results_dynamic, results_extreme, design_checks, fatigue, summary, appendices, utils`. The "16-section canonical layout" excludes `utils.py` (XSS helper).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/` — 11 Pydantic composition schemas (analysis, boundary_conditions, design_checks, fatigue, geometry, loads, materials, mesh, other_structures, report, results). `models/other_structures.py:20` ships `vessels: List[dict]` — vessel already has nested-representation today.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/` — **8 files** (not 7): `aggregator.py, boundary_conditions_extractor.py, geometry_extractor.py, loads_extractor.py, materials_extractor.py, mesh_extractor.py, mooring_extractor.py, results_extractor.py`. `aggregator.py:24` imports `extract_boundary_conditions`; `aggregator.py:68` calls it via `_safe_extract`. **Missing: `vessel_extractor.py`.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/__init__.py` — 1-line empty file.
- Found (legacy parallel path): `digitalmodel/src/digitalmodel/orcaflex/reporting/` — 8-section `OrcaFlexReportBuilder` (`builder.py:31` uses `#0d6efd`) vs. spec's `#2c3e50`. Superseded by `solvers/orcaflex/reporting/` tree but still shipped.
- Found: `digitalmodel/tests/solvers/orcaflex/reporting/` — 13 test files; `test_report_generator.py:112` already has `test_generate_report_invalid_structure_type` (dispatch coverage). No `fixtures/` subdirectory exists today; fixtures are loaded via `fixture_helpers.py` / `snapshot_helpers.py` from in-module references.
- **Docs path state (rename-risk probe):** `docs/modules/` EXISTS but has NO `orcaflex/` subdirectory; `docs/domains/` does NOT exist. Resolution of the rename decision is unresolved — directly affects where golden HTML examples land.
- Gap: no `vessel` renderer, no `vessel_extractor`, no per-type fixtures for pipeline/riser/jumper/installation/vessel (only mooring + FPSO via `test_fpso_*` exist).
- Gap: no `fixtures/{type}/` directory skeleton; `fixture_helpers.py` is flat.
- Gap: no committed golden HTML examples at the docs-path (neither `docs/modules/orcaflex/reporting/examples/` nor the would-be `docs/domains/` counterpart).
- Gap: no CI guard that XSS-escape tests accompany new `str`/`list[str]` model fields (spec P12).
- Gap: no guard that Plotly wheel version matches `PLOTLY_JS_VERSION` constant **AND** that `PLOTLY_JS_SRI` hash matches the declared version (SRI drift).
- Gap: no parity test across dispatch ladder ↔ renderer registry.
- Gap: no `from_dict()`-without-OrcFxAPI roundtrip across all 11 models (spec P-requirement).

### Standards
| Standard | Status | Source |
|---|---|---|
| N/A — reporting-framework issue | n/a | reporting is format/presentation, no engineering code |

Standards ledger not applicable: the design-check *content* (DNV-OS-F101, API-RP-2SK, etc.) is consumed as pre-computed data from `mooring_analysis/` and `orcaflex_fatigue_analysis.py`; this plan does not evaluate standards, it renders results.

### LLM Wiki pages consulted
- No relevant wiki pages. Marine-engineering wiki entries describe physical analyses, not reporting conventions. Explicitly verified empty set.

### Documents consulted
- Issue body `/tmp/orca-batch-2026-04-24/issue-279-body.txt` — embedded Final Plan v1.13, module target `solvers/orcaflex/reporting`, 6 structure types including vessel, 16-section canonical layout, Codex APPROVE iter 14, Gemini NO_OUTPUT x14. **AC line 945** mandates golden HTML examples at `docs/modules/orcaflex/reporting/examples/` (also referenced at lines 870, 876, 1155, 1318).
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — cross-cutting parent; does not supersede.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — batch-orchestration doc creating this plan.
- Pod intel `/tmp/orca-batch-2026-04-24/intel-279.md` — Explorer CRITICAL FINDING: framework substantially built; delta = vessel + fixtures + cleanup.
- Related issue #282 — OrcaWave reporting; shared HTML scaffold opportunity flagged but explicitly out of scope here.
- Related issues WRK-125/WRK-127/WRK-045/WRK-046/WRK-064 — upstream analyzers that feed pre-computed check data; not modified.
- Related issue #510 — prior rename-drift failure mode that `docs/modules/` → `docs/domains/` migration surfaces; same trap applies here.
- r1 adversarial review `scripts/review/results/2026-04-24-plan-279-adversarial.md` — 3 MAJOR + 5 MINOR.
- r1 Claude review `scripts/review/results/2026-04-24-plan-279-claude.md` — MAJOR, 12 findings (merged above).

### Gaps identified
1. `vessel` renderer — spec lists 6 structure types, only 5 exist; `report_generator.py` falls through to `BaseRenderer`.
2. `vessel_extractor.py` — no hull RAO / watch-circle / 6DOF motion extractor.
3. `structure_types/` package — empty; disposition required (default: remove — Option A).
4. Legacy `digitalmodel/orcaflex/reporting/` disposition — default: deprecate (Option A).
5. Per-type snapshot fixtures for pipeline, riser, jumper, installation, vessel — `fixtures/` directory must be created; `fixture_helpers.py` refactored.
6. FPSO snapshot baseline will diverge once vessel renderer is wired — must be re-baselined with explicit before/after commits.
7. XSS-escape lint hook for new model string fields.
8. SRI version-drift AND SRI hash-drift guard (both checks, not just version).
9. Docs-path rename risk: `docs/modules/orcaflex/reporting/examples/` target unresolved against possible `docs/domains/` migration.
10. Golden HTML examples (spec-mandated deliverable) — missing; must be committed for ≥ 2 structure types.
11. `from_dict()` offline construction coverage across all 11 Pydantic models (spec P-requirement, not just vessel).
12. Dispatch ladder ↔ renderer-registry parity (no test today).
13. Vessel-as-top-level vs. vessel-as-subcomponent data-contract alignment (`VesselExtract` ↔ `OtherStructures.vessels[]`).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#279` — OPEN — "WRK-129: Standardize analysis reporting for each OrcaFlex structure type"
- `#282` — referenced; OrcaWave reporting sibling; shared-scaffold flag only
- `#510` — referenced for rename-drift failure precedent

**File existence** (`ls` 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/css.py` (213 lines)
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/{base,pipeline,riser,jumper,mooring,installation}.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py`
- EXISTS (empty): `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/__init__.py`
- EXISTS (legacy): `digitalmodel/src/digitalmodel/orcaflex/reporting/{builder.py,config.py,sections/}`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/reporting/` (13 test files, no `fixtures/` subdir)
- EXISTS: `docs/modules/` — but NO `docs/modules/orcaflex/` subdir
- MISSING: `docs/domains/` — directory does not exist
- MISSING (new — this plan creates, path TBD per § Docs Path Binding): `$EXAMPLES_DIR/riser_scr001.html`, `$EXAMPLES_DIR/mooring_fpso_turret.html`

**Line excerpts**:
- `aggregator.py:24`: `from .boundary_conditions_extractor import extract_boundary_conditions` (confirms wiring — refutes r1 Gap #8).
- `aggregator.py:68`: `bc = _safe_extract(...)` using above (confirms call).
- `report_generator.py:60-74`: `if stype == "riser": ... elif ... else: BaseRenderer(...)` — if/elif ladder, not dict map.
- `report_generator.py:45`: `PLOTLY_JS_VERSION = "2.26.0"`; `PLOTLY_JS_SRI = "sha384-..."` also declared.
- `builder.py:31` (legacy): `#0d6efd` — Bootstrap blue.
- `test_fpso_fixture_snapshot.py:13-25`: `test_fpso_snapshot_contains_expected_structural_markers` + byte-level snapshot — already baselined against BaseRenderer fallback for the vessel type.
- `test_report_generator.py:112`: `test_generate_report_invalid_structure_type` — dispatch coverage already exists.

**Gap proofs**:
- `ls digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py 2>&1` → "No such file or directory".
- `ls digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py 2>&1` → "No such file or directory".
- `ls digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/` → only `__init__.py`.
- `ls digitalmodel/tests/solvers/orcaflex/reporting/fixtures/ 2>&1` → "No such file or directory".
- `ls docs/modules/orcaflex 2>&1` → "No such file or directory"; `ls docs/domains 2>&1` → "No such file or directory".
- `ls scripts/enforcement/check-report-model-xss-coverage.sh 2>&1` → "No such file or directory".
- `ls scripts/enforcement/check-plotly-sri-pin.sh 2>&1` → "No such file or directory".

<!-- Source count: issue body + r1 adversarial review + r1 Claude review + pod intel + batch-design plan + intensive-plan + legacy module listing + #282 cross-ref + #510 rename-precedent = 9 distinct sources. -->

---

## Docs Path Binding (Rename-Risk Lock)

The issue body hard-codes `docs/modules/orcaflex/reporting/examples/` (lines 870, 876, 945, 1155, 1318). The batch brief flagged the `docs/modules/` → `docs/domains/` rename risk as the same failure mode that broke #510. Current state (verified 2026-04-24):
- `docs/modules/` exists; `docs/modules/orcaflex/` does NOT.
- `docs/domains/` does NOT exist.
- The rename decision is unresolved.

**Resolution protocol:**
1. Before implementation begins, the implementer MUST resolve `$EXAMPLES_DIR` via one of:
   - (a) Confirm with user: "rename not happening in this batch" → `$EXAMPLES_DIR=docs/modules/orcaflex/reporting/examples/` and a sibling docs-governance issue to ensure future renamers sweep this path.
   - (b) Confirm with user: "rename is happening; #279 lands after" → `$EXAMPLES_DIR=docs/domains/orcaflex/reporting/examples/` and depend-on the rename issue closure.
   - (c) If unresolved, block on the rename-tracking issue (user names it at approval) rather than race.
2. The plan does NOT choose — it binds the variable and defers.
3. Acceptance Criteria reference `$EXAMPLES_DIR` textually; at close, paths must match the resolved value.

---

## FPSO Snapshot Re-baseline Protocol

`test_fpso_fixture_snapshot.py` currently captures the FPSO turret report **as rendered by `BaseRenderer` fallback** (FPSO is a vessel; vessel has no renderer today). Once `VesselRenderer` is wired:
1. The FPSO snapshot will diverge (different HTML output from the new renderer).
2. The existing test must be **re-baselined** — not silently updated. Re-baselining requires:
   - Commit A: add `VesselRenderer` with tests disabled for fpso_turret.
   - Commit B: regenerate `test_fpso_report_matches_snapshot` expected output; diff-review by implementer; commit the new baseline.
   - Commit C: decide — either migrate `fpso_turret` fixture into `fixtures/vessel/` subtree as the canonical vessel fixture, OR keep it as a standalone FPSO integration test and add a separate minimal `fixtures/vessel/generic.json` for `test_per_type_snapshot_vessel`. Default: migrate (simpler fixture set).

This protocol is an explicit Acceptance Criterion.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md |
| Vessel renderer | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py` |
| Vessel extractor | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py` |
| Vessel model fields | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/report.py` (extend `StructureData`), new `models/vessel_motion.py` if needed |
| Renderer dispatch | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py` (append `elif` branch for `"vessel"`) |
| Vessel tests | extend `digitalmodel/tests/solvers/orcaflex/reporting/test_report_generator.py` + new `test_vessel_renderer.py`, `test_vessel_extractor.py` |
| Fixtures dir (NEW) | `digitalmodel/tests/solvers/orcaflex/reporting/fixtures/{pipeline,riser,jumper,mooring,installation,vessel}/` |
| Fixture helpers refactor | `digitalmodel/tests/solvers/orcaflex/reporting/fixture_helpers.py` (re-index by structure_type) |
| Per-type snapshot sweep | `digitalmodel/tests/solvers/orcaflex/reporting/test_per_type_snapshots.py` |
| From-dict offline parity | `digitalmodel/tests/solvers/orcaflex/reporting/test_from_dict_all_models.py` |
| **Golden HTML example 1** | `$EXAMPLES_DIR/riser_scr001.html` (spec-mandated deliverable — resolves MAJOR-2) |
| **Golden HTML example 2** | `$EXAMPLES_DIR/mooring_fpso_turret.html` (spec-mandated deliverable — resolves MAJOR-2) |
| Examples README | `$EXAMPLES_DIR/README.md` |
| XSS escape lint | `scripts/enforcement/check-report-model-xss-coverage.sh` |
| SRI drift guard (version + hash) | `scripts/enforcement/check-plotly-sri-pin.sh` |
| Legacy deprecation notice | `digitalmodel/src/digitalmodel/orcaflex/reporting/__init__.py` (emit `DeprecationWarning`) |
| Plan review — Claude (r2) | scripts/review/results/2026-04-24-plan-279-claude.md (r1 exists; r2 re-review required) |
| Plan review — Codex (r2) | scripts/review/results/2026-04-24-plan-279-codex.md |
| Plan review — Gemini (r2) | scripts/review/results/2026-04-24-plan-279-gemini.md (fallback: NO_OUTPUT tolerated with stderr capture) |
| Docs updates | docs/plans/README.md (index entry) |

---

## Deliverable

A completed 6-structure-type reporting framework at `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/` with `VesselRenderer` + `vessel_extractor`, per-type snapshot-tested fixtures housed under `tests/.../fixtures/{type}/`, committed golden HTML examples at `$EXAMPLES_DIR` (spec-mandated), XSS + SRI (version+hash) regression guards, FPSO snapshot re-baselined against the new vessel renderer, and a documented deprecation path for the legacy `digitalmodel/orcaflex/reporting/` builder.

---

## Pseudocode

**Vessel renderer (`renderers/vessel.py`):**
```
class VesselRenderer(BaseRenderer):
    structure_type = "vessel"

    def render_sections(self, report_data):
        assemble canonical 16-section payload
        inject vessel-specific subsections:
          - model_overview: hull particulars (LPP, beam, draft, displacement)
          - other_structures: thrusters, mooring-interface refs, turret (if any)
          - loads: environmental matrix (Hs/Tp/Dir), RAO-applied response
          - results_static: equilibrium heel/trim, mean offset
          - results_dynamic: 6DOF motion stats (mean/std/max per DOF)
          - results_extreme: watch-circle radius, peak heel/trim, nearest asset
          - design_checks: station-keeping pass/fail (pre-computed input)
        return list[SectionHtml] escaped via utils._escape
```

**Vessel extractor (`extractors/vessel_extractor.py`):**
```
def extract_vessel(orcfx_model, vessel_name) -> VesselExtract:
    locate Vessel object via OrcFxAPI
    read hull particulars from model data (no live sim)
    read applied RAO references (file + label; file-hash optional per open Q)
    from static result: equilibrium position, heel/trim
    from dynamic result: per-DOF time-series summary (mean/std/p95/max)
    compute watch-circle radius from horizontal plane excursion
    return Pydantic VesselExtract for aggregator

def VesselExtract.to_other_structures_dict() -> dict:
    # Adapter so the same vessel renders consistently whether top-level
    # structure_type="vessel" OR nested in a mooring/riser report via
    # models/other_structures.py:20 vessels: List[dict]. Resolves r1-Claude
    # Finding 4 (vessel-as-primary vs. vessel-as-subcomponent divergence).
    return {
      "name": self.name, "hull": self.hull.model_dump(),
      "mean_offset_m": self.results_static.mean_offset_m,
      "watch_circle_m": self.results_extreme.watch_circle_m,
    }
```

**Dispatch addition — APPEND `elif` (commit to this form, NOT dict rewrite):**
```python
# report_generator.py around lines 60-74 — current shape
# if stype == "riser": renderer = RiserRenderer(...)
# elif stype == "pipeline": renderer = PipelineRenderer(...)
# elif stype == "jumper": renderer = JumperRenderer(...)
# elif stype == "mooring": renderer = MooringRenderer(...)
# elif stype == "installation": renderer = InstallationRenderer(...)
# else: renderer = BaseRenderer(...)

# APPEND one line before the else:
# elif stype == "vessel": renderer = VesselRenderer(...)
```
Rationale: preserves the per-branch-kwargs surface; no behaviour change outside the new branch; minimal review diff. Refactor-to-dict deferred to a follow-up issue.

**XSS-coverage guard (`scripts/enforcement/check-report-model-xss-coverage.sh`):**
```
for each model file in solvers/orcaflex/reporting/models/:
  collect str / list[str] fields added since last tag
  for each field: require a matching assertion in test_html_injection.py
  exit 1 if any field lacks coverage
```

**SRI pin guard (`scripts/enforcement/check-plotly-sri-pin.sh`) — extended scope:**
```
read PLOTLY_JS_VERSION from report_generator.py
read PLOTLY_JS_SRI from report_generator.py
read plotly wheel version from uv lock
if PLOTLY_JS_VERSION != wheel_version: exit 1 (version drift)
compute expected_sri = sha384(curl https://cdn.plot.ly/plotly-$PLOTLY_JS_VERSION.min.js)
if expected_sri != PLOTLY_JS_SRI: exit 1 (SRI-hash drift)
```

**Legacy deprecation (aligned — no self-contradiction):**
```
# digitalmodel/orcaflex/reporting/__init__.py
warnings.warn(
  "digitalmodel.orcaflex.reporting is superseded by "
  "digitalmodel.solvers.orcaflex.reporting; will be removed in v<N+2>",
  DeprecationWarning, stacklevel=2,
)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py` | 6th renderer strategy |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py` | vessel-specific OrcFxAPI adapter + `to_other_structures_dict` bridge |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py` | append one `elif` to dispatch (NOT dict-rewrite) |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/aggregator.py` | wire vessel extractor into `_safe_extract` chain |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/report.py` + add `models/vessel_motion.py` | Pydantic fields for hull particulars, RAO refs, 6DOF stats, watch-circle |
| Delete | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/` | Option A (default): empty package removed |
| Extend | `digitalmodel/tests/solvers/orcaflex/reporting/test_report_generator.py` | add vessel-dispatch case (NOT new file — r1 Finding 8) |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_vessel_renderer.py` | TDD vessel renderer (rendering-specific cases only; dispatch lives in `test_report_generator.py`) |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_vessel_extractor.py` | TDD vessel extractor |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/fixtures/{pipeline,riser,jumper,mooring,installation,vessel}/` | per-type fixture subtree |
| Modify | `digitalmodel/tests/solvers/orcaflex/reporting/fixture_helpers.py` | refactor to index by structure_type; migrate FPSO/mooring fixtures |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_per_type_snapshots.py` | fixture parity sweep |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_from_dict_all_models.py` | spec P-requirement: offline `from_dict` across all 11 models |
| Re-baseline | `digitalmodel/tests/solvers/orcaflex/reporting/test_fpso_fixture_snapshot.py` + snapshot file | FPSO snapshot diverges once `VesselRenderer` wired — protocol: A/B/C commits |
| Modify | `digitalmodel/tests/solvers/orcaflex/reporting/test_html_injection.py` | extend with vessel fields |
| **Create** | **`$EXAMPLES_DIR/riser_scr001.html`** | **spec AC line 945 — golden HTML example 1** |
| **Create** | **`$EXAMPLES_DIR/mooring_fpso_turret.html`** | **spec AC line 945 — golden HTML example 2** |
| **Create** | **`$EXAMPLES_DIR/README.md`** | context for golden examples + regen instructions |
| Create | `scripts/enforcement/check-report-model-xss-coverage.sh` | L2 guard per `.claude/rules/patterns.md` |
| Create | `scripts/enforcement/check-plotly-sri-pin.sh` | L2 guard (version + SRI-hash, both checks) |
| Modify | `digitalmodel/src/digitalmodel/orcaflex/reporting/__init__.py` | emit `DeprecationWarning` (Option A default) |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_generate_report_dispatches_vessel (in `test_report_generator.py`) | `report_generator` routes `structure_type="vessel"` to `VesselRenderer` via the elif ladder | ReportData with structure_type="vessel" | renderer is `VesselRenderer` instance, not `BaseRenderer` |
| test_dispatch_ladder_parity | every `renderers/*.py` class with `structure_type` attribute has a matching elif branch | current tree | no orphan renderer / no missing branch |
| test_vessel_renderer_all_16_sections | canonical 16-section layout emitted | minimal vessel ReportData | 16 section anchors present in order |
| test_vessel_extractor_hull_particulars | hull LPP/beam/draft/displacement read | mock OrcFxAPI vessel object | `VesselExtract.hull.length_pp == expected` |
| test_vessel_extractor_6dof_stats | per-DOF mean/std/p95/max computed | mock time-series array | stats match numpy reference within 1e-6 |
| test_vessel_extractor_watch_circle | watch-circle radius from XY excursion | synthetic circular motion | radius matches geometric expectation |
| test_vessel_renderer_xss_escaped | hull name / RAO ref escaped | `<script>alert(1)</script>` in name | `&lt;script&gt;` in output, no raw `<script>` |
| test_vessel_to_other_structures_dict_consistent | same vessel renders consistent fields top-level vs. nested | `VesselExtract` instance | `to_other_structures_dict()` ⊂ `OtherStructures.vessels[]` shape |
| test_from_dict_all_models_offline (parameterised) | spec P-requirement: all 11 models construct from `dict` without OrcFxAPI | serialized fixture for each model | round-trips via `model_validate` |
| test_per_type_snapshot_pipeline | pipeline snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_riser | riser snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_jumper | jumper snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_mooring | mooring snapshot stable (migrated from FPSO path) | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_installation | installation snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_vessel | vessel snapshot stable (migrated FPSO or generic) | fixture → renderer | matches stored snapshot |
| test_fpso_rebaselined_with_vessel_renderer | re-baselined FPSO turret snapshot uses `VesselRenderer`, not `BaseRenderer` | `fpso_turret` fixture | html contains vessel-section markers, NOT BaseRenderer fallback markers |
| test_golden_riser_html_committed | golden example exists and parses | `$EXAMPLES_DIR/riser_scr001.html` | file exists, `html.parser.HTMLParser` parses, has all mandatory anchors |
| test_golden_mooring_html_committed | golden example exists and parses | `$EXAMPLES_DIR/mooring_fpso_turret.html` | file exists, `html.parser.HTMLParser` parses, has all mandatory anchors |
| test_xss_coverage_script_fails_on_unguarded_field | new str field without test triggers exit 1 | synthetic commit adding `foo: str` | script exit code != 0 |
| test_sri_pin_script_detects_version_drift | mismatched plotly wheel vs `PLOTLY_JS_VERSION` | synthetic mismatch | script exit code != 0 |
| test_sri_pin_script_detects_hash_drift | `PLOTLY_JS_VERSION` bumped but `PLOTLY_JS_SRI` stale | synthetic mismatch | script exit code != 0 (MINOR-4 fix) |
| test_legacy_module_emits_deprecation | importing `digitalmodel.orcaflex.reporting` warns | `import` statement | `DeprecationWarning` raised |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest digitalmodel/tests/solvers/orcaflex/reporting/ -v`
- [ ] Full regression: `uv run pytest digitalmodel/` passes
- [ ] `report_generator.generate_orcaflex_report(..., structure_type="vessel", ...)` emits a 16-section vessel report without `BaseRenderer` fallback
- [ ] Dispatch change is an **append-elif**, not a ladder-to-dict rewrite (diff review)
- [ ] FPSO snapshot **re-baselined** against `VesselRenderer` per A/B/C commit protocol (§ FPSO Snapshot Re-baseline Protocol)
- [ ] Per-type snapshot tests for all 6 structure types exist under `tests/.../fixtures/{type}/` and pass
- [ ] `fixture_helpers.py` refactored to index by `structure_type`; existing fpso/mooring fixtures migrated
- [ ] **spec P-requirement:** `test_from_dict_all_models_offline` passes — all 11 Pydantic models construct from `dict` without OrcFxAPI handle (MINOR-2 fix)
- [ ] **spec AC line 945:** ≥ 2 golden HTML example reports committed to `$EXAMPLES_DIR/` (default path resolution from § Docs Path Binding); files parse via `html.parser.HTMLParser` and contain all mandatory anchors
- [ ] `$EXAMPLES_DIR` resolved against current `docs/modules/` vs `docs/domains/` rename decision at implementation start (not at plan time)
- [ ] `scripts/enforcement/check-report-model-xss-coverage.sh` exits 0 on clean tree, catches synthetic str-field regression
- [ ] `scripts/enforcement/check-plotly-sri-pin.sh` exits 0 on clean tree, catches BOTH synthetic version drift AND synthetic SRI-hash drift (MINOR-4 fix)
- [ ] Legacy `digitalmodel.orcaflex.reporting` emits `DeprecationWarning` on import (default Option A); deprecation comment language self-consistent ("will be removed in v<N+2>")
- [ ] `structure_types/` empty package removed (default Option A); no import references remain
- [ ] Docs updated: `docs/plans/README.md` indexes this plan
- [ ] **r2 re-cross-review:** fresh Claude + Codex adversarial reviews posted to `scripts/review/results/` for r2 BEFORE `status:plan-approved`; Gemini attempted with explicit fallback (NO_OUTPUT ≥ 2 attempts with stderr capture → proceed on Claude+Codex consensus) (MINOR-5 fix)
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled in after r2 review completes. r1 verdicts captured below as history; r2 needs its own reviews. -->

| Provider | Verdict (r1) | Key findings (r1) |
|---|---|---|
| Claude (r1) | MAJOR | 12 findings; 7 blockers — dispatch refactor ambiguity, FPSO re-baseline, Gap #8 false, vessel data-contract, fixtures dir, TRADEOFFs, Gemini fallback |
| Codex/adversarial (r1) | MAJOR (REQUEST_CHANGES) | 3 MAJOR + 5 MINOR — docs-rename ignored, golden HTML missing, fabricated boundary-conditions TDD, dispatch pseudocode mismatch, from_dict coverage, source-count, SRI-hash-scope, Gemini lineage |
| Gemini (r1) | NO_OUTPUT | 14 attempts on spec v1.13; r2 re-attempt with explicit fallback |

**Overall result (r1):** REQUEST_CHANGES — r2 rewrite in progress (this document).

**Overall result (r2):** TBD — pending fresh review sweep.

Revisions made based on r1 review:
- See § Revision Notes (r2) at top of plan for defect-by-defect mapping.

---

## Risks and Open Questions

- **Risk (NEW — MAJOR-1):** `docs/modules/` → `docs/domains/` rename decision is unresolved. Plan binds `$EXAMPLES_DIR` variable rather than hardcoding; implementation blocks until resolution. Same failure mode as #510.
- **Risk (NEW — r1 Finding 2):** FPSO snapshot silent regression. `test_fpso_fixture_snapshot.py` today captures the vessel-as-BaseRenderer fallback output. Wiring `VesselRenderer` without the A/B/C re-baseline commit protocol will silently break or corrupt the snapshot assertion.
- **Risk (NEW — r1 Finding 4):** Vessel-as-top-level vs. vessel-as-subcomponent: `models/other_structures.py:20` already carries `vessels: List[dict]`; a mooring report embeds vessels. New `VesselExtract` must use `to_other_structures_dict()` adapter to avoid two divergent vessel-data shapes.
- **Risk (NEW — r1 Finding 5):** `tests/.../fixtures/` directory does not exist. Creating the subtree + migrating FPSO/mooring fixtures + refactoring `fixture_helpers.py` is a non-trivial step; treated as its own Files-to-Change row, not a single create.
- **Risk:** Vessel extractor requires live OrcFxAPI for RAO introspection; `from_dict()` offline path must be preserved per spec — mock interface must mirror the live one byte-for-byte on all required fields.
- **Risk:** Snapshot tests for pipeline/riser/jumper/installation will likely reveal rendering drift that was never caught (mooring+FPSO were the only snapshot-covered types). Budget time for initial snapshot baselining.
- **Risk:** Pre-computed design-check data interface with `mooring_analysis/` and `orcaflex_fatigue_analysis.py` is a consumption contract; do NOT expand scope into those analyzers.
- **Risk:** Shared HTML primitives (header bar, CDN pin, `_escape`) are attractive to promote into a common lib with #282 (OrcaWave), but that promotion is **out of scope** for this plan and flagged for separate coordination.
- **Risk (MINOR-5):** Gemini NO_OUTPUT x14 lineage on spec v1.13. r2 acceptance requires re-cross-review with explicit NO_OUTPUT fallback to avoid an un-gated blocker.

**Locked TRADEOFFS (defaults applied; user may override before implementation):**

- **Legacy `digitalmodel/orcaflex/reporting/` disposition:** **Default = Option A (Deprecate).** Emit `DeprecationWarning` on import; remove in release N+2. Option B (Merge) or C (Coexist) available by user override.
- **Vessel renderer scope:** **Default = Option A (Minimum-viable).** 16-section layout with hull particulars, 6DOF motion stats, watch-circle, pass/fail hook. RAO plotting / thruster viz / motion-trace animation deferred. Option B (Full first-class) available by user override (bumps complexity to T2-large).
- **`structure_types/` empty package:** **Default = Option A (Remove).** Delete the package; `renderers/` is canonical. Option B (populate as type enum) available by user override.

- **Open:** Should the vessel RAO reference be captured by file hash (reproducibility) or just by filename (convenience)?
- **Open:** Should the XSS-coverage script be promoted to a pre-commit hook (Level 3 per `.claude/rules/patterns.md`) or stay Level-2 (CI-only)?
- **Open (MAJOR-1):** Name of the rename-tracking issue (`docs/modules/` → `docs/domains/`) that `$EXAMPLES_DIR` depends on.

---

## Complexity: T2-large

**Re-evaluated from r1's T2.** Justification for upgrade:
- r1 treated `fixtures/` subtree creation as a single "Create" row; r1-Claude Finding 5 shows this is a T2-task-on-its-own (directory creation + `fixture_helpers.py` refactor + FPSO/mooring fixture migration).
- r1 did not account for the FPSO snapshot re-baseline A/B/C commit protocol.
- r1 did not account for the spec-mandated golden HTML examples (MAJOR-2) — net-new deliverable requiring rendered output from real fixtures.
- r1 did not account for `from_dict_all_models_offline` parametrisation across 11 models (MINOR-2 promoted to AC).
- r1 did not account for the docs-rename-binding resolution step (MAJOR-1).
- SRI guard scope doubled (MINOR-4).

The work remains **completion + gap-close**, not greenfield, and does NOT introduce new architectural layers — but the defect list expanded the deliverable surface beyond T2's typical envelope. If the user selects Legacy Option B (Merge) or Vessel Option B (Full first-class) on top of T2-large, escalate to T3.
