> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_report_hub_design_system.md

---
name: feedback_report_hub_design_system
description: "Owner-approved report-hub design = THE consistent design for all worldwide field-data surfaces; self-contained pages, evidence badges, drill-down tiers, navigable site, data on HF"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cbc7324a-9fb1-42c9-a2c4-de216e1958cb
  modified: 2026-07-25T01:03:28.882Z
---

**2026-07-25 owner directive:** the report-hub design (first seen in the Tank Sloshing CFD artifact, then approved for D&C QA/QC) is **the consistent design for all worldwide oil & gas field data surfaces**, "with drill down to assets, engineering etc." Plus two riders: **"aceengineer website should be navigable"** and **"data should belong to hugging face"**.

**Why:** the site grew as disconnected report families (atlas, lifecycle, cost, benchmark, decommissioning) with no shared visual grammar, no cross-navigation, and provenance scattered between GitHub and HF. The hub design solves all three at once and encodes the honesty system visually.

**How to apply:**
- New/refactored report surfaces follow the hub grammar: self-contained single file (inline CSS tokens light+dark, system fonts, inline SVG, zero external assets); sticky mono capability nav; hero = eyebrow + h1 + lede + **disposition pill** (one-line verdict incl. open caveats) + facts row; at-a-glance tiles + chart card; **evidence badges** on every card (ok=reconciled / warn=caveat retained / accent=interactive index / grey=pending-provenance); tiered depth Understand→Explore→Open question→Source; guided reading path; badge legend; provenance footer.
- Reference implementation: wed `reports/lower_tertiary/wo-april-2026-qaqc-hub.html` (PR #1058) + artifact 387999d3-91c7-4dab-accf-97e4cff41d36; original pattern = sloshing hub artifact 019ab20f.
- Every page reachable from every page (nav, no dead ends) — wed epic **#1059**, aceengineer-website **#76**.
- Source/provenance cards point at canonical `aceengineer/*` Hugging Face datasets (sloshing pattern); committed-CSV links are interim until the family's data is on HF.
- Flow that worked: artifact mockup → owner approve → commit as page with self-containment gate tests (no link/script/img/@import; relative-link enumeration; both themes present).

Related: [[feedback_ace_standard_html_calc_report]] [[feedback_unique_live_links_traffic_credibility]] [[project_wo_april_validation_roy_qaqc]]
