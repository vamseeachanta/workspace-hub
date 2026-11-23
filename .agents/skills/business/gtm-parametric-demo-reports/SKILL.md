---
name: gtm-parametric-demo-reports
version: 1.0.0
category: business
description: "Create parametric engineering demo reports (HTML+PDF) for cold outreach to marine/offshore contractors. Data-first architecture: input DBs → parametric sweep → output DBs → comparison matrices → branded interactive report."
type: workflow
capabilities:
- parametric_engineering_analysis
- interactive_html_reports
- vessel_structure_comparison
- cold_outreach_collateral
requires: []
trigger: manual
---

# GTM Parametric Demo Reports

> Workflow for building self-contained interactive HTML engineering reports as cold outreach sales collateral. The report IS the deliverable -- not a mockup.

## When to Use

- Building demo/sample reports to send to prospective clients
- Creating parametric engineering studies that showcase capability
- Comparing vessels, structures, pipe sizes, or codes across a matrix
- Any "overnight engineering" demonstration

## Cold Outreach Design Principles

1. **Self-explanatory** -- no one walks them through it; must stand alone
2. **Case-count headline** -- lead with volume: "108 cases screened overnight"
3. **First 5 seconds matter** -- the headline must trigger: "this would take my team 2 weeks"
4. **Real deliverable feel** -- not a toy, not a slide deck
5. **Defensible engineering** -- proper code clause refs, safety factors, material data; senior engineers will spot-check
6. **LIVE MODE teaser** -- plant seed for higher-value retainer: "In LIVE MODE, feed VMMS/IMMS for real-time go/no-go"

## Data Architecture (Three Layers)

### Layer 1: Input Databases (`gtm/data/`)

Create JSON databases per category BEFORE writing any demo code:

| File | Purpose |
|------|---------|
| `pipelines.json` | Pipe catalog: OD, WT schedules, grades, SMYS/SMTS, submerged weight |
| `csv_hlv_vessels.json` | Construction vessels: crane curves (SWL vs radius), dims, RAOs |
| `pipelay_vessels.json` | Pipelay vessels: tensioner capacity, stinger config, depth range |
| `mudmat_structures.json` | Structures: dims, mass, CoG, hydro coefficients (C_s, C_D, C_a) |
| `rigid_jumpers.json` | Jumpers: length, OD, WT, mass per meter, total mass |
| `freespan_scenarios.json` | Environmental: currents, span lengths, soil types, gap ratios |
| `design_codes.json` | Code metadata: safety factors, clause refs, edition years |

**Key rule**: Calculate derived values (mass/m, submerged weight) from first principles using a calc script, don't guess. Include `_description`, `_version`, `_references` in every JSON.

### Layer 2: Output Results (`gtm/results/`)

One JSON per demo, array of case objects. Every case has:
```json
{
  "case_id": "XXX-001",
  "inputs": { "vessel": {...}, "structure": {...}, "environment": {...} },
  "results": { "utilisation": N, "status": "PASS|FAIL", "governing_check": "..." },
  "code_ref": "DNV-RP-XXXX Sec Y.Z",
  "timestamp": "ISO-8601"
}
```

Create schema files with `null` result values BEFORE building the demo scripts. This forces you to think through the output structure.

### Layer 3: Comparison Matrices (`gtm/results/`)

Two cross-demo aggregation files:

**vessel_comparison_matrix.json** -- "What can each vessel do?"
- Per vessel: go/no-go grid across all structures x depths
- Head-to-head: Vessel A vs B, where does one become limited?
- Overall score: total pass rate, strongest/weakest capability

**structure_comparison_matrix.json** -- "Which structure is hardest?"
- Per category: compare structures on same vessel at same depth
- Breakpoints: at what size/weight/length does it go from GO to NO_GO
- Code comparison: which code is most conservative, weight penalty %

## Report Format (HTML + PDF)

- **Primary**: Interactive HTML with embedded Plotly (single .html file, works offline)
- **Fallback**: PDF via print-friendly CSS (`@media print` in same HTML)
- Both from same Python script

### HTML Template Requirements
- digitalmodel branding (header, colors)
- Plotly charts (hover, zoom, pan)
- Color-coded pass/fail tables (green/red/amber)
- Methodology section with code clause references
- Assumptions and limitations footer
- LIVE MODE teaser section at bottom
- Case count in the title: "84 Freespan Cases Screened Overnight"

## Workflow Steps

1. **Discuss scope** -- nail down parameter matrix, audience, pitch
2. **Create input databases** -- JSON files with real engineering values
3. **Create output schemas** -- empty result templates with null values
4. **Create comparison matrix templates** -- vessel x structure grids
5. **Identify data gaps** -- spin GH issues for missing data (e.g. vessel specs)
6. **Build demo scripts** -- start with demos that have all data available
7. **Generate reports** -- run scripts, populate results, build HTML
8. **Populate comparison matrices** -- aggregate across demos

## Pitfalls

- **Don't let missing data block everything**: Create representative/generic databases, spin GH issues for real data, build demos with what you have. Swap real data in later.
- **Vessel data is always the hardest to get**: Crane curves, RAOs need public spec sheets or industry databases. Pipeline data is easy (API 5L tables).
- **Senior engineers spot-check numbers**: If wall thickness or safety factors look wrong, the entire demo loses credibility. Use real code formulas.
- **Email attachment gotcha**: Some corporate email servers block .html files. Zip it or host on a link. PDF fallback covers this.
- **Case count is the hook**: "36 cases" doesn't impress. Aim for 50-200+ cases per demo to trigger "this would take weeks."

## Shared Report Template (report_template.py)

