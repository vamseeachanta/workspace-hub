---
agent: adversarial-review-A-html
date: 2026-05-01
stance: defect-hunt (assume broken)
verdict: MAJOR
---

# 1. Verdict & headline

**MAJOR** — three real defects ship to prospects. (a) The two new methodology pages each carry an inline-prose dead link to `https://aceengineer.com/contact` that 307-redirects then 404s on the live site (verified live). (b) The outreach hub `content/outreach/index.html` — the page meant to be sent directly to clients — lists only Demos 1–5 and silently omits the brand-new Demo 6 (mooring) added in the same commit (`f5186ca`). (c) `sitemap.xml` indexes the two new methodology pages but leaves the four pre-existing methodology pages and the `/demos/` gallery hub un-indexed despite all returning 200 live; the sitemap-expansion commit was the natural moment to fix this and didn't.

Build is clean (52 pages built, 146/146 jest tests pass). All asset references resolve in `dist/`, all `download` attributes are present on every capability-summary CTA across all 11 changed files, all images carry meaningful `alt` text, and rootPath substitution is correct at both depths. The defect set is concentrated in cross-page coherence and one bad URL pattern that propagated into the new pages from existing peers.

# 2. MAJOR findings

- **MAJOR** `content/methodology/compliance-dashboard/index.html:73` and `content/methodology/cross-review/index.html:104` — `<a href="https://aceengineer.com/contact">Contact ACE Engineering</a>`. Live behavior verified: apex `aceengineer.com/contact` 307-redirects to `www.aceengineer.com/contact` which returns **404** (the real page is `/contact.html`). Both new pages prominently feature this dead link in the body's call-to-action prose. The bottom CTA buttons on the same pages correctly use `../../contact.html`, so the bug is the inline-prose anchor only. Same broken pattern exists in the four older methodology pages (compound-engineering, orchestrator-worker, multi-agent-parity, enforcement) — pre-existing, but the new pages knowingly replicated it. **Why MAJOR:** these are the methodology pages a prospect lands on from the capability summary; the most prominent in-text CTA returns 404. Fix: change to `../../contact.html` to match the bottom button, or to `https://www.aceengineer.com/contact.html`.

- **MAJOR** `content/outreach/index.html:170-200` — the "Demos to attach" grid lists Demos 1–5 only; Demo 6 (mooring, `demos/mooring.html`) is absent. Commit `f5186ca` added `content/demos/mooring.html` and updated the gallery + sitemap + tests to reflect six demos, but did not update the outreach hub. The outreach hub is described in the commit message of `e069d11` as "the page meant to be sent directly to prospective clients." A prospect arriving via the brochure or FOWT page reaches the hub and sees five demos despite Demo 6 being the one most relevant to the FOWT audience. **Why MAJOR:** the audience-specific brief on the same hub (`fowt-mooring-screening.html`) is mooring-themed; the hub forces the FOWT prospect to discover the mooring demo by guessing or by URL spelunking. Fix: add a sixth `<a class="card" href="{{ rootPath }}demos/mooring.html">` block in the demo grid, mirroring the existing five.

- **MAJOR** `sitemap.xml` — missing five live URLs. The commit message for `f5186ca` claims "sitemap expansion" but only adds entries for the two new methodology pages and the new demo/outreach pages, leaving these confirmed-live (HTTP 200) URLs un-indexed:
  1. `https://www.aceengineer.com/demos/` (gallery hub — the canonical entry point for the whole demo set)
  2. `https://www.aceengineer.com/methodology/compound-engineering/`
  3. `https://www.aceengineer.com/methodology/orchestrator-worker/`
  4. `https://www.aceengineer.com/methodology/multi-agent-parity/`
  5. `https://www.aceengineer.com/methodology/enforcement/`
  All five exist in `content/` and were built into `dist/` in this run. **Why MAJOR for SEO surface:** Google's discovery of the four older methodology pages now relies on inbound link graph alone; the demo-gallery hub being un-indexed is a self-inflicted SEO regression for the highest-priority customer-acquisition surface. The fix is mechanical — add five `<url>` blocks dated `2026-05-01` (or the older pages' real published dates).

# 3. MINOR findings

- **MINOR** `content/outreach/index.html:219` vs `content/outreach/vessel-contractor-brochure.html:205` — three different contact addresses on the new outreach surface: `vamsee.achanta@aceengineer.com` (hub mailto), `info@aceengineer.com` (brochure mailto), `support@aceengineer.com` (canonical site footer + contact.html schema). `info@aceengineer.com` may not even be provisioned. Pick one (probably `support@` for the brochure, founder address for the hub is fine if intentional) and document the convention so future outreach pages don't pick a third again.

