---
name: feedback_ace_standard_html_calc_report
description: "AceEngineer standard HTML format for ALL engineering calculation reports (structure, formulas, flowcharts, provenance)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 837b8583-739c-434d-b895-82d39f7397e9
---

Vamsee set (2026-07-11) the **standard single-file HTML format for every engineering
calculation report**. Use it for all calcs, not just dm#1528.

**Required structure — 2 heading levels (L1 numbered `1..N`, L2 `N.1`), ALL sections
anchor-linked from a sticky Table-of-Contents nav (scrollspy highlights current):**
1. **Objective** (at top) — purpose/scope callout
2. **Design data** (at top) — inputs, constants, geometry, parameter sweep, vessel/case data as KV tables
3. **Analysis methodology** — governing **formulas shown explicitly so users can review/verify**
   (equation cards with equation numbers + a variable-definitions table under each) + methodology
   **flowcharts** (inline SVG)
4. **Detailed results** — one L2 subsection per result, each with its chart/figure
5. **Validation status** — honest provenance ladder (validated / projection / pending)
6. **References & provenance**

**Why:** client-facing engineering deliverable that must be self-contained, portable
(email/PDF), and let a reviewer check the math. Objective+design-data first = reviewer sees
the basis before the results.

**How to apply:**
- **Blank template** `/mnt/local-analysis/ace_calc_report_TEMPLATE.html` (reusable CSS + skeleton
  with example eq card, KV table, flowchart, chart stub, scrollspy). Start here.
- **Reference instance** dm#1528: `/mnt/local-analysis/dm1528_anti_roll_stabiliser_report.html`
  (standalone) + artifact https://claude.ai/code/artifact/56530cd6-e388-43f5-92cd-28052381ec20
- **Formulas WITHOUT MathJax** (CSP blocks CDNs): native HTML/CSS formula cards — italic serif
  `<var>`, fractions via `.frac>.n/.d`, roots via `.rad>.rc` (overline), eq number via `.eno`.
- **Flowcharts** = inline SVG, theme-aware via CSS vars; boxes `.fb`/`.fb.cfd`/`.fb.ro`/`.fb.proj`,
  arrows use a shared `<marker>` arrowhead.
- **Provenance = COLOR** (the honesty guardrail): teal=validated, amber=reduced-order projection,
  muted=pending. Never let a projection read as proven. [[reference_headless_chrome_pdf_image_gotchas]]
- **Charts**: validate palette with dataviz `validate_palette.js` (light+dark surfaces); render in
  headless Chrome (light/dark/mobile) and LOOK before shipping. [[project_dm1528_sloshing_reduced_order]]
- Theme-aware (light/dark tokens), self-contained (no external fetch), AceEngineer branding
  (not "A&CE" per [[feedback_avoid_ace_branding]]). Publish both an Artifact (hosted) AND a
  durable standalone file (portable/emailable — Artifacts are org-auth only).