The GTMReportBuilder class handles all branding, charts, and PDF export. Key API:

```python
from report_template import GTMReportBuilder, COLORS, CHART_PALETTE

report = GTMReportBuilder(
    title="Pipeline Wall Thickness — Multi-Code Comparison",
    subtitle="72 parametric cases across 6 pipe sizes and 3 design codes",
    demo_id="demo_02",
    case_count=72,
    code_refs=["DNV-ST-F101 (2021)", "API RP 1111 (2015)", "PD 8010-2 (2015)"],
)
report.add_methodology("<p>...</p>")          # Goes first
report.add_chart("chart_id", plotly_fig, title="...", subtitle="...")
report.add_table("title", df, status_col="Status")  # Auto color-codes PASS/FAIL
report.add_live_mode_teaser("this analysis")  # VC funding + VMMS/IMMS pitch
report.add_assumptions(["assumption 1", "assumption 2"])
report.build("output/report.html")
```

**Template features**: Inter font, navy/orange brand colors, 8-color chart palette, animated LIVE badge, $500K VC funding badge, CTA mailto link, `@media print` for PDF.

## Lifecycle Utilisation Chart Pattern (Wall Thickness Hero Chart)

The strongest visualization for pipeline demos: a single chart showing utilisation across ALL lifecycle phases with code comparison.

- X-axis: lifecycle phases (Installation, Hydrotest, Operation-Early, Operation-Late, Shutdown)
- Y-axis: utilisation ratio (0 to max, unity line at 1.0)
- Grouped bars: one per design code
- Dropdown selector: pipe size
- Color: green (<0.7), amber (0.7-0.9), red (>0.9)
- Use `create_standard_phases(water_depth, design_pressure)` + `PhaseAnalysisRunner`

This pattern applies to ANY parametric engineering demo -- show utilisation across conditions, not just pass/fail.

## GIF Screencast Pattern (Issue #1809)

Each demo should produce a .gif showing the FULL WORKFLOW:
1. User types natural language prompt in CLI (3s)
2. Agent navigates digitalmodel codebase (5s)
3. Parametric analysis runs with case counter ticking (10s)
4. Report generated message (3s)
5. Browser showing interactive HTML with hover/zoom (10s)

Tool: `vhs` (charmbracelet/vhs) for reproducible scripted terminal GIFs. Target: <5MB, 20-30s, 1024x768.

## Pre-Build Discussion Checklist (MANDATORY)

Before writing any code, resolve these with the user:

1. **Who is the audience?** Cold outreach vs follow-up vs live demo changes everything
2. **What's the sales message?** "Overnight engineering" vs "real-time ops" vs "cost savings"
3. **Engineering rigor level?** Real defensible calcs (slower, credible) vs approximate (faster, less impressive)
4. **Data availability?** Do we have vessel data or need GH issues to collect it?
5. **Branding?** digitalmodel vs aceengineer vs client-specific
6. **Format?** HTML primary + PDF fallback is the proven choice
7. **Chart lineup?** Discuss specific visualisations BEFORE building -- the user will have opinions on what tells the story

The user thinks in terms of "what chart will land the point" not "what data do we have." Start from the chart concept and work backwards to the engineering.

## Lessons Learned

- **Discuss before building**: The user will course-correct the demo scope, format, and chart lineup. Items 3 and 5 were duplicates. The user added "rigid jumper" to item 5 mid-conversation. Discuss FIRST.
- **Build order matters**: Start with demos where modules already exist (wall thickness had full analyzer + parametric sweep + phase analysis). Demos needing new engineering calcs (freespan, catenary) take 2-3x longer.
- **Mid-range WT from catalog gives better demo than minimum WT**: Using minimum standard WT often shows 0.1 utilisation (boring). Mid-range shows variation across 0.2-1.4 (interesting PASS/FAIL mix).
- **FAIL cases are a selling point**: 16"/20" pipes all FAIL at mid-range WT -- this is GOOD for the demo. It shows "you would have caught this overnight." Don't sanitise results to all-PASS.
- **Progress counter is part of the demo**: Print "Case 42/72 | 12in X65 | DNV-ST-F101 | 20 MPa... util=0.716 [PASS]" -- this becomes the GIF content.
- **Binary search for min WT**: Finding minimum required wall thickness uses binary search with 0.1mm tolerance, not brute-force sweep. Much faster.
- **Propagation buckling often governs at 500m+**: At deepwater, collapse/propagation checks drive the design more than pressure containment. The demo should show this insight explicitly.
- **PYTHONPATH setup**: Scripts run with `PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_XX.py`
- **try/except per case**: Wrap individual parametric cases so one failure doesn't kill the sweep. Record failed cases as N/A in results JSON.
- **First `uv run` takes ~17-20s** for bytecode compilation (32K+ files). Subsequent runs are ~2-3s. Account for this in GIF timing -- either pre-warm or start the GIF after the compile step.
- **Don't let missing vessel data block everything**: Create generic databases immediately, spin GH issues for real data in parallel. The user explicitly said "create databases as needed" rather than wait.

## Reference Implementation

Location: `digitalmodel/examples/demos/gtm/`
- `report_template.py` -- shared HTML builder (GTMReportBuilder class)
- `data/` -- 7 input databases
- `results/` -- 5 output schemas + 2 comparison matrices
- `output/` -- generated HTML reports
- `demo_02_wall_thickness_multicode.py` -- reference demo (1116 lines, 72 cases, 5 charts)
- GitHub tracking: #1800 (master), #1798 (CSV/HLV data), #1799 (pipelay data), #1809 (GIF screencasts)
