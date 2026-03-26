# Phase 3: GTM and Marketing -- aceengineer-website - Research

**Researched:** 2026-03-26
**Domain:** Static website marketing, client-side engineering calculators, SEO for niche B2B
**Confidence:** HIGH

## Summary

This phase enhances the existing aceengineer.com static site (Vercel-hosted, PostHTML build pipeline, Bootstrap 3.x) to position it as the go-to platform for offshore engineering calculations. The codebase is mature with 3 working calculators, 15 blog posts, 7 case studies, GA4 analytics, Web3Forms contact flow, and full Schema.org structured data. The primary work is: (1) adding 2-3 new calculators following the established pattern, (2) refining the landing page value proposition around "timeless engineering / single source of truth," (3) adding a display-only pricing page, (4) enhancing SEO with calculator-focused long-tail content, and (5) adding "Calculators" to the main nav and a "Request Pricing" CTA.

The technical risk is LOW. Every pattern needed (calculator HTML + inline JS + Plotly + GA4 events, Schema.org WebApplication markup, Web3Forms contact, PostHTML partials) already exists in the codebase and simply needs replication. The engineering domain knowledge (manifest-to-form-field mapping) is well-documented in Phase 1 YAML manifests.

**Primary recommendation:** Clone the existing calculator pattern (fatigue-life-calculator.html) for each new calculator, map inputs directly from Phase 1 YAML manifest function signatures, use Plotly for visualization, and keep all calculations client-side in JavaScript. Extend existing SEO infrastructure rather than rebuilding it.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Add 2-3 new calculators showcasing Phase 1 modules (on-bottom stability, wall thickness comparison, scatter fatigue) alongside the 3 existing calculators (fatigue-life, fatigue-sn-curve, npv-field-development). Existing calculators count toward UAT.
- **D-02:** New calculators follow the existing pattern: client-side JavaScript with Plotly charts and GA4 event tracking. Input forms map to YAML manifest function signatures from Phase 1.
- **D-03:** Content sync script (`scripts/content_sync.py`) pulls stats from digitalmodel (module count, standards count) for dynamic homepage claims.
- **D-04:** Stay static site on Vercel with client-side JS calculators. No Python API backend this phase.
- **D-05:** Existing posthtml build pipeline (`build.js`) handles templating. No framework migration.
- **D-06:** Calculators are labeled "illustrative" with a CTA to contact for full standard-compliant analysis.
- **D-07:** Free calculators as lead generation. Consultation-based pricing only -- no payment infrastructure, no auth, no user accounts this phase.
- **D-08:** Contact form (web3forms + GA4 conversion tracking) is the sole conversion path. Add "Request Pricing" CTA alongside existing contact options.
- **D-09:** Optionally display a simple tiered pricing page (display-only) showing Free/Pro/Enterprise to signal platform intent. All tiers route to contact form.
- **D-10:** Enhance existing SEO foundation -- don't rebuild. Structured data, sitemap, GA4, 15 blog posts, 7 case studies are the base.
- **D-11:** Add calculation-focused long-tail content targeting queries like "on-bottom stability calculator DNV-RP-F109", "ASME B31.4 wall thickness calculator".
- **D-12:** Each new calculator page gets full Schema.org WebApplication markup, Open Graph tags, and sitemap entry (matching existing calculator pattern).
- **D-13:** Theme: "Tethering timeless engineering to a single source of truth" -- every calculation traces to its standard, every standard to its implementation.
- **D-14:** Landing page communicates: (1) engineering calculations you can trust, (2) traceable to international standards, (3) powered by open-source digitalmodel.

### Claude's Discretion
- Exact calculator UI design and interaction patterns
- Blog content topics and publishing schedule
- Landing page layout and visual design
- Competitor differentiation messaging specifics
- Whether to add a newsletter/waitlist signup vs. contact-only

### Deferred Ideas (OUT OF SCOPE)
- Python API backend for exact calculations -- Phase 5+
- Payment integration (Stripe, auth, user accounts) -- Phase 4 if needed
- Newsletter/email marketing automation -- Phase 4 or backlog
- Interactive API documentation (Swagger/FastAPI docs) -- future phase when API exists
</user_constraints>

