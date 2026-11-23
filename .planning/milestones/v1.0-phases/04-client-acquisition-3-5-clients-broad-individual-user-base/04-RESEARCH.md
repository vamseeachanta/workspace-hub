# Phase 4: Client Acquisition — 3-5 Clients + Broad Individual User Base - Research

**Researched:** 2026-03-26
**Domain:** Client acquisition (enterprise outreach + individual SEO growth), website conversion optimization, analytics instrumentation, prospect pipeline tracking
**Confidence:** HIGH

## Summary

Phase 4 is a business execution phase with targeted website enhancements, not a greenfield build. The aceengineer.com website is already live with 5 calculators, 6 case studies, a contact form (web3forms + GA4 conversion tracking), display-only tiered pricing, and full SEO infrastructure. The phase adds (1) 2-3 new case studies showcasing digitalmodel capabilities as the primary enterprise sales tool, (2) enhanced GA4 custom events for granular user behavior tracking, (3) a project type selector on the contact form, (4) stronger calculator-to-case-study-to-contact CTAs, and (5) a GitHub Issues pipeline for prospect tracking. Enterprise acquisition is manual direct outreach via existing network -- no CRM tooling or email automation.

The website code changes are straightforward static HTML edits following established patterns in the `aceengineer-website/content/` directory. The real risk in this phase is not technical but organizational: the case studies must be compelling enough to serve as enterprise sales collateral, the GA4 event taxonomy must produce actionable insights (not vanity metrics), and the prospect pipeline must be lightweight enough to actually get used.

**Primary recommendation:** Structure plans around three workstreams: (1) case study creation (the enterprise sales engine), (2) website conversion optimization (GA4 events, CTA enhancement, contact form upgrade), and (3) pipeline and process setup (GitHub Issues board, prospect outreach templates, manual review cadence).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Enterprise outreach via direct network -- leverage existing industry contacts and LinkedIn connections. Personal outreach to known consultancies and operators. Manual effort, no automation tooling.
- **D-02:** Individual engineer growth via SEO + open calculators -- keep all calculators free and ungated. Engineers find the site through Google, use calculators, bookmark and return. Scale with content.
- **D-03:** No outreach automation this phase -- no CRM software, no email sequences, no LinkedIn campaigns. Keep focus on conversations, not tools.
- **D-04:** Content strategy is case study focused -- create 2-3 detailed case studies showing real engineering problems solved with digitalmodel. These are the primary enterprise sales tools, paired with calculator demos.
- **D-05:** No user accounts or authentication this phase -- calculators stay fully open, no login required. Auth adds complexity with uncertain payoff at 3-5 client scale.
- **D-06:** Invoice-based payment -- manual invoicing after consultation. No Stripe, no payment infrastructure. Phase 3's contact form handles lead capture.
- **D-07:** "Paying client" for UAT = paid invoice or signed pilot agreement with defined scope. Concrete, verifiable.
- **D-08:** Lead service offering is custom analysis reports -- full standard-compliant engineering analysis (fatigue, wall thickness, VIV, OBS) using digitalmodel as the engine. Calculators demonstrate capability, reports are the product.
- **D-09:** Enterprise prospect journey: calculator (found via Google or shared link) -> relevant case study -> contact form submission. Natural funnel from demo to sales conversation.
- **D-10:** Individual user experience: fully open access, zero friction. No signup, no gating, no email capture required. Growth measured by GA4 traffic and calculator usage events.
- **D-11:** Redefine UAT metric -- replace "individual user signups trending upward" with measurable proxies: unique visitors, calculator sessions, returning users, contact form submissions. GA4 already tracks all of this.
- **D-12:** Enhance existing pages rather than creating new ones -- add stronger CTAs to calculator pages, link case studies to relevant calculators, improve contact form with project type selector. Better flow between existing pages.
- **D-13:** Prospect pipeline tracked via GitHub Issues in a private repo/project board -- labels for stages (contacted, responded, pilot, client). Consistent with existing GitHub-based task tracking.
- **D-14:** User feedback captured through GA4 analytics + contact form analysis -- analyze calculator traffic patterns, search terms that bring users in, and what's requested through contact. No new feedback infrastructure.
- **D-15:** Enhanced GA4 custom events -- add more granular tracking: which calculator inputs users try, scroll depth on case studies, which CTAs get clicked. Better signal from existing infrastructure.
- **D-16:** Manual review cycle for feedback-to-roadmap -- periodically review GA4 data + contact requests + client conversations. Feed insights into digitalmodel roadmap (Phase 6) and future calculator additions. No automated reporting.

