---
title: "WRK-146: Website Overhaul — Positioning, Narrative, and Social Proof"
description: "Complete content overhaul of aceengineer-website: replace AI buzzwords with engineering-outcome language, rewrite About page, add social proof, narrative case studies"
version: "1.0"
module: aceengineer-website
session:
  id: wrk-146-website-overhaul
  agent: claude-opus-4-6
review: pending
---

# WRK-146: Website Overhaul — Positioning, Narrative, Social Proof

## Context

External feedback identified a **positioning problem**: strong engineering substance packaged as generic AI consultancy. The site has 233+ "AI" buzzword occurrences. Competitor research (Cognite, Akselos, Wood Group, 2H Offshore) confirms: **successful offshore firms do NOT lead with "AI"**. They lead with engineering outcomes and quantified results.

**Key strategic decision**: Position A&CE as an engineering analytics firm that happens to use computational methods, not a technology vendor selling AI. Follow the 2H Offshore / Akselos model — engineering credibility first, technology as tools.

**Language principle**: Replace "AI-native/AI-enhanced/AI-powered" with precise engineering language — "computational methods", "automated workflows", "data-driven analysis", "surrogate models". Keep "AI" only where it's the actual technical subject (certain blog posts).

## GTM Stream Context (WRK-148 Parent)

This is a child of **WRK-148: A&CE Go-to-Market Strategy Stream**. The website must support:

**Positioning**: "Offshore engineering analytics at scale" — a FIRM with a computational platform, not a person with skills. Clients buy from firms; procurement justifies $120K retainers to companies, not freelancers.

**Ideal Customer Profile (ICP)**: Mid-market offshore engineering firms (10-50 engineers) who:
- Run OrcaFlex/AQWA manually for every project
- Have 2-3 senior engineers bottlenecked on repetitive analysis
- Need standards compliance (DNV, API, ABS) but can't afford full-time code development

**Revenue target**: 3-5 retainers at $120K = $360-600K annual

**Target company tiers** (website must credibly support outreach to):
- Tier 1: Subsea7, Wood Group, Worley, TechnipFMC
- Tier 2: 2H Offshore, McDermott, Saipem
- Tier 3: DNV Digital, ABS, Bureau Veritas
- Tier 4: Akselos, Cognite (tech partnership)
- Tier 5: Orsted, Equinor, Shell, Chevron (direct operator)

**Conference strategy**: OTC Houston (May 4-7), ISOPE (May 31-Jun 5), OMAE (Jun 7-12) — website must be polished before May 2026.

**Key numbers to feature**: 704+ modules, 221 S-N curves from 17 standards, 15+ years experience, 8 design codes, 245 curated datasets, OrcaFlex/AQWA batch automation.

**Positioning sequence**: Phase 1 (now) = Firm positioning + win clients. Phase 2 (parallel) = Build founder's personal brand as expert BEHIND A&CE. "Sell the firm. Promote the founder."

## Tech Stack

- **Framework**: Custom static HTML + PostHTML build system (Node.js)
- **Source**: `src/` directory (edit here)
- **Output**: `dist/` directory (build output) + root HTML files (GitHub Pages serves root)
- **CSS**: Bootstrap 3.x (United theme) + `marketing.css` + `responsive.css`
- **Build**: `npm run build` → PostHTML includes/expressions → PurgeCSS → minified output

## AI Language Replacement Table

| Current | Replacement |
|---------|-------------|
| "AI-native" (22+ occurrences) | "Advanced computational" or "Data-driven" |
| "AI-enhanced" (8+ occurrences) | "Automated" or remove entirely |
| "AI-powered" | "Computational" or "Algorithmic" |
| "Machine learning" (in headlines) | "Surrogate model" or "Data-driven prediction" |
| "AI engineering" (in meta/SEO) | "Computational engineering" |
| "ML-Enhanced" (case study titles) | "Computational" or "Data-Driven" |

**Keep AI in**: Blog posts where AI/ML is the actual technical subject (not a modifier), and ONE strategic mention on the About page as part of the technology story.

## Implementation Plan

### Phase 1: Homepage + About (Highest Impact)

#### 1A. Homepage — `src/index.html` (534 lines)

The homepage hero ("Run 50 Riser Configurations Overnight") is already strong — keep it.

**Changes:**
1. Add **firm identity line** under hero subtitle: "Analytical & Computational Engineering — 15+ years of offshore engineering distilled into 704 production-tested Python modules"
2. Add **"Why A&CE" section** after Pain Points (3 cards):
   - "704+ Production Modules" — validated, tested, production code
   - "15+ Years Offshore" — DNV, API, ABS standards compliance
   - "Automated Workflows" — batch processing, not consulting hours