## Project Constraints (from CLAUDE.md)

- Retrieval first -- consult docs, rules, memory before training knowledge
- Prefer targeted single-site edits over bulk find-replace
- In scripts: use relative paths or `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` -- never hardcode absolute paths
- CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md must not exceed 20 lines
- Context budget: 16KB max

## Standard Stack

### Core (Already in Place)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PostHTML | 0.16.6 | HTML templating with includes and expressions | Already used for all pages; partials for nav/head/footer |
| posthtml-include | 2.0.1 | Partial includes in templates | Shared header, nav, footer across all pages |
| posthtml-expressions | 1.11.3 | Template variable interpolation (rootPath) | Handles relative paths in nested pages |
| Bootstrap | 3.x (United theme) | CSS framework | Entire site uses Bootstrap 3 classes; migration is out of scope |
| Plotly.js | 2.27.0 (CDN) | Interactive charting for calculators | Already used in fatigue-sn-curve and NPV calculators |
| Web3Forms | API-based | Contact form submission (no backend) | Already integrated with access key `c7338953-...` |
| GA4 | G-K31E51DQ47 | Analytics and event tracking | Already on every page via head-common.html partial |
| PurgeCSS | 8.0.0 | Strip unused Bootstrap CSS in build | Part of existing build pipeline |
| CleanCSS | 5.3.3 | CSS minification | Part of existing build pipeline |
| Jest | 30.2.0 | JavaScript testing | Existing test suite for build, navbar, NPV engine |

### Supporting (To Add)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None | -- | -- | All new calculators use vanilla JS + existing CDN libs |

**Note on Plotly version:** The existing site uses Plotly 2.27.0 via CDN. The latest Plotly.js is 3.4.0. Recommendation: keep 2.27.0 for consistency with existing calculators this phase. Upgrading to v3 would require testing all existing calculator charts, which is out of scope.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Inline JS calculators | Separate .js engine files | NPV already uses this pattern; new calculators can go either way. Inline is simpler for small calculators. |
| Bootstrap 3 | Bootstrap 5 or Tailwind | Would require rewriting all HTML. Locked as out of scope per D-05. |
| PostHTML | Astro/Next.js/Hugo | Framework migration is explicitly deferred per D-05. |

**Installation:** No new packages needed. Existing `package.json` has everything required.

## Architecture Patterns

### Existing Project Structure (Relevant Parts)
```
aceengineer-website/
+-- content/                    # PostHTML source templates
|   +-- partials/
|   |   +-- head-common.html    # GA4, favicon, CSS, navbar JS
|   |   +-- nav.html            # Main navigation (Bootstrap 3)
|   |   +-- footer.html         # Footer with quick links
|   +-- calculators/
|   |   +-- index.html          # Calculator listing page
|   |   +-- fatigue-life-calculator.html
|   |   +-- fatigue-sn-curve.html
|   |   +-- npv-field-development.html
|   +-- index.html              # Homepage / landing page
|   +-- contact.html            # Web3Forms contact form
|   +-- blog/                   # Blog posts
+-- assets/
|   +-- css/                    # Bootstrap United + custom CSS
|   +-- js/
|   |   +-- navbar-toggle.js
|   |   +-- npv-calculator-engine.js  # Standalone engine (testable)
+-- calculators/                # Built output (dist copies here too)
+-- dist/                       # Build output directory
+-- build.js                    # PostHTML build pipeline
+-- scripts/content_sync.py     # Stats sync from digitalmodel
+-- config/content-sync.yaml    # Sync configuration
+-- stats.json                  # Current: {"standards": 17}
+-- sitemap.xml                 # 30+ URLs
+-- vercel.json                 # Build + deploy config
+-- tests/js/                   # Jest test suite
```

