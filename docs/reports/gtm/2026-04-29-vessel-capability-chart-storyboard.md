# Vessel Capability Chart Storyboard — Brochure Pack v0

> **Date:** 2026-04-29
> **Status:** draft (planning artifact — no rendered assets exist yet)
> **Issue:** [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555)
> **Plan:** [`docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md`](../../plans/2026-04-29-issue-2555-vessel-capability-charts.md)
> **Sibling lanes:** [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) (contractor matrix) · [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) (brochure send) · [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) (productivity review)

---

## Purpose

Lock the chart pack design for ACE Engineer's vessel-contractor brochure (week of April 1 GTM target). Produce ≥3 brochure-ready capability charts, each derived from existing repo data with explicit public-source/representative-class disclosure and a binding legal sanity gate before any external send.

This document is **planning-only**. No PNG/SVG/PDF assets are emitted by this artifact. Asset generation is a follow-on plan-approved implementation slice.

---

## Source-Data Surface (no client/proprietary data)

| Path | Provides | Disclosure |
|---|---|---|
| `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` | Large PLV (Castorone/Seven Navica representative class), Shallow Water Barge (DLB representative class): tensioner capacity, stinger length/angle, water-depth range, pipe-size range, sea-state limits | Header: "representative of real vessel classes" |
| `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` | Large CSV (Aegir/Borealis representative class), Medium CSV (Normand Maximus/Seven Arctic representative class): crane SWL curve, RAO peaks, lift operability limits | Header: "representative of real vessel classes but are not exact specifications of any named vessel" |
| `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` | Cross-demo go/no-go matrix across 4 vessels (mudmat, jumper, shallow pipelay), pass-rates, head-to-head narratives | Computed from above two sources via demos 3/4/5 |
| `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json` | By-vessel crane utilisation values at 1500 m for mudmat S/M/L | Computed feed |
| Standards inherited (citations) | DNV-ST-F101, DNV-RP-H103, DNV-ST-N001, DNV-OS-H101, API RP 1111 | Cited in `_references` arrays of the JSON inputs |

**Out-of-bounds paths** (must NOT appear in any chart):
- `client_projects/**`
- `acma-projects/**`
- `seanation/**`
- `frontierdeepwater/**` (5% stake, not a public reference)
- Any vessel-name-keyed measured-telemetry claim sourced from an engagement.

---

## Output-Format Manifest

| Format | Use | Dimensions | Palette | Notes |
|---|---|---|---|---|
| `chart-name.brochure.png` | Brochure embed | 1600 × 900 px @ 2× | ACE primary (TBC against `aceengineer-website` brand), with the existing demo green/amber/red traffic light only for go/no-go cells | Flat — no Plotly hover; no interactive controls |
| `chart-name.print.svg` | Print-quality | vector | Same | Embedded fonts; CMYK-safe colour |
| `chart-name.1page.pdf` | Standalone leave-behind | 8.5 × 11 in | Same | Caption + scope disclosure rendered into the PDF, not just the brochure body |
| `chart-name.html` (optional) | Demo report embed | per `report_template.py` | Plotly defaults | Already exists for demo 4; reuse rather than rebuild |

The brochure assets live under `docs/reports/gtm/assets/` once rendered unless adversarial review explicitly rejects that home. Demo HTML reports remain at `digitalmodel/examples/demos/gtm/output/` and are not duplicated.

The future render entry point is a new wrapper script at `scripts/gtm/render_brochure_charts.py`. That wrapper may import `digitalmodel/examples/demos/gtm/report_template.py` helpers, but #2555 itself does not edit `digitalmodel/` source.

Per memory `aceengineer-website` brand hierarchy and visual-DNA were locked 2026-04-21 (project_claude_design_adoption). Asset palette must be re-confirmed against that contract before rendering.

---

## Chart Inventory

The four charts below cover all four issue acceptance criteria. C1, C2, C3 are the "must-render" set (≥3 required by AC1). C4 is recommended-but-optional and depends on whether the brochure has room.

---

### Chart C1 — Vessel-vs-Job Capability Heatmap (cross-demo)