3. Add **Social Proof section** before CTA: standards badges (DNV, API, ABS, BS, Norsok), industry verticals served, "17 international standards codified"
4. Add **ICP-targeted verticals** (from WRK-148): explicit messaging for mid-market offshore engineering firms (10-50 engineers), EPC contractors, and classification societies — these are the primary buyer personas
5. Add **conference/event badges** if appropriate: "See us at OTC Houston 2026" or similar CTA
6. **AI language fixes**:
   - Blog preview: "AI-enhanced RBI approaches" → "Data-driven RBI approaches"
   - Case study card: "ML-Enhanced Fatigue Assessment" → "Computational Fatigue Assessment"

#### 1B. About Page — `src/about.html` (204 lines)

**Complete rewrite** from 4 stale sentences to full firm story:

- **Hero**: "Offshore Engineering Analytics at Scale"
- **The A&CE Story**: Founded 2010 by Vamsee Achanta. 15+ years deepwater experience (GoM, North Sea, global). Evolved from consulting to computational engineering firm by codifying offshore knowledge into 704+ production modules. Frame as FIRM journey, not personal bio — "A&CE was founded..." not "I started..."
- **By The Numbers**: 704+ modules | 221 S-N curves from 17 standards | 8 design codes | 245 curated datasets
- **How We Work**: "We deliver automated workflows, not consulting hours. You send a design matrix, we return validated results."
- **Who We Serve** (ICP from WRK-148): Mid-market offshore engineering firms (10-50 engineers) who run OrcaFlex/AQWA manually, EPC contractors needing standards compliance, classification societies exploring digital services
- **Technology Stack**: OrcaFlex API, AQWA, Python/Polars, open-source computational tools. ONE permitted mention of advanced tooling: "Our workflows leverage automated orchestration to deliver team-scale throughput from a focused engineering practice."
- **Founder** (separate subsection): Vamsee Achanta, Principal Engineer — 15+ years, former [relevant companies if public]. Position as expert BEHIND the firm, not the firm itself.
- **Standards**: DNV-RP-C203, API RP 2A, BS 7608, ABS, Norsok, IEC 61400-3, ASME B31.8
- **Meta tags**: Remove "machine learning, artificial intelligence" → "computational analysis, engineering automation, offshore engineering"
- **JSON-LD**: Remove "AI-Native Engineering Services" → "Computational Engineering Services"

### Phase 2: Service Pages + Navigation

#### 2A. Engineering Page — `src/engineering.html` (492 lines)

1. **Link pricing claims to case studies**: Each pricing row gets a "See case study →" link
2. **Replace "ML-Enhanced"** in case study references → "Computational"
3. **Add standards compliance badges** under pricing table
4. **Add "Related Articles" section** linking to technical blog posts

#### 2B. Energy Page — `src/energy.html`

**Pre-requisite**: The `src/energy.html` (224 lines) has diverged from root `energy.html` (580 lines). Back-port root content into `src/` using PostHTML `<include>` partials, then review for AI language.

#### 2C. Navigation — `src/partials/nav.html` (31 lines)

Add "Energy Data" as separate nav item alongside "Engineering" (currently not in nav). Update CTA text if appropriate.

#### 2D. Footer — `src/partials/footer.html` (34 lines)

Add Energy Data link, add "Standards: DNV, API, ABS, BS, Norsok" trust signal.

### Phase 3: Case Study Rewrites (2 narratives)

#### 3A. OrcaFlex Riser Sensitivity — `src/case-studies/orcaflex-riser-sensitivity-automation.html`

Rewrite as narrative:
- **Challenge**: "A mid-market firm faced 3-week timeline for GoM SCR sensitivity..."
- **Process**: "Design matrix received Monday. 50 configurations ran overnight..."
- **Outcome**: "3 weeks → 3 days. $35K savings. Engineers focused on interpretation."

#### 3B. Offshore Platform Fatigue — `src/case-studies/offshore-platform-fatigue-optimization.html`

- Title: "ML-Enhanced" → "Computational" or "Data-Driven"
- Add narrative opening (Challenge → Process → Outcome)
- Keep ML methodology details in technical section (correct context)
- Remove "AI-native structural assessment" → "computational structural assessment"

#### 3C. Case Studies Index — `src/case-studies/index.html`

Bulk AI language replacement in meta tags, titles, descriptions:
- "AI-native approaches" → "advanced computational methods" (~6 occurrences)
- "AI-Enhanced Wind Turbine" → "Computational Wind Turbine"
- "ML-based anomaly detection" → "algorithmic anomaly detection"

### Phase 4: Blog Integration + AI Cleanup

#### 4A. Blog Index — `src/blog/index.html`

Replace "AI-native engineering approaches" → "advanced computational methods" in meta tags and lead paragraph (~7 occurrences).

#### 4B. Blog Posts — Selective Cleanup (NOT wholesale rewrite)

