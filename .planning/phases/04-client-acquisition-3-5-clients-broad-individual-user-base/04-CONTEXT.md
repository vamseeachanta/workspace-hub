# Phase 4: Client Acquisition — 3-5 Clients + Broad Individual User Base - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Acquire 3-5 paying enterprise clients (consultancies, operators) through direct network outreach, while growing a broad base of individual engineers using the free calculators. Enterprise clients pay via invoice for custom analysis reports. Individual users access everything for free — growth measured by traffic and calculator usage, not signups.

</domain>

<decisions>
## Implementation Decisions

### Acquisition Channels
- **D-01:** Enterprise outreach via direct network — leverage existing industry contacts and LinkedIn connections. Personal outreach to known consultancies and operators. Manual effort, no automation tooling.
- **D-02:** Individual engineer growth via SEO + open calculators — keep all calculators free and ungated. Engineers find the site through Google, use calculators, bookmark and return. Scale with content.
- **D-03:** No outreach automation this phase — no CRM software, no email sequences, no LinkedIn campaigns. Keep focus on conversations, not tools.
- **D-04:** Content strategy is case study focused — create 2-3 detailed case studies showing real engineering problems solved with digitalmodel. These are the primary enterprise sales tools, paired with calculator demos.

### Service & Payment Model
- **D-05:** No user accounts or authentication this phase — calculators stay fully open, no login required. Auth adds complexity with uncertain payoff at 3-5 client scale.
- **D-06:** Invoice-based payment — manual invoicing after consultation. No Stripe, no payment infrastructure. Phase 3's contact form handles lead capture.
- **D-07:** "Paying client" for UAT = paid invoice or signed pilot agreement with defined scope. Concrete, verifiable.
- **D-08:** Lead service offering is custom analysis reports — full standard-compliant engineering analysis (fatigue, wall thickness, VIV, OBS) using digitalmodel as the engine. Calculators demonstrate capability, reports are the product.

### Onboarding & Conversion Flow
- **D-09:** Enterprise prospect journey: calculator (found via Google or shared link) → relevant case study → contact form submission. Natural funnel from demo to sales conversation.
- **D-10:** Individual user experience: fully open access, zero friction. No signup, no gating, no email capture required. Growth measured by GA4 traffic and calculator usage events.
- **D-11:** Redefine UAT metric — replace "individual user signups trending upward" with measurable proxies: unique visitors, calculator sessions, returning users, contact form submissions. GA4 already tracks all of this.
- **D-12:** Enhance existing pages rather than creating new ones — add stronger CTAs to calculator pages, link case studies to relevant calculators, improve contact form with project type selector. Better flow between existing pages.

### Feedback & Tracking
- **D-13:** Prospect pipeline tracked via GitHub Issues in a private repo/project board — labels for stages (contacted, responded, pilot, client). Consistent with existing GitHub-based task tracking.
- **D-14:** User feedback captured through GA4 analytics + contact form analysis — analyze calculator traffic patterns, search terms that bring users in, and what's requested through contact. No new feedback infrastructure.
- **D-15:** Enhanced GA4 custom events — add more granular tracking: which calculator inputs users try, scroll depth on case studies, which CTAs get clicked. Better signal from existing infrastructure.
- **D-16:** Manual review cycle for feedback-to-roadmap — periodically review GA4 data + contact requests + client conversations. Feed insights into digitalmodel roadmap (Phase 6) and future calculator additions. No automated reporting.