### Claude's Discretion
- Case study topic selection and structure (within the 2-3 target)
- Exact GA4 event taxonomy for enhanced tracking
- CTA copy and placement on calculator pages
- Contact form project type selector options
- GitHub Issues label scheme for prospect tracking

### Deferred Ideas (OUT OF SCOPE)
- User accounts and authentication
- Stripe/payment infrastructure
- Email newsletter/marketing automation
- Automated CRM tooling
- Enterprise landing page (/enterprise or /for-teams)
- Services detail page (/services)
- Heatmap tools (Hotjar/Clarity)
- Automated GA4 reporting/dashboards
</user_constraints>

## Standard Stack

### Core (already in place -- enhance, not replace)
| Library/Tool | Version | Purpose | Status |
|-------------|---------|---------|--------|
| Static HTML + JS | N/A | All pages are static, client-side only on Vercel | In place |
| PostHTML | 0.16.6 | Build system with includes/partials (`build.js`) | In place |
| GA4 (gtag.js) | G-K31E51DQ47 | Analytics and event tracking | In place |
| web3forms | API | Contact form submission to email | In place |
| Plotly.js | CDN | Calculator charting | In place |
| Bootstrap 3 | CDN | CSS framework (United theme) | In place |
| Jest | 30.2.0 | JS test framework | In place |

### Supporting (new for this phase)
| Tool | Purpose | When to Use |
|------|---------|-------------|
| GitHub Projects (v2) | Prospect pipeline board with custom fields | Enterprise prospect tracking per D-13 |
| gh CLI | Create/manage issues and project board from command line | Pipeline setup automation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| GitHub Issues pipeline | HubSpot CRM free tier | Overkill at 3-5 clients, adds a new tool to learn. D-03 explicitly locks out CRM software. |
| Manual GA4 review | Looker Studio dashboard | D-16 locks this out -- deferred. Manual review sufficient at current traffic. |
| web3forms contact form | Formspree or Netlify Forms | No benefit to switching; web3forms is working and integrated. |

**No new packages to install.** All changes are content edits and GA4 instrumentation in existing HTML/JS files.

## Architecture Patterns

### Existing Project Structure (enhance, don't change)
```
aceengineer-website/
  content/                    # Source HTML files (PostHTML processes these)
    partials/                 # nav.html, footer.html, head-common.html
    calculators/              # 5 calculator pages + index
      index.html              # Calculator collection page
      on-bottom-stability.html
      wall-thickness.html
      fatigue-life-calculator.html
      fatigue-sn-curve.html
      npv-field-development.html
    case-studies/             # 6 case studies + index (add 2-3 new here)
      index.html
      offshore-platform-fatigue-optimization.html
      subsea-fea-automation.html
      wind-turbine-foundation-analysis.html
      orcaflex-riser-sensitivity-automation.html
      marine-safety-correlation.html
      bsee-field-economics.html
    contact.html              # Contact form (web3forms + GA4)
    pricing.html              # Display-only tiered pricing
    blog/                     # 15 blog posts
  dist/                       # Build output (deployed to Vercel)
  build.js                    # PostHTML build pipeline
  CASE_STUDY_TEMPLATE.md      # Template for new case studies
```

### Pattern 1: Calculator CTA Section (Existing, to be enhanced)
**What:** Every calculator page has an info-section at the bottom with a professional services CTA and links to case studies.
**When to use:** All calculator pages -- enhance existing CTAs, don't add new sections.
**Example (existing pattern on OBS, wall-thickness, fatigue-life):**
```html
<div class="info-section">
    <h2>Need Professional Pipeline Stability Analysis?</h2>
    <p>
        For complex scenarios including soil liquefaction, span assessment, seabed intervention,
        and multi-directional wave loading, we offer professional consulting services with validated
        methodologies.
    </p>
    <p>
        <a href="../contact.html" class="btn btn-success btn-lg">Discuss Your Project</a>
        <a href="../case-studies/" class="btn btn-default btn-lg">View Case Studies</a>
    </p>
</div>
```

