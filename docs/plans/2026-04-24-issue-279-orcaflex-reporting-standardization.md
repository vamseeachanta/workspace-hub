# Plan for #279: Standardize analysis reporting for each OrcaFlex structure type (WRK-129)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/279
> **Review artifacts:** scripts/review/results/2026-04-24-plan-279-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py` (107 lines) — `generate_orcaflex_report()` entry point, Plotly 2.26.0 CDN pinning + SRI, renderer-strategy dispatch by `structure_type.lower()`, `_escape()` XSS guard integration.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/` — 5 of 6 renderers (`pipeline.py`, `riser.py`, `jumper.py`, `mooring.py`, `installation.py`) plus `base.py`. **Missing: `vessel.py`.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/` — 17 section modules matching the canonical 16-section FEA layout + `utils.py` with `_escape()`.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/` — 11 Pydantic composition schemas (analysis, boundary_conditions, design_checks, fatigue, geometry, loads, materials, mesh, other_structures, report, results).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/` — 7 OrcFxAPI live adapters (`aggregator.py`, `boundary_conditions_extractor.py`, `geometry_extractor.py`, `loads_extractor.py`, `materials_extractor.py`, `mesh_extractor.py`, `mooring_extractor.py`, `results_extractor.py`). **Missing: `vessel_extractor.py`.**
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/__init__.py` — **empty package**, intent unclear (possible duplicate of `renderers/`).
- Found (legacy parallel path): `digitalmodel/src/digitalmodel/orcaflex/reporting/` — 8-section `OrcaFlexReportBuilder` (`builder.py`, `config.py`, `sections/`) using Bootstrap blue (`#0d6efd`) vs. spec's `#2c3e50`. Superseded by the `solvers/orcaflex/reporting/` tree but still shipped.
- Found: `digitalmodel/tests/solvers/orcaflex/reporting/` — 13 test files including `test_cdn_security.py`, `test_html_injection.py`, `test_fixture_integration.py`, `test_fixture_snapshot.py`, `test_fpso_fixture_integration.py`, `test_fpso_fixture_snapshot.py`, `test_mooring_report.py`, `test_renderers.py`, `test_section_builders.py`, `test_extractors.py`, `test_models.py`.
- Gap: no `vessel` renderer, no `vessel_extractor`, no per-type fixtures for pipeline/riser/jumper/installation/vessel (only mooring + FPSO exist).
- Gap: no CI guard that XSS-escape tests accompany new `str`/`list[str]` model fields (spec P12).
- Gap: no guard that Plotly wheel version matches `PLOTLY_JS_VERSION` constant (SRI drift).

### Standards
| Standard | Status | Source |
|---|---|---|
| N/A — reporting-framework issue | n/a | reporting is format/presentation, no engineering code |

Standards ledger not applicable: the design-check *content* (DNV-OS-F101, API-RP-2SK, etc.) is consumed as pre-computed data from `mooring_analysis/` and `orcaflex_fatigue_analysis.py`; this plan does not evaluate standards, it renders results.

### LLM Wiki pages consulted
- No relevant wiki pages. Marine-engineering wiki entries describe physical analyses, not reporting conventions. Explicitly verified empty set.

### Documents consulted
- Issue body `/tmp/orca-batch-2026-04-24/issue-279-body.txt` — embedded Final Plan v1.13, module target `solvers/orcaflex/reporting`, 6 structure types including vessel, 16-section canonical layout, Codex APPROVE iter 14, Gemini NO_OUTPUT x14.
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — cross-cutting parent; does not supersede.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — batch-orchestration doc creating this plan.
- Pod intel `/tmp/orca-batch-2026-04-24/intel-279.md` — Explorer CRITICAL FINDING: framework substantially built; delta = vessel + fixtures + cleanup; T2 not T3.
- Related issue #282 — OrcaWave reporting; shared HTML scaffold opportunity flagged but explicitly out of scope here.
- Related issues WRK-125/WRK-127/WRK-045/WRK-046/WRK-064 — upstream analyzers that feed pre-computed check data; not modified by this plan.

