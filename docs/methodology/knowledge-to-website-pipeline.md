# Knowledge-to-Website Content Pipeline

> Turn repo knowledge bases into client-facing aceengineer.com content

## Mission

The repo contains deep engineering knowledge that clients would find valuable. This pipeline converts wiki pages, skills, and methodology docs into published web content on aceengineer.com.

## Content Inventory

| Content Type | Quantity | Source | Readiness |
|---|---|---|---|
| Wiki pages (marine engineering) | 31+ | knowledge/wikis/marine-engineering/ | Raw markdown |
| Wiki pages (naval architecture) | 20+ | knowledge/wikis/naval-architecture/ | Raw markdown |
| Wiki pages (maritime law) | ? | knowledge/wikis/maritime-law/ | Raw markdown |
| Engineering skills | 729 | .claude/skills/ (filtered) | Structured YAML + markdown |
| Methodology docs | 2 | docs/methodology/ | Ready for publication |
| Parametric demo reports | ? | gtm-parametric-demo-reports skill | Branded HTML+PDF |

## Pipeline Architecture

### Phase 1: Content Extraction and Normalization

```
Source (repo) -> Normalize -> Stage -> Review -> Publish
```

**Normalize:** Convert raw wiki markdown to web-ready content with:
- Navigation structure (TOC, breadcrumbs)
- Cross-links between related pages
- Author attribution (ACE Engineer)
- Call-to-action (contact us, request analysis)
- SEO metadata (title, description, keywords)

**Stage:** Build static site from normalized content:
- Use MkDocs, Hugo, or custom generator
- Apply aceengineer.com branding/theme
- Include interactive elements (Plotly charts from engineering reports)

### Phase 2: Service Pages from Skills

**Pattern:** Each engineering skill becomes a service description page.

```
.claude/skills/marine-offshore/orcaflex/modeling/SKILL.md
    -> aceengineer.com/services/orcaflex-modeling/
    -> Title: "OrcaFlex Marine Dynamic Analysis"
    -> Content: What we do, methodology, deliverables, contact
```

729 engineering skills = 100+ service pages covering:
- OrcaFlex modeling, analysis, post-processing
- Mooring design (CALM, SALM, spread mooring)
- Riser analysis (catenary, lazy wave, top-tensioned)
- FEA (slender structures, global-local)
- Cathodic protection design
- API 579 Fitness-for-Service
- DNV, ISO, NORSOK standards compliance
- Hydrodynamics (AQWA, OrcaWave, diffraction)
- VIV assessment
- Signal processing, rainflow
- Risk assessment, Monte Carlo

### Phase 3: Methodology as Marketing

Published methodology documents serve dual purpose:
1. **Technical credibility** -- "This firm follows rigorous engineering practices"
2. **Client education** -- "Here's why our review process catches what others miss"

Documents ready for publication:
- compound-engineering.md
- enforcement-over-instruction.md
- More to be written from #2019 remaining work

### Phase 4: Daily Automation

**Existing:** aceengineer-website-update skill runs competitor analysis.

**Add to cron:**
```
Daily 2AM:
  1. Check for new wiki pages (git diff knowledge/wikis/)
  2. Check for new methodology docs (git diff docs/methodology/)
  3. Check for new engineering skills (git diff .claude/skills/)
  4. Regenerate site from normalized sources
  5. Commit + deploy to aceengineer.com
  6. Log what changed
```

## Implementation Options

### Option A: Static Site Generator (Recommended)
- **Tool:** MkDocs with Material theme, or Hugo
- **Pros:** Fast, version-controlled, deployable to GitHub Pages
- **Cons:** Requires build pipeline
- **Deploy:** GitHub Pages or custom server

### Option B: API-Driven (Hermes as Backend)
- **Tool:** Hermes generates HTML responses on demand
- **Pros:** Always current, no build step
- **Cons:** Server cost, slower page loads

### Option C: CMS Integration
- **Tool:** Convert docs to WordPress/Ghost content
- **Pros:** Easy for non-technical editing
- **Cons:** Disconnects from version control

## Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Pages published | 100+ | Count of published pages |
| Engineering skills converted | 50+ | Skills -> service pages |
| Methodology docs published | 5+ | docs/methodology/ |
| Daily updates working | 90% uptime | Cron job success rate |
| Site traffic (first month) | track baseline | Analytics |
| Contact form submissions | track | CRM integration |
| SEO ranking (target keywords) | top 10 | Google Search Console |

## Related Issues

- #2016 -- Client conversion pipeline (website feeds this funnel)
- #2019 -- Document compound engineering methodology (source content)
- gtm-parametric-demo-reports skill -- branded HTML reports
- aceengineer-website-update skill -- existing daily competitor analysis cron