- **Keep as-is**: `ai-native-structural-analysis.html`, `machine-learning-fatigue-prediction.html` — AI/ML is the actual topic
- **Fix author bios** (4 files): "specializing in AI-native approaches" → "specializing in computational methods"
- **Fix category labels**: "AI-Native Engineering" → "Computational Engineering"
- **Blog MD files** (AI_AGENT_ORCHESTRATION.md, etc.): Internal documentation — skip unless rendered on site

#### 4C. Blog-to-Sales Alignment (from WRK-147/148)

Map existing blog articles to ICP pain points for strategic linking:
- **For OrcaFlex firms**: link `python-engineering-automation` and `orcaflex-riser-sensitivity` from engineering page
- **For fatigue assessment**: link `machine-learning-fatigue-prediction` and `offshore-platform-fatigue` case study
- **For standards compliance**: link `offshore-engineering-standards` from pricing section
- **For offshore wind**: link `wind-turbine-foundation-analysis` case study from engineering verticals section

This alignment ensures blog content acts as sales collateral, not just SEO.

### Phase 5: FAQ + Contact Cleanup

#### 5A. FAQ — `src/faq.html` (275 lines)

- Remove "AI, machine learning" from meta tags and JSON-LD
- Replace "machine learning and artificial intelligence" → "computational analysis and automated workflows"
- Add modern FAQs: "How does A&CE deliver 60-80% time savings?", "What standards do you support?"

#### 5B. Contact — `src/contact.html` (519 lines)

- Add "Energy Data" to subject dropdown
- Minor trust signal additions

### Phase 6: Build + Visual Review

```bash
cd /mnt/local-analysis/workspace-hub/aceengineer-website && npm run build
```

**Verification**:
1. Build completes without errors
2. No unresolved `<include>` tags in `dist/`
3. All internal links work: `grep -roh 'href="[^"]*"' dist/ | sort -u`
4. **AI audit**: `grep -ri "AI-native\|AI-enhanced\|AI-powered" dist/` — only hits in blog posts where AI is the actual subject
5. Visual review of every page in browser
6. Copy `dist/` to root for GitHub Pages deployment

## Files Modified (Summary)

| File | Change | Phase |
|------|--------|-------|
| `src/index.html` | +firm identity, +Why A&CE, +social proof, AI fixes | 1A |
| `src/about.html` | **Complete rewrite** ~200 lines | 1B |
| `src/engineering.html` | +case study links, +standards badges, AI fixes | 2A |
| `src/energy.html` | **Back-port** root content to PostHTML | 2B |
| `src/partials/nav.html` | +Energy Data nav item | 2C |
| `src/partials/footer.html` | +Energy Data, +standards | 2D |
| `src/case-studies/orcaflex-riser-sensitivity-automation.html` | Narrative rewrite | 3A |
| `src/case-studies/offshore-platform-fatigue-optimization.html` | Narrative + AI fixes | 3B |
| `src/case-studies/index.html` | AI language replacement (~6 spots) | 3C |
| `src/blog/index.html` | AI language replacement (~7 spots) | 4A |
| 4 blog post files | Author bio + category fixes | 4B |
| `src/faq.html` | Meta/JSON-LD cleanup + modern FAQs | 5A |
| `src/contact.html` | +subject option | 5B |

**Estimated**: ~15-20 files modified, ~800-1,200 lines changed/added

## Sequencing

```
Phase 1 (Homepage + About) — highest impact, do first
    ↓
Phase 2 (Services + Nav) — depends on energy back-port
    ↓
Phase 3 (Case studies) — depends on positioning decisions from Phase 1
    ↓
Phase 4 (Blog cleanup) — depends on language decisions being finalized
    ↓
Phase 5 (FAQ + Contact) — small changes, lowest priority
    ↓
Phase 6 (Build + visual review) — final verification
```

## Verification

1. `npm run build` succeeds
2. AI audit: `grep -ri "AI-native\|AI-enhanced\|AI-powered" dist/` — only blog posts about AI as subject
3. Visual review of all 8 main pages + 6 case studies + blog index
4. Link integrity check
5. Mobile responsive check (key breakpoints)
6. Standards badges and social proof sections render correctly

### GTM Readiness Check (from WRK-148)

7. **Tier-1 outreach test**: Would a VP Engineering at Subsea7 or Wood Group find this site credible? Does it read as a firm or a freelancer?
8. **ICP resonance**: Does homepage messaging speak directly to a mid-market offshore engineering firm's pain points (manual OrcaFlex work, bottlenecked senior engineers, standards compliance burden)?
9. **Pricing credibility**: Are pricing claims linked to verifiable case studies?
10. **No AI buzzwords in first scroll**: Homepage above-the-fold should contain zero AI terminology — only engineering outcomes and quantified results
11. **Conference-ready**: Site is polished enough to share on a business card at OTC Houston (May 2026)
