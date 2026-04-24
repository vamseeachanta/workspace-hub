# Adversarial Review — Plan for Issue #282 (OrcaWave Reporting Standardization, WRK-130)

**Reviewer:** Claude (adversarial stance, defect-hunter)
**Date:** 2026-04-24
**Plan under review:** `docs/plans/2026-04-24-issue-282-orcawave-reporting-standardization.md`
**Intel:** `/tmp/orca-batch-2026-04-24/intel-282.md`
**Issue JSON:** `/tmp/orca-batch-2026-04-24/issue-282.json`

---

## Verdict: **MINOR**

The plan is well-researched, evidence-grounded, and honestly flags open questions. However it suffers from **six MINOR defects** centered on (1) unresolved tradeoff decisions left as `[TRADEOFF FOR USER]` rather than a recommended default the planner commits to, (2) an acceptance-criteria omission against the issue body, (3) one TDD gap, (4) an ambiguous alias-map decision, and (5) a scope-boundary risk with the benchmark plotter modules. Nothing rises to MAJOR: no self-labeling, no past-tense drift, no hallucinated paths, no scope-drift into #279. The plan is approvable once the tradeoffs collapse to single choices and the acceptance criteria are reconciled with the issue body.

---

## Defect Checklist

| # | Category | Status | Severity |
|---|---|---|---|
| 1 | Scope drift | MINOR | §1 |
| 2 | Evidence gaps | CLEAN | — |
| 3 | TDD completeness | MINOR | §2, §3 |
| 4 | Missing edge cases | MINOR | §4 |
| 5 | Coupling risk | MINOR | §5 |
| 6 | Past-tense drift | CLEAN | — |
| 7 | Self-labeling | CLEAN | — |
| 8 | Plan-vs-intel contradiction | MINOR | §6 |
| 9 | Complexity mismatch | CLEAN | — |
| 10 | Template-dispatch mechanism named? | MINOR | §7 |
| 11 | WRK-115 coupling addressed? | MINOR | §8 |
| 12 | `ship` vs `tanker` / `semi-sub` vs `semi_pontoon` aliasing | MINOR | §9 |

---

## Specific Defects

### §1. Scope-creep risk around benchmark_plotter modules (MINOR)

The plan's Deliverable says *"reusing all existing builders, models, and plotters unchanged where possible"* — but Gap #4 in the Resource-Intelligence section states r4 layout decisions are *"distributed across benchmark_* modules,"* and the plan never decides whether those modules are treated as part of the dispatched template strategy or left alone. If a strategy's `section_order` includes per-DOF benchmark sections, the dispatch layer will necessarily drive `benchmark_plotter.py` / `benchmark_dof_sections.py` / `benchmark_dof_tables.py` — yet none of these appear in the Files-to-Change table. Either:
- the strategies only compose `builders_header` / `builders_hydrostatics` / `builders_responses` (plan should say so explicitly and drop the r4-canonical-template framing), **or**
- the strategies also orchestrate benchmark-plotter outputs (plan needs a clear reuse contract and at least one test proving a benchmark section renders via the new dispatch).

**Fix:** state unambiguously in the Deliverable section which existing modules the strategies call and which they do not touch.

### §2. Missing TDD for spec-mandated "roll critical damping" computation (MINOR)

The issue body's acceptance criterion reads: *"Roll critical damping plot: radiation damping as % of critical vs frequency, with annotation at peak roll RAO period"*. The plan's acceptance criteria item 7 only says *"Roll-damping peak-period annotation verified rendered in at least one hull template"* — that covers the annotation but **not** the % of critical damping computation itself. The TDD test `test_roll_damping_peak_period_annotation` verifies annotation presence only. No test verifies that radiation damping is correctly normalized as a percentage of critical damping (i.e., `b_rad(ω) / b_crit` where `b_crit = 2·sqrt((A+I)·C)`).

**Fix:** add a test (e.g., `test_roll_damping_percent_critical_computation`) with a known input where `b_crit` can be hand-computed and verify the rendered curve/value.

### §3. Missing TDD coverage for solver-comparison and mesh-quality sections (MINOR)