### Pattern 2: GA4 Custom Event (Existing, extend with new events)
**What:** All calculators fire `calculator_use` events with domain-specific parameters. Contact form fires `contact_form_submission`.
**When to use:** New granular events for CTA clicks, case study scroll depth, calculator input patterns.
**Example (existing pattern):**
```javascript
// Guard for GA4 availability (established pattern from Phase 3)
if (typeof gtag !== 'undefined') {
    gtag('event', 'calculator_use', {
        'event_category': 'engagement',
        'event_label': 'on_bottom_stability',
        'pipe_diameter': D_outer,
        'current_velocity': U,
        'result_utilisation': result.utilisation
    });
}
```

### Pattern 3: Case Study Structure (Template exists)
**What:** `CASE_STUDY_TEMPLATE.md` defines the HTML structure. Existing case studies follow it.
**When to use:** New case studies demonstrating digitalmodel-powered analysis.
**Example structure:** Industry | Location | Year | Client -> Problem -> Methodology -> Results -> Schema.org Article markup + Open Graph + GA4.

### Pattern 4: web3forms Contact Form Field (extend existing)
**What:** web3forms sends all named form fields to email. Standard HTML select/input elements work.
**When to use:** Adding project type selector to contact form.
**Example:**
```html
<!-- Add project type selector to existing contact form -->
<div class="form-group">
    <label for="project-type">Project Type</label>
    <select id="project-type" name="project_type" class="form-control">
        <option value="">Select project type...</option>
        <option value="Pipeline Stability Analysis">Pipeline Stability (OBS)</option>
        <option value="Wall Thickness Design">Wall Thickness Design</option>
        <option value="Fatigue Assessment">Fatigue Assessment</option>
        <option value="VIV Analysis">VIV Analysis</option>
        <option value="Full Engineering Study">Full Engineering Study</option>
        <option value="Other">Other</option>
    </select>
</div>
```

### Anti-Patterns to Avoid
- **Building new pages when existing ones can be enhanced:** D-12 is explicit -- enhance calculator pages, case study index, and contact form. Do not create /enterprise, /services, or new landing pages.
- **Over-instrumenting GA4:** Resist tracking every click. Focus on events that map to the enterprise funnel: calculator use -> case study engagement -> CTA click -> contact submission. Register only events you will actually review manually (D-16).
- **Automating outreach:** D-01 and D-03 are explicit -- manual outreach via personal network. No email sequences, no LinkedIn automation, no CRM. The temptation to "just set up HubSpot" must be resisted.
- **Gating content:** D-05 and D-10 are explicit -- everything free, no login, no email capture gates. Growth is measured by traffic, not signups.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Prospect tracking | Custom spreadsheet or database | GitHub Issues + Project Board | D-13 locks this in. Custom fields, labels, and kanban views cover 3-5 client pipeline. Consistent with existing workflow. |
| Contact form handling | Custom backend API | web3forms (already integrated) | Static site constraint (D-04 from Phase 3). web3forms handles email delivery, no backend needed. |
| Analytics | Custom tracking scripts or dashboards | GA4 with gtag.js (already integrated) | Enhanced Measurement auto-tracks scroll, outbound clicks. Custom events extend this. Manual review per D-16. |
| Case study templating | Build custom CMS | PostHTML partials + CASE_STUDY_TEMPLATE.md | Existing build system handles includes. Template provides structure. Static HTML is the pattern. |
| CTA components | React/Vue component library | Inline HTML in PostHTML-processed files | The site is static HTML with Bootstrap 3. Keep it simple. PostHTML `<include>` can share repeated CTA blocks. |

**Key insight:** This phase has almost no new technical infrastructure to build. The website, analytics, forms, and build system all exist. The work is content creation (case studies), surgical HTML edits (CTAs, form enhancement, GA4 events), and process definition (pipeline setup, outreach templates).

