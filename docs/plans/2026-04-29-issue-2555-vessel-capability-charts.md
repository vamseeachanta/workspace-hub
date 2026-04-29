# Plan for #2555: feat(gtm): vessel capability charts for contractor brochure

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2555
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2555-claude.md (TBD) | ...-codex.md (TBD) | ...-gemini.md (TBD)
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

### Standards
| Standard | Status | Source |
|---|---|---|
| DNV-ST-F101 (Submarine Pipeline Systems) | referenced (Demo 4 inputs) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:5` |
| DNV-RP-H103 (Marine Operations modelling) | referenced (Demos 3/5 inputs) | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:5` |
| DNV-ST-N001 (Marine Operations & Marine Warranty) | referenced (Demos 3/5 inputs) | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:6` |
| API RP 1111 (Offshore Hydrocarbon Pipelines) | referenced (Demo 4 inputs) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:7` |

Standards are already cited in the upstream data files. This plan does not introduce new standards work; it inherits the existing chain. Citation contract `.claude/rules/calc-citation-contract.md` remains binding for any *new* numeric constants used by future brochure annotations.

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
| Plan review — Claude | scripts/review/results/2026-04-29-plan-2555-claude.md (TBD) |
| Plan review — Codex | scripts/review/results/2026-04-29-plan-2555-codex.md (TBD) |
| Plan review — Gemini | scripts/review/results/2026-04-29-plan-2555-gemini.md (TBD) |
| Overnight result | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md` |
| Plan index update | `docs/plans/README.md` |

Out-of-scope (handed off):
- Contractor recipient list — sibling #2554.
- Brochure assembly + send mechanics — sibling #2556.
- Productivity-flow review — sibling #2557.
- New vessel-class data ingestion (#1799) — explicitly deferred; this plan's chart pack uses only the 4 representative classes already coded.

---

## Deliverable

A planning-only artifact pair (canonical plan + chart storyboard) under `docs/plans/` and `docs/reports/gtm/` that locks chart inventory, data inputs, evidence/legal gate, output format, and acceptance criteria for ≥3 brochure-ready vessel capability charts derivable from existing repo data — without changing `digitalmodel/` source code.

---

## Pseudocode

This is a planning artifact. The "code" here is the storyboard's chart-derivation contract, written so a downstream implementer (Codex, Claude exec, or operator) can produce assets in a single bounded slice.

```
For each chart concept C in {C1..Cn}:
    inputs = read(C.data_paths)            # all from existing JSON files only
    assert inputs.fields ⊇ C.required_fields
    assert all(inputs.disclaimer == "representative of real vessel classes")  # legal gate
    headline = compute_headline_number(inputs, C.headline_rule)
    figure   = render(C.style, inputs, headline)        # Plotly or matplotlib via report_template.py
    caption  = C.caption_template.format(headline=headline,
                                         scope=C.scope_disclosure,
                                         standards=C.standards_cited)
    legal_scan(figure, caption, C.scope_disclosure)     # scripts/legal/legal-sanity-scan.sh
    export(figure, formats=["png_brochure", "svg_print", "pdf_1page"])
