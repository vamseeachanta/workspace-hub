# Plan for #2555: feat(gtm): vessel capability charts for contractor brochure

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2555
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2555-claude.md (live MINOR, 2026-04-29) | ...-codex.md (live MINOR, 2026-04-29) | ...-gemini.md (live MINOR, 2026-04-29)
> **Sibling overnight prompt:** `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2555-capability-charts.md`
> **Storyboard artifact:** `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` — 2 representative S-lay vessel classes (Large PLV, Shallow Water Barge) with tensioner capacity, stinger config, water-depth range, pipe-size range, sea-state limits. Header explicitly states "representative of real vessel classes" — not exact named-vessel specs. Acceptable public/inferred dataset for the chart inputs.
- Found: `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` — 2 representative CSV/HLV classes (Large CSV ~Aegir/Borealis, Medium CSV ~Normand Maximus/Seven Arctic) with crane SWL curve, RAO peaks, operational limits. Same representative-class disclaimer.
- Found: `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` — pre-computed cross-demo go/no-go matrix across 4 vessels for mudmat installation, jumper installation, and shallow pipelay. Includes head-to-head comparison narratives. This is the primary chart-feed.
- Found: `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json` — by-vessel structure comparison with crane utilisation values at fixed depth. Useful for utilisation-margin chart.
- Found: `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` — already renders a Plotly Go/No-Go heatmap (`chart-go_nogo`) for shallow pipelay at line 1086. Demonstrates that chart-rendering scaffolding exists.
- Found: `digitalmodel/examples/demos/gtm/report_template.py` — templating module that the existing 5 demo reports share. New brochure-bound charts should reuse this template path rather than introduce a new renderer.
- Gap: no consolidated brochure-ready capability chart pack exists across `digitalmodel/`, `docs/gtm/`, or `docs/reports/`. `docs/reports/gtm/` did not exist before this plan and is created here.
- Gap: the future chart-rendering entry point outside `digitalmodel/` was previously unnamed; this patch locks the intended implementation home to a new follow-on wrapper script at `scripts/gtm/render_brochure_charts.py`, which may import existing `digitalmodel/examples/demos/gtm/report_template.py` helpers without editing `digitalmodel/` source.

### Standards
| Standard | Status | Source |
|---|---|---|
| DNV-ST-F101 (Submarine Pipeline Systems, 2021) | referenced (Demo 4 inputs) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:5` |
| DNV-OS-F101 (Submarine Pipeline Systems, 2013) | inherited from upstream JSON; intentionally omitted from chart captions because DNV-ST-F101 (2021) is the controlling/current citation for shallow-pipelay framing — see C1 caption omission rationale (storyboard line 82) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:6` |
| DNV-RP-H103 (Marine Operations modelling, 2011) | referenced (Demos 3/5 inputs) | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:5` |
| DNV-ST-N001 (Marine Operations & Marine Warranty, 2021) | referenced (Demos 3/5 inputs) | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:6` |
| DNV-OS-H101 (Marine Operations, General, 2011) | referenced (Demos 3/5 inputs) — covers general marine-operations governing-load envelope alongside DNV-ST-N001 | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:7` |
| API RP 1111 (Offshore Hydrocarbon Pipelines, 2015) | referenced (Demo 4 inputs) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:7` |

Standards are already cited in the upstream data files. This plan does not introduce new standards work; it inherits the existing chain. Six distinct standards span the two source JSONs; five are cited in chart captions and DNV-OS-F101 is intentionally omitted with the rationale recorded in the table row above and at storyboard C1 caption (line 82). Citation contract `.claude/rules/calc-citation-contract.md` remains binding for any *new* numeric constants used by future brochure annotations.

### LLM Wiki pages consulted
- No relevant wiki pages — capability charts are GTM artifacts, not domain knowledge promotion. Wiki promotion is explicitly out-of-scope per `.claude/rules/calc-citation-contract.md` and the deny-list policy on vendor-derivative content.

