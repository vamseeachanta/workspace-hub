# Plan for #2342 + #2343: Publish Demo Detail Pages 1-4 and Wire Gallery CTAs

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issues:**
> - https://github.com/vamseeachanta/workspace-hub/issues/2342 (publish 4 detail pages)
> - https://github.com/vamseeachanta/workspace-hub/issues/2343 (wire gallery CTAs)
> **Combined rationale:** Both ship through the same `aceengineer-website` repo and deploy; splitting would double review and deploy overhead without reducing risk.
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2342-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `aceengineer-website/content/demos/jumper-installation.html` (91 lines) — reference pattern for a detail page. Uses YAML frontmatter `rootPath: "../"`, self-contained inline `<style>`, no partial includes.
- Found: `aceengineer-website/content/demos/index.html` (468 lines) — gallery with 5 `.demo-card` blocks at lines 290/310/330/350/370. Only Demo 5 (line 383) has the `View detailed report` CTA. Demo 2 has a `Try free calculator` CTA at line 323. Demos 1/3/4 have no detail-level CTA.
- Found: `aceengineer-website/build.js` — posthtml pipeline that processes `content/` → `dist/`, skips files under `partials/`, parses YAML frontmatter for `rootPath`, applies `posthtml-include` for partials and `posthtml-expressions` for templating.
- Found: `digitalmodel/examples/demos/gtm/output/demo_0{1..5}_*_report.html` — full Plotly-embedded HTML reports. Sizes 66 KB–118 KB. Each has `<!DOCTYPE html><html lang="en"><head>` with `<title>`; they are standalone documents with no include directives, so the build step will pass them through unchanged.
- Gap: four of the five detail pages (`freespan.html`, `wall-thickness.html`, `mudmat.html`, `pipelay.html`) do not exist under `content/demos/` or `dist/demos/`.
- Gap: gallery cards for Demos 1, 3, 4 have no `View detailed report` CTA; Demo 2 has a calculator CTA instead of a detail CTA.

### Standards
Not applicable — this is a website-publishing issue, not an engineering standard implementation.

### LLM Wiki pages consulted
No relevant wiki pages — content is GTM collateral, not engineering knowledge.

### Documents consulted
- `docs/gtm/gtm-plan-30day.md` lines 97-108 — Week 3 "Email Campaign — Tier 1" sends Template A with `[Link to relevant demo GIF]` and detailed follow-up (Template B) attaches `[relevant demo PDF]`. Cold emails will link to these detail pages. If pages 404, open rate and response rate collapse.
- `docs/reports/2026-04-15-gtm-exit-summary.md` lines 17-27 — exit summary claims "detailed Demo 5 page now live" and methodology pages published; silent on Demos 1-4.
- `docs/reports/2026-04-15-gtm-cross-review-readiness.md` lines 40-47 — records that `jumper-installation.html` was added to both source and dist; no mention of the other four demos.
- Issue #2116 (closed 2026-04-15) — acceptance required embedding GIFs in all 5 cards with "Run this on your data" CTA. "View detailed report" was added only for Demo 5.
- Issue #1800 (closed 2026-04-10) — umbrella for all 5 demo HTML reports. Confirms reports were generated and committed under `digitalmodel/examples/demos/gtm/output/`.
- Parent deploy mechanism: `aceengineer-website/CNAME` = `aceengineer.com`. No `.github/workflows/` dir. Deploy is GitHub Pages on push to main with `dist/` served. Verified 2026-04-17 by live 200 on `www.aceengineer.com/methodology/*`.

### Gaps identified
- 4 detail page HTML files to author in `content/demos/` and mirror to `dist/demos/`
- Gallery index must gain 3 new `View detailed report` buttons (Demos 1, 3, 4) and 1 additional button alongside the existing calculator CTA for Demo 2
- No regression test exists that verifies gallery-link targets return 200 — should be added to avoid recurrence

Source count: 8 distinct sources (issue body × 2 + 6 others) ✓

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` |
| New content | `aceengineer-website/content/demos/freespan.html` |
| New content | `aceengineer-website/content/demos/wall-thickness.html` |
| New content | `aceengineer-website/content/demos/mudmat.html` |
| New content | `aceengineer-website/content/demos/pipelay.html` |
| Built output | `aceengineer-website/dist/demos/{freespan,wall-thickness,mudmat,pipelay}.html` |
| Gallery edit | `aceengineer-website/content/demos/index.html` |
| Gallery built | `aceengineer-website/dist/demos/index.html` |
| Link-check script | `aceengineer-website/scripts/check-demo-links.sh` |
| Plan index row | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2342-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2342-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2342-gemini.md` |

---

## Deliverable

Four demo detail pages (`freespan.html`, `wall-thickness.html`, `mudmat.html`, `pipelay.html`) live on `www.aceengineer.com/demos/`, each linked from its gallery card's "View detailed report" button, verified by an automated link-check that will run on future PRs.

---

## Pseudocode

Two workstreams:

**A. Publish 4 detail pages**
```
for demo in [freespan, wall_thickness, mudmat, pipelay]:
    source   = digitalmodel/examples/demos/gtm/output/demo_<N>_<demo>_report.html
    target   = aceengineer-website/content/demos/<slug>.html
    prepend YAML frontmatter: 'rootPath: "../"'
    copy remainder of source verbatim
    ensure <title> tag reads "A&CE — <Demo Title>" for brand consistency
run `node build.js` to regenerate dist/
verify dist/demos/<slug>.html exists and matches content version semantically
```