Issue body mandates *"Solver comparison layout when multiple results available"* and *"Mesh quality summary section with panel statistics."* The plan acceptance criteria mentions neither explicitly, and no TDD entry covers either. The intel explicitly flags this (Gap #6: "Confirm coverage matches spec asks — panel count, aspect ratio, skewness; GM, KB, KG, displacement"). Absent tests, the "standardization" can ship without these sections and still pass the suite.

**Fix:** add `test_dispatch_includes_mesh_quality_section` and `test_dispatch_solver_comparison_when_multi_solver_results`.

### §4. Edge case: LNGC side-by-side / multi-body hook is hand-waved (MINOR)

The strategies table includes `strategies/lngc.py` with comment *"sloshing note (optional); side-by-side preamble hook"*. The related plan #2458 handles multi-body explicitly, and #282's intel calls out the LNGC side-by-side relevance. But the plan leaves "side-by-side preamble hook" as a comment with no contract, no test, and no deliverable for multi-body report data shape. This is an edge case that the plan acknowledges but does not resolve. Either (a) scope it OUT and say so, or (b) define the hook signature and add a test.

**Fix:** declare side-by-side OUT of scope (defer to #2458 integration) or define the hook with a TDD entry.

### §5. Coupling risk: `report_builders_header.py` compat shim adds indirection to a shared primitive (MINOR)

The plan modifies `report_builders_header.py` to add *"a deprecation-compat shim on `HULL_TYPE_NOTES` keys via alias lookup (no hard rename)."* But the intel flags `report_builders_header.py` as a **shared** primitive across both the OrcaWave pod (#282) and implicitly OrcaFlex (#279) via Plotly-layout reuse. Mutating a shared header module with hull-taxonomy logic couples the two pods' failure modes: a bug in the alias shim now breaks both report pipelines. A safer design is to isolate the alias shim inside `report_templates/hull_taxonomy.py` and have it wrap `_get_hull_type_note()` without modifying `report_builders_header.py` directly.

**Fix:** either prove #279 does not import `HULL_TYPE_NOTES` (one grep; cite result) or move the shim out of the shared module.

### §6. Plan-vs-intel contradiction: alias-direction ambiguity (MINOR)

The intel (Gap #1) says: *"Need alias/remap: `ship` -> `tanker` (or new entry), `semi-sub` -> `semi_pontoon` (rename or add key)."* — i.e., the intel suggests aliasing runs FROM the spec vocabulary (`ship`, `semi-sub`) TO the existing dict keys (`tanker`, `semi_pontoon`).

The plan (line 117-123) instead says: *"`tanker` -> `ship`", "`semi_pontoon` -> `semi_sub`"* — i.e., aliasing runs the OPPOSITE direction, from the existing keys to a NEW canonical vocabulary. This is a silent reversal of the intel's recommendation and implies the plan is introducing NEW keys `ship` and `semi_sub` into `HULL_TYPE_NOTES` (or a new registry) rather than aliasing to the 8 existing keys.

This is NOT obviously wrong — the canonical-naming direction is defensible — but the plan never justifies why it inverted the intel's direction, and the "Open question" at line 292 explicitly admits the plan *"assumes add + alias, no rename"* without stating which keys get added where. Reviewers will legitimately ask: does `HULL_TYPE_NOTES` gain `ship` and `semi_sub` keys (doubling content)? or does the alias map live entirely in `hull_taxonomy.py` and never touch the dict? The plan is ambiguous.

**Fix:** pick one direction and state the resulting state of `HULL_TYPE_NOTES` keys explicitly (8 keys unchanged + alias map in taxonomy module, OR 10 keys after adding `ship`/`semi_sub` + back-compat aliases).

### §7. Template-dispatch mechanism: recommendation given, but plan text waffles (MINOR)

The plan **does** name three candidates (Registry / Strategy / match-case) and picks Strategy pattern as the default absent user input. This is a legitimate presentation of the tradeoff per `feedback_never_offer_to_self_label_plan_approved` (user-gated).

**However**, the Pseudocode section at line 133 uses `TEMPLATE_STRATEGIES: Dict[canonical_hull_type, TemplateStrategy]` which is the **Registry** shape (dict of callables) while the per-file list in Files-to-Change shows six `strategies/*.py` modules which is the **Strategy-pattern** shape. The plan's own artifacts contradict its own stated preference.

**Fix:** align the pseudocode to the chosen option (Strategy pattern → Protocol-based classes dispatched through a small registry, with explicit class definitions per hull), OR flip the recommendation to Registry and drop the 6 strategy files. Pick one.

### §8. WRK-115 coupling: addressed, but stub-adapter's failure mode is under-specified (MINOR)

The plan presents the block-vs-stub tradeoff clearly and recommends Option 2 (stub adapter). Good.

But the adapter's failure modes are thin: `test_adapter_missing_profile_logs_warning` covers one case. What about:
- `hull_library.catalog` module itself being absent (ImportError on the adapter import)?
- `find_by_hull_type` returning multiple matches (ambiguity)?
- `find_by_hull_type` returning a profile whose `hull_type` contradicts `report_data.hull_type` (conflict resolution)?

The plan's pseudocode silently merges `profile.metadata` into a new `catalog_metadata` field on `report_data` — but `DiffractionReportData` is a Pydantic model per the intel, and adding fields requires a model change not listed in Files-to-Change.

**Fix:** either add `report_data_models.py` to Files-to-Change with the new `catalog_metadata: Optional[Dict[str, Any]]` field, or store catalog metadata in a side-channel that doesn't require model mutation.

### §9. Existing 8-hull `HULL_TYPE_NOTES` treatment: `cylinder` and `sphere` dropped silently (MINOR)

The intel enumerates 8 existing `HULL_TYPE_NOTES` keys: **barge, fpso, tanker, semi_pontoon, spar, lngc, cylinder, sphere**. The plan's canonical set is **{barge, ship, spar, semi_sub, fpso, lngc}** (6). The alias map handles `tanker`→`ship` and `semi_pontoon`→`semi_sub`. But what about `cylinder` and `sphere`?

- Are they deprecated? (no deprecation note)
- Do they become canonical 7th/8th entries? (not in the canonical set)
- Do they get their own strategies? (no `strategies/cylinder.py` or `strategies/sphere.py`)
- Are they quietly broken? (the dispatch function at line 140 raises `UnknownHullTypeError` for anything not in the alias map or canonical set — so existing fixtures using `cylinder` or `sphere` will CRASH)

This is a silent regression risk against existing `HULL_TYPE_NOTES` consumers. The issue spec lists 6 hull types; the plan faithfully implements 6; but the plan's own Risks section promises *"`HULL_TYPE_NOTES` keys unchanged — compat shim routes alias lookups via `hull_taxonomy.resolve_hull_type()`"* which is **false** if `resolve_hull_type("cylinder")` raises.

**Fix:** either (a) add `cylinder` and `sphere` to `CANONICAL_HULL_TYPES` with minimal no-op strategies, or (b) add them to the alias map routed to a generic "other" strategy, or (c) explicitly declare them out-of-scope and add a test `test_resolve_cylinder_preserves_legacy_behavior` that documents the transition.

---

## Verdict Justification

- **Not APPROVE** because six MINOR defects land on verifiable, fixable issues — the plan as written would produce code that (i) silently reverses intel direction on aliasing, (ii) crashes on `cylinder`/`sphere` legacy inputs, (iii) ships without tests for two acceptance-criteria items (solver comparison, mesh quality coverage, % critical damping calculation), (iv) contradicts itself on registry-vs-strategy dispatch shape, and (v) mutates a shared primitive (`report_builders_header.py`) without proving #279 safety.
- **Not MAJOR** because: no self-labeling, no past-tense drift, no hallucinated file paths (all cited paths verified in intel at byte-size-confirmed locations), no scope-drift into #279 (explicit Risk mitigation present), no silently-picked tradeoff on the big decisions (both big tradeoffs are flagged for user decision with recommended defaults). Evidence contract is satisfied (8 sources, verified file existence, grep proofs). Complexity T3 is consistent with 9 new files + 2 modifications + 4 test modules.

The plan is recoverable with focused edits; it is not a re-plan.

---

## Recommended Remediation Order

1. **Close the tradeoff loops** (§7, §8): pick Strategy pattern OR Registry; align pseudocode + files-to-change. Pick stub-adapter approach and add the `DiffractionReportData.catalog_metadata` field (or side-channel) to Files-to-Change.
2. **Resolve alias direction** (§6, §9): state explicitly what `HULL_TYPE_NOTES` looks like after this change; handle `cylinder`/`sphere` explicitly (no silent regression).
3. **Fill TDD gaps** (§2, §3): add tests for % critical damping, mesh quality, solver comparison.
4. **Scope hygiene** (§1, §4, §5): state whether benchmark_plotter modules are in-scope; declare side-by-side hook in-scope with contract or out-of-scope with defer-to-#2458 note; prove or move the `report_builders_header.py` shim.

No adversarial review artifact writes to git; no label change recommended until user triage.

---

## Self-check Against Reviewer Forbiddens

- No Write outside the review path (this file only).
- No `gh` / `git` calls made.
- No claim of "approved for implementation."
- Defect-hunter stance maintained; no charitable reading of ambiguous passages.