### Gaps identified
1. `vessel` renderer — spec lists 6 structure types, only 5 exist; `report_generator.py` falls through to `BaseRenderer`.
2. `vessel_extractor.py` — no hull RAO / watch-circle / 6DOF motion extractor.
3. `structure_types/` package — empty; decision required (populate or remove).
4. Legacy `digitalmodel/orcaflex/reporting/` disposition — deprecate vs. merge vs. coexist.
5. Per-type snapshot fixtures for pipeline, riser, jumper, installation, vessel.
6. XSS-escape lint hook for new model string fields.
7. SRI / Plotly wheel drift guard.
8. Wiring audit: `boundary_conditions_extractor.py` referenced in intel but import path into `aggregator.py` unverified.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#279` — OPEN — "WRK-129: Standardize analysis reporting for each OrcaFlex structure type" (per issue JSON)
- `#282` — referenced; OrcaWave reporting sibling; shared-scaffold flag only

**File existence** (`ls` 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/{base,pipeline,riser,jumper,mooring,installation}.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py`
- EXISTS (empty): `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/__init__.py`
- EXISTS (legacy): `digitalmodel/src/digitalmodel/orcaflex/reporting/{builder.py,config.py,sections/}`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/reporting/` with 13 test files

**Line excerpts** — `renderers/` directory listing confirms 6 files (base + 5 types, no vessel); `extractors/` listing confirms 8 files (no vessel_extractor).

**Gap proofs**:
- `ls digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py 2>&1` → "No such file or directory" (confirms missing renderer).
- `ls digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py 2>&1` → "No such file or directory" (confirms missing extractor).
- `ls digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/` → only `__init__.py` (confirms empty package).

<!-- Source count: issue body + pod intel + batch-design plan + intensive-plan + legacy module listing = 5 distinct sources. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md |
| Vessel renderer | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/vessel.py` |
| Vessel extractor | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py` |
| Vessel model fields | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/report.py` (extend `StructureData`), new `models/vessel_motion.py` if needed |
| Renderer dispatch | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py` (add `"vessel"` branch) |
| Vessel tests | `digitalmodel/tests/solvers/orcaflex/reporting/test_vessel_renderer.py`, `test_vessel_extractor.py` |
| Per-type fixtures | `digitalmodel/tests/solvers/orcaflex/reporting/fixtures/{pipeline,riser,jumper,installation,vessel}/` + snapshot tests |
| XSS escape lint | `scripts/enforcement/check-report-model-xss-coverage.sh` |
| SRI drift guard | `scripts/enforcement/check-plotly-sri-pin.sh` |
| Legacy deprecation notice | `digitalmodel/src/digitalmodel/orcaflex/reporting/__init__.py` (emit `DeprecationWarning`) |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-279-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-279-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-279-gemini.md |
| Docs updates | docs/plans/README.md (index entry) |

---

## Deliverable

A completed 6-structure-type reporting framework at `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/` with vessel support, per-type snapshot-tested fixtures, XSS and SRI regression guards, and a documented deprecation path for the legacy `digitalmodel/orcaflex/reporting/` builder.

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
    read applied RAO references (file + label)
    from static result: equilibrium position, heel/trim
    from dynamic result: per-DOF time-series summary (mean/std/p95/max)
    compute watch-circle radius from horizontal plane excursion
    return Pydantic VesselExtract for aggregator
```

**Dispatch addition (`report_generator.py`):**
```
renderer_map = {
  "pipeline": PipelineRenderer, "riser": RiserRenderer,
  "jumper": JumperRenderer, "mooring": MooringRenderer,
  "installation": InstallationRenderer,
  "vessel": VesselRenderer,   # <- new
}
```

**XSS-coverage guard (`scripts/enforcement/check-report-model-xss-coverage.sh`):**
```
for each model file in solvers/orcaflex/reporting/models/:
  collect str / list[str] fields added since last tag
  for each field: require a matching assertion in test_html_injection.py
  exit 1 if any field lacks coverage
```

**SRI pin guard (`scripts/enforcement/check-plotly-sri-pin.sh`):**
```
read PLOTLY_JS_VERSION from report_generator.py
read plotly wheel version from uv lock
if mismatch: exit 1 with remediation hint
```

**Legacy deprecation (non-removal, single release):**
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
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/vessel_extractor.py` | vessel-specific OrcFxAPI adapter |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py` | add `"vessel"` to dispatch map |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/aggregator.py` | wire vessel extractor + verify `boundary_conditions_extractor` is wired |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/report.py` (or add `models/vessel_motion.py`) | Pydantic fields for hull particulars, RAO refs, 6DOF stats, watch-circle |
| Decide + Edit | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/structure_types/__init__.py` | populate with type-enum OR delete package (see TRADEOFF) |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_vessel_renderer.py` | TDD vessel renderer |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_vessel_extractor.py` | TDD vessel extractor |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/fixtures/{pipeline,riser,jumper,installation,vessel}/` | per-type snapshot fixtures |
| Create | `digitalmodel/tests/solvers/orcaflex/reporting/test_per_type_snapshots.py` | fixture parity sweep |
| Modify | `digitalmodel/tests/solvers/orcaflex/reporting/test_html_injection.py` | extend with vessel fields |
| Create | `scripts/enforcement/check-report-model-xss-coverage.sh` | L2 guard per `.claude/rules/patterns.md` |
| Create | `scripts/enforcement/check-plotly-sri-pin.sh` | L2 guard |
| Modify | `digitalmodel/src/digitalmodel/orcaflex/reporting/__init__.py` | emit `DeprecationWarning` (if TRADEOFF = deprecate) |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_vessel_renderer_dispatched | `report_generator` routes `structure_type="vessel"` to `VesselRenderer` | ReportData with structure_type="vessel" | html containing vessel sections, not BaseRenderer fallback |
| test_vessel_renderer_all_16_sections | canonical 16-section layout emitted | minimal vessel ReportData | 16 section anchors present in order |
| test_vessel_extractor_hull_particulars | hull LPP/beam/draft/displacement read | mock OrcFxAPI vessel object | `VesselExtract.hull.length_pp == expected` |
| test_vessel_extractor_6dof_stats | per-DOF mean/std/p95/max computed | mock time-series array | stats match numpy reference within 1e-6 |
| test_vessel_extractor_watch_circle | watch-circle radius from XY excursion | synthetic circular motion | radius matches geometric expectation |
| test_vessel_renderer_xss_escaped | hull name / RAO ref escaped | `<script>alert(1)</script>` in name | `&lt;script&gt;` in output, no raw `<script>` |
| test_vessel_from_dict_no_orcfxapi | `VesselExtract.from_dict()` works without OrcFxAPI handle | plain Python dict | valid Pydantic instance |
| test_per_type_snapshot_pipeline | pipeline snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_riser | riser snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_jumper | jumper snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_installation | installation snapshot stable | fixture → renderer | matches stored snapshot |
| test_per_type_snapshot_vessel | vessel snapshot stable | fixture → renderer | matches stored snapshot |
| test_boundary_conditions_wired_in_aggregator | `boundary_conditions_extractor` called by `aggregator.extract_all()` | mock model | call asserted once |
| test_xss_coverage_script_fails_on_unguarded_field | new str field without test triggers exit 1 | synthetic commit adding `foo: str` | script exit code != 0 |
| test_sri_pin_script_detects_drift | mismatched plotly wheel vs `PLOTLY_JS_VERSION` | synthetic mismatch | script exit code != 0 |
| test_legacy_module_emits_deprecation | importing `digitalmodel.orcaflex.reporting` warns | `import` statement | `DeprecationWarning` raised |
| test_structure_types_decision_consistent | `structure_types/` contents match dispatch map | current tree | no orphan/duplicate declarations |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest digitalmodel/tests/solvers/orcaflex/reporting/ -v`
- [ ] Full regression: `uv run pytest digitalmodel/` passes
- [ ] `report_generator.generate_orcaflex_report(..., structure_type="vessel", ...)` emits a 16-section vessel report without `BaseRenderer` fallback
- [ ] Snapshot tests for all 6 structure types exist and pass
- [ ] `scripts/enforcement/check-report-model-xss-coverage.sh` exits 0 on clean tree, catches synthetic regression
- [ ] `scripts/enforcement/check-plotly-sri-pin.sh` exits 0 on clean tree, catches synthetic version drift
- [ ] Legacy `digitalmodel.orcaflex.reporting` emits `DeprecationWarning` on import (if TRADEOFF choice = deprecate)
- [ ] `structure_types/` package disposition applied (populated or removed per TRADEOFF)
- [ ] Docs updated: `docs/plans/README.md` indexes this plan
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | placeholder |
| Codex | TBD | placeholder |
| Gemini | TBD | placeholder |

**Overall result:** TBD

Revisions made based on review:
- (none yet — draft)

---

## Risks and Open Questions

- **Risk:** Vessel extractor requires live OrcFxAPI for RAO introspection; `from_dict()` offline path must be preserved per spec — mock interface must mirror the live one byte-for-byte on all required fields.
- **Risk:** Snapshot tests for pipeline/riser/jumper/installation will likely reveal rendering drift that was never caught (mooring+FPSO were the only snapshot-covered types). Budget time for initial snapshot baselining.
- **Risk:** Spec v1.13 had Gemini NO_OUTPUT x14 — the plan should re-run cross-review against the as-shipped code, not just the spec, before close.
- **Risk:** Pre-computed design-check data interface with `mooring_analysis/` and `orcaflex_fatigue_analysis.py` is a consumption contract; do NOT expand scope into those analyzers.
- **Risk:** Shared HTML primitives (header bar, CDN pin, `_escape`) are attractive to promote into a common lib with #282 (OrcaWave), but that promotion is **out of scope** for this plan and flagged for separate coordination.

**[TRADEOFF FOR USER] — Legacy `digitalmodel/orcaflex/reporting/` disposition:**
- **Option A — Deprecate (recommended):** Emit `DeprecationWarning` on import; remove in release N+2. Pros: one canonical path, minimal churn. Cons: users of the 8-section quick report lose it without a direct replacement.
- **Option B — Merge:** Fold the 8-section `OrcaFlexReportBuilder` into `solvers/orcaflex/reporting/` as a "quick" preset alongside the 16-section "full" preset. Pros: preserves both UX modes. Cons: two section schemas in one tree; surface-area doubles.
- **Option C — Coexist:** Leave both paths; document the legacy as a "sim-quick-look" tool. Pros: zero risk. Cons: confusion persists, Bootstrap-blue vs. `#2c3e50` styling diverges, two test suites to maintain.

**[TRADEOFF FOR USER] — Vessel renderer scope:**
- **Option A — Minimum-viable (recommended for #279):** 16-section layout with hull particulars, 6DOF motion stats, watch-circle, pass/fail hook for pre-computed station-keeping checks. Defer RAO plotting, thruster-allocation visualizations, and time-domain motion traces to a follow-up.
- **Option B — Full first-class:** Include interactive RAO polar plots, thruster-load pie charts, watch-circle animation, time-domain 6DOF traces. Pros: matches riser/mooring depth. Cons: ~3x work; pulls plotting primitives that don't exist yet and may belong in a shared lib with #282.

**[TRADEOFF FOR USER] — `structure_types/` empty package:**
- **Option A — Remove:** Delete the package; `renderers/` is the canonical strategy location. Cleanest.
- **Option B — Populate as type enum / registry:** Use `structure_types/` for a central `StructureType` enum and a registry mapping; `renderers/` becomes implementation-only. Slightly cleaner dispatch but new abstraction layer.

- **Open:** Should the vessel RAO reference be captured by file hash (reproducibility) or just by filename (convenience)? Flag for user.
- **Open:** Should the XSS-coverage script be promoted to a pre-commit hook (Level 3 per `.claude/rules/patterns.md`) or stay Level-2 (CI-only)?

---

## Complexity: T2

**T2** — completion + gap-close of an already-substantial framework. One new renderer, one new extractor, one dispatch edit, ~5 fixture sets, 2 enforcement scripts, 1 legacy-deprecation edit, 1 `structure_types/` disposition. No new architectural layer; no cross-repo coordination (shared primitives with #282 explicitly flagged out of scope). If the user selects Legacy Option B (Merge) or Vessel Option B (Full first-class), promote to T2-large.