### Pattern 1: Calculator Page Structure
**What:** Each calculator is a self-contained HTML page in `content/calculators/` with front matter, PostHTML includes, inline CSS, form inputs, Plotly chart, and inline JS calculation logic.
**When to use:** Every new calculator.
**Template anatomy:**
```html
---
rootPath: "../"
---
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- SEO meta tags (description, keywords) -->
    <!-- Open Graph tags -->
    <title>[Calculator Name] - A&CE</title>
    <include src="partials/head-common.html"></include>
    <!-- Plotly CDN -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <!-- Schema.org WebApplication JSON-LD -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "[Calculator Name]",
        "applicationCategory": "Engineering Calculator",
        "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
        "featureList": [...],
        "provider": { "@id": "https://aceengineer.com/#organization" },
        "isPartOf": { "@id": "https://aceengineer.com/calculators/#collection" }
    }
    </script>
    <style>/* Calculator-specific CSS */</style>
</head>
<body>
    <include src="partials/nav.html"></include>
    <!-- Calculator form + results + Plotly chart -->
    <!-- Illustrative disclaimer per D-06 -->
    <!-- CTA to contact for full analysis -->
    <include src="partials/footer.html"></include>
    <script>
    // Calculation logic + GA4 event tracking
    gtag('event', 'calculator_use', {
        'event_category': 'engagement',
        'event_label': '[calculator_name]',
        // ...input values for analytics
    });
    </script>
</body>
</html>
```

### Pattern 2: Manifest-to-Calculator Mapping
**What:** Phase 1 YAML manifests define function signatures (inputs, outputs, standard references) that map directly to calculator form fields.
**When to use:** When building new calculator input forms.
**Mapping rules:**
- Each manifest `inputs` array becomes form fields
- Input names (e.g., `rho_w_kg_m3`) become field IDs with human-readable labels
- `primary_standard.id` and `functions[].clause` become the standard reference displayed
- Output values map to result display boxes
- Multiple functions in a manifest can map to a single calculator with step-by-step sections

**On-bottom stability manifest inputs for calculator form:**
| Manifest Input | Form Label | Unit | Default |
|----------------|------------|------|---------|
| rho_w_kg_m3 | Seawater density | kg/m3 | 1025 |
| D_outer_m | Pipe outer diameter | m | 0.3238 |
| t_wall_m | Wall thickness | m | 0.0127 |
| rho_steel_kg_m3 | Steel density | kg/m3 | 7850 |
| rho_coat_kg_m3 | Coating density | kg/m3 | 900 |
| t_coat_m | Coating thickness | m | 0.003 |
| rho_contents_kg_m3 | Contents density | kg/m3 | 800 |
| U_m_s | Current velocity | m/s | 0.5 |
| a_m_s2 | Wave acceleration | m/s2 | 0.3 |
| C_D | Drag coefficient | - | 0.9 |
| C_M | Inertia coefficient | - | 3.29 |
| C_L | Lift coefficient | - | 0.9 |
| mu_soil | Soil friction coeff | - | 0.6 |

**Wall thickness manifest inputs for calculator form:**
| Manifest Input | Form Label | Unit | Default |
|----------------|------------|------|---------|
| PipeGeometry (D_outer, t_wall) | Pipe OD, Wall thickness | m, m | 0.3238, 0.0127 |
| PipeMaterial (SMYS, SMTS, E) | SMYS, SMTS, Young's mod | MPa | 450, 535, 207000 |
| DesignLoads (P_i, P_e, T) | Int. pressure, Ext. pressure, Temperature | MPa, MPa, C | 15, 5, 60 |
| DesignFactors (corrosion_allowance) | Corrosion allowance | m | 0.003 |

### Pattern 3: GA4 Event Tracking for Calculators
**What:** Every calculator fires a `calculator_use` event on form submission with calculator name, key inputs, and result.
**Example:**
```javascript
gtag('event', 'calculator_use', {
    'event_category': 'engagement',
    'event_label': 'on_bottom_stability',
    'pipe_diameter': D_outer_m,
    'current_velocity': U_m_s,
    'result_utilisation': utilisation
});
```

### Pattern 4: PostHTML Build Pipeline
**What:** `content/` directory is source, `dist/` is output. Build runs `node build.js` which processes PostHTML includes/expressions, then PurgeCSS, then CSS bundle/minify.
**Build command:** `npm run build` (runs `node build.js`)
**Key behavior:** Files in `content/` with front matter (`rootPath: "../"`) get includes resolved and variables interpolated. Built files go to `dist/`. Vercel serves from `dist/`.

