# Plan for #2342 + #2343: Publish Demo Detail Pages 1-4 and Wire Gallery CTAs

> **Status:** draft (revised after 2026-04-17 adversarial review — MAJOR verdict)
> **Revision history:**
> - 2026-04-17 v1 — initial draft
> - 2026-04-19 v2 — rewritten after Claude MAJOR + Codex MAJOR: corrected Vercel deploy model, committed to `head-common` include, resolved title contradiction, added sitemap.xml updates, wired link-check to Jest, added rollback + SRI/vendoring, restructured TDD
> **Complexity:** T2
> **Issues:**
> - https://github.com/vamseeachanta/workspace-hub/issues/2342 (publish 4 detail pages)
> - https://github.com/vamseeachanta/workspace-hub/issues/2343 (wire gallery CTAs)
> **Combined rationale:** Both ship through the same `aceengineer-website` repo and the same Vercel build on push. Splitting doubles review and deploy overhead without reducing blast radius — the gallery edit is a single-line add per card, too small to warrant its own PR.
> **Review artifacts:**
> - v1: `scripts/review/results/2026-04-17-plan-2342-claude.md` (MAJOR), codex review blocked by sandbox (no artifact)
> - v2: pending — will be written to `scripts/review/results/2026-04-19-plan-2342-claude.md` and `-codex.md`

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

Four demo detail pages (`freespan.html`, `wall-thickness.html`, `mudmat.html`, `pipelay.html`) live on `www.aceengineer.com/demos/`, each served with site nav + GA, linked from its gallery card's "View detailed report" button, indexed in `sitemap.xml`, rendered with vendored Plotly (no CDN dependency), and guarded by a Jest link-check that fails CI if any gallery anchor 404s.

---

## Pseudocode

**A. Author 4 detail pages (content/demos/)**
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
            <!-- original inline styles preserved -->
            <style>...source styles...</style>
            <!-- vendored Plotly -->
            <script src="{{ rootPath }}assets/js/plotly-2.32.0.min.js"></script>
        </head>
        <body>...source body...</body>
```

**B. Retrofit jumper-installation.html**
Same head rewrite + Plotly vendor point, single atomic commit. Closes the pre-existing analytics gap.

**C. Gallery CTA wiring**
```
in content/demos/index.html, for each demo_card lacking "View detailed report":
    add <a class="btn btn-info" href="{{ rootPath }}demos/<slug>.html">View detailed report</a>
    Demo 2 card: keep existing "Try free calculator" CTA AND add detail button alongside (flex-column on mobile)
```

**D. Sitemap update**
```
in sitemap.xml, append 5 <url> entries:
    https://aceengineer.com/demos/freespan.html
    https://aceengineer.com/demos/wall-thickness.html
    https://aceengineer.com/demos/mudmat.html
    https://aceengineer.com/demos/pipelay.html
    https://aceengineer.com/demos/jumper-installation.html  (backfill)
with lastmod=2026-04-19, changefreq=monthly, priority=0.8
```

**E. Vercel cache header**
```
in vercel.json "headers" array, add:
    { source: "/demos/(.*).html",
      headers: [{key: "Cache-Control", value: "public, max-age=3600, s-maxage=86400"}] }