**B. Wire gallery CTAs**
```
in content/demos/index.html, for each demo_card lacking "View detailed report":
    add <a class="btn btn-info" href="{{ rootPath }}demos/<slug>.html">View detailed report</a>
    for Demo 2: keep existing "Try free calculator" CTA; add the detail button alongside
run `node build.js`
verify 5 detail-report anchors exist in dist/demos/index.html
```

**C. Link-check script (new)**
```
for each anchor in dist/demos/index.html matching href="demos/...":
    curl -s -o /dev/null -w "%{http_code}\n" $anchor
    assert 200
exit non-zero if any fail
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-website/content/demos/freespan.html` | Detail page for Demo 1 |
| Create | `aceengineer-website/content/demos/wall-thickness.html` | Detail page for Demo 2 |
| Create | `aceengineer-website/content/demos/mudmat.html` | Detail page for Demo 3 |
| Create | `aceengineer-website/content/demos/pipelay.html` | Detail page for Demo 4 |
| Modify | `aceengineer-website/content/demos/index.html` | Add 3 detail CTAs (Demos 1, 3, 4); add 1 additional CTA alongside Demo 2's calculator |
| Build | `aceengineer-website/dist/demos/*` | Regenerate via `node build.js` |
| Create | `aceengineer-website/scripts/check-demo-links.sh` | Link-check regression guard |
| Update | `docs/plans/README.md` | Register this plan in index table |
| Commit | `aceengineer-website/` | Push to main triggers GitHub Pages deploy |

---

## TDD Test List

This issue class is website publishing, not a pytest module. Tests here are HTTP + DOM assertions.

| Test | Tool | What it verifies | Pass criterion |
|---|---|---|---|
| local_build_produces_4_files | bash | `node build.js` creates `dist/demos/{freespan,wall-thickness,mudmat,pipelay}.html` | All 4 files exist, non-empty |
| local_dist_titles_match_source | grep | Each dist page `<title>` matches "A&CE — `<Demo Title>`" | 4/4 titles correct |
| local_gallery_has_5_detail_anchors | grep | `dist/demos/index.html` contains 5 `demos/*.html` anchors | Count ≥ 5 |
| local_demo2_has_both_ctas | grep | Demo 2 card contains BOTH calculator and detail-report anchors | Both present |
| prod_4_pages_200 | curl | `https://www.aceengineer.com/demos/{freespan,wall-thickness,mudmat,pipelay}.html` | All return HTTP 200 after deploy |
| prod_gallery_links_resolve | `scripts/check-demo-links.sh` | Every `demos/*.html` anchor in live gallery returns 200 | Script exits 0 |
| browser_manual_mobile | manual | Page renders on mobile viewport, Plotly charts interactive | Visual pass |

Write tests before implementation in this order: local_build_produces_4_files, local_gallery_has_5_detail_anchors, prod_4_pages_200, prod_gallery_links_resolve.

---

## Acceptance Criteria

- [ ] `content/demos/{freespan,wall-thickness,mudmat,pipelay}.html` exist with correct frontmatter and `<title>`
- [ ] `dist/demos/{freespan,wall-thickness,mudmat,pipelay}.html` regenerated via `node build.js`
- [ ] Gallery `content/demos/index.html` has 5 `View detailed report` buttons total (one per card)
- [ ] Demo 2 card retains its `Try free calculator` CTA alongside the new detail button
- [ ] After deploy: all 4 URLs return HTTP 200 on `https://www.aceengineer.com`
- [ ] `scripts/check-demo-links.sh` committed and exits 0 locally against the built `dist/`
- [ ] Browser validation: desktop + mobile, Plotly charts interactive
- [ ] #2342 and #2343 closed with links to live pages
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled after Step 3. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk: detail pages are large and may be slow on mobile.** Demo 1's source HTML is 118 KB with Plotly CDN. Options: (a) publish verbatim and accept size, (b) defer Plotly to lazy-load, (c) produce a stripped summary page like `jumper-installation.html` (91 lines) linking to a downloadable full report. **Recommendation:** ship verbatim first (fast path), open a follow-up issue for size optimization if analytics show bounce.
- **Risk: source HTML reports reference remote CDN `cdn.plot.ly` — offline or CSP policy on aceengineer.com may break charts.** Verify CSP headers before deploy; if blocked, vendor Plotly locally under `assets/js/`.
- **Risk: GitHub Pages deploy latency after push to main (typically 2-10 min).** Add an explicit deploy-verify step in the runbook; do not mark issues closed until `curl` returns 200.
- **Open: should the 4 new pages include the same nav/header as `jumper-installation.html` (which is stripped) or the full gallery header?** `jumper-installation.html` is bare; methodology pages use the full partials header. Pick one and apply consistently.
- **Open: Demo 2 has a "Try free calculator" CTA pointing to `/calculators/wall-thickness.html`. Confirm that calculator page exists and still works, since a detail page added alongside a broken calculator looks incoherent.**
- **Open: is there a CSP or analytics snippet that every published page must carry?** `build.js` uses `posthtml-include` for `partials/head-common.html` — the 4 new pages should include it for SEO/analytics parity.
- **Dependency to flag:** this plan depends on N3 (capability-summary PDF, #2344) only indirectly. If PDF link is added to detail pages, sequence N3 first; otherwise parallel.

---

## Complexity: T2

Standard multi-file website publish, combined with gallery edit. No new Python/engineering code. Two workstreams (detail pages + gallery CTAs) that share deploy and test infrastructure, hence the combined plan.