**The hero chart.** Single grid that answers, for every (vessel × job) pair, "how does the screening-grade analysis say this goes?" — covering mudmat installation, rigid jumper installation, and shallow-water S-lay pipelay.

**Why it leads the brochure:** vessel contractors recognise the go/no-go matrix immediately and can scan their own vessel class against ACE's screening envelope without reading prose.

**Required data fields**
- vessel.name, vessel.type, vessel.crane_capacity_te (where defined), vessel.tensioner_capacity_te (where defined)
- per (job, vessel): pass_rate_pct, total_cases, limiting_factor

**Data inputs** (existing repo paths only)
- `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` — primary feed (pass-rate by capability)

**Headline-number rule**
- Pick the highest pass-rate vessel-job pair from the matrix. As of the 2026-04-15 demo run, the headline reads: **"Shallow Water Barge: 100% pass rate across 30 cases for 8-24 in pipe at 7-30 m water depth."**

**Verification scope (now vs later)**
- **Verified in this planning wave:** `vessel_comparison_matrix.json` confirms the Shallow Water Barge pair is the highest pass-rate vessel-job pair with `pass_rate_pct = 100.0` and `cases_total = 30`.
- **Deferred to render slice:** the pipe-size span (`8-24 in`) and water-depth span (`7-30 m`) must be re-verified from the latest pipelay input/result files at render time and then regenerated if demo outputs changed.

**Caption draft**
> Vessel-vs-job screening envelope from ACE Engineer's parametric analysis suite (108 cases across mudmat, jumper, and shallow-pipelay screening). Coloured cells show pass rate of cases meeting governing-load checks per DNV-RP-H103, DNV-ST-N001, DNV-ST-F101, and API RP 1111 where shallow-pipelay screening is involved. Vessel parameters reflect representative classes — not measured telemetry of any named vessel. Send-screening grade for shortlist purposes; detailed feasibility requires per-project metocean and rigging inputs.

**Evidence & legal scope**
- All 4 vessels are representative classes, disclosed in source JSON headers.
- All standards citations inherited from upstream JSON `_references` arrays.
- No client/named-vessel telemetry.
- Required: `scripts/legal/legal-sanity-scan.sh --diff-only` against the generated PNG/SVG/PDF before external send.

**Output formats:** PNG brochure, SVG print, PDF 1-page.

**Maps to issue ACs:** AC1 (≥3 brochure-ready charts — covers 3 jobs in one), AC2 (public-source disclosure), AC3 (legal-suitable framing), AC4 (feeds brochure without re-assembly).

---

### Chart C2 — Pipelay Operating Envelope (water depth × pipe size, by vessel)

**The "shallow water" wedge.** Pipelay-vessel contractors care most about the depth-vs-pipe-size operating window. This chart compares the Large PLV class against the Shallow Water Barge class on a single (water depth, pipe OD) plane, with go/marginal/no-go bands.

**Why it earns brochure space:** the PLV-vs-Barge crossover at ~7 m water depth is a concrete, defensible technical claim that separates ACE from a hand-wave consultancy pitch. The barge dominates ultra-shallow (100% pass rate); the PLV fails at 7 m for all sizes (vessel draft limit).

**Required data fields**
- vessel.name, vessel.tensioner_capacity_te, vessel.water_depth_range, vessel.pipe_capacity
- per (vessel × pipe size × water depth): GO / MARGINAL / NO_GO; limiting factor

**Data inputs**
- `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json`
- `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` (`plv_comparison.head_to_head` block)

**Headline-number rule**
- Compute pass-rate ratio between barge and PLV in shallow water (≤30 m). As drafted today, the headline reads: **"Shallow Water Barge handles 8-24 in pipe at 7 m depth where the Large PLV cannot operate (vessel-draft limited)."**

**Verification scope (now vs later)**
- **Verified in this planning wave:** the cross-demo narrative and the Large PLV shallow-water limitation are directionally supported by the current comparison matrix and cited pipelay dataset.
- **Deferred to render slice:** the exact `8-24 in` and `7 m depth` phrasing must be recomputed from the latest demo 4 source/result files before export, because this planning wave did not exhaustively trace every plotted cell.