```

Chart concepts and their headline-number rules are spec'd in the storyboard artifact so reviewers can assess plausibility without re-deriving them inline.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | this plan |
| Create | `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | chart inventory + caption drafts + format manifest |
| Update | `docs/plans/README.md` | add draft index row |
| Create | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md` | overnight worker handoff |
| (Out of scope) | `digitalmodel/examples/demos/gtm/**` | NO edits in this plan |
| (Out of scope) | actual PNG/SVG/PDF chart assets | deferred to plan-approved implementation slice |

---

## TDD Test List

Planning-only deliverable. The tests below are *plan-readiness checks*, not unit tests:

| Check | Verifies | How |
|---|---|---|
| chart_count_ge_3 | Storyboard documents ≥3 chart concepts | grep `^## Chart C` count in storyboard |
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
- [ ] Storyboard explicitly enumerates the legal sanity-scan gate before any chart is exported for external use, and binds the gate to `scripts/legal/legal-sanity-scan.sh` per `docs/BUSINESS_BRAIN.md:124`.
- [ ] Storyboard has a traceability matrix mapping issue #2555 ACs to chart concepts.
- [ ] Plan index row added to `docs/plans/README.md`.
- [ ] Cross-provider adversarial review run (Claude + Codex + Gemini) before any `status:plan-review` label is applied. Until then, status remains `draft`.
- [ ] No edits to `digitalmodel/` source code during this plan's lifecycle.
- [ ] No proprietary/client telemetry referenced in any chart concept.
- [ ] Rendering and brochure-export work is *not* attempted under this plan; a follow-on slice plan is created if implementation is desired.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (next-wave self-review, 2026-04-29) | MINOR | (1) TDD Test List row 1 grep `^## Chart C` is off-by-one heading depth vs. actual storyboard `^### Chart C`; literal pattern returns 0 instead of 4. (2) AC #5 (cross-provider review) unmet without Codex+Gemini live evidence. (3) Chart-rendering code-home unspecified — Files-to-Change marks `digitalmodel/**` out of scope but storyboard pseudocode reuses `report_template.py` which lives there; entry-point path needs naming. (4) Brochure-asset target `docs/reports/gtm/assets/` does not yet exist. (5) Caption draft for C1 cites three of four inherited standards; API RP 1111 omitted without justification despite shallow-S-lay job inheriting it. **Positive verification (not a finding):** Shallow Water Barge headline-number claim ("100% pass rate across 30 cases") matches `vessel_comparison_matrix.json` exactly. |
| Codex (next-wave) | UNAVAILABLE | Lane permission did not auto-approve fanout invocation; codex-cli 0.124.0 upstream regression also unverified on this host. See `scripts/review/results/2026-04-29-plan-2555-nextwave-codex.md`. |
| Gemini (next-wave) | UNAVAILABLE | Lane permission did not auto-approve fanout invocation. See `scripts/review/results/2026-04-29-plan-2555-nextwave-gemini.md`. |

**Overall result:** PENDING — `status:plan-review` cannot be applied this wave. AC §197 requires Claude + Codex + Gemini cross-provider review; only Claude evidence exists. Plan stays `draft`. No revisions to the plan body are required for the MINOR findings listed above; they are recorded as **patch tasks** below for a future wave.

**Patch tasks for the next permitted lane:**
- Fix TDD Test List row 1 grep pattern to `^### Chart C` (or `^#+ Chart C`).
- Name the chart-rendering code-home explicitly (e.g., `scripts/gtm/render_brochure_charts.py` or equivalent), and clarify whether `report_template.py` is *imported* from `digitalmodel/` or whether a new shim is needed; resolve the "NO edits to digitalmodel/" tension.
- Add `docs/reports/gtm/assets/` mkdir to the follow-on implementation slice's Files-to-Change.
- Either add API RP 1111 to the C1 caption draft or document why it is intentionally omitted.
- Drive a permitted-lane fanout that produces Codex and Gemini live verdicts so AC §197 can be satisfied.

Revisions made based on review:
- N/A — MINOR findings recorded but plan body not revised this wave per user prompt's "leave as draft and list patch tasks" guidance.

Review evidence: `scripts/review/results/2026-04-29-plan-2555-nextwave-{claude,codex,gemini}.md` (this wave); canonical-fanout artifacts at `…/2026-04-29-plan-2555-{claude,codex,gemini}.md` (no `-nextwave` suffix) reserved for a permitted-lane re-run.

---

## Risks and Open Questions

- **Risk: representative-class data may be miscommunicated as named-vessel data.** Mitigation: storyboard mandates a "Scope & Disclosure" line on every chart caption stating the data is representative of vessel classes, not measured telemetry of any named vessel; legal scan gate before export.
- **Risk: charts that look "good enough" get sent to contractors without legal-scan completion.** Mitigation: acceptance criteria binds `scripts/legal/legal-sanity-scan.sh` as a hard gate; sibling #2556 (brochure-send) must verify the gate before transmission.
- **Risk: chart pack drifts from upstream demo numbers when demos rerun.** Mitigation: chart inputs are explicit JSON paths; rerun-and-regenerate is single-step. Storyboard documents the regen contract.
- **Risk: contractor-facing charts overclaim vessel capabilities ACE has not validated against client engagements.** Mitigation: caption template surfaces "screening-grade analysis envelope" framing — never "we have built and operated" framing.
- **Risk: sibling #2554 contractor matrix may add segments (e.g., FOWT installation vessels) that the existing 4-class data does not cover.** Mitigation: storyboard's traceability matrix flags coverage gaps; expansion to new vessel classes is gated on #1799 closure, not on this plan.
- **Risk: Codex review-runner regression** (per memory: codex-cli stdin-hang and sandbox-no-execution issues) **may block adversarial review.** Mitigation: wait for clean Codex evidence rather than self-approve; if blocked, document with same provenance pattern used in `aces-2`/`aces-3`/`aces-4` (Codex UNAVAILABLE annotated) and rely on Claude + Gemini cross-coverage.
- **Open:** Should chart pack default to a 4-class scope (existing data) or wait for #1799 to expand to 8-12 classes? Default in this plan: ship 4-class to unblock #2556; #1799 expansion is a follow-on.
- **Open:** Should rendered chart assets live under `docs/reports/gtm/` (workspace-hub) or `digitalmodel/examples/demos/gtm/output/`? Default: brochure-bound assets live under `docs/reports/gtm/` so they decouple from demo regeneration. Demo HTML reports continue to embed their hero charts as before.

---

## Complexity: T2

**T2** — multi-file planning artifact (canonical plan + storyboard + index update + summary), sources from 4 existing JSON files and 2 existing demo HTML reports, requires cross-provider adversarial review before any status escalation. Implementation slice (rendering + export + legal scan) is intentionally split into a follow-on plan once the storyboard is approved.