```

**F. Vendor Plotly**
```
curl -o assets/js/plotly-2.32.0.min.js https://cdn.plot.ly/plotly-2.32.0.min.js
verify checksum against upstream release
commit as binary asset
```

**G. Link-check Jest test**
```
tests/js/demo-links.test.js:
    parse dist/demos/index.html (after local npm run build)
    extract every href matching "demos/.*\.html"
    for each, assert file exists under dist/demos/
    expected anchor count >= 5 ("View detailed report" × 5 + calculator)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-website/content/demos/freespan.html` | Detail page for Demo 1 |
| Create | `aceengineer-website/content/demos/wall-thickness.html` | Detail page for Demo 2 |
| Create | `aceengineer-website/content/demos/mudmat.html` | Detail page for Demo 3 |
| Create | `aceengineer-website/content/demos/pipelay.html` | Detail page for Demo 4 |
| Modify | `aceengineer-website/content/demos/jumper-installation.html` | Add head-common include; swap CDN Plotly → local vendor |
| Modify | `aceengineer-website/content/demos/index.html` | Add 3 detail CTAs (Demos 1, 3, 4); add 1 alongside Demo 2 calculator |
| Modify | `aceengineer-website/sitemap.xml` | Add 5 `<url>` entries (4 new + jumper backfill) |
| Modify | `aceengineer-website/vercel.json` | Add `/demos/(.*).html` cache-control header |
| Create | `aceengineer-website/assets/js/plotly-2.32.0.min.js` | Vendored Plotly — eliminates CDN + SRI concerns |
| Create | `aceengineer-website/tests/js/demo-links.test.js` | Jest link-check, picked up by existing `jest` test command |
| Update | `docs/plans/README.md` | Register v2 status |

**No `dist/*` entries** — gitignored; Vercel rebuilds from `content/`.

---

## TDD Test List

**Pre-deploy (local, run before commit):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| frontmatter_rootPath_correct | grep / Jest | Each of 4 new pages starts with `---\nrootPath: "../"\n---` | 4/4 match |
| head_common_included | grep / Jest | Each of 4 new pages + retrofitted jumper contains `<include src="partials/head-common.html">` | 5/5 match |
| title_is_branded | grep / Jest | Each of 4 new pages has `<title>A&CE — ...</title>`; source "— digitalmodel" removed | 4/4 match |
| plotly_is_vendored | grep / Jest | Each of 5 detail pages references `{{ rootPath }}assets/js/plotly-2.32.0.min.js` and NOT `cdn.plot.ly` | 5/5 match |
| build_produces_5_files | bash + `npm run build` | `dist/demos/{freespan,wall-thickness,mudmat,pipelay,jumper-installation}.html` exist, non-empty | 5/5 files |
| gallery_has_5_detail_ctas | Jest (new `demo-links.test.js`) | `dist/demos/index.html` contains 5 anchors matching `demos/*.html` | count === 5 |
| demo2_has_both_ctas | Jest | Demo 2 card contains BOTH `/calculators/wall-thickness.html` and `/demos/wall-thickness.html` anchors | both present |
| sitemap_has_5_demo_entries | Jest | `sitemap.xml` contains 5 `<loc>` entries for `/demos/*.html` | 5/5 match |
| vercel_has_demos_cache_header | Jest | `vercel.json` `headers` array contains entry for `/demos/(.*).html` | present |

**Post-deploy (live, run after Vercel finishes):**

| Test | Tool | Claim | Pass criterion |
|---|---|---|---|
| prod_5_pages_200 | bash + curl | `https://www.aceengineer.com/demos/{freespan,wall-thickness,mudmat,pipelay,jumper-installation}.html` | all 200 |
| prod_pages_serve_analytics | curl + grep | Each returns HTML containing `G-K31E51DQ47` | 5/5 match |
| prod_plotly_loads_locally | curl | Each page body contains `/assets/js/plotly-2.32.0.min.js`, not `cdn.plot.ly` | 5/5 match |
| prod_gallery_links_resolve | bash | Every `demos/*.html` anchor in live gallery returns 200 | 0 failures |
| prod_cache_header_on_demos | curl -I | `Cache-Control` present on `/demos/*.html` response headers | present |

**Manual (explicitly out-of-scope for automation):**

- Desktop + mobile browser visual check. Flagged as manual QA, not an automated test.

Test-writing order: pre-deploy tests first (frontmatter, head-common, title, plotly, build, gallery). Post-deploy tests run after deploy lands.

---

## Acceptance Criteria

- [ ] `content/demos/{freespan,wall-thickness,mudmat,pipelay}.html` exist with correct frontmatter and branded `<title>`
- [ ] All 5 detail pages (4 new + retrofitted jumper) include `<include src="partials/head-common.html">` → GA + nav present
- [ ] All 5 detail pages reference vendored `/assets/js/plotly-2.32.0.min.js`, not `cdn.plot.ly`
- [ ] `content/demos/index.html` has 5 "View detailed report" CTAs; Demo 2 retains calculator CTA alongside
- [ ] `sitemap.xml` has 5 new `<url>` entries (4 new + jumper backfill)
- [ ] `vercel.json` has cache-control header for `/demos/(.*).html`
- [ ] `assets/js/plotly-2.32.0.min.js` committed with checksum-verified content
- [ ] `tests/js/demo-links.test.js` Jest project passes locally via `npm test`
- [ ] `npm run build` completes without error; `dist/demos/*.html` render correctly in local `npm run serve`
- [ ] After Vercel deploy: all 9 post-deploy tests pass
- [ ] GA pageview beacon fires on each detail page (verified in browser devtools Network tab for one page, spot-check)
- [ ] #2342 and #2343 closed with links to live pages and the PR
- [ ] Review artifacts v2 posted to `scripts/review/results/`

---

## Rollback Plan

Vercel rebuilds from git state on every push. Rollback = `git revert <merge-commit>` → push → Vercel redeploys prior state automatically (~2-5 min). No database, no migrations, no external state.

Known-good commit to revert to: last green commit on `aceengineer-website` main before this plan's merge (captured at PR time).

Failure modes and responses:
- **Charts broken on one page:** revert the single `content/demos/<slug>.html` change; leave other 3 live.
- **GA not firing:** `head-common` include syntax issue; revert the include line, investigate locally.
- **Gallery card broken:** single-line revert on `content/demos/index.html`.
- **Vercel cache poisoning:** purge via Vercel dashboard or push an empty commit.

---

## Adversarial Review Summary

### v1 (2026-04-17)
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Deploy model wrong (Vercel, not Pages); head-common absent; title contradiction; sitemap omission; link-check write-only; perf/CSP/Plotly unaddressed |
| Codex | MAJOR (artifact blocked) | Deployment assumption unproven; TDD mixes pre/post; no rollback; no SRI; combined vs split question |

**Revisions applied in v2:** deploy model corrected (Vercel + `dist/` gitignored); head-common include now mandatory (closes v1 open question Q3); title explicitly rewritten to `A&CE — X` (contradiction resolved); sitemap.xml added to Files to Change; link-check converted to Jest project; Plotly vendored locally (removes CDN/SRI/CSP exposure); TDD split into pre-deploy and post-deploy sections; rollback plan added; source sizes corrected to 68-116 KB.

### v2 (pending)
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |

**Overall result (v2):** pending

---

## Risks and Open Questions

- **Risk: Vercel build may fail on 4 new files if posthtml can't resolve the include inside source reports' `<style>` context.** Mitigation: run `npm run build` locally before commit; fix any include resolution errors by ensuring `<include>` appears before `<style>` in `<head>`.
- **Risk: Plotly vendor at 3+ MB bloats repo size.** Mitigation: accept as cost-of-trust. Vendoring a version-pinned script once is cheaper than chasing CDN breakage across 5 pages.
- **Risk: GA `requestIdleCallback` deferral may race with Plotly chart init on slow networks.** Mitigation: head-common uses deferred GA load; Plotly script is non-async. Order by priority in `<head>`: head-common first, Plotly after. Verify in DevTools.
- **Risk: first cold-email recipient hits a still-propagating Vercel edge cache.** Mitigation: deploy at least 30 min before first send; spot-check from 2+ geographic regions.
- **Risk: Jest link-check false-positive on a transient symlink or build artifact.** Mitigation: assert against `dist/` contents only after a clean build; include a `beforeAll` that runs `npm run build`.
- **Accepted risk: inline Plotly JSON in 118 KB detail pages means no lazy-load above the fold.** Optimization tracked as a follow-up issue (ticket TBD) — not a v1 blocker. GTM campaign launches with full-weight pages; follow-up adds `<img>` above-fold fallback + deferred Plotly init.
- **Open (for user): should this ship as one PR or split into (a) "publish 4 detail pages + retrofit jumper + vendor Plotly" and (b) "gallery CTAs + sitemap + vercel cache"?** Recommended: ship as one PR — the two halves are mutually dependent for a coherent user flow (gallery link + live target), and split-PR review overhead exceeds the blast-radius benefit. But splittable cleanly if the reviewer disagrees.

---

## Complexity: T2

Multi-file website publish + config + Jest integration + vendored asset. No new Python/engineering code. Scope intentionally widened in v2 to cover the pre-existing `jumper-installation.html` analytics gap — doing it in the same commit is cheaper than a separate issue, and catches the latent sitemap defect.