### Claude's Discretion
- Case study topic selection and structure (within the 2-3 target)
- Exact GA4 event taxonomy for enhanced tracking
- CTA copy and placement on calculator pages
- Contact form project type selector options
- GitHub Issues label scheme for prospect tracking

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Website infrastructure (enhance, don't rebuild)
- `aceengineer-website/content/contact.html` — Contact form (web3forms + GA4 conversion tracking) — sole conversion path
- `aceengineer-website/content/pricing.html` — Display-only tiered pricing page (Free/Pro/Enterprise, all route to contact)
- `aceengineer-website/content/calculators/index.html` — Calculator index page (add CTAs linking to case studies)
- `aceengineer-website/GOOGLE_ANALYTICS_SETUP.md` — GA4 configuration and event tracking setup

### Existing calculators (add CTAs and case study links)
- `aceengineer-website/content/calculators/on-bottom-stability.html` — OBS calculator (DNV-RP-F109)
- `aceengineer-website/content/calculators/wall-thickness.html` — Wall thickness calculator (ASME B31.4)
- `aceengineer-website/calculators/fatigue-life-calculator.html` — Fatigue life calculator
- `aceengineer-website/calculators/fatigue-sn-curve.html` — S-N curve interactive demo
- `aceengineer-website/calculators/npv-field-development.html` — NPV field development calculator

### Case studies (template for new ones)
- `aceengineer-website/case-studies/` — Existing 7 case studies (pattern for new ones)
- `aceengineer-website/CASE_STUDY_TEMPLATE.md` — Template for creating case studies

### Prior phase context (carry-forward decisions)
- `.planning/phases/03-gtm-and-marketing-aceengineer-website/03-CONTEXT.md` — Phase 3 decisions: consultation pricing (D-07), contact form as sole conversion (D-08), display-only pricing page (D-09)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Contact form (web3forms):** Working contact form with GA4 conversion tracking — sole conversion path, enhance with project type selector
- **GA4 infrastructure:** Already integrated across all pages with custom event tracking on calculators — extend with more granular events
- **Calculator pages (5 live):** Each has consistent structure (HTML + JS + Plotly + GA4) — add CTAs and case study cross-links
- **Case study template:** `CASE_STUDY_TEMPLATE.md` provides structure for creating new case studies
- **PostHTML build system:** `build.js` handles includes/partials — use for consistent CTA components across calculator pages

### Established Patterns
- **Static site on Vercel:** No backend, no server-side rendering. All enhancements must be client-side.
- **web3forms for form handling:** Contact form submits via web3forms API. Extend pattern for enhanced contact form.
- **GA4 event tracking pattern:** Calculators fire custom events — follow same pattern for new tracking events
- **SEO infrastructure:** Schema.org markup, sitemap, robots.txt, Open Graph — all in place

### Integration Points
- **Calculator pages → case studies:** Cross-link relevant case studies from calculator result sections
- **GA4 events → manual review:** Enhanced events feed into periodic analytics review
- **GitHub Issues → prospect tracking:** New use of GitHub for CRM-style pipeline tracking
- **Content sync:** `content_sync.py` pulls digitalmodel stats — could surface new module capabilities in case studies

</code_context>

<specifics>
## Specific Ideas

- Enterprise clients get custom analysis reports as the product — calculators are the demo, reports are what they pay for
- Case studies should show real engineering problems solved with digitalmodel (fatigue, wall thickness, VIV, OBS) — paired with calculator demos
- Calculator → case study → contact is the natural enterprise funnel
- "Measurable individual user signups" UAT metric redefined as GA4 traffic/usage proxies since there's no auth

</specifics>

<deferred>
## Deferred Ideas

- **User accounts and authentication** — revisit when user base outgrows anonymous access or when self-service is needed
- **Stripe/payment infrastructure** — revisit when client volume exceeds manual invoicing capacity
- **Email newsletter/marketing automation** — revisit when there's a mailing list worth emailing (requires email capture, deferred)
- **Automated CRM tooling** — GitHub Issues sufficient at 3-5 client scale, revisit at 10+
- **Enterprise landing page (/enterprise or /for-teams)** — defer until there's social proof (client logos, testimonials) to populate it
- **Services detail page (/services)** — defer until service offerings are validated through first clients
- **Heatmap tools (Hotjar/Clarity)** — defer until traffic justifies the overhead
- **Automated GA4 reporting/dashboards** — manual review sufficient at current scale

</deferred>

---

*Phase: 04-client-acquisition-3-5-clients-broad-individual-user-base*
*Context gathered: 2026-03-26*