- **MINOR** `content/outreach/vessel-contractor-brochure.html:172` — figcaption claims "rigid jumper installation (300 cases)" inside the 1,292-cases-total summation. The Demo 5 detail page (`content/demos/jumper-installation.html`) describes a **single** Ballymore manifold-PLET project with 81 validated tests, not a 300-case parametric sweep. The "300 parametric cases" figure is also propagated from `content/demos/index.html:385` (pre-existing in the gallery). The artifact does not substantiate 300 cases, so the brochure's "1,292 parametric cases" total is inflated by ~300 and risks a credibility hit if a contractor opens Demo 5 and counts. Either replace Demo 5 with a real 300-case parametric run, or reduce the brochure total and figcaption to ~992 cases + "+ Ballymore worked example."

- **MINOR** `content/outreach/fowt-mooring-screening.html:100` — `1.0×10^8 N·m/rad` renders as literal `^8` in HTML (no `<sup>`). Cosmetic but in a screening report shown to engineering managers, plain-text exponents look unfinished. Use `1.0&times;10<sup>8</sup>` or `1.0e8` per surrounding style.

- **MINOR** `content/demos/mooring.html` and `content/outreach/fowt-mooring-screening.html` — `.data-table` has up to 7 columns and is not wrapped in `.table-responsive` or any horizontal-scroll container. On a 360px viewport the cells will collapse text-wrap aggressively. The methodology pages (`compliance-dashboard`, `cross-review`) correctly use `<div class="table-responsive">` around their Bootstrap tables. The new pages should adopt the same wrapper for the data-table sections, especially since the FOWT page is the one most likely to be opened on a phone after an email tap.

- **MINOR** `content/outreach/index.html:155-167` — the two audience-brief cards expose word counts ("418 words", "789 words") in `.meta` text. Word-count is an internal authoring metric, not a useful prospect-facing signal; it tends to read as filler. Consider replacing with audience or read-time ("3-min read · vessel installation contractors").

- **MINOR** `content/demos/index.html:397` — the new Demo 6 card reuses `demo_comparison_matrix.gif` as its visual. That gif visualises the *other five* demos (matching the figcaption text on `content/demos/mooring.html:325`). Inside a clickable card on the gallery, the image-without-figcaption is misleading: a prospect scanning thumbnails will see a freespan/wall-thickness/mudmat/pipelay/jumper composite under the "DEMO 06 Mooring & Station-Keeping Screening" headline. Either ship a mooring-specific placeholder or move Demo 6 to the bottom of the grid with a "screened on commission" badge instead of the matrix gif. (The page-internal use on `mooring.html:319-329` is fine because the figcaption explains the substitution.)

- **MINOR** `content/methodology/compliance-dashboard/index.html:73` and `content/methodology/cross-review/index.html:104` — these pages mix `{{ rootPath }}` style (in head-common include) with hardcoded `../../contact.html` and `../../assets/capability-summary-v1.pdf` in the inline CTA block. Other pages use `{{ rootPath }}contact.html`. Functionally equivalent, but the inconsistency makes it easier for a future page-move to break only the methodology branch. Convert to `{{ rootPath }}` for parity with peer pages.

# 4. NIT findings

- **NIT** `content/demos/jumper-installation.html:27` — `<div style="display:flex;flex-wrap:wrap;justify-space-between">`. `justify-space-between` is not a valid CSS value (correct: `justify-content: space-between`). The four KPI tiles will pack to the start of the flex line instead of distributing across it. Pre-existing (introduced in `de49d21`, not in the review-scope commits) but commit `20f5e59` modified this file and did not fix it. One-line fix.

- **NIT** `content/demos/jumper-installation.html:82` — `<td>...20 more sections...</td>` is filler text presented to clients. Replace with the full 27-row table or with a deliberate "(20 additional sections elided for brevity — full list in the project deliverable)" framing. Pre-existing.

- **NIT** `content/outreach/vessel-contractor-brochure.html:15` — `<meta property="og:site_name" content="Analytical & Computational Engineering">` uses bare `&`. Most parsers tolerate it inside attribute content, but strict XHTML expects `&amp;`. Cosmetic.

- **NIT** `content/outreach/vessel-contractor-brochure.html:26` — `.brochure-hero { margin-top: -20px }`. Negative top margin is a fragile coupling to the navbar's bottom-margin and breaks if the navbar height changes. Pre-existing pattern from other landing pages.

- **NIT** `content/methodology/compliance-dashboard/index.html` and `cross-review/index.html` — both pages are minified to a single line (line 4 carries the entire style block, line 6 is one giant block of body markup with embedded `<h1>` titles inside the `<article>`). Diff-readability is poor and editorial revisions are error-prone. Pre-existing pattern in the methodology directory.