## Common Pitfalls

### Pitfall 1: GA4 Custom Dimensions Not Registered
**What goes wrong:** Custom event parameters (like `calculator_name`, `cta_location`, `project_type`) are sent but never appear in GA4 reports.
**Why it happens:** GA4 requires explicit registration of custom dimensions for event parameters to show up in standard reports. Sending parameters via gtag is only half the setup.
**How to avoid:** After deploying events, register each custom parameter as a Custom Dimension in GA4 Admin -> Custom definitions -> Create custom dimension. Map parameter name to dimension name.
**Warning signs:** Events appear in Realtime but parameters are missing from Explore reports.

### Pitfall 2: Case Studies That Are Self-Congratulatory Instead of Problem-Focused
**What goes wrong:** Case studies read like marketing brochures ("We delivered excellence...") instead of technical problem-solution narratives.
**Why it happens:** Natural tendency to focus on company capabilities instead of the client problem.
**How to avoid:** Follow the Situation -> Trigger -> Barrier -> Solution -> Results structure. Lead with the engineering problem, show the methodology, quantify the outcome. Engineering clients care about technical credibility, not marketing copy.
**Warning signs:** Case study has no specific numbers, no standard references, no methodology details.

### Pitfall 3: Over-Complex GA4 Event Taxonomy
**What goes wrong:** 20+ custom events defined, none reviewed, no custom dimensions registered, no actionable insights generated.
**Why it happens:** Instrumenting everything feels productive but creates noise. D-16 specifies manual review -- if nobody looks at it, it's wasted effort.
**How to avoid:** Define 5-8 new events maximum, each mapping to a specific question you want to answer: "Which calculator drives the most contact form submissions?" "Do case study readers click the CTA?" "What project types are most requested?"
**Warning signs:** More than 10 new custom events, no documented review cadence.

### Pitfall 4: GitHub Issues Pipeline Gets Abandoned
**What goes wrong:** Pipeline is set up but never updated. Prospects tracked in the founder's head, not the board.
**Why it happens:** At 3-5 clients, mental tracking feels sufficient. The board adds overhead without obvious value.
**How to avoid:** Keep the label scheme dead simple (4-5 labels max). Update the board as part of the manual review cadence (D-16), not as a separate task. Make it part of the same weekly check where GA4 data is reviewed.
**Warning signs:** Board has issues from setup week but no updates since.

### Pitfall 5: Deploying CTA Changes Without Verifying Build
**What goes wrong:** HTML edits in `content/` look correct but PostHTML build produces broken output in `dist/`.
**Why it happens:** PostHTML processes includes and front matter. Mismatched tags or broken include paths fail silently.
**How to avoid:** Run `node build.js` after every content edit. Verify output in `dist/` matches expectations. Run `npm test` (jest) to catch build regressions.
**Warning signs:** Edits in `content/` not reflected in `dist/`, broken layouts in local serve.

## Code Examples

### Enhanced GA4 Event Taxonomy (Claude's Discretion)

Recommended event taxonomy -- 7 new events plus 2 enhanced existing events:

```javascript
// NEW: CTA click tracking (on all calculator and case study pages)
gtag('event', 'cta_click', {
    'event_category': 'conversion',
    'cta_text': 'Discuss Your Project',       // button text
    'cta_location': 'calculator_bottom',       // where on page
    'page_type': 'calculator',                 // calculator|case_study|pricing
    'calculator_name': 'on_bottom_stability'   // which page
});

// NEW: Case study engagement
gtag('event', 'case_study_view', {
    'event_category': 'content',
    'case_study_name': 'offshore_platform_fatigue',
    'referrer_type': 'calculator'  // how they got here: calculator|direct|search
});

// NEW: Case study scroll depth (fire at 25%, 50%, 75%, 100%)
gtag('event', 'case_study_scroll', {
    'event_category': 'content',
    'case_study_name': 'offshore_platform_fatigue',
    'percent_scrolled': 50
});

// NEW: Contact form project type selected
gtag('event', 'contact_project_type', {
    'event_category': 'contact',
    'project_type': 'Pipeline Stability Analysis'
});

// NEW: Calculator-to-case-study navigation
gtag('event', 'funnel_step', {
    'event_category': 'funnel',
    'step_name': 'calculator_to_case_study',
    'from_calculator': 'wall_thickness',
    'to_case_study': 'subsea_pipeline_design'
});

// NEW: Pricing page CTA click
gtag('event', 'pricing_cta_click', {
    'event_category': 'conversion',
    'tier_clicked': 'enterprise',
    'cta_text': 'Contact Us'
});

// NEW: Calculator input pattern (fire on calculate, captures what users are testing)
// ENHANCED existing calculator_use events: add input_count parameter
gtag('event', 'calculator_use', {
    'event_category': 'engagement',
    'event_label': 'on_bottom_stability',
    'pipe_diameter': D_outer,
    'current_velocity': U,
    'result_utilisation': result.utilisation,
    'input_count': sessionCalculationCount  // how many times they calculated this session
});
```

