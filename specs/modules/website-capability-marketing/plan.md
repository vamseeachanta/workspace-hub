---
title: Market digitalmodel & worldenergydata capabilities on aceengineer website
description: Roll two platform capabilities into the marketing website with new service pages, updated navigation, and lead-generation content
version: 1.0.0
module: website-capability-marketing
source_work_item: WRK-073
session:
  id: 20260202-website-marketing
  agent: claude-opus-4.5
review:
  status: pending
  iterations: 0
---

# Plan: Market digitalmodel & worldenergydata on aceengineer website

## Context

The aceengineer.com website currently markets only **engineering automation** (OrcaFlex, AQWA, fatigue analysis). Two major platforms with business-generating potential are absent:

1. **digitalmodel** — 47+ analysis modules, 221 S-N curves, digital twin workflows, OrcaFlex/AQWA/WAMIT/Blender/GMSH integration
2. **worldenergydata** — 15+ global data sources, marine safety (10+ authorities), field development economics (NPV/IRR/MIRR), production analytics

### Current Website State
- Static HTML + Bootstrap 3, PostHTML build, Vercel hosting
- Pages: index.html, about.html, engineering.html (strong), energy.html (weak/stub), faq.html, contact.html
- 9 blog posts, 4 case studies, 2 interactive calculators
- Lighthouse scores: 100 accessibility/SEO
- Design: marketing.css with established component patterns

### Gap Analysis
| Capability | Currently on Website | Missing |
|-----------|---------------------|---------|
| OrcaFlex automation | Yes (strong) | - |
| AQWA integration | Yes (strong) | - |
| Fatigue analysis | Yes (strong) | - |
| Mooring/riser design | Yes (strong) | - |
| Digital twin platform | Mentioned once | Full capability showcase |
| Energy data analytics | Not present | Entire service line |
| Marine safety intelligence | Not present | Entire service line |
| Field development economics | Not present | Entire service line |
| Production forecasting | Not present | Entire service line |
| Multi-source data aggregation | Not present | Entire service line |

## Implementation Plan

### Step 1: Revamp energy.html (Primary Impact)

**Current state**: Bare stub page with placeholder text, no marketing.css, no verticals.
**Target state**: Full marketing-grade page matching engineering.html quality.

**Content structure**:
- Hero: "Turn Raw Energy Data Into Strategic Decisions"
- Solution features (4 cards):
  - **Energy Data Aggregation** — 15+ sources, unified CLI, automated collection
  - **Field Development Economics** — NPV/IRR/MIRR, Excel-validated, production forecasting
  - **Marine Safety Intelligence** — 10+ global authorities, incident correlation, risk scoring
  - **Production Analytics** — BSEE, SODIR, AER/BCER, Texas RRC, Mexico CNH
- Industry verticals (3 sections):
  - **For E&P Operators** — field economics, production tracking, regulatory compliance
  - **For Energy Investors** — due diligence data, economic modeling, portfolio analytics
  - **For Maritime & Offshore Operators** — safety intelligence, incident tracking, risk dashboards
- Metrics section: 15+ data sources, 10+ safety authorities, 100% Excel-validated, Global coverage
- Pricing comparison (data services vs manual research)
- CTA: "Get a Data Assessment"

**Files**: `energy.html`, `assets/css/marketing.css` (if new styles needed)

### Step 2: Update index.html Homepage

**Changes**:
- Add "Energy Data & Analytics" vertical card alongside existing 3 verticals
- Update metrics section to reflect combined platform numbers
- Add new badge items for data capabilities (BSEE, SODIR, NPV)
- Update hero subtitle to encompass both engineering + data services

**Files**: `index.html`

### Step 3: Update Navigation

**Changes**:
- Add dropdown or restructure nav to show services hierarchy:
  - Engineering (existing)
  - Energy Data (revamped energy.html)
- Ensure consistent nav across all pages
- Update footer links to include new service areas

**Files**: All HTML files with nav (index.html, about.html, engineering.html, energy.html, faq.html, contact.html, blog pages, case study pages)

### Step 4: Update contact.html

**Changes**:
- Add new industry verticals to dropdown selector:
  - Energy Operator
  - Energy Investor/Analyst
  - Maritime/Shipping
  - Regulatory/Government
- Update form subject options

**Files**: `contact.html`

### Step 5: Add JSON-LD Structured Data

**Changes**:
- Service schema for energy data services on energy.html
- Update Organization schema knowsAbout on index.html
- BreadcrumbList for energy.html

**Files**: `energy.html`, `index.html`

### Step 6: Update faq.html

**Changes**:
- Add 3-4 FAQs about energy data services:
  - "What energy data sources do you integrate?"
  - "How do your financial models compare to Excel?"
  - "What marine safety databases do you cover?"
  - "Can I get custom data dashboards?"

**Files**: `faq.html`

## Marketing Strategy Embedded in Implementation

### Lead Magnets (Free Tools)
- Existing: S-N Curve Calculator, Fatigue Life Calculator
- Future (mention as "Coming Soon"): NPV Calculator, Marine Safety Search

### Service Packages to Market
| Package | Source Platform | Target Buyer |
|---------|---------------|-------------|
| Engineering Automation | digitalmodel | Offshore firms, EPC |
| Energy Data as a Service | worldenergydata | Operators, investors |
| Safety Intelligence | worldenergydata | Maritime, insurers |
| Field Development Advisory | worldenergydata | E&P companies |
| Digital Twin Platform | digitalmodel | Asset owners |

### Key Marketing Numbers
- 47+ analysis modules (digitalmodel)
- 221 S-N curves from 17 standards (digitalmodel)
- 15+ energy data sources (worldenergydata)
- 10+ marine safety authorities (worldenergydata)
- 100% Excel-validated financial models (worldenergydata)
- 60-80% time savings vs manual analysis (both)

## File Change Summary

| File | Change Type | Scope |
|------|------------|-------|
| `energy.html` | **Major rewrite** | Complete page rebuild with marketing content |
| `index.html` | Edit | Add energy data vertical, update metrics/badges |
| `contact.html` | Edit | Add new industry verticals to form |
| `faq.html` | Edit | Add energy data FAQs |
| `engineering.html` | Minor edit | Nav consistency, footer links |
| `about.html` | Minor edit | Nav consistency |

## Implementation Order

1. `energy.html` — biggest impact, standalone page
2. `index.html` — homepage updates to reference new services
3. Navigation updates across all pages
4. `contact.html` — new verticals in form
5. `faq.html` — new Q&As
6. Verify build and Lighthouse scores

## Out of Scope (Future Work Items)
- New blog posts about energy data topics
- New case studies for data services
- Interactive NPV calculator tool
- Marine safety search dashboard
- Newsletter/email capture implementation
