# Phase 3: GTM and marketing — aceengineer-website - Context

**Gathered:** 2026-03-26 (assumptions mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Position aceengineer.com as the go-to platform for offshore engineering calculations. Website live with clear value prop, at least 3 calculation demos, and a signup/contact flow. UAT: Website live with clear value prop, at least 3 calculation demos, and a signup/contact flow.

</domain>

<decisions>
## Implementation Decisions

### Calculation Demo Scope
- **D-01:** Add 2-3 new calculators showcasing Phase 1 modules (on-bottom stability, wall thickness comparison, scatter fatigue) alongside the 3 existing calculators (fatigue-life, fatigue-sn-curve, npv-field-development). Existing calculators count toward UAT.
- **D-02:** New calculators follow the existing pattern: client-side JavaScript with Plotly charts and GA4 event tracking. Input forms map to YAML manifest function signatures from Phase 1.
- **D-03:** Content sync script (`scripts/content_sync.py`) pulls stats from digitalmodel (module count, standards count) for dynamic homepage claims.

### Website Architecture
- **D-04:** Stay static site on Vercel with client-side JS calculators. No Python API backend this phase.
- **D-05:** Existing posthtml build pipeline (`build.js`) handles templating. No framework migration.
- **D-06:** Calculators are labeled "illustrative" with a CTA to contact for full standard-compliant analysis.

### Pricing and Access Model
- **D-07:** Free calculators as lead generation. Consultation-based pricing only — no payment infrastructure, no auth, no user accounts this phase.
- **D-08:** Contact form (web3forms + GA4 conversion tracking) is the sole conversion path. Add "Request Pricing" CTA alongside existing contact options.
- **D-09:** Optionally display a simple tiered pricing page (display-only) showing Free/Pro/Enterprise to signal platform intent. All tiers route to contact form.

### SEO and Content Strategy
- **D-10:** Enhance existing SEO foundation — don't rebuild. Structured data, sitemap, GA4, 15 blog posts, 7 case studies are the base.
- **D-11:** Add calculation-focused long-tail content targeting queries like "on-bottom stability calculator DNV-RP-F109", "ASME B31.4 wall thickness calculator".
- **D-12:** Each new calculator page gets full Schema.org WebApplication markup, Open Graph tags, and sitemap entry (matching existing calculator pattern).

### Value Proposition Messaging
- **D-13:** Theme: "Tethering timeless engineering to a single source of truth" — every calculation traces to its standard, every standard to its implementation.
- **D-14:** Landing page communicates: (1) engineering calculations you can trust, (2) traceable to international standards, (3) powered by open-source digitalmodel.

### Claude's Discretion
- Exact calculator UI design and interaction patterns
- Blog content topics and publishing schedule
- Landing page layout and visual design
- Competitor differentiation messaging specifics
- Whether to add a newsletter/waitlist signup vs. contact-only

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Website codebase
- `aceengineer-website/README.md` — Site architecture, build system, deployment
- `aceengineer-website/build.js` — PostHTML build pipeline
- `aceengineer-website/vercel.json` — Vercel deployment config
- `aceengineer-website/sitemap.xml` — Current URL structure (30+ URLs)

### Existing calculators (pattern to follow)
- `aceengineer-website/calculators/fatigue-life-calculator/` — Reference calculator: JS engine + Plotly + GA4
- `aceengineer-website/calculators/fatigue-sn-curve/` — S-N curve interactive demo
- `aceengineer-website/calculators/npv-field-development/` — NPV calculator with JS engine
- `aceengineer-website/assets/js/npv-calculator-engine.js` — Standalone JS calculation engine pattern

### Phase 1 outputs (calculation modules to showcase)
- `digitalmodel/src/digitalmodel/subsea/on_bottom_stability/manifest.yaml` — On-bottom stability function signatures and standard refs
- `digitalmodel/src/digitalmodel/structural/fatigue/manifest.yaml` — Scatter fatigue manifest
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/` — Wall thickness implementations (DNV, API, ASME)

### Content infrastructure
- `aceengineer-website/scripts/content_sync.py` — Pulls stats from digitalmodel into website
- `aceengineer-website/content-sync.yaml` — Content sync config
- `aceengineer-website/reports/competitor-analysis/` — Automated competitor analysis reports

### SEO and analytics
- `aceengineer-website/contact.html` — Contact form (web3forms + GA4 conversion tracking)
- `aceengineer-website/google36887341ed911d28.html` — Google Search verification

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Calculator template pattern:** 3 working calculators with consistent structure (HTML + inline JS + Plotly + GA4). New calculators can clone and adapt.
- **Content sync pipeline:** `content_sync.py` + `content-sync.yaml` already pulls digitalmodel stats. Extend for new module counts.
- **SEO infrastructure:** Schema.org markup, sitemap, robots.txt, GA4 — all in place and extensible.
- **PostHTML build system:** `build.js` handles includes/partials for consistent headers/footers.

### Established Patterns
- **Static-first:** All pages are static HTML. No server-side rendering. Vercel serves directly.
- **Calculator structure:** Each calculator lives in `calculators/<name>/` with its own `index.html`.
- **GA4 event tracking:** Calculators fire custom events for user interactions (form submits, chart renders).
- **Web3forms contact:** Contact form submits via web3forms API, no backend needed.

### Integration Points
- **YAML manifests → calculator inputs:** Phase 1 manifests define function signatures (inputs, outputs, units, standard refs) that map directly to calculator form fields.
- **Content sync → homepage:** Stats pulled from digitalmodel feed into homepage claims ("X calculations", "Y standards").
- **Competitor analysis → content strategy:** Reports in `reports/competitor-analysis/` inform keyword targeting.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. Key reference: existing calculators establish the pattern; new calculators should feel like natural extensions.

</specifics>

<deferred>
## Deferred Ideas

- **Python API backend for exact calculations** — Phase 5+ (requires separate hosting, ops overhead)
- **Payment integration (Stripe, auth, user accounts)** — Phase 4 if client acquisition requires self-service
- **Newsletter/email marketing automation** — Could be Phase 4 or backlog depending on client strategy
- **Interactive API documentation (Swagger/FastAPI docs)** — Future phase when API exists

</deferred>

---

*Phase: 03-gtm-and-marketing-aceengineer-website*
*Context gathered: 2026-03-26*