**Caption draft**
> Shallow-water S-lay envelope: where each vessel class can install which pipe size. Green cells indicate cases meeting tension, overbend, sagbend, and stinger checks per DNV-ST-F101 and API RP 1111. Marginal cells flag governing constraint within 5% of allowable. Source vessel parameters are representative-class — not exact specs of any named vessel. Detailed go/no-go for a specific project requires metocean, soil, and rigging inputs.

**Evidence & legal scope**
- Uses the same 2 representative-class vessels disclosed in source JSON.
- Limiting-factor labels (`tension`, `overbend`, `vessel_capability`) come directly from demo 4 results, not from interpretation.
- Legal-scan gate identical to C1.

**Output formats:** PNG brochure, SVG print, PDF 1-page.

**Maps to issue ACs:** AC1, AC2, AC3, AC4.

---

### Chart C3 — Crane-Utilisation Margin Map (lift jobs)

**The "we don't just say go/no-go, we tell you the headroom" chart.** Two-vessel comparison (Large CSV vs Medium CSV) showing crane utilisation % at 1500 m water depth for 50 / 100 / 200 te mudmats. Both vessels are GO across the matrix, but the utilisation deltas (Large CSV at 20.6% vs Medium CSV at 71.5% for 200 te) tell the operability story.

**Why it earns brochure space:** contractor decision-makers know "GO" doesn't mean "comfortable margin." This chart shows ACE doing what most screeners skip — surfacing the margin curve, not just the binary verdict.

**Required data fields**
- vessel.name, vessel.crane_main.swl_max_te, vessel.crane_main.crane_capacity_curve
- per vessel × structure: crane_util_at_1500m

**Data inputs**
- `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json`
- `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json` (`by_vessel.*.crane_util_at_1500m`)

**Headline-number rule**
- Compute the largest utilisation delta between vessels for a single structure. As drafted today, the headline reads: **"At 200 te mudmat, 1500 m depth: Large CSV at 20.6% crane utilisation, Medium CSV at 71.5% — same go-decision, very different margin."**

**Verification scope (now vs later)**
- **Verified in this planning wave:** the intended metric source is locked to `structure_comparison_matrix.json` `by_vessel.*.crane_util_at_1500m`.
- **Deferred to render slice:** the exact utilisation percentages and the identity of the largest delta pair must be recomputed from the latest matrix before export.

**Caption draft**
> Crane-utilisation margin at 1500 m water depth for the 50 / 100 / 200 te mudmat installation cases. Both vessel classes pass go/no-go, but margin matters: lower utilisation reduces sensitivity to weight growth, rigging revisions, and weather stand-by. Vessel crane curves are representative-class. Per DNV-RP-H103 dynamic amplification framework; full lift sensitivity requires project-specific RAO/sea-state inputs.

**Evidence & legal scope**
- Both vessels are representative-class; disclosure in source JSON.
- Utilisation values are direct demo 3 outputs, not interpretive.
- Legal-scan gate identical to C1.

**Output formats:** PNG brochure, SVG print, PDF 1-page.

**Maps to issue ACs:** AC1, AC2, AC3, AC4.

---

### Chart C4 — Capability Coverage Map (optional, recommended)

**The "what ACE is willing to take to screening today" chart.** A 17-row coverage map (cross-walked from `docs/gtm/capability-map.md`) showing for each discipline: production / available / planned readiness, demos / cases, and standards citations. Not vessel-vs-vessel — capability-vs-readiness instead.

**Why it earns brochure space:** answers the second question every contractor asks: "what else can you screen?"

**Required data fields**
- discipline name, module path, GTM demo, standards list, readiness, client-value text

**Data inputs**
- `docs/gtm/capability-map.md` (already produced)

**Headline-number rule**
- Headline reads: **"10 of 17 disciplines at production readiness today; 1,292 parametric cases across 5 demos."** (Source: lines 38-42 of capability-map.md.)

**Verification scope (now vs later)**
- **Verified in this planning wave:** the headline is sourced from the cited `docs/gtm/capability-map.md` lines.
- **Deferred to render slice:** re-check those counts against the latest capability map before brochure export in case readiness totals changed.