### Anti-Patterns to Avoid
- **Adding calculators outside content/ directory:** All new calculator pages go in `content/calculators/`. The built output lands in `dist/calculators/`. Never edit `dist/` or root-level `calculators/` directly -- those are build artifacts.
- **Hardcoding nav/head/footer:** Always use `<include src="partials/...">`. Never copy-paste the GA4 snippet or nav HTML.
- **Mixing Plotly versions:** All calculators must use the same Plotly CDN version (2.27.0). Do not upgrade individual pages.
- **Adding npm dependencies for calculators:** Calculators are client-side vanilla JS. No bundler, no React, no framework. Keep it simple.
- **Forgetting the rootPath front matter:** Every page in a subdirectory needs `rootPath: "../"` for correct asset paths.
- **Forgetting sitemap entry:** Every new public page needs a `<url>` entry in sitemap.xml.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form submission | Custom backend | Web3Forms API (already integrated) | Zero backend, spam filtering, email delivery built-in, 250 submissions/mo free |
| Analytics | Custom tracking | GA4 (already integrated) | Event tracking, conversion funnels, audience segmentation all built-in |
| Interactive charts | Canvas/SVG manually | Plotly.js CDN (already used) | Responsive, interactive zoom/pan/hover, export to PNG, well-documented |
| CSS framework | Custom styles | Bootstrap 3.x (already used) | Grid system, responsive breakpoints, form controls, all consistent |
| HTML templating | Manual copy-paste | PostHTML includes (already used) | Single source of truth for nav, header, footer across all pages |
| Schema.org markup | Custom JSON-LD generator | Hand-write per-page JSON-LD (established pattern) | Simple enough; the pattern is well-established across existing calculator pages |
| Contact form validation | Custom JS validators | HTML5 `required` + Web3Forms server validation | Already working; no JS validation needed |

**Key insight:** This phase is almost entirely about replicating established patterns with new engineering content. The infrastructure is fully built. The work is content creation and calculator implementation.

## Common Pitfalls

### Pitfall 1: Calculator JavaScript Errors in Client-Side Math
**What goes wrong:** Division by zero, negative square roots, or NaN results when user enters edge-case inputs (zero wall thickness, zero velocity, etc.).
**Why it happens:** Engineering calculators accept physical quantities that have valid ranges, but HTML number inputs accept any value.
**How to avoid:** Add input validation before calculation. Use the NPV engine pattern: return descriptive results for edge cases rather than crashing. The digitalmodel Python code already handles these (e.g., zero submerged weight returns `inf` utilisation).
**Warning signs:** NaN or Infinity showing in result boxes, Plotly chart not rendering.

### Pitfall 2: Forgetting the Content/ vs Dist/ Distinction
**What goes wrong:** Editing files in `calculators/` (root level, which is build output) instead of `content/calculators/` (source). Changes get overwritten on next build.
**Why it happens:** Both directories contain HTML files with similar names. Root-level `calculators/` is the current built output.
**How to avoid:** Always edit in `content/`. Run `npm run build` to verify. Check `dist/` output.
**Warning signs:** Changes disappear after build.

### Pitfall 3: Inconsistent SEO Markup Between Pages
**What goes wrong:** Missing Open Graph tags, incomplete Schema.org JSON-LD, or wrong canonical URLs on new pages.
**Why it happens:** Copy-paste from existing calculator and forgetting to update all URLs, names, descriptions.
**How to avoid:** Use the fatigue-life-calculator.html as the reference template. Check every URL, name, description, and featureList in the JSON-LD after copying.
**Warning signs:** Google Rich Results Test shows errors or warnings.

### Pitfall 4: Web3Forms Rate Limit
**What goes wrong:** Contact form stops accepting submissions.
**Why it happens:** Free tier is 250 submissions/month. If calculators drive significant traffic, contact form submissions could hit the limit.
**How to avoid:** Monitor Web3Forms dashboard. For this phase, 250/month is likely sufficient for a B2B niche site. If approaching limit, consider upgrading to Pro ($4/month for 10k submissions).
**Warning signs:** Form submissions silently failing, users reporting no confirmation.