### Documents consulted
- `docs/BUSINESS_BRAIN.md:106-112` — confirms the April-1 weekly target is "produce vessel capability charts and send a good brochure to all researched vessel contractors." Sets the scope boundary: charts feed the brochure/send issue (#2556), do not stand alone.
- `docs/BUSINESS_BRAIN.md:122-132` — Legal Sanity Gates for Public Artifacts. Public-promotion sanity gate enumerated: source provenance recorded, public/private inputs identified, methodology and standards citations attached, tests/review state known, legal scan run, no confidential/client content. This plan binds those gates to chart promotion.
- `docs/gtm/capability-map.md` — already documents per-demo "Hero chart" framing for Demos 1-5 (lines 92, 98, 103, 112, 118). Brochure charts must compose with these hero charts, not duplicate them.
- `docs/plans/_template-issue-plan.md` — canonical template followed here. Resource Intelligence + Evidence + Pseudocode + Acceptance Criteria sections retained.
- Issue #1799 (OPEN) — public pipelay vessel specs collection. Source for any *additional* vessel classes the chart pack wants to add beyond the 4 representative classes already coded. Currently OPEN, so any chart-pack expansion is gated on #1799.
- Issue #1669 (OPEN) — Tier-1/2/3 vessel installation contractor target list. Defines downstream brochure recipients; sibling #2554 (contractor matrix) decomposes the recipient surface.
- Issue #2016 (OPEN) — GTM client-conversion pipeline parent. Confirms #1669 depends on demos + outreach infrastructure (Tier-3 ordering at line 91). Charts produced under #2555 are the hero-asset slice that #2016 marks as "Needs: parametric demo reports".
- Sibling: `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2554-contractor-matrix.md`, `2556-brochure-send.md`, `2557-productivity-review.md` — all sibling weekly-target prompts. #2555 must hand off chart artifacts to #2556 without requiring the operator to reassemble context.

### Gaps identified
1. No chart pack exists at `docs/reports/gtm/` (the directory did not exist before this plan).
2. No brochure-bound caption/narrative copy exists for any chart.
3. No legal/evidence sanity-scan record exists for charts about to be sent to external contractors. Required gate per `docs/BUSINESS_BRAIN.md:122-132` and `scripts/legal/legal-sanity-scan.sh`.
4. No defined output-format manifest (PNG/SVG/PDF dimensions, colour palette, typography) exists for brochure-grade exports. Existing demo HTML reports use Plotly defaults — too rich for a 1-2 page brochure.
5. No "headline number" computed from the comparison matrix exists yet (e.g., "Shallow Water Barge: 100% pass rate at 7-30 m water depth, all pipe sizes 8-20 in, 16-row evidence trail"). Headline numbers are the brochure's first hook.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29 via `gh issue view`):
- `#2555` — OPEN — feat(gtm): vessel capability charts for contractor brochure (labels: priority:high, cat:business, cat:strategy, domain:gtm)
- `#1799` — OPEN — DATA: Collect public pipelay barge/vessel specs for shallow water GTM demo
- `#1669` — OPEN — [WRK] GTM: Vessel Installation Contractor Email Outreach Campaign
- `#2016` — OPEN — feat(gtm): client conversion pipeline -- turn repo capability into paying clients

**File existence** (`ls -la` 2026-04-29):
- EXISTS: `docs/BUSINESS_BRAIN.md`
- EXISTS: `docs/gtm/capability-map.md`
- EXISTS: `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json`
- EXISTS: `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json`
- EXISTS: `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json`
- EXISTS: `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json`
- EXISTS: `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` (already renders chart-go_nogo Plotly heatmap)
- MISSING (this plan creates): `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`
- MISSING (this plan creates): `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md`
- MISSING (created on directory creation): `docs/reports/gtm/`

**Line excerpts** (`sed -n` 2026-04-29):

Confirms representative-class disclaimer in the vessel data — basis for the public/non-proprietary claim:
```
digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:1-2
{
  "_description": "Construction Support Vessel (CSV) and Heavy Lift Vessel (HLV) database for GTM demos 3 and 5. Vessel parameters are representative of real vessel classes but are not exact specifications of any named vessel.",
```

Confirms BUSINESS_BRAIN target binding for week of April 1:
```
docs/BUSINESS_BRAIN.md:110
Current/next weekly target seed: **for the week of April 1, produce vessel capability charts and send a good brochure to all researched vessel contractors**.
```

Confirms existing chart scaffolding in demo 4 HTML output:
```
demo_04_shallow_pipelay_report.html:1086-1088
<div class="chart-container">
    <div class='chart-title'>Chart 1: Go/No-Go Installation Matrix</div>
    <div class='chart-subtitle'>Side-by-side vessel comparison across all pipe sizes and water depths.</div>
```

**Gap proofs**:
- `ls docs/reports/gtm/ 2>&1` → "No such file or directory" before this plan ran → confirms the chart storyboard surface must be created.
- `find docs/plans -name "*2555*"` → only `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2555-capability-charts.md` (overnight prompt body, not a plan) → confirms this is the first canonical plan for the issue.
- `find scripts/review/results -name "*2555*"` → empty → no prior adversarial review evidence.

Distinct sources: 8 (issue #2555 body + 3 related issues #1799/#1669/#2016 + 5 in-repo files: pipelay_vessels.json, csv_hlv_vessels.json, vessel_comparison_matrix.json, BUSINESS_BRAIN.md, capability-map.md). Exceeds the ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` |
| Chart storyboard | `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` |
| Existing data inputs | `digitalmodel/examples/demos/gtm/data/{pipelay_vessels,csv_hlv_vessels}.json` |
| Existing result feeds | `digitalmodel/examples/demos/gtm/results/{vessel,structure}_comparison_matrix.json` |
| Existing chart precedent | `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2555-claude.md` (live MINOR, 2026-04-29) |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2555-codex.md` (live MINOR, 2026-04-29) |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2555-gemini.md` (live MINOR, 2026-04-29) |
| Overnight result | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md` |
| Plan index update | `docs/plans/README.md` |

Out-of-scope (handed off):
- Contractor recipient list — sibling #2554.
- Brochure assembly + send mechanics — sibling #2556.
- Productivity-flow review — sibling #2557.
- New vessel-class data ingestion (#1799) — explicitly deferred; this plan's chart pack uses only the 4 representative classes already coded.

---

## Deliverable

A planning-only artifact pair (canonical plan + chart storyboard) under `docs/plans/` and `docs/reports/gtm/` that locks chart inventory, data inputs, evidence/legal gate, output format, and acceptance criteria for ≥3 storyboard-ready vessel capability chart specifications derivable from existing repo data. Rendered charts become brochure-ready only in the follow-on implementation slice after recomputation, export, visual QA, legal scan, and required review evidence — without changing `digitalmodel/` source code.

---

## Pseudocode

This is a planning artifact. The "code" here is the storyboard's chart-derivation contract, written so a downstream implementer (Codex, Claude exec, or operator) can produce assets in a single bounded slice.

```
For each chart concept C in {C1..Cn}:
    inputs = read(C.data_paths)
    if C.source_type == "representative_vessel_json":
        assert inputs.fields ⊇ C.required_fields
        assert all(inputs.disclaimer == "representative of real vessel classes")  # legal gate for C1-C3 JSON feeds
        assert set(C.inherited_standards) <= set(C.caption.standards) | set(C.omission_rationale.keys())
    elif C.source_type == "capability_map_markdown":
        assert C.id == "C4"
        assert inputs.path == "docs/gtm/capability-map.md"
        assert each_rendered_row_has_standard_or_inline_omission_rationale(inputs)
    else:
        raise UnsupportedChartInput(C.source_type)

    headline = compute_headline_number(inputs, C.headline_rule)
    figure   = render_via_scripts_gtm(inputs, headline)  # future entry point: scripts/gtm/render_brochure_charts.py; may import report_template.py without editing digitalmodel/
    caption  = C.caption_template.format(headline=headline,
                                         scope=C.scope_disclosure,
                                         standards=C.standards_cited)
    # Asset-directory creation gate: brochure asset home must exist before export.
    # Directory is created by the follow-on implementation-slice plan (mkdir -p docs/reports/gtm/assets/),
    # not by this planning artifact. Render aborts cleanly if the gate is missing.
    assert exists("docs/reports/gtm/assets/"), "asset-directory gate not met; create via follow-on slice"
    exported_paths = export(figure, asset_home="docs/reports/gtm/assets/", formats=["png_brochure", "svg_print", "pdf_1page"])
    legal_scan(exported_paths, caption, C.scope_disclosure)  # scripts/legal/legal-sanity-scan.sh in a mode that scans actual generated collateral/caption text, not only textual git diffs
```

Chart concepts and their headline-number rules are spec'd in the storyboard artifact so reviewers can assess plausibility without re-deriving them inline.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | this plan |
| Create | `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | chart inventory + caption drafts + format manifest |
| Create (future implementation slice) | `scripts/gtm/render_brochure_charts.py` | exact non-`digitalmodel/` chart-rendering entry point; may import demo rendering helpers without mutating them |
| Create (future implementation slice) | `docs/reports/gtm/assets/` | locked home for brochure PNG/SVG/PDF outputs unless adversarial review rejects it |
| Update | `docs/plans/README.md` | add draft index row |
| Create | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md` | overnight worker handoff |
| (Out of scope) | `digitalmodel/examples/demos/gtm/**` | NO edits in this plan |
| (Out of scope) | actual PNG/SVG/PDF chart assets | deferred to plan-approved implementation slice |

---

## TDD Test List

Planning-only deliverable. The tests below are *plan-readiness checks*, not unit tests:

| Check | Verifies | How |
|---|---|---|
| chart_count_ge_3 | Storyboard documents ≥3 chart concepts | grep `^### Chart C` count in storyboard |
| every_chart_has_data_inputs | Each chart names exact JSON file paths | per-chart "Data Inputs" subsection present |
| every_chart_has_evidence_note | Each chart has public-source/assumption note | per-chart "Evidence & Legal Scope" subsection present |
| every_chart_has_caption_draft | Each chart has draft caption text | per-chart "Caption Draft" subsection present |
| every_chart_has_format_spec | Each chart names target output formats | per-chart "Output Formats" subsection present |
| no_proprietary_input_paths | Storyboard cites only representative-class data | absence of `client_projects/`, `acma-projects/`, `seanation/`, `frontierdeepwater/` paths in storyboard |
| no_named_real_vessel_telemetry | Storyboard does not promise telemetry-from-named-named-vessel | absence of bare named-vessel claims like "Allseas Lorelay measured 3.2m heave on 2024-08-01" — claims must be classed as `representative_class` framings |
| acceptance_criteria_mapped | Each issue AC has at least one chart concept addressing it | traceability matrix in storyboard |

Implementation-time tests (deferred to a follow-on plan-approved slice) include rendering smoke tests against the comparison matrices and a brochure-export integration test.

---

## Acceptance Criteria

- [ ] Plan and storyboard exist under the paths in the Artifact Map.
- [ ] Storyboard inventory has ≥3 chart concepts, each addressing at least one issue AC.
- [ ] Each chart concept names: data inputs (existing repo paths only), required data fields, public-source/representative-class disclosure, standards citations inherited from upstream JSON, draft caption, headline-number rule, and output-format spec (PNG/SVG/PDF dimensions, palette).
- [ ] Storyboard explicitly enumerates the legal sanity-scan gate before any chart is exported for external use, and binds the gate to `scripts/legal/legal-sanity-scan.sh` per `docs/BUSINESS_BRAIN.md:124`; the implementation slice must run the scanner in a mode that covers actual generated PNG/SVG/PDF/caption artifacts, not only textual diffs, and archive the scanner output.
- [ ] Storyboard has a traceability matrix mapping issue #2555 ACs to chart concepts.
- [ ] Plan index row added to `docs/plans/README.md`.
- [ ] Cross-provider adversarial review evidence is recorded before any `status:plan-review` label is applied: required evidence is Claude **and** Codex **and** Gemini live verdicts (each APPROVE or MINOR). UNAVAILABLE provenance is NOT sufficient for any of the three providers — a `*-nextwave-*` UNAVAILABLE artifact records that the lane could not exercise the provider but does **not** satisfy this AC. If Codex or Gemini is blocked on the host (codex-cli regression, lane-permission scope, sandbox restriction), status remains `draft` until a permitted lane on a working host produces the canonical live artifact at `scripts/review/results/2026-04-29-plan-2555-{codex,gemini}.md` (no `-nextwave` suffix). Until all three live verdicts exist, status remains `draft`.
- [ ] No edits to `digitalmodel/` source code during this plan's lifecycle.
- [ ] No proprietary/client telemetry referenced in any chart concept.
- [ ] Future implementation home is explicitly `scripts/gtm/render_brochure_charts.py` (new wrapper outside `digitalmodel/`), and brochure asset home is explicitly `docs/reports/gtm/assets/` unless adversarial review rejects that location.
- [ ] Future implementation-slice plan creates `docs/reports/gtm/assets/` via `mkdir -p` as an explicit Files-to-Change row before any render call. Render aborts cleanly if the directory is missing (asset-directory gate is enumerated in the Pseudocode `assert exists(...)` step). This planning artifact does NOT create the directory itself.
- [ ] Every chart caption cites the full inherited-standards set from the upstream JSON `_references` arrays (DNV-ST-F101, DNV-RP-H103, DNV-ST-N001, DNV-OS-H101 where applicable, API RP 1111 where shallow-pipelay screening is in scope). If a standard is intentionally omitted (e.g., scope-limited to deepwater-only or crane-lift-only jobs), the storyboard chart entry must record the omission rationale inline; bare omission is not acceptable.
- [ ] Storyboard distinguishes headline numbers verified in this planning wave from headline numbers that must be recomputed/verified during the later render slice.
- [ ] Rendering and brochure-export work is *not* attempted under this plan; a follow-on slice plan is created if implementation is desired.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (live canonical rerun, 2026-04-29) | MINOR | `scripts/review/results/2026-04-29-plan-2555-claude.md`: independent live review found one HIGH numeric-caption defect (`108 cases` wrong; current matrix totals 156), standards-completeness/rationale drift, and stale review-state metadata. Required document-level patches applied before promotion. Prior next-wave self-review also found: (1) TDD Test List row 1 grep `^## Chart C` is off-by-one heading depth vs. actual storyboard `^### Chart C`; literal pattern returns 0 instead of 4. (2) AC #5 (cross-provider review) unmet without Codex+Gemini live evidence. (3) Chart-rendering code-home unspecified — Files-to-Change marks `digitalmodel/**` out of scope but storyboard pseudocode reuses `report_template.py` which lives there; entry-point path needs naming. (4) Brochure-asset target `docs/reports/gtm/assets/` does not yet exist. (5) Caption draft for C1 cites three of four inherited standards; API RP 1111 omitted without justification despite shallow-S-lay job inheriting it. **Positive verification (not a finding):** Shallow Water Barge headline-number claim ("100% pass rate across 30 cases") matches `vessel_comparison_matrix.json` exactly. |
| Codex (live canonical rerun, 2026-04-29) | MINOR | `scripts/review/results/2026-04-29-plan-2555-codex.md`: no critical/high findings; document-level fixes requested for generated-asset legal scan coverage, planning-only vs brochure-ready wording, C4 citation completeness, brand palette re-confirmation, and C1 `108 cases` recomputation. Safe textual patches applied to plan/storyboard; live Gemini evidence still required before status promotion under the current AC. |
| Gemini (live canonical rerun, 2026-04-29) | MINOR | `scripts/review/results/2026-04-29-plan-2555-gemini.md`: conditional plan-review readiness if live Claude and Codex artifacts are present; requested pseudocode fixes for C4 Markdown input handling, export-before-legal-scan ordering, and C4 row-by-row standards validation. Pseudocode patches applied after review. |

**Overall result:** READY-FOR-`status:plan-review` after this document patch wave. Cross-provider live-evidence gate (AC §213) is now satisfied with three canonical live MINOR verdicts: Claude, Codex, and Gemini (all 2026-04-29). User approval was recorded via live GitHub `status:plan-approved` label on 2026-04-29 and reconciled locally in `.planning/plan-approved/2555.md`; implementation/rendering/outbound work remains gated by the approved scope, legal-scan requirements, and sibling #2556 send approval boundary.

**Remaining tasks for the next permitted lane:**
- Live GitHub approval label has been reconciled to local marker `.planning/plan-approved/2555.md`.
- During the later implementation slice, create `scripts/gtm/render_brochure_charts.py` and `docs/reports/gtm/assets/` exactly as specified here; neither is created by the planning artifact itself.
- Keep #2556 external-send mechanics blocked until chart assets, legal scan output, and explicit outbound approval are available.

Revisions made based on review:
- Fixed the TDD heading-depth check from `^## Chart C` to `^### Chart C`.
- Clarified the provider-review acceptance criterion and documented the permitted unavailable-provider fallback (subsequently tightened — see next-wave patch row below).
- Named the future non-`digitalmodel/` render entry point as `scripts/gtm/render_brochure_charts.py` and locked brochure assets to `docs/reports/gtm/assets/` unless review rejects that home.
- Added an explicit acceptance criterion requiring the storyboard to mark which headline numbers are verified now versus regenerated later.

**Next-wave patch (2026-04-29, planning-only lane — `nextwave-followup-plan-patch-2555-20260429-1446.md`):**
- **Tightened cross-provider AC** so UNAVAILABLE provenance is NOT sufficient for `status:plan-review` for any of the three providers; required evidence is Claude + Codex + Gemini *live* verdicts (each APPROVE or MINOR). Reverses the earlier "permitted fallback" clause that admitted Claude + 1 live + 1 UNAVAILABLE-documented.
- **Added pseudocode mkdir gate** for `docs/reports/gtm/assets/` — render aborts cleanly via `assert exists(...)` if the asset directory is missing; directory creation belongs to the follow-on implementation-slice plan, not this artifact.
- **Added pseudocode standards-citation completeness check** so every inherited standard from upstream JSON `_references` either appears in caption.standards or is recorded in `C.omission_rationale` (defensibility-of-claims rule covering the API RP 1111 concern).
- **Added two acceptance criteria** binding the asset-directory gate and the caption-completeness/omission-rationale rule at plan-AC level.
- Verified during this patch wave: Finding 1 (TDD grep pattern) was already corrected to `^### Chart C` by a prior wave (see Test List row 1 in §"TDD Test List"). Finding 3 (rendering home) was already named to `scripts/gtm/render_brochure_charts.py` in §"Resource Intelligence Summary", §"Files to Change", and §"Acceptance Criteria". Finding 5 (API RP 1111 omitted) was already cited in storyboard C1 caption (line 82); this patch enforces the rule at plan-AC level.
- Patch lane intentionally did NOT (a) edit the storyboard/report files, (b) drive cross-provider fanout, (c) mutate any GitHub label, comment, or status, (d) apply `status:plan-review` or `status:plan-approved`. Cross-provider AC remains unmet and the plan stays `draft`.

Review evidence: `scripts/review/results/2026-04-29-plan-2555-nextwave-{claude,codex,gemini}.md` (this wave); canonical-fanout artifacts at `…/2026-04-29-plan-2555-{claude,codex,gemini}.md` (no `-nextwave` suffix) reserved for a permitted-lane re-run.

## Implementation Slice Completion — 2026-04-30

Approved rendering/export slice executed after live GitHub `status:plan-approved` reconciliation.

Artifacts created:
- Renderer: `scripts/gtm/render_brochure_charts.py`
- Tests: `tests/test_render_brochure_charts.py`
- Closeout handoff: `docs/session-handoffs/2026-04-29-issue-2555-closeout.md`
- Legal scan archive: `docs/reports/gtm/legal-scans/2026-04-30-chart-pack-scan.json`
- Manifest: `docs/reports/gtm/assets/vessel-capability-chart-pack-manifest.json`
- C1/C2/C3 brochure PNGs: `docs/reports/gtm/assets/c{1,2,3}-*.brochure.png`
- C1/C2/C3 print SVGs: `docs/reports/gtm/assets/c{1,2,3}-*.print.svg`
- C1/C2/C3 one-page PDFs: `docs/reports/gtm/assets/c{1,2,3}-*.1page.pdf`
- C1/C2/C3 caption sidecars: `docs/reports/gtm/assets/c{1,2,3}-*.caption.txt`
- C1/C2/C3 metadata sidecars: `docs/reports/gtm/assets/c{1,2,3}-*.metadata.json`

Validation evidence:
- `uv run pytest tests/test_render_brochure_charts.py -q` → `3 passed`.
- `uv run python scripts/gtm/render_brochure_charts.py --digitalmodel-root /mnt/local-analysis/digitalmodel-issue-2514-impl --output-dir docs/reports/gtm/assets --legal-scan-dir docs/reports/gtm/legal-scans --create-output-dirs` → rendered C1/C2/C3 PNG/SVG/PDF/caption/metadata outputs.
- `scripts/legal/legal-sanity-scan.sh --diff-only --json` → `rc=0` with no output on pass.
- `uv run python -m py_compile scripts/gtm/render_brochure_charts.py` and `git diff --check` passed during closeout.
- Artifact leak scan over `docs/reports/gtm/assets docs/reports/gtm/legal-scans` found no `/mnt/local-analysis`, `/tmp/pytest`, `client_projects`, `acma-projects`, `seanation`, or `frontierdeepwater` strings.
- Visual QA inspected C1 PNG for legibility and obvious rendering corruption; remaining visual polish caveats are non-blocking and belong in #2556 brochure assembly if desired.

Boundary retained:
- #2555 is closed with `status:done` as of commit `a6d95c4a4`; handoff commit `71840decf` records closeout evidence.
- These are internal-review chart-pack assets until #2556 brochure/outbound approval. #2556 remains blocked on #2554/#2560 evidence gating or explicit owner waiver, plus explicit owner approval before any external outreach.
- C4 remains optional/internal and was not rendered in this slice.

---

## Risks and Open Questions

- **Risk: representative-class data may be miscommunicated as named-vessel data.** Mitigation: storyboard mandates a "Scope & Disclosure" line on every chart caption stating the data is representative of vessel classes, not measured telemetry of any named vessel; legal scan gate before export.
- **Risk: charts that look "good enough" get sent to contractors without legal-scan completion.** Mitigation: acceptance criteria binds `scripts/legal/legal-sanity-scan.sh` as a hard gate in a mode that covers actual generated collateral/caption artifacts, not only textual diffs; sibling #2556 (brochure-send) must verify the gate before transmission.
- **Risk: chart pack drifts from upstream demo numbers when demos rerun.** Mitigation: chart inputs are explicit JSON paths; rerun-and-regenerate is single-step. Storyboard documents the regen contract.
- **Risk: contractor-facing charts overclaim vessel capabilities ACE has not validated against client engagements.** Mitigation: caption template surfaces "screening-grade analysis envelope" framing — never "we have built and operated" framing.
- **Risk: sibling #2554 contractor matrix may add segments (e.g., FOWT installation vessels) that the existing 4-class data does not cover.** Mitigation: storyboard's traceability matrix flags coverage gaps; expansion to new vessel classes is gated on #1799 closure, not on this plan.
- **Risk: Codex review-runner regression** (per memory: codex-cli stdin-hang and sandbox-no-execution issues) **may block adversarial review.** Mitigation: live Codex evidence is required before any status escalation per the tightened AC §209 — Claude + Gemini cross-coverage does NOT satisfy the cross-provider gate when Codex is blocked. If Codex CLI 0.124.0 stdin-hang or sandbox-execution restrictions persist, escalate to the operator for a host-level pin or downgrade per `feedback_codex_cli_0_124_upstream_regression.md` (#2479). Document the UNAVAILABLE provenance for audit, but treat the plan as `draft` until a permitted lane on a working host produces the canonical live artifact at `scripts/review/results/2026-04-29-plan-2555-codex.md`.
- **Open:** Should chart pack default to a 4-class scope (existing data) or wait for #1799 to expand to 8-12 classes? Default in this plan: ship 4-class to unblock #2556; #1799 expansion is a follow-on.
- **Open:** Should rendered chart assets live under `docs/reports/gtm/` (workspace-hub) or `digitalmodel/examples/demos/gtm/output/`? Default: brochure-bound assets live under `docs/reports/gtm/` so they decouple from demo regeneration. Demo HTML reports continue to embed their hero charts as before.

---

## Complexity: T2

**T2** — multi-file planning artifact (canonical plan + storyboard + index update + summary), sources from 4 existing JSON files and 2 existing demo HTML reports, requires cross-provider adversarial review before any status escalation. Implementation slice (rendering + export + legal scan) is intentionally split into a follow-on plan once the storyboard is approved.