- **NIT** `content/demos/mooring.html` — uses an `<h1>` inside the report-header (line 175) and another `<h1>` is not present, but the page sits under a navbar that doesn't have its own `<h1>`. Document outline is fine. The page is honest about being a template (case-badge, illustrative-note, where-this-stops, figcaption). Verbose hedging is correct here — an under-hedged screening page would be a defect.

- **NIT** `tests/js/demo-links.test.js:7-9` — module-level docstring still says "the 5 demo detail pages... and — for the four chart pages" while `DETAIL_SLUGS.length === 6`. Assertion logic is correct (`expect(reportAnchors.length).toBe(6)`); only the prose comment is stale.

- **NIT** `tests/js/demo-links.test.js:97` — test description string `'has 5 <loc> entries for /demos/*.html at www host'` is stale (the assertion checks against `DETAIL_SLUGS.sort()` which is now 6 entries). Test passes; only the human-readable name lies.

# 5. What I checked but found clean

- All 11 changed HTML files build to `dist/` without errors (52 pages, 146/146 tests pass)
- All `<include src="partials/...">` resolve at build time — partials files exist at `content/partials/{head-common,nav,footer}.html`; built output contains the navbar/footer/GA markers across every changed page
- `rootPath` substitution: every page's frontmatter declares `"../"` (one level) or `"../../"` (two levels) and the substitution produces correct relative paths in `dist/` — verified by grep
- All 6 demo GIFs (`demo_01..05_*.gif` + `demo_comparison_matrix.gif`) exist at `assets/img/demos/` with correct case
- `assets/capability-summary-v1.pdf` exists; SHA256 sidecar present
- Every `<img>` in the 11 changed files has a non-trivial `alt` attribute
- Every PDF CTA across all 11 files has the `download` attribute (verified programmatically)
- Every `<a>` has either inner text or `aria-label`
- Sitemap: 45 URLs, all unique, all valid ISO-8601 dates, all conform to `https://www.aceengineer.com/...`
- Live HTTP probe: all 11 new pages return 200 on Vercel; capability PDF and matrix GIF return 200
- FOWT page numeric claims hedged with "illustrative", "OC4 reference", "screening-only — replace with project values", and the explicit "Where this stops" boundary blocks Section 2 (`docs/gtm/fowt-engineering-scope.md`) — no IEC over-claim, no certification claim, no full-coupled-time-domain claim
- Mooring page numeric claims similarly hedged — every k-value, pass-rate %, and case count carries an "illustrative" or "screening-only" note
- Brochure pricing claims ($5K–$15K screening, $25K–$75K detailed) match `docs/gtm/capability-map.md:151-152`
- NREL TP-5000-60601 reference cited on FOWT page resolves (verified live)
- "AceEngineer" capitalization is consistent across the new pages (no "aceEngineer" or "ACE Engineer" mid-sentence drift inside the 6 changed pages)

# 6. What I did NOT check (out of time/scope)

- Cross-browser CSS rendering (only verified the build step and DOM grep; did not open Chrome/Firefox/Safari devtools)
- Real screen-reader pass with NVDA / VoiceOver
- Lighthouse / pagespeed score deltas
- Email-client tolerance of the embedded GIF figures (Outlook/Gmail/Apple Mail) — the figures use `<figure>` + `<figcaption>` as the commit message claims for email tolerance, but I did not actually paste into a mail client
- Whether the four pre-existing methodology pages have OTHER drift relative to the two new ones (only checked the dead-`/contact` link, not the rest of the templates)
- The sitemap missing entries — I confirmed they're missing and live, but did NOT check robots.txt for any disallow rules that would intentionally hide them
- Brochure pricing claim "23 years of subsea/installation engineering" (line 139) — not verified against a CV or About page
- The capability-summary-v1.pdf content itself (only checked it loads as HTTP 200 and is referenced consistently across the new CTAs)
- The brochure's "1,292 parametric cases" arithmetic check vs. the per-demo gallery numbers (680+72+180+60+300=1,292) is correct, but rests on the unverified Demo 5 = 300 cases assumption flagged in MINOR #2

---

**6-line summary**

```
verdict:  MAJOR
major:    3
minor:    7
nit:      8
sharpest: methodology pages link to https://aceengineer.com/contact which redirects to /contact and 404s — both new pages carry the same dead inline CTA verbatim
file:     /mnt/local-analysis/workspace-hub/aceengineer-website/content/methodology/compliance-dashboard/index.html:73
```