### Pitfall 5: Stale Stats in Homepage Claims
**What goes wrong:** Homepage claims "704+ Python modules" but the actual count has changed since last sync.
**Why it happens:** Content sync (`scripts/content_sync.py`) must be run manually or via CI.
**How to avoid:** Run content sync as part of the build process or manually before deployment. Update `stats.json` and reference it in homepage.
**Warning signs:** Discrepancy between homepage numbers and actual digitalmodel repo counts.

### Pitfall 6: Nav Not Including Calculators
**What goes wrong:** Users cannot discover calculators from any page except the footer.
**Why it happens:** Current `content/partials/nav.html` does not have a "Calculators" link (it is only in the footer).
**How to avoid:** Add Calculators link to nav.html. This is a high-impact, low-effort improvement for discoverability.
**Warning signs:** Low calculator page views despite being live.

## Code Examples

### New Calculator: On-Bottom Stability (Key Calculation Logic)
```javascript
// Source: digitalmodel/src/digitalmodel/subsea/on_bottom_stability/manifest.yaml
// Implements DNV-RP-F109 Eq 3.1, 3.2, 4.1

function hydrodynamicForcePerMeter(rho_w, D, U, a, C_D, C_M) {
    // F_H = 0.5 * rho * D * C_D * U * |U| + (pi/4) * rho * D^2 * C_M * a
    const drag = 0.5 * rho_w * D * C_D * U * Math.abs(U);
    const inertia = (Math.PI / 4) * rho_w * D * D * C_M * a;
    return drag + inertia;
}

function liftForcePerMeter(rho_w, D, U, C_L) {
    // F_L = 0.5 * rho * D * C_L * U^2
    return 0.5 * rho_w * D * C_L * U * U;
}

function submergedWeightPerMeter(D_outer, t_wall, rho_steel, rho_coat, t_coat, rho_contents, rho_w) {
    const D_inner = D_outer - 2 * t_wall;
    const A_steel = (Math.PI / 4) * (D_outer * D_outer - D_inner * D_inner);
    const D_coated = D_outer + 2 * t_coat;
    const A_coat = (Math.PI / 4) * (D_coated * D_coated - D_outer * D_outer);
    const A_contents = (Math.PI / 4) * D_inner * D_inner;
    const A_displaced = (Math.PI / 4) * D_coated * D_coated;

    const W_dry = (A_steel * rho_steel + A_coat * rho_coat + A_contents * rho_contents) * 9.81;
    const buoyancy = A_displaced * rho_w * 9.81;
    return W_dry - buoyancy;
}

function absoluteStabilityCheck(W_s, F_H, F_L, mu) {
    // DNV-RP-F109 Eq 4.1: gamma_SC * F_H <= mu * (W_s - F_L)
    if (W_s <= 0) return { utilisation: Infinity, is_stable: false, details: 'Negative/zero submerged weight' };
    const resistance = mu * (W_s - F_L);
    if (resistance <= 0) return { utilisation: Infinity, is_stable: false, details: 'Insufficient weight for stability' };
    const utilisation = F_H / resistance;
    return { utilisation: utilisation, is_stable: utilisation <= 1.0, details: `Utilisation: ${(utilisation * 100).toFixed(1)}%` };
}
```

### New Calculator: Wall Thickness Comparison (Key Logic)
```javascript
// Source: digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/manifest.yaml
// Implements ASME B31.4 S403.2.1 (Barlow formula burst check)

function burstCheck(D_outer, t_wall, SMYS, P_internal, P_external, corrosion_allowance, design_factor) {
    // Effective thickness after corrosion
    const t_eff = t_wall - corrosion_allowance;
    if (t_eff <= 0) return { utilisation: Infinity, details: 'Zero effective thickness' };

    // Barlow formula: P_burst = 2 * SMYS * t_eff * design_factor / D_outer
    const P_burst = 2 * SMYS * t_eff * design_factor / D_outer;
    const delta_P = P_internal - P_external;
    const utilisation = delta_P / P_burst;
    return { utilisation: utilisation, is_passing: utilisation <= 1.0, details: `Burst utilisation: ${(utilisation * 100).toFixed(1)}%` };
}
```