**GA4 parameter limits (verified):** Maximum 25 parameters per event, 40 character event name limit, 40 character parameter name limit, 100 character parameter value limit. Maximum 50 event-scoped custom dimensions per property.

### Case Study Scroll Depth Implementation
```javascript
// Lightweight scroll depth tracker for case study pages
(function() {
    var thresholds = [25, 50, 75, 100];
    var fired = {};
    var caseName = '{{ case_study_name }}'; // set per page

    window.addEventListener('scroll', function() {
        var scrollPercent = Math.round(
            (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
        );
        thresholds.forEach(function(threshold) {
            if (scrollPercent >= threshold && !fired[threshold]) {
                fired[threshold] = true;
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'case_study_scroll', {
                        'event_category': 'content',
                        'case_study_name': caseName,
                        'percent_scrolled': threshold
                    });
                }
            }
        });
    });
})();
```

### CTA Click Tracking (add to each CTA button)
```html
<!-- Enhanced CTA with click tracking -->
<a href="../contact.html?vertical=offshore"
   class="btn btn-success btn-lg"
   onclick="if(typeof gtag!=='undefined'){gtag('event','cta_click',{'event_category':'conversion','cta_text':'Discuss Your Project','cta_location':'calculator_bottom','page_type':'calculator','calculator_name':'on_bottom_stability'})}">
   Discuss Your Project
</a>
```

### Contact Form Project Type Selector
```html
<!-- Insert after the existing "subject" select, before "message" textarea -->
<div class="form-group">
    <label for="project-type">Project Type (optional)</label>
    <select id="project-type" name="project_type" class="form-control">
        <option value="">Select analysis type...</option>
        <option value="Pipeline Stability (OBS)">Pipeline Stability (OBS)</option>
        <option value="Wall Thickness Design">Wall Thickness Design</option>
        <option value="Fatigue Assessment">Fatigue Assessment</option>
        <option value="Riser/Mooring Analysis">Riser/Mooring Analysis</option>
        <option value="Full Engineering Study">Full Engineering Study</option>
        <option value="Data/Analytics">Data/Analytics</option>
        <option value="Other">Other</option>
    </select>
</div>
```

### GitHub Issues Label Scheme (Claude's Discretion)
```
Labels for prospect pipeline:
  pipeline:contacted    (color: #0075ca) - Initial outreach made
  pipeline:responded    (color: #e4e669) - Prospect responded
  pipeline:pilot        (color: #d876e3) - Pilot/trial in progress
  pipeline:client       (color: #0e8a16) - Paying client
  pipeline:lost         (color: #b60205) - Did not convert

  type:consultancy      - Small-mid engineering consultancy
  type:operator         - Asset owner/operator
  type:individual       - Independent engineer

Issue template:
  Title: [Company] - [Contact Name]
  Body: Company, contact info, how they found us, what they need, next action, date
```

### Case Study Topic Recommendations (Claude's Discretion)

Based on existing case studies and calculator coverage, recommended new case studies:

