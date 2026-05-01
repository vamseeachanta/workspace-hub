---
agent: triage-B-artifacts
date: 2026-05-01
scope: docs/gtm + aceengineer-website demos + GIF renders
---

# GTM Artifacts Audit Report
**Scope:** On-disk reality check for GTM deliverables (docs/gtm, aceengineer-website/content/demos, rendered GIFs)  
**Purpose:** Ground-truth comparison against issue #2422 claims  
**Date:** 2026-05-01

---

## Section 1: `docs/gtm/` Inventory

**Total files:** 21 markdown files (including intake subdirectory)

| File Path | Words | Last Modified | Placeholders | Description |
|-----------|-------|---------------|--------------|-------------|
| `capability-map.md` | 1655 | 2026-04-22 | 0 | Engineering Capability Map — matrix of 17 disciplines with demo assignments, standards, and readiness states (DNV, API, etc.) |
| `capability-summary.md` | 209 | 2026-04-22 | 0 | 1-page executive brief on parametric engineering and GTM positioning |
| `chatbot_fundamentals.md` | 1592 | 2026-04-13 | 0 | Chatbot ontology and design patterns for expert system interaction |
| `client-conversion-pipeline.md` | 2856 | 2026-04-22 | 0 | Prospect-to-closed sales cycle, touchpoint map, objection handler |
| `core-engineering-work-conversion.md` | 1639 | 2026-04-22 | 0 | FIL positioning document: how core engineering work converts to client sales |
| `deliveries-log.md` | 272 | 2026-04-23 | 0 | Handoff log for demos and materials (sparse: 6 entries) |
| `email-outreach-templates.md` | 1567 | 2026-04-13 | 0 | 5 cold email templates for prospect outreach, including follow-up sequences |
| `expert-network-profiles.md` | 1456 | 2026-04-13 | 0 | 3 persona profiles (oil-man, offshore PM, regulatory) for decision-maker targeting |
| `fowt-engineering-scope.md` | 2802 | 2026-04-22 | 0 | Floating Offshore Wind engineering scope: mooring, installation, O&G-to-wind transfer |
| `gif-screencast-scripts.md` | 2474 | 2026-04-13 | 0 | 5 storyboards for demo GIF production (terminal + browser interaction, 30s each) |
| `gtm-plan-30day.md` | 1732 | 2026-04-22 | 0 | 30-day rollout plan with daily milestones, content calendar, and cold email target list |
| `installation-analysis-method-note.md` | 2525 | 2026-04-22 | 0 | Technical deep-dive: DNV H103, OrcaFlex coupling, vessel RAO, mudmat installation |
| `intake/IMPLEMENTATION-STATUS.md` | 768 | 2026-05-01 | 0 | Status tracker for SOP intake documents (3 in progress, 7 TBD per headers) |
| `intake/README.md` | 219 | 2026-04-20 | 0 | Intake folder description: standardized intake templates and process |
| `linkedin-content-calendar.md` | 4718 | 2026-04-22 | 0 | 30-day LinkedIn content calendar with 90 posts, case studies, KPIs, and engagement tactics |
| `lng-berth-operability-framing.md` | 1898 | 2026-04-22 | 0 | Berth operability engineering scope: maritime safety, FSRU ops, terminal screening |
| `marine-terminal-engineering-scope.md` | 2434 | 2026-04-22 | 0 | Marine terminal engineering as GTM vector: mooring checks, fendering, PIANC/OCIMF standards |
| `oil-man-persona.md` | 956 | 2026-04-13 | 0 | Decision-maker persona: oil and gas subsea engineer, pain points, buying signals |
| `outreach-candidate-briefs-2026-04-28.md` | 6836 | 2026-04-29 | 0 | 24 prospect company briefs with decision-maker names, contact, pain points, fit scoring |
| `overnight-client-ready-material-2026-04-28.md` | 2573 | 2026-04-29 | 0 | Client-facing material prep: demo scripts, capability summary, email templates |
| `prospect-demo-sop.md` | 1778 | 2026-05-01 | 0 | Standard Operating Procedure for prospect demo execution (prep, walkthrough, close) |

**Key observations:**
- **No TBD/TODO/FIXME placeholders detected** in any file (all appear content-complete)
- Most files last modified 2026-04-13 to 2026-04-29 (active in April)
- Two files refreshed 2026-05-01: `intake/IMPLEMENTATION-STATUS.md` and `prospect-demo-sop.md`
- **Total word count across 21 files:** ~45,000 words

---

## Section 2: `aceengineer-website/content/demos/` Audit

**Total demos:** 6 files (1 index + 5 demo pages)