### GA4 Conversion Tracking Pattern (From Contact Form)
```javascript
// Source: aceengineer-website/content/contact.html
// Track form submission event
document.getElementById('contact-form').addEventListener('submit', function() {
    gtag('event', 'contact_form_submission', {
        'event_category': 'contact',
        'event_label': document.getElementById('subject').value
    });
});

// Track successful submission (redirect-based)
if (urlParams.get('success') === 'true') {
    gtag('event', 'contact_form_success', {
        'event_category': 'contact',
        'event_label': 'form_submitted_successfully'
    });
}
```

### Schema.org WebApplication Markup Template
```json
{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "@id": "https://aceengineer.com/calculators/[slug].html#calculator",
    "name": "[Calculator Full Name]",
    "description": "[2-3 sentence description with standard references]",
    "url": "https://aceengineer.com/calculators/[slug].html",
    "applicationCategory": "Engineering Calculator",
    "applicationSubCategory": "[Specific discipline]",
    "operatingSystem": "Any web browser",
    "browserRequirements": "Requires JavaScript",
    "softwareVersion": "1.0",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
    },
    "featureList": ["[Feature 1]", "[Feature 2]"],
    "provider": { "@type": "Organization", "@id": "https://aceengineer.com/#organization" },
    "isPartOf": { "@type": "CollectionPage", "@id": "https://aceengineer.com/calculators/#collection" }
}
```

## Competitive Landscape

### On-Bottom Stability Calculators
| Competitor | Type | Limitation | A&CE Differentiator |
|------------|------|------------|---------------------|
| TheNavalArch | Paid spreadsheet tool | Not free, requires download | Free, browser-based, instant |
| Pipeng Toolbox | Online but basic | Limited UI, no visualization | Interactive Plotly charts, DNV clause references |
| DNV StableLines | Professional desktop software | Requires license, complex | Simple, educational, links to full consulting |
| Aurora AuroraCAT | Specialized tool | Focused on cables only | Broader pipeline coverage |

### Wall Thickness Calculators
| Competitor | Type | Limitation | A&CE Differentiator |
|------------|------|------------|---------------------|
| piping-world.com | Free online | Single standard per page | Multi-code comparison (B31.4 + B31.8 + API) |
| pipeflowcalculations.com | Free online | B31.8 only | Multi-code with standard traceability |
| pipeng.com | Online modules | Dated UI | Modern UI, Plotly visualization |
| planetcalc.com | Free online | Generic Barlow only | Standard-specific with corrosion allowance |

**Opportunity:** No competitor offers a free, browser-based, multi-standard wall thickness comparison tool with interactive visualization. This is a gap A&CE can uniquely fill given Phase 1 implementations of ASME B31.4, B31.8, and API codes.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Plotly.js 1.x with `plotly-latest.min.js` | Plotly.js 2.x/3.x with exact version pinning | 2021 (v2 release) | Must use exact version URL; `plotly-latest` frozen at v1.58.5 |
| Bootstrap 3.x | Bootstrap 5.x is current | 2021 | Site uses BS3; migration is out of scope per D-05 |
| jQuery for DOM manipulation | Vanilla JS | 2020+ | Site already uses vanilla JS for calculators; no jQuery dependency |
| Google Universal Analytics | GA4 | July 2023 | Site already uses GA4 (G-K31E51DQ47) |