**Caption draft**
> ACE Engineer's screening-grade discipline coverage for offshore installation, integrity, and field-development scope. Production rows have parametric demos and traceable code-versus-code outputs ready for client review. Available rows have working modules without packaged demos. Planned rows have GitHub-tracked work with named dependencies. Per-discipline standards citations inherited from upstream.

**Evidence & legal scope**
- All entries cite repo paths and standards bodies; no client engagements claimed.
- No vessel-named telemetry.
- Legal-scan gate identical to C1.

**Output formats:** PNG brochure, SVG print, PDF 1-page (single-page summary).

**Maps to issue ACs:** AC4 primarily (brochure self-containment).

---

## Traceability Matrix (Issue ACs → Chart concepts)

| Issue #2555 AC | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| AC1 — ≥3 brochure-ready capability charts produced or planned with exact data inputs | ✓ | ✓ | ✓ | (optional) |
| AC2 — every chart has public-source/evidence notes or explicit assumption notes | ✓ | ✓ | ✓ | ✓ |
| AC3 — chart claims suitable for public-facing GTM collateral after legal/evidence sanity review | ✓ | ✓ | ✓ | ✓ |
| AC4 — outputs feed the brochure/send issue without requiring the user to reassemble context | ✓ | ✓ | ✓ | ✓ |

The C1+C2+C3 set alone covers all four ACs. C4 is added if brochure layout permits.

---

## Legal & Evidence Gate (binding)

Before any chart is exported for external use, all of the following must be true and recorded:

1. **Source provenance recorded** — chart's data-input paths cited in the export's accompanying caption/footnote.
2. **Public-vs-private inputs identified** — every data path is from `digitalmodel/examples/demos/gtm/**` (representative-class disclosure inherited) or `docs/gtm/capability-map.md`. No paths from `client_projects/`, `acma-projects/`, `seanation/`, `frontierdeepwater/`, or any private archive.
3. **Methodology and standards citations attached** — caption names DNV/API standards inherited from the JSON `_references`.
4. **Tests/review state known** — chart-render run cleanly; demo source data not regenerated since last cross-provider review.
5. **Legal scan run** — `scripts/legal/legal-sanity-scan.sh --diff-only` over the changed export files passes; output archived alongside the asset commit.
6. **No confidential/client-identifying content promoted** — automated check + manual eyeball before each send.

Provider-review readiness for this storyboard follows the paired plan: preferred evidence is Claude + Codex + Gemini live verdicts; permitted fallback is Claude plus at least one additional live provider verdict, with any unavailable provider explicitly documented with timestamp and blocking reason in `scripts/review/results/2026-04-29-plan-2555-*.md`.

Per `docs/BUSINESS_BRAIN.md:122-132`, this gate is mandatory and cannot be waived for "small" sends.

---

## Operational Notes

- **Re-render trigger:** when any of the source JSONs change (typically a demo rerun), regenerate every chart and re-run the legal scan.
- **Brand alignment:** colour palette and typography must match the locked brand contract from #2426/2435 (per memory `project_claude_design_adoption`). Reconfirm against `aceengineer-website` brand assets before rendering.
- **Headline-number discipline:** only C1's `100% across 30 cases` pair is partially verified in this planning wave; every exact brochure headline must be recomputed against the latest source/result files during rendering, even when a draft number is quoted here.
- **Sibling handoff to #2556:** brochure-send agent reads this storyboard's chart inventory + caption drafts as the canonical chart spec. Headline-number values must be regenerated against the latest demo run before send, not copied from this draft.
- **Sibling handoff to #2554:** contractor recipient list determines whether the chart pack needs additional vessel classes. If recipients include contractors operating outside the 4 representative classes, escalate to #1799 before sending.

---

## Out of Scope (do not attempt under #2555)

- New vessel-class data ingestion → #1799.
- Brochure layout, copy, or send mechanics → #2556.
- Live website embed of charts → not requested by #2555 ACs.
- Per-client-project chart customisation → outside the public-collateral boundary.
- Editing `digitalmodel/` source code → explicitly forbidden by the #2555 plan rules.