| File | HTML Title | PDF CTA (capability-summary-v1.pdf) | Media Assets | Body Word Count |
|------|-----------|-------|--------|---------|
| `index.html` | Overnight Parametric Engineering Demos - AceEngineer | **YES** (line 276: `{{ rootPath }}assets/capability-summary-v1.pdf` download link) | 6 GIFs: `demo_01_freespan.gif`, `demo_02_wall_thickness.gif`, `demo_03_mudmat_installation.gif`, `demo_04_shallow_pipelay.gif`, `demo_05_jumper_installation.gif`, `demo_comparison_matrix.gif` | 502 |
| `freespan.html` | AceEngineer — Freespan / VIV Screening | NO | 0 images, 0 videos | 994 |
| `jumper-installation.html` | AceEngineer — Subsea Jumper Installation Analysis Demo | NO | 0 images, 0 videos | 251 |
| `mudmat.html` | AceEngineer — Deepwater Mudmat Installation | NO | 0 images, 0 videos | 1320 |
| `pipelay.html` | AceEngineer — Shallow Water Pipelay | NO | 0 images, 0 videos | 1886 |
| `wall-thickness.html` | AceEngineer — Pipeline Wall Thickness | NO | 0 images, 0 videos | 1753 |

**Key observations:**
- **PDF CTA is ONLY on the demos index page** (`index.html`), not on individual demo pages
- **All 5 demo GIFs are present and rendered** (checked in `aceengineer-website/assets/img/demos/`)
  - `demo_01_freespan.gif` (874 KB, dated 2026-04-15)
  - `demo_02_wall_thickness.gif` (820 KB)
  - `demo_03_mudmat_installation.gif` (788 KB)
  - `demo_04_shallow_pipelay.gif` (873 KB)
  - `demo_05_jumper_installation.gif` (877 KB)
- Individual demo pages contain **no embedded images or videos** — they are text/table based, not visual reports
- Individual demo pages do NOT link to the PDF

---

## Section 3: GIF/Video Render Reality Check

**Source:** `docs/gtm/gif-screencast-scripts.md` (5 storyboards defined)

| Storyboard | Filename Convention (from script) | Rendered File Found? | Location | Size |
|-----------|------|------|----------|------|
| Demo 1: DNV Freespan/VIV (680 cases) | `demo_01_dnv_freespan_viv.gif` | **YES** | `aceengineer-website/assets/img/demos/demo_01_freespan.gif` | 874 KB |
| Demo 2: Wall Thickness Multi-Code (72 cases) | `demo_02_wall_thickness_multicode.gif` | **YES** | `aceengineer-website/assets/img/demos/demo_02_wall_thickness.gif` | 820 KB |
| Demo 3: Deepwater Mudmat Installation (180 cases) | `demo_03_deepwater_mudmat_installation.gif` | **YES** | `aceengineer-website/assets/img/demos/demo_03_mudmat_installation.gif` | 788 KB |
| Demo 4: Shallow Water Pipelay (60 cases) | `demo_04_shallow_water_pipelay.gif` | **YES** | `aceengineer-website/assets/img/demos/demo_04_shallow_pipelay.gif` | 873 KB |
| Demo 5: Deepwater Rigid Jumper (300 cases) | `demo_05_deepwater_rigid_jumper.gif` | **YES** | `aceengineer-website/assets/img/demos/demo_05_jumper_installation.gif` | 877 KB |

**Key observations:**
- **All 5 storyboards have corresponding rendered GIFs** ✓
- Files stored in `aceengineer-website/assets/img/demos/` (not in `docs/gtm/media/` as script suggests)
- All GIFs are **between 788–877 KB** (well under 5 MB LinkedIn limit)
- **No GIF files in `docs/gtm/media/`** (directory does not exist)
- Script anticipates `docs/gtm/media/demo_0X_*.gif` output path, but actual renders are in website asset folder

---

## Section 4: `docs/gtm/website-pages/` Audit

**Total files:** 5 HTML files

| File | HTML Title | PDF CTA | Media Assets | Body Word Count |
|------|-----------|-------|--------|---------|
| `capability-summary.html` | ACE Engineer — Capability Summary | NO | 0 images, 0 videos | 126 |
| `methodology-compound-engineering.html` | Compound Engineering — ACE Engineer Methodology | NO | 0 images, 0 videos | 947 |
| `methodology-enforcement.html` | Enforcement Over Instruction — ACE Engineer Methodology | NO | 0 images, 0 videos | 920 |
| `methodology-multi-agent-parity.html` | Multi-Agent Parity — ACE Engineer Methodology | NO | 0 images, 0 videos | 1096 |
| `methodology-orchestrator-worker.html` | Orchestrator-Worker Architecture — ACE Engineer Methodology | NO | 0 images, 0 videos | 984 |

**Key observations:**
- All 5 files are **text-only (no embedded media)**
- None link to or reference the PDF CTA
- Total word count: 4,073 words (light content)
- These appear to be methodology reference pages, not demo landing pages

---

## Section 5: Cross-Reference — The 5 Demos in #2422

**Issue #2422 references these 5 demos:** freespan, jumper-installation, mudmat, pipelay, wall-thickness