**Deprecated/outdated:**
- Bootstrap 3.x is end-of-life but functional. No security risk for a static content site. Migration deferred.
- `plotly-latest.min.js` CDN URL is frozen at v1.58.5. Site correctly uses versioned URL.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Jest 30.2.0 with jsdom and node environments |
| Config file | `package.json` (inline jest config) |
| Quick run command | `cd aceengineer-website && npm test` |
| Full suite command | `cd aceengineer-website && npm test -- --coverage` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-01 | New calculators render correct results | unit | `npm test -- --testPathPattern=on-bottom-stability` | No -- Wave 0 |
| D-01 | Wall thickness calculator produces correct utilisation | unit | `npm test -- --testPathPattern=wall-thickness` | No -- Wave 0 |
| D-02 | Calculator JS engines are testable standalone modules | unit | `npm test -- --testPathPattern=calculator` | No -- Wave 0 |
| D-03 | Content sync outputs updated stats.json | unit (Python) | `cd aceengineer-website && python -m pytest tests/python/test_content_sync.py -x` | Yes |
| D-05 | Build pipeline produces dist/ with all pages | unit | `npm test -- --testPathPattern=build` | Yes (build.test.js) |
| D-06 | Calculators display illustrative disclaimer | smoke | Manual inspection of built pages | No -- manual |
| D-08 | Contact form CTA present on calculator pages | smoke | Manual inspection | No -- manual |
| D-12 | Schema.org markup validates | smoke | Google Rich Results Test (manual) | No -- manual |
| UAT | Website live with 3+ calculators, value prop, signup/contact | e2e | Manual browser testing on Vercel preview | No -- manual |

### Sampling Rate
- **Per task commit:** `cd aceengineer-website && npm test`
- **Per wave merge:** `cd aceengineer-website && npm test -- --coverage`
- **Phase gate:** Full suite green + manual verification of built pages

### Wave 0 Gaps
- [ ] `tests/js/on-bottom-stability.test.js` -- unit tests for OBS calculator engine
- [ ] `tests/js/wall-thickness.test.js` -- unit tests for wall thickness calculator engine
- [ ] `assets/js/obs-calculator-engine.js` -- standalone engine file (NPV pattern)
- [ ] `assets/js/wall-thickness-engine.js` -- standalone engine file (NPV pattern)

*(Scatter fatigue calculator is optional per D-01 "2-3 new calculators." If included, add `tests/js/scatter-fatigue.test.js` + `assets/js/scatter-fatigue-engine.js`.)*

## SEO Strategy Details

### Long-Tail Keywords to Target
| Keyword | Monthly Search (Est.) | Difficulty | Calculator Page |
|---------|----------------------|------------|-----------------|
| on-bottom stability calculator | Low-Medium | Low (niche) | on-bottom-stability.html |
| DNV-RP-F109 calculator | Low | Very Low | on-bottom-stability.html |
| pipeline wall thickness calculator ASME | Medium | Medium | wall-thickness.html |
| ASME B31.4 wall thickness calculator | Medium | Low-Medium | wall-thickness.html |
| ASME B31.8 wall thickness calculator | Medium | Low-Medium | wall-thickness.html |
| scatter fatigue calculator DNV | Low | Very Low | scatter-fatigue.html (if built) |
| S-N curve fatigue calculator | Medium | Medium | fatigue-sn-curve.html (existing) |
| offshore fatigue calculator | Medium | Medium | fatigue-life-calculator.html (existing) |

### SEO Checklist Per New Page
1. Unique `<title>` with primary keyword + "- A&CE"
2. `<meta name="description">` under 160 chars with keyword
3. `<meta name="keywords">` with 5-8 terms
4. Open Graph: og:title, og:description, og:type, og:url, og:site_name
5. Schema.org WebApplication JSON-LD
6. Add URL to `sitemap.xml` with `<lastmod>` date
7. Internal links: from calculator index, from relevant blog posts, from landing page
8. H1 with primary keyword
9. Descriptive alt text on any images
10. "Illustrative" disclaimer and CTA to contact

## New Pages to Create

| Page | Path | Purpose |
|------|------|---------|
| On-Bottom Stability Calculator | `content/calculators/on-bottom-stability.html` | DNV-RP-F109 pipeline stability |
| Wall Thickness Calculator | `content/calculators/wall-thickness.html` | Multi-code comparison (ASME B31.4/B31.8) |
| Scatter Fatigue Calculator (optional) | `content/calculators/scatter-fatigue.html` | Spectral fatigue from scatter diagram |
| Pricing Page | `content/pricing.html` | Display-only tiered pricing (D-09) |

## Files to Modify