| Topic | Paired Calculator | Gap Filled | Enterprise Appeal |
|-------|------------------|------------|-------------------|
| Pipeline On-Bottom Stability Assessment | OBS Calculator | No OBS-specific case study exists despite new Phase 3 calculator | High -- operators need this for every subsea pipeline project |
| Multi-Code Wall Thickness Comparison | Wall Thickness Calculator | No wall thickness case study exists despite new Phase 3 calculator | High -- consultancies compare standards constantly |
| Spectral Fatigue from Scatter Diagrams | Fatigue Life Calculator | Complements existing fatigue optimization case study with more advanced methodology | Medium-High -- demonstrates advanced capability |

Each case study should:
1. Follow `CASE_STUDY_TEMPLATE.md` structure
2. Include Schema.org Article markup and Open Graph tags
3. Reference specific digitalmodel modules used
4. Quantify results (analysis time reduction, safety factor comparisons, cost impact)
5. Link back to the relevant calculator as an interactive demo
6. End with a CTA to the contact form

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Universal Analytics (UA) | GA4 event-based model | UA sunset July 2023 | All tracking is GA4 native. No migration needed. |
| Session-based analytics | Event-parameter model with custom dimensions | GA4 standard since 2020 | Custom events are first-class citizens. Must register parameters as custom dimensions to see them in reports. |
| Gated content for lead capture | Open access + high-quality free tools as funnel top | Industry trend 2024-2026 | Aligns perfectly with D-02 and D-05. Free calculators attract engineers; quality builds trust; contact form captures serious buyers. |
| CRM-first sales process | Network-first at early stage | Perennial for bootstrapped B2B | D-01 and D-03 reflect this correctly. At 3-5 clients, personal relationships outperform any CRM. |

**Deprecated/outdated:**
- Universal Analytics: fully sunset. Do not reference UA patterns.
- jQuery-dependent GA tracking: existing site uses vanilla gtag.js calls. Keep it that way.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Jest 30.2.0 (JS) + pytest (Python) |
| Config file | `aceengineer-website/package.json` (jest config inline) |
| Quick run command | `cd aceengineer-website && npm test` |
| Full suite command | `cd aceengineer-website && npm test && cd .. && python -m pytest aceengineer-website/tests/python/ -x` |

### Phase Requirements -> Test Map

Since no formal requirement IDs were provided, the test map covers CONTEXT.md decisions:

| Decision | Behavior | Test Type | Automated Command | File Exists? |
|----------|----------|-----------|-------------------|-------------|
| D-12 (enhance pages) | PostHTML builds all enhanced pages without errors | unit | `cd aceengineer-website && npm test` (build.test.js covers this) | Yes |
| D-15 (GA4 events) | New gtag calls have correct event names and parameters | manual + grep | `grep -r "gtag('event'" aceengineer-website/content/ \| wc -l` | N/A (grep check) |
| D-04 (case studies) | New case study pages build and appear in sitemap | unit | `cd aceengineer-website && npm test` (build.test.js) | Yes |
| D-09 (funnel flow) | Calculator pages link to case studies and contact form | manual | Visual verification in browser | N/A (manual) |
| D-13 (GitHub pipeline) | Issues and labels exist in target repo | smoke | `gh issue list --label pipeline:contacted --state all` | N/A (CLI check) |
| Contact form enhancement | Project type selector field present and web3forms receives it | manual | Submit test form, verify email received with project_type field | N/A (manual) |

### Sampling Rate
- **Per task commit:** `cd aceengineer-website && npm test` (6 test suites)
- **Per wave merge:** Full JS + Python test suite
- **Phase gate:** Full suite green + visual verification of all enhanced pages + test contact form submission

### Wave 0 Gaps
- None -- existing test infrastructure (Jest build tests) covers structural integrity of HTML enhancements. New case study pages will be validated by the existing build.test.js which processes all HTML files in `content/`.
- Manual verification checklist needed for GA4 events (Realtime report) and contact form project type field (test submission).

## Open Questions

1. **Which private repo for the prospect pipeline?**
   - What we know: D-13 says "a private repo/project board" for GitHub Issues pipeline.
   - What is unclear: Whether to use an existing private repo or create a new one. The workspace-hub repo is private but used for planning, not CRM.
   - Recommendation: Create issues in the workspace-hub repo with `pipeline:` labels, or create a dedicated `aceengineer-crm` private repo. Planner should decide based on separation-of-concerns preference. Using workspace-hub is simpler; a separate repo is cleaner.