| Demo | Demo HTML exists? | PDF CTA on page? | Embedded Media (count) | Body Word Count | Storyboard in gif-screencast-scripts.md? | Rendered GIF found? |
|------|---------|------|-------|-----------|-----------|-------|
| **freespan** | YES (`freespan.html`) | NO | 0 | 994 | YES (Demo 1: 680 cases) | **YES** (`demo_01_freespan.gif`, 874 KB) |
| **jumper-installation** | YES (`jumper-installation.html`) | NO | 0 | 251 | YES (Demo 5: 300 cases) | **YES** (`demo_05_jumper_installation.gif`, 877 KB) |
| **mudmat** | YES (`mudmat.html`) | NO | 0 | 1320 | YES (Demo 3: 180 cases) | **YES** (`demo_03_mudmat_installation.gif`, 788 KB) |
| **pipelay** | YES (`pipelay.html`) | NO | 0 | 1886 | YES (Demo 4: 60 cases) | **YES** (`demo_04_shallow_pipelay.gif`, 873 KB) |
| **wall-thickness** | YES (`wall-thickness.html`) | NO | 0 | 1753 | YES (Demo 2: 72 cases) | **YES** (`demo_02_wall_thickness.gif`, 820 KB) |

**Verdict:**
- **All 5 demos exist and are rendered** ✓
- **PDF CTA is missing from all individual demo pages** (only on index page) ✗
- **Zero embedded images/videos on individual demo pages** — all are text-based technical reports, not visual showcases ✗
- GIF storyboards are complete and rendered

---

## Section 6: Top 5 Delivery Gaps

### Gap 1: Individual Demo Pages Lack PDF CTA Button
**Severity:** HIGH | **Impact:** Conversion friction  
**What's missing:** Each of the 5 demo detail pages (`freespan.html`, `jumper-installation.html`, `mudmat.html`, `pipelay.html`, `wall-thickness.html`) should have a prominent "Download Capability Summary" CTA button or link to `{{ rootPath }}assets/capability-summary-v1.pdf`. Currently only the demos index has this.  
**Evidence:** Grep for "capability-summary-v1.pdf" returns only `index.html` at line 276; zero matches on individual demo pages.

### Gap 2: Demo Pages Are Text-Only Technical Reports, Not Visual Showcases
**Severity:** HIGH | **Impact:** Marketing friction — no embedded demo visualization  
**What's missing:** Issue #2422 and sales collateral suggest "interactive demos" with "embedded media," but the HTML pages contain **zero embedded images or video players**. The GIFs exist (in `aceengineer-website/assets/img/demos/`) but are not linked/embedded on the individual demo pages.  
**Evidence:** `mudmat.html` (1320 words) and `pipelay.html` (1886 words) are dense tables and technical text. No `<img>`, `<video>`, or `<iframe>` tags detected on any demo page.

### Gap 3: GIF Output Path in Script vs. Actual File Location Mismatch
**Severity:** MEDIUM | **Impact:** Future demo recording confusion  
**What's missing:** `gif-screencast-scripts.md` anticipates output to `docs/gtm/media/demo_0X_*.gif`, but all actual rendered GIFs are in `aceengineer-website/assets/img/demos/`. The script section 2 "Pre-Recording Checklist" says `mkdir -p docs/gtm/media`, but `docs/gtm/media/` does not exist and GIFs are elsewhere.  
**Evidence:** No files in `/mnt/local-analysis/workspace-hub/docs/gtm/media/` (directory missing). GIFs confirmed in `aceengineer-website/assets/img/demos/`.

### Gap 4: Jumper-Installation Demo Page Has Suspiciously Low Word Count
**Severity:** MEDIUM | **Impact:** Incomplete content?  
**What's missing:** `jumper-installation.html` has only 251 body words — significantly lower than the other 4 demos (994–1886 words). While the page does contain a functional engineering report, it may be under-developed vs. peers. Possible stub or placeholder that was not fully fleshed out.  
**Evidence:** Word count audit in Section 2 shows: freespan (994), wall-thickness (1753), mudmat (1320), pipelay (1886), jumper-installation (251).

### Gap 5: No "Run This on Your Data" / "Request Demo" CTA on Individual Pages
**Severity:** MEDIUM | **Impact:** Sales funnel leak  
**What's missing:** The demos index (`index.html`) has "Run this on your data" buttons on each demo card, but individual demo pages do not appear to have equivalent conversion CTAs beyond the generic page header/footer.  
**Evidence:** Reading `jumper-installation.html` (line 23–92) shows no visible CTA buttons tied to contact, request, or "run this analysis" flows.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total GTM artifacts audited** | 31 (21 markdown + 5 website-pages HTML + 5 demos HTML) |
| **Files with TBD/TODO/FIXME** | 0 |
| **Demo GIFs rendered** | 5/5 (100%) ✓ |
| **Individual demos with PDF CTA** | 0/5 (0%) ✗ |
| **Individual demos with embedded media** | 0/5 (0%) ✗ |
| **Demos with storyboard + rendered output match** | 5/5 (100%) ✓ |

---

## Report Generation

- **Report file:** `docs/sessions/2026-05-01-gtm-triage-agent-b.md`
- **Date generated:** 2026-05-01 13:47 UTC
- **Agent:** triage-B-artifacts (read-only file discovery and audit)
