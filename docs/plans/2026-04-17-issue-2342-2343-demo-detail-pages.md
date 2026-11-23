# Plan for #2342 + #2343: Publish Demo Detail Pages 1-4 and Wire Gallery CTAs

> **Status:** plan-approved (self-approved 2026-04-19 after v4-lite inline fixes — user chose V4-lite path: apply MAJORs inline, accept MEDIUMs/MINORs as documented debt, no round-4 review dispatch)
> **Revision history:**
> - 2026-04-17 v1 — initial draft
> - 2026-04-19 v2 — rewritten after Claude MAJOR + Codex MAJOR: corrected Vercel deploy model, committed to `head-common` include, resolved title contradiction, added sitemap.xml updates, wired link-check to Jest, added rollback + SRI/vendoring, restructured TDD
> - 2026-04-19 v3 — tightened after Claude MAJOR + Codex MAJOR on v2: fixed sitemap host (apex → www), added `package.json` to Files to Change with explicit jest.projects entry (link-check now actually runs), split jumper retrofit into a preceding commit for clean rollback (also removes unnecessary Plotly tag from chart-less page), added "Known minor debt" section for D/F/G/H
> - 2026-04-19 v4-lite — fixed all 3 Codex MAJORs on v3 inline: (1) added `partials/nav.html` + `partials/footer.html` includes to 4 new pages AND jumper retrofit — head-common alone does NOT provide nav; (2) removed "fails CI" overclaim — no GH Actions workflow in this repo, Jest runs locally via `npm test` (CI workflow filed as follow-up); (3) Plotly integrity: `sha256sum assets/js/plotly-2.32.0.min.js` sidecar file + vendored BSD-3 LICENSE — replaces v3's SHA1/tarball error. Also: jsdom env, `--selectProjects` verification, 4/4 Plotly post-deploy, scoped sitemap test, moved jumper sitemap entry to Commit 1
> **Complexity:** T2
> **Issues:**
> - https://github.com/vamseeachanta/workspace-hub/issues/2342 (publish 4 detail pages)
> - https://github.com/vamseeachanta/workspace-hub/issues/2343 (wire gallery CTAs)
> **Combined rationale:** Both ship through the same `aceengineer-website` repo and the same Vercel build on push. Splitting the two issues doubles review overhead without reducing blast radius. The jumper retrofit is a separate preceding commit (see Rollback Plan) so its independent revert is clean.
> **Review artifacts:**
> - v1: `scripts/review/results/2026-04-17-plan-2342-claude.md` (MAJOR); Codex review blocked by sandbox (no artifact).
> - v2: `scripts/review/results/2026-04-19-plan-2342-claude.md` (MAJOR); `scripts/review/results/2026-04-19-plan-2342-codex.md` (MAJOR — artifact manually transcribed because Codex sandbox blocked the write).
> - v3: pending — will be written to `scripts/review/results/2026-04-19-v3-plan-2342-claude.md` and `-codex.md`.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `aceengineer-website/content/demos/jumper-installation.html` (91 lines) — existing detail page. Uses YAML frontmatter `rootPath: "../"`, inline `<style>`, **does NOT include `partials/head-common.html`** — this is a pre-existing defect on the already-live page (no GA, no nav) that this plan will also fix as an in-scope side-effect.
- Found: `aceengineer-website/content/demos/index.html` (468 lines) — gallery with 5 `.demo-card` blocks at lines 290, 310, 330, 350, 370. Only Demo 5 (line 383) has a `View detailed report` CTA. Demo 2 has a `Try free calculator` CTA at line 323. Demos 1, 3, 4 have no detail-level CTA. Gallery DOES include `partials/head-common.html` at line 26 — so the reference partial-include pattern is already established on the site.
- Found: `aceengineer-website/content/partials/head-common.html` — supplies favicon, site CSS (`styles.min.css`), deferred `navbar-toggle.js`, and Google Analytics (`G-K31E51DQ47`) with `requestIdleCallback` deferral. Every branded page must include it.
- Found: `aceengineer-website/build.js` — posthtml pipeline: `content/` → `dist/`, skips `partials/`, parses YAML frontmatter for `rootPath`, applies `posthtml-include` for partials and `posthtml-expressions` for `{{ rootPath }}` templating.
- Found: `aceengineer-website/vercel.json` — **Vercel deploy**, `buildCommand: npm run build`, `outputDirectory: dist`. Host redirect `aceengineer.com` → `www.aceengineer.com`. Cache-control headers only for `/assets/(.*)` (immutable 1yr). Security headers `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`. **No `Content-Security-Policy` header** — confirmed via direct read — so Plotly CDN is not CSP-blocked.
- Found: `aceengineer-website/.gitignore` line 2 = `dist/` → **`dist/` is NOT committed**. Vercel rebuilds from `content/` on every push.
- Found: `aceengineer-website/sitemap.xml` — hand-maintained XML; uses `aceengineer.com` host (the redirect source). **Zero `/demos/` entries** currently, including the already-live `jumper-installation.html` (pre-existing gap).
- Found: `aceengineer-website/robots.txt` — `Allow: /`; no disallow for `/demos/*`. Crawling is unblocked.
- Found: `aceengineer-website/package.json` — `scripts.test = jest`, multi-project Jest config. Existing JS tests under `tests/js/`. Link-check can be added as a Jest project to inherit CI.
- Found: `aceengineer-website/.github/workflows/` — directory exists but is empty. No CI runs today. Vercel integration watches pushes; Jest must be run locally or added as a workflow.
- Found: `digitalmodel/examples/demos/gtm/output/demo_0{1..5}_*_report.html` — full Plotly-embedded HTML reports. Sizes **68 KB-116 KB** (measured with `du -sh`; v1 plan's "66-118 KB" was estimated, not measured). Each source `<title>` reads "`<Demo Title>` — digitalmodel" — conflicts with site branding; plan rewrites titles on copy. Source reports reference `https://cdn.plot.ly/plotly-2.32.0.min.js` (version-pinned but no SRI).

### Standards
Not applicable — website-publishing issue.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- `docs/gtm/gtm-plan-30day.md` lines 97-108 — Week 3 cold-email Templates A/B/C link to demo GIFs and demo reports. Without live detail pages, CTAs 404.
- `docs/reports/2026-04-15-gtm-exit-summary.md` lines 17-27 — claims Demo 5 detail page went live; silent on Demos 1-4.
- `docs/reports/2026-04-15-gtm-cross-review-readiness.md` lines 40-47 — records jumper-installation.html publish; doesn't address Demos 1-4.
- Issue #2116 (closed 2026-04-15) — gallery acceptance required GIFs + "Run this on your data" CTAs; detail CTAs shipped only for Demo 5.
- Issue #1800 (closed 2026-04-10) — confirms all 5 source reports are generated and committed under `digitalmodel/`.
- `scripts/review/results/2026-04-17-plan-2342-claude.md` — v1 MAJOR verdict; 10 defects, 3 of them blocker/major. All 4 correctness-critical claims verified by file inspection in this revision.
- Codex verbal review of v1 (sandbox-blocked artifact) — MAJOR verdict: rollback missing, SRI unaddressed, TDD mixes pre/post, split vs combine question. All folded into v2.
- Memory: `feedback_codex_needs_pushed_artifact.md` (2026-04-17) — Codex sandbox cannot read local files; plan must be pushed to GitHub before re-dispatching Codex review.

### Gaps identified
- 4 new detail-page files in `content/demos/` (no `dist/` — gitignored).
- Gallery edit adds 3 new detail-report buttons (Demos 1, 3, 4) and 1 alongside Demo 2's calculator CTA.
- `jumper-installation.html` retrofit: add `<include src="partials/head-common.html"></include>` — fixes pre-existing analytics/nav gap in scope.
- 5 new `sitemap.xml` entries (4 new detail pages + 1 backfill for `jumper-installation.html`).
- `vercel.json`: add cache-control header for `/demos/*.html`.
- Vendor `plotly-2.32.0.min.js` locally under `assets/js/` to eliminate CDN supply-chain risk + obviate SRI; update all 5 detail pages (4 new + jumper retrofit) to reference local copy.
- Link-check script wired into `package.json` as a Jest project so `npm test` fires it.
- TDD split into pre-deploy local checks vs post-deploy live checks.
- Rollback runbook: single-commit revert triggers Vercel rebuild to known-good state.

### Source count
Distinct sources consulted: 12 (repo code + 4 repo-file reads + 2 issue bodies + 2 exit/review reports + 2 parent issues + memory feedback). Exceeds minimum 3 required.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` |
| New content: Demo 1 detail | `aceengineer-website/content/demos/freespan.html` |
| New content: Demo 2 detail | `aceengineer-website/content/demos/wall-thickness.html` |
| New content: Demo 3 detail | `aceengineer-website/content/demos/mudmat.html` |
| New content: Demo 4 detail | `aceengineer-website/content/demos/pipelay.html` |
| Retrofit | `aceengineer-website/content/demos/jumper-installation.html` (add head-common include; point Plotly at local vendor) |
| Gallery edit | `aceengineer-website/content/demos/index.html` |
| Sitemap | `aceengineer-website/sitemap.xml` (add 5 entries) |
| Vercel config | `aceengineer-website/vercel.json` (add `/demos/(.*).html` cache header) |
| Vendored Plotly | `aceengineer-website/assets/js/plotly-2.32.0.min.js` |
| Link-check | `aceengineer-website/tests/js/demo-links.test.js` (Jest project) |
| Plan index row | `docs/plans/README.md` |
| Plan review v2 — Claude | `scripts/review/results/2026-04-19-plan-2342-claude.md` |
| Plan review v2 — Codex | `scripts/review/results/2026-04-19-plan-2342-codex.md` |

**`dist/*` is deliberately absent from this map** — `.gitignore` excludes it; Vercel rebuilds from `content/` on push. Local `npm run build` is for verification only.

---

## Deliverable

Four demo detail pages (`freespan.html`, `wall-thickness.html`, `mudmat.html`, `pipelay.html`) live on `www.aceengineer.com/demos/`, each served with full site chrome (GA + `partials/nav.html` + `partials/footer.html`), linked from its gallery card's "View detailed report" button, indexed in `sitemap.xml`, rendered with vendored Plotly (no CDN dependency), and guarded by a Jest link-check that fails `npm test` locally if any gallery anchor 404s. (No CI workflow exists in this repo today — v4-lite Codex finding; adding a GH Actions workflow is filed as a separate follow-up.)

---

## Pseudocode

**A. Author 4 detail pages (content/demos/) — v4-lite: adds nav + footer includes**
```
for demo in [(freespan, "Freespan / VIV Screening"),
             (wall_thickness, "Pipeline Wall Thickness"),
             (mudmat, "Deepwater Mudmat Installation"),
             (pipelay, "Shallow Water Pipelay")]:
    source = digitalmodel/examples/demos/gtm/output/demo_<N>_<slug>_report.html
    target = content/demos/<slug>.html
    extract body content from <body>...</body>
    rewrite <head> to:
        ---
        rootPath: "../"
        ---
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>A&CE — <Demo Title></title>
            <include src="partials/head-common.html"></include>
            <!-- Google Fonts preserved verbatim from source -->
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <!-- original inline styles preserved -->
            <style>...source styles...</style>
            <!-- vendored Plotly (Demo pages only — jumper retrofit skips this) -->
            <script src="{{ rootPath }}assets/js/plotly-2.32.0.min.js"></script>
        </head>
        <body>
            <include src="partials/nav.html"></include>
            ...source body content...
            <include src="partials/footer.html"></include>
        </body>
```
**v4-lite correction (Codex MAJOR 1):** `head-common.html` supplies favicon/CSS/navbar-toggle JS/GA only — it does NOT contain nav markup. Site nav lives in `partials/nav.html` (verified: gallery includes BOTH at lines 26 and 249). Without `partials/nav.html`, the 4 new detail pages render as orphaned pages with no way back to the site — a direct GTM regression. Same applies to `partials/footer.html` for brand consistency.

**B. Retrofit jumper-installation.html (v3: head-common include ONLY; NO Plotly)**

The live jumper page has zero Plotly charts — it is a static HTML table-based report. Adding a 3.5 MB Plotly `<script>` tag to it would degrade performance for no functional gain.

```
in content/demos/jumper-installation.html:
    insert <include src="partials/head-common.html"></include> immediately after the opening <head> tag (before existing <style>)
    insert <include src="partials/nav.html"></include> as the first child of <body>
    insert <include src="partials/footer.html"></include> as the last child of <body>
    do NOT add the vendored Plotly script tag
    leave existing inline <style>, <title>, and body table content unchanged
```

**v4-lite correction (Codex MAJOR 1):** The jumper retrofit must ALSO add `partials/nav.html` + `partials/footer.html`, not just `head-common`. Otherwise the retrofit fixes GA but still leaves the already-live page nav-less. Commit 1 now spans three includes on one file.

This lands as **Commit 1** (see Files to Change). Commit 1 is independently revertable — if any include somehow breaks the already-live page, revert restores the pre-v3 state without touching Commit 2 content.

**C. Gallery CTA wiring**
```
in content/demos/index.html, for each demo_card lacking "View detailed report":
    add <a class="btn btn-info" href="{{ rootPath }}demos/<slug>.html">View detailed report</a>
    Demo 2 card: keep existing "Try free calculator" CTA AND add detail button alongside (flex-column on mobile)
```

**D. Sitemap update (v3: use `www.` — the redirect target, not the apex)**
```
in sitemap.xml, append 5 <url> entries using the canonical (non-redirected) host:
    https://www.aceengineer.com/demos/freespan.html
    https://www.aceengineer.com/demos/wall-thickness.html
    https://www.aceengineer.com/demos/mudmat.html
    https://www.aceengineer.com/demos/pipelay.html
    https://www.aceengineer.com/demos/jumper-installation.html  (backfill)
with lastmod=2026-04-19, changefreq=monthly, priority=0.8
```
Rationale: `vercel.json` permanently 301-redirects `aceengineer.com` → `www.aceengineer.com`. New sitemap entries at the apex would be canonically poisoned on every Googlebot fetch. Existing 20+ apex entries remain as pre-existing debt (tracked as follow-up, not this PR's scope).

**E. Vercel cache header**
```
in vercel.json "headers" array, add:
    { source: "/demos/(.*).html",
      headers: [{key: "Cache-Control", value: "public, max-age=3600, s-maxage=86400"}] }
```

**F. Vendor Plotly (v4-lite: SHA256 of the committed file, not the npm tarball)**
```
curl -fSLo assets/js/plotly-2.32.0.min.js https://cdn.plot.ly/plotly-2.32.0.min.js
sha256sum assets/js/plotly-2.32.0.min.js > assets/js/plotly-2.32.0.min.js.sha256
# record the resulting SHA256 in the commit message body for provenance
curl -fSLo assets/js/plotly-LICENSE.txt https://raw.githubusercontent.com/plotly/plotly.js/v2.32.0/LICENSE
# commit both the .min.js, its .sha256 sidecar, and the LICENSE file
```
**v4-lite correction (Codex MAJOR 3):** v3 used `npm view plotly.js-dist-min@2.32.0 dist.shasum` — that returns the **SHA1 of the npm tarball**, not the SHA256 of the browser asset we're actually committing. The integrity check must hash the committed file itself (`sha256sum assets/js/plotly-2.32.0.min.js`). The upstream BSD-3 LICENSE is vendored alongside the bundle, closing v2 Defect H as well.

**G. Link-check Jest test (v3: must also register in `package.json`)**

Create the test file:
```
tests/js/demo-links.test.js:
    parse dist/demos/index.html (after local npm run build)
    extract every href matching "demos/.*\.html"
    for each, assert file exists under dist/demos/
    expected anchor count >= 5 ("View detailed report" × 5 + calculator)
    assert sitemap.xml contains a <loc> for each demos/*.html page
    assert no href uses cdn.plot.ly (Plotly must be vendored)
```

**This file alone will NOT run under `npm test`.** `package.json` uses an explicit `jest.projects` allowlist (6 projects, one per test file). A new test file outside the registered list is silently skipped. v3 added the `package.json` entry; v4-lite fixes the environment choice and the verification command:
```
jest.projects: append
    {
      "displayName": "demo-links",
      "testEnvironment": "jsdom",
      "testMatch": ["<rootDir>/tests/js/demo-links.test.js"]
    }
```
**v4-lite correction (Codex MEDIUM 6):** `testEnvironment: jsdom` is safe for DOM parsing of `dist/demos/index.html`. v3's `node` would break if the test uses `document.querySelectorAll`.

**Verification command (v4-lite correction — Codex MEDIUM 4):** use `npx jest --selectProjects demo-links --listTests` which exits 0 iff the project is registered and points at an existing file. v3's `grep 'RUNS demo-links'` string does not match real Jest output (which uses `PASS` / `FAIL`). Acceptance criterion and TDD test `link_check_project_registered_in_npm_test` updated accordingly.

---

## Files to Change

v3 groups changes into **two commits** so rollback is clean (see Rollback Plan):

**Commit 1 of 2 — jumper retrofit (lands first, independently revertable)**

| Action | Path | Reason |
|---|---|---|
| Modify | `aceengineer-website/content/demos/jumper-installation.html` | Add 3 partial includes: `head-common.html` (first child of `<head>`, before `<style>`), `nav.html` (first child of `<body>`), `footer.html` (last child of `<body>`). Fixes pre-existing GA + nav + footer gap. **Do NOT add Plotly** — page has no charts. |
| Modify | `aceengineer-website/sitemap.xml` | Add the single `<url>` entry for `https://www.aceengineer.com/demos/jumper-installation.html` (v4-lite Claude MINOR 9 — co-locate the sitemap entry with the page it describes so Commit 2 revert doesn't orphan it). |

**Commit 2 of 2 — Demos 1-4 + infrastructure (lands after Commit 1 verified live)**

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-website/content/demos/freespan.html` | Detail page for Demo 1 |
| Create | `aceengineer-website/content/demos/wall-thickness.html` | Detail page for Demo 2 |
| Create | `aceengineer-website/content/demos/mudmat.html` | Detail page for Demo 3 |
| Create | `aceengineer-website/content/demos/pipelay.html` | Detail page for Demo 4 |
| Modify | `aceengineer-website/content/demos/index.html` | Add 3 detail CTAs (Demos 1, 3, 4); add 1 alongside Demo 2 calculator |
| Modify | `aceengineer-website/sitemap.xml` | Add 4 `<url>` entries at the www host (jumper backfill moved to Commit 1) |
| Modify | `aceengineer-website/vercel.json` | Add `/demos/(.*).html` cache-control header |
| Create | `aceengineer-website/assets/js/plotly-2.32.0.min.js` | Vendored Plotly — used ONLY by the 4 new pages (not jumper) |
| Create | `aceengineer-website/assets/js/plotly-2.32.0.min.js.sha256` | Sidecar file with the committed asset's SHA256 (v4-lite fix of Codex MAJOR 3 — integrity measured on the browser asset, not the npm tarball) |
| Create | `aceengineer-website/assets/js/plotly-LICENSE.txt` | BSD-3-Clause license text vendored alongside the bundle (closes v2 Defect H / Codex round-2 provenance finding) |
| Create | `aceengineer-website/tests/js/demo-links.test.js` | Jest link-check implementation |
| Modify | **`aceengineer-website/package.json`** | **Register `demo-links` Jest project so `npm test` actually runs the link-check (v3 fix for v2 Defect B)** |
| Update | `docs/plans/README.md` | Register v3 status |

**No `dist/*` entries** — gitignored; Vercel rebuilds from `content/`.

Rationale for two commits: if Commit 2 breaks a Plotly-heavy page, `git revert Commit2` leaves the jumper retrofit (Commit 1) intact. v2's single-PR-11-file structure couldn't do this.

---

## TDD Test List

**Pre-deploy (local, run before commit):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| frontmatter_rootPath_correct | grep / Jest | Each of 4 new pages starts with `---\nrootPath: "../"\n---` | 4/4 match |
| head_common_included | grep / Jest | Each of 4 new pages + retrofitted jumper contains `<include src="partials/head-common.html">` | 5/5 match |
| nav_and_footer_included | grep / Jest | Each of 4 new pages + retrofitted jumper contains `<include src="partials/nav.html">` AND `<include src="partials/footer.html">` (v4-lite Codex MAJOR 1 fix) | 5/5 pairs present |
| plotly_license_committed | bash | `assets/js/plotly-LICENSE.txt` exists and starts with "The MIT License" or "BSD 3-Clause" (Plotly.js is BSD-3) | 1/1 present |
| plotly_sha256_sidecar_matches | bash | `sha256sum -c assets/js/plotly-2.32.0.min.js.sha256` returns OK (v4-lite Codex MAJOR 3 fix — integrity of the committed file, not tarball) | exit 0 |
| title_is_branded | grep / Jest | Each of 4 new pages has `<title>A&CE — ...</title>`; source "— digitalmodel" removed | 4/4 match |
| plotly_is_vendored | grep / Jest | Each of 4 **new** chart-bearing pages references `{{ rootPath }}assets/js/plotly-2.32.0.min.js` and NOT `cdn.plot.ly` (jumper excluded — no charts) | 4/4 match |
| jumper_has_no_plotly_tag | grep / Jest | `content/demos/jumper-installation.html` contains no `plotly-` or `cdn.plot.ly` reference (v3 Defect E fix) | 0 hits |
| build_produces_5_files | bash + `npm run build` | `dist/demos/{freespan,wall-thickness,mudmat,pipelay,jumper-installation}.html` exist, non-empty | 5/5 files |
| gallery_has_5_detail_ctas | Jest (new `demo-links.test.js`) | `dist/demos/index.html` contains 5 anchors matching `demos/*.html` | count === 5 |
| demo2_has_both_ctas | Jest | Demo 2 card contains BOTH `/calculators/wall-thickness.html` and `/demos/wall-thickness.html` anchors | both present |
| sitemap_has_5_demo_entries | Jest | `sitemap.xml` contains 5 `<loc>` entries for `/demos/*.html` | 5/5 match |
| sitemap_uses_www_host | Jest | All entries whose `<loc>` matches `/demos/*.html` use `https://www.aceengineer.com/` host (existing apex entries at other paths are out of scope for this PR — v4-lite Claude MINOR 7 scoping fix) | all `/demos/*` entries www-hosted |
| vercel_has_demos_cache_header | Jest | `vercel.json` `headers` array contains entry for `/demos/(.*).html` | present |
| link_check_project_registered_in_npm_test | bash | `cd aceengineer-website && npx jest --selectProjects demo-links --listTests` exits 0 and prints at least one test file (v4-lite Codex MEDIUM 4 — replaces v3's unreliable `grep 'RUNS demo-links'`) | exit 0 + ≥1 test file |

**Post-deploy (live, run after Vercel finishes):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| prod_5_pages_200 | bash + curl | `https://www.aceengineer.com/demos/{freespan,wall-thickness,mudmat,pipelay,jumper-installation}.html` | all 200 |
| prod_pages_serve_analytics | curl + grep | Each of 5 pages returns HTML containing `G-K31E51DQ47` (all 5 include head-common) | 5/5 match |
| prod_pages_have_nav_and_footer | curl + grep | Each of 5 pages' HTML body contains nav + footer markers from the partials (v4-lite addition) | 5/5 match |
| prod_plotly_on_chart_pages_only | curl | The 4 chart pages reference `/assets/js/plotly-2.32.0.min.js` and NOT `cdn.plot.ly`; jumper page references neither (v4-lite Codex MEDIUM 5 fix — removes the v3 5/5 vs 4/4 contradiction) | 4/4 chart pages + 0/1 on jumper |
| prod_gallery_links_resolve | bash | Every `demos/*.html` anchor in live gallery returns 200 | 0 failures |
| prod_cache_header_on_demos | curl -I | `Cache-Control` present on `/demos/*.html` response headers | present |

**Manual (explicitly out-of-scope for automation):**

- Desktop + mobile browser visual check. Flagged as manual QA, not an automated test.

Test-writing order: pre-deploy tests first (frontmatter, head-common, title, plotly, build, gallery). Post-deploy tests run after deploy lands.

---

## Acceptance Criteria

- [ ] **Commit 1 lands first:** `content/demos/jumper-installation.html` retrofit — head-common include added; NO Plotly script tag added
- [ ] Commit 1 verified in production: live `/demos/jumper-installation.html` serves GA beacon (check DevTools Network for `gtag/js?id=G-K31E51DQ47`); nav bar + footer visible; page still renders static report identically
- [ ] Commit 1 also appended the jumper `<url>` entry to `sitemap.xml` (co-location fix, v4-lite Claude MINOR 9)
- [ ] **Commit 2 lands after Commit 1 verified:**
- [ ] `content/demos/{freespan,wall-thickness,mudmat,pipelay}.html` exist with `rootPath: "../"` frontmatter and branded `<title>A&CE — ...</title>` (source's "— digitalmodel" removed)
- [ ] All 5 detail pages include THREE partial includes: `head-common.html` (GA + CSS + favicon + navbar-toggle JS), `nav.html` (site nav bar), `footer.html` (site footer) — v4-lite Codex MAJOR 1 fix
- [ ] All 5 detail pages preserve the source's Google Fonts `<link rel="preconnect">` + Inter stylesheet (v4-lite Pseudocode A)
- [ ] **4 new chart-bearing pages** reference vendored `/assets/js/plotly-2.32.0.min.js`, not `cdn.plot.ly`. Jumper page has NO Plotly reference (v3 Defect E)
- [ ] `content/demos/index.html` has 5 "View detailed report" CTAs; Demo 2 retains calculator CTA alongside
- [ ] `sitemap.xml` has 4 new Demo-1-to-4 `<url>` entries at `https://www.aceengineer.com/` host (Commit 1 added the 5th, jumper, entry)
- [ ] `vercel.json` has cache-control header for `/demos/(.*).html`
- [ ] `assets/js/plotly-2.32.0.min.js` committed PLUS `plotly-2.32.0.min.js.sha256` sidecar matches via `sha256sum -c`; PLUS `plotly-LICENSE.txt` (BSD-3) vendored (v4-lite Codex MAJOR 3 fix — was SHA1/tarball in v3)
- [ ] `tests/js/demo-links.test.js` created AND `package.json` updated with new `jest.projects` entry for `demo-links` (v4-lite: `testEnvironment: jsdom`) — verified by `npx jest --selectProjects demo-links --listTests` exiting 0 (v4-lite Codex MEDIUM 4 — was `grep 'RUNS demo-links'` in v3)
- [ ] `npm run build` completes without error; `dist/demos/*.html` render correctly in local `npm run serve`
- [ ] Local `npm test` passes (note: there is no GitHub Actions workflow in this repo today — v4-lite Codex MAJOR 2 clarification; CI addition is filed as a separate follow-up)
- [ ] After Vercel deploy: all post-deploy tests pass (prod_5_pages_200, prod_pages_serve_analytics 5/5, prod_pages_have_nav_and_footer 5/5, prod_plotly_on_chart_pages_only 4/4 + 0/1, prod_gallery_links_resolve, prod_cache_header_on_demos)
- [ ] GA pageview beacon fires on each of 5 detail pages (verified in browser devtools Network tab, spot-check)
- [ ] #2342 and #2343 closed with links to live pages and the PR
- [ ] Review artifacts v3 + v4-lite posted to `scripts/review/results/`
- [ ] Follow-up issues filed at PR time: (a) add GH Actions workflow for `npm test`; (b) pin Node `engines` in `package.json` + `vercel.json`; (c) backfill 20+ pre-existing sitemap apex entries to `www.` host

---

## Rollback Plan

v3 splits the work into **two independently revertable commits** because repo policy is direct commits to `main` (no merge-commit umbrella) and the 11-file v2 blast radius mixed the already-live jumper page with new work. The two-commit structure means each piece can roll back without dragging the other.

**Commit 1 — jumper retrofit**  
Single file modified: `content/demos/jumper-installation.html` (add head-common include only).
- Rollback: `git revert <commit1-sha>` → push → Vercel redeploys ≤5 min.
- Blast radius: 1 file; failure can only affect the already-live `/demos/jumper-installation.html` page. If GA breaks it, revert restores pre-v3 state of that single page without touching the Commit 2 demos.

**Commit 2 — Demos 1-4 + infrastructure**  
Lands only after Commit 1's production render is verified.
- Rollback: `git revert <commit2-sha>` → push → Vercel redeploys. Removes all 4 new detail pages, gallery CTAs, sitemap entries, cache header, vendored Plotly, Jest test + project registration — **Commit 1 (jumper retrofit) stays live**.
- Blast radius: 10 files, but all net-new except gallery `index.html`, `sitemap.xml`, `vercel.json`, `package.json`. Those three modifications are additive (new entries / new keys), so revert cleanly removes only the additions.

Known-good commit to revert to:
- For Commit 1 rollback: the last commit on `aceengineer-website` `main` before Commit 1.
- For Commit 2 rollback: Commit 1.
Both SHAs captured at PR time in the PR description.

Failure modes and responses:
- **Commit 1 breaks jumper GA or renders:** `git revert <commit1-sha>`; do NOT land Commit 2.
- **Commit 2 breaks one of Demos 1-4 charts:** revert the single `content/demos/<slug>.html` change in a follow-up commit (leave other 3 live). `dist/demos/<slug>.html` regenerates from the reverted source on next Vercel build.
- **Commit 2 breaks gallery or site-wide nav:** `git revert <commit2-sha>` — demos 1-4 disappear from site but jumper retrofit remains live.
- **Jest link-check fails after Commit 2:** do NOT revert — fix forward in a follow-up commit. CI failure is louder than silently-skipped tests from v2.
- **Vercel cache poisoning on any page:** purge via Vercel dashboard or push an empty commit to trigger rebuild.
- **Vendored Plotly path 404:** verify `assets/js/plotly-2.32.0.min.js` was committed (not gitignored accidentally) and Vercel build picked it up; if not, revert Commit 2 and re-commit with the asset included.

---

## Adversarial Review Summary

### v1 (2026-04-17)
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Deploy model wrong (Vercel, not Pages); head-common absent; title contradiction; sitemap omission; link-check write-only; perf/CSP/Plotly unaddressed |
| Codex | MAJOR (artifact blocked) | Deployment assumption unproven; TDD mixes pre/post; no rollback; no SRI; combined vs split question |

**Revisions applied in v2:** deploy model corrected (Vercel + `dist/` gitignored); head-common include now mandatory (closes v1 open question Q3); title explicitly rewritten to `A&CE — X` (contradiction resolved); sitemap.xml added to Files to Change; link-check converted to Jest project; Plotly vendored locally (removes CDN/SRI/CSP exposure); TDD split into pre-deploy and post-deploy sections; rollback plan added; source sizes corrected to 68-116 KB.

### v2 (2026-04-19)
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | 8/10 v1 fixed. New defects: A sitemap host apex vs www, B Jest unwired (package.json missing from Files to Change), C rollback vs 11-file reality, D Plotly checksum unexecutable, E jumper Plotly unneeded, F Google Fonts ambiguous |
| Codex | MAJOR (artifact manually transcribed) | Agrees with A, B, C. Adds: Node/Vercel runtime not pinned (G), vendored Plotly provenance/license (H) |

**Revisions applied in v3 (this document):**
- Defect A (major): sitemap entries rewritten to `https://www.aceengineer.com/demos/*` (the redirect target); TDD gains `sitemap_uses_www_host` test.
- Defect B (major): `aceengineer-website/package.json` added to Files to Change with explicit new `jest.projects` entry; TDD gains `link_check_project_registered_in_npm_test` test that greps `npm test` output.
- Defect C (minor): split into two commits — Commit 1 = jumper retrofit (1 file), Commit 2 = Demos 1-4 + infrastructure. Each independently revertable.
- Defect E (minor): Pseudocode B now says "head-common ONLY, no Plotly" for jumper. New TDD `jumper_has_no_plotly_tag` asserts this.
- Defects D, F, G, H: accepted as known minor debt with inline mitigations — see "Known Minor Debt" section.

### v3 (2026-04-19)
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MINOR** | v3 fixes all 3 v2 majors (A sitemap www, B jest-projects wired, C rollback split). 5 new minor defects: SHA1 vs SHA256 mislabel, Jest `RUNS` grep string wrong, sitemap test scoping, head-include injection point ambiguous, commit 2 revert orphans jumper sitemap entry. Artifact: `scripts/review/results/2026-04-19-v3-plan-2342-claude.md` |
| Codex | **MAJOR** | Caught overclaim that v1/v2/v3 all missed: `head-common` does NOT include nav — nav is a separate `partials/nav.html`. Also: "fails CI" overclaim (no GH Actions workflow exists); Plotly SHA1/tarball mismatch with SHA256/browser-asset promise; post-deploy 5/5 vs 4/4 contradiction; `testEnvironment: node` unsafe for DOM parsing. Artifact: `scripts/review/results/2026-04-19-v3-plan-2342-codex.md` (manually transcribed) |

**Divergence note:** Claude MINOR vs Codex MAJOR — real divergence, not stylistic. Codex forced a fresh file-read of `partials/head-common.html` and found the nav overclaim that anchored against v2 language in Claude's review missed. Reinforces `feedback_cross_provider_review_payoff.md`.

### v4-lite (2026-04-19) — self-approved
| Fix | Provider finding | Applied inline in this document |
|---|---|---|
| Add `partials/nav.html` + `partials/footer.html` includes to 4 new pages + jumper retrofit | Codex MAJOR 1 | Pseudocode A, Pseudocode B, TDD `nav_and_footer_included`, Acceptance |
| Correct "fails CI" → "fails `npm test` locally"; file GH Actions follow-up | Codex MAJOR 2 | Deliverable, Acceptance |
| `sha256sum` of committed Plotly file + sidecar + LICENSE | Codex MAJOR 3 | Pseudocode F, Files to Change (Commit 2), TDD `plotly_sha256_sidecar_matches` + `plotly_license_committed` |
| `testEnvironment: jsdom` not `node` | Codex MEDIUM 6 | Pseudocode G |
| `npx jest --selectProjects demo-links --listTests` not `grep RUNS` | Codex MEDIUM 4 | Pseudocode G, TDD `link_check_project_registered_in_npm_test`, Acceptance |
| Post-deploy Plotly 4/4 chart pages + 0/1 jumper (resolves 5/5 vs 4/4 contradiction) | Codex MEDIUM 5 | TDD `prod_plotly_on_chart_pages_only` |
| `sitemap_uses_www_host` scoped to `/demos/*` only | Claude MINOR 7 | TDD row updated |
| Jumper sitemap entry moved to Commit 1 (co-located with page it describes) | Claude MINOR 9 | Files to Change Commit 1, Acceptance |
| Explicit injection point for jumper retrofit includes | Claude MINOR 8 | Pseudocode B (head-common before `<style>`; nav first child of body; footer last child) |
| Preserve Google Fonts `<link>` verbatim from source | Codex round 2 finding F | Pseudocode A (explicit) |

**Overall result (v4-lite):** self-approved. No round-4 review dispatched. User's call per conversation. Risk accepted: plan may still contain defects neither reviewer caught — mitigated by keeping changes behind the two-commit structure and the explicit rollback runbook.

---

## Risks and Open Questions

- **Risk: Vercel build may fail on 4 new files if posthtml can't resolve the include inside source reports' `<style>` context.** Mitigation: run `npm run build` locally before commit; fix any include resolution errors by ensuring `<include>` appears before `<style>` in `<head>`.
- **Risk: Plotly vendor at 3+ MB bloats repo size.** Mitigation: accept as cost-of-trust. Vendoring a version-pinned script once is cheaper than chasing CDN breakage across 5 pages.
- **Risk: GA `requestIdleCallback` deferral may race with Plotly chart init on slow networks.** Mitigation: head-common uses deferred GA load; Plotly script is non-async. Order by priority in `<head>`: head-common first, Plotly after. Verify in DevTools.
- **Risk: first cold-email recipient hits a still-propagating Vercel edge cache.** Mitigation: deploy at least 30 min before first send; spot-check from 2+ geographic regions.
- **Risk: Jest link-check false-positive on a transient symlink or build artifact.** Mitigation: assert against `dist/` contents only after a clean build; include a `beforeAll` that runs `npm run build`.
- **Accepted risk: inline Plotly JSON in 118 KB detail pages means no lazy-load above the fold.** Optimization tracked as follow-up — not a blocker for Week-3 GTM launch. Follow-up adds `<img>` above-fold fallback + deferred Plotly init.

**Resolved in v3:**
- ~~Open: one PR or split?~~ → resolved. Two commits in one PR (see Rollback Plan).

---

## Known Minor Debt (status after v4-lite)

| Ref | Defect | v4-lite status | Follow-up |
|---|---|---|---|
| D | Plotly SHA256 concrete | **FIXED in v4-lite:** `sha256sum assets/js/plotly-2.32.0.min.js > ...sha256` sidecar committed; TDD test `plotly_sha256_sidecar_matches` enforces integrity via `sha256sum -c`. No longer deferred. | — |
| F | Google Fonts preservation | FIXED in v3/v4-lite Pseudocode A (explicit `<link rel="preconnect">` + Inter stylesheet preservation) | — |
| G | No `engines` field in `package.json`; no Node runtime in `vercel.json` | **STILL DEFERRED** — Vercel defaults are stable and Node drift risk is low over campaign timeframe. | New follow-up issue at PR time: "pin Node engine in aceengineer-website/package.json and vercel.json" |
| H | Vendored Plotly LICENSE | **FIXED in v4-lite:** `plotly-LICENSE.txt` vendored alongside the bundle (BSD-3-Clause from Plotly 2.32.0 upstream) | — |
| CI-1 | No GH Actions workflow to run `npm test` | **STILL DEFERRED** — Codex MAJOR 2 from v3 flagged the "fails CI" overclaim; v4-lite removes the wording, but a real CI workflow would add defensive depth. | New follow-up issue at PR time: "add GH Actions workflow to run npm test on aceengineer-website PRs" |
| SITE-1 | 20+ pre-existing sitemap apex entries | **STILL DEFERRED** — v4-lite only corrects NEW entries to `www.`; backfilling existing entries is a separate scope. | New follow-up issue at PR time: "backfill existing sitemap.xml apex entries to www host" |

**Total accepted debt at self-approval:** 3 items (G, CI-1, SITE-1). All documented as follow-up issues to be filed at PR time. No single accepted item blocks a GTM prospect from landing on a live, fully-nav'd, GA-tracked page.

Follow-up issue filing is part of the PR description — not a v4-lite acceptance checkbox — to avoid blocking the merge on issue creation.

---

## Complexity: T2

Multi-file website publish + config + Jest integration + vendored asset + two-commit structure. No new Python/engineering code. v3 narrowed scope by splitting jumper retrofit into its own preceding commit; v4-lite corrected the Codex-caught nav/CI/SHA256 overclaims inline. Self-approved after three review rounds.