2. **GA4 Custom Dimensions registration timing**
   - What we know: Custom event parameters must be registered as custom dimensions in GA4 Admin to appear in reports.
   - What is unclear: Whether the GA4 property is fully configured with admin access on this machine, or if this is a manual step the user does in the GA4 web console.
   - Recommendation: Include "register custom dimensions in GA4 Admin" as a manual step in the plan, with the exact parameter-to-dimension mapping documented.

3. **Case study content source**
   - What we know: Case studies should show "real engineering problems solved with digitalmodel." The `CASE_STUDY_TEMPLATE.md` provides structure.
   - What is unclear: Whether case study content comes from actual past client work (anonymized) or is constructed as realistic demonstrations.
   - Recommendation: Planner should note that case study technical content requires domain expertise. The plan should provide structure and HTML scaffolding; the engineering content itself may require user input or review.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | PostHTML build, Jest tests | Needs verification | -- | Required, no fallback |
| npm | Package management | Needs verification | -- | Required, no fallback |
| gh CLI | GitHub Issues pipeline setup | Needs verification | -- | Manual GitHub web UI |
| GA4 web console | Custom dimension registration | Browser-based | N/A | No fallback (must be done in GA4 Admin) |

**Missing dependencies with no fallback:**
- None identified. All code changes are static HTML edits. Node.js and npm are required for build/test but are almost certainly present given Phase 3 was just completed.

**Missing dependencies with fallback:**
- `gh` CLI: If not installed, GitHub Issues and labels can be created via GitHub web UI. Less efficient but functional.

## Sources

### Primary (HIGH confidence)
- aceengineer-website codebase: direct inspection of `content/`, `build.js`, `package.json`, all calculator pages, case studies, contact form, pricing page
- Phase 3 CONTEXT.md: carry-forward decisions on static site, web3forms, GA4 integration
- Phase 4 CONTEXT.md: all 16 locked decisions and discretion areas
- [Google GA4 Events documentation](https://developers.google.com/analytics/devguides/collection/ga4/events) - Custom event setup patterns with gtag.js
- [GA4 Configuration limits](https://support.google.com/analytics/answer/12229528) - 25 parameters per event, 50 custom dimensions per property
- [GA4 Event collection limits](https://support.google.com/analytics/answer/9267744) - Parameter name/value character limits
- [web3forms advanced options](https://docs.web3forms.com/getting-started/examples/advanced-all-options) - Custom fields, hidden metadata

### Secondary (MEDIUM confidence)
- [GitHub Projects documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects) - Custom fields, kanban views, label-based filtering
- [GA4 scroll depth tracking patterns](https://www.analyticsmania.com/post/scroll-tracking-with-google-analytics-4-and-google-tag-manager/) - Custom scroll tracking without GTM
- [B2B case study structure](https://brixongroup.com/en/compelling-case-studies-how-to-create-impactful-b2b-success-stories-in) - Situation -> Trigger -> Barrier -> Solution -> Results structure
- [Engineering firm marketing 2026](https://www.sevenatoms.com/blog/marketing-for-engineering-firms) - Niche engineering SEO and content strategies
- [SEO for lead generation 2026](https://www.ingeniom.com/post/seo-for-lead-generation-complete-strategy-guide-2026) - SEO ROI data and niche keyword strategy

### Tertiary (LOW confidence)
- None. All findings verified against codebase or official documentation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries, all existing infrastructure verified by direct code inspection
- Architecture: HIGH -- patterns extracted directly from existing calculator pages, case studies, and contact form
- Pitfalls: HIGH -- GA4 dimension registration is a documented requirement; case study quality and pipeline adoption are common B2B challenges
- GA4 event taxonomy: MEDIUM -- recommended events are based on the enterprise funnel described in D-09, but actual utility depends on traffic volume and manual review discipline
- Case study topics: MEDIUM -- recommendations based on calculator-to-case-study gap analysis, but final topic selection depends on user's domain expertise and actual project history

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (30 days -- stable domain, no fast-moving dependencies)