| File | Change | Why |
|------|--------|-----|
| `content/partials/nav.html` | Add "Calculators" link | Currently only in footer; major discoverability gap |
| `content/index.html` | Update value prop messaging per D-13/D-14 | Align with "timeless engineering" theme |
| `content/index.html` | Add calculator showcase section | Highlight interactive demos |
| `content/calculators/index.html` | Add new calculator cards, update Schema.org ItemList | Listing page for all calculators |
| `sitemap.xml` | Add new calculator URLs + pricing URL | SEO indexing |
| `content/contact.html` | Add "Request Pricing" as subject option | D-08 pricing CTA |
| `config/content-sync.yaml` | Extend to count new module types | D-03 stats |
| `scripts/content_sync.py` | Add manifest count function | D-03 dynamic stats |
| `content/partials/footer.html` | Add Pricing link | Navigation consistency |

## Open Questions

1. **Scatter Fatigue Calculator Complexity**
   - What we know: The scatter fatigue manifest has complex inputs (scatter_table, stress_transfer_function, sn_curve, frequencies). This is significantly more complex than the other two calculators.
   - What's unclear: Can a meaningful illustrative version work with simplified inputs (e.g., pre-defined scatter tables), or does this require too many inputs for a web form?
   - Recommendation: Start with on-bottom stability and wall thickness (simpler, clearer form inputs). Add scatter fatigue only if time permits, with a simplified UI using pre-set example data and a "Run Example" button approach rather than requiring all inputs.

2. **Newsletter/Waitlist vs Contact-Only**
   - What we know: D-07 says consultation-based only. Claude's discretion includes newsletter/waitlist decision.
   - What's unclear: Whether a lightweight email capture (just email field) would help for future phases without overcomplicating this phase.
   - Recommendation: Skip newsletter signup this phase. The contact form is the conversion path. Adding email capture adds scope (privacy policy, email service integration, GDPR considerations) with minimal benefit at this traffic level.

3. **Landing Page Rewrite Scope**
   - What we know: Current homepage is OrcaFlex/AQWA automation focused. D-13/D-14 want "timeless engineering" + "single source of truth" positioning.
   - What's unclear: How much of the landing page to rewrite vs. enhance.
   - Recommendation: Enhance, don't rewrite. Update the hero section and add a calculator showcase section. Keep the existing pain-point, solution, metrics, and vertical sections -- they still apply and have SEO value. The messaging shift is additive (add standard traceability narrative) not replacement.

## Sources

### Primary (HIGH confidence)
- Codebase inspection: `aceengineer-website/` -- all file structures, patterns, and code examples verified directly
- Phase 1 manifests: `digitalmodel/src/digitalmodel/subsea/on_bottom_stability/manifest.yaml`, `structural/analysis/wall_thickness_codes/manifest.yaml`, `structural/fatigue/manifest.yaml`
- Vercel deployment config: `vercel.json` -- build command, output directory, headers
- PostHTML build pipeline: `build.js` -- confirmed content/ -> dist/ flow

### Secondary (MEDIUM confidence)
- [Plotly.js releases](https://github.com/plotly/plotly.js/releases) -- v3.4.0 is latest; existing site uses 2.27.0
- [Web3Forms pricing](https://web3forms.com/pricing) -- free tier 250 submissions/month
- [Schema.org WebApplication](https://schema.org/WebApplication) -- structured data type definition
- Competitor calculator landscape: TheNavalArch, Pipeng Toolbox, piping-world.com, pipeflowcalculations.com

### Tertiary (LOW confidence)
- Search volume estimates for long-tail engineering keywords -- based on niche assessment, not actual keyword tools

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- entirely based on existing codebase inspection; no new libraries needed
- Architecture: HIGH -- patterns are established and working in 3 existing calculators
- Pitfalls: HIGH -- identified from direct codebase analysis and engineering domain knowledge
- SEO strategy: MEDIUM -- keyword difficulty estimates are approximate; competitive landscape verified via web search
- Calculator complexity: MEDIUM -- JS implementations derived from Python manifests; edge cases need testing

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable -- no fast-moving dependencies)
