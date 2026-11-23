# Plan for #2438: resolve AceEngineer canonical brand identity and ship real logo asset

> **Status:** plan-review — ready for user approval review; not approved for implementation
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2438
> **Review artifacts:** `scripts/review/results/2026-04-23-plan-2438-review-1.md` (REQUEST_CHANGES) | `scripts/review/results/2026-04-23-plan-2438-review-2.md` (REQUEST_CHANGES) | `scripts/review/results/2026-04-23-plan-2438-r2-review-1.md` (REQUEST_CHANGES) | `scripts/review/results/2026-04-23-plan-2438-r2-review-2.md` (REQUEST_CHANGES) | `scripts/review/results/2026-04-23-plan-2438-r3-final-review.md` (MINOR)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `aceengineer-website/content/partials/nav.html:9-14` still renders the visible brand as an inline placeholder SVG containing `A&CE`; this is not a reusable asset and conflicts with the 2026-04-21 decision that consumer-facing brand treatment is `AceEngineer`.
- Found: `aceengineer-website/build.js` renders `content/` into `dist/`, and `aceengineer-website/vercel.json` deploys `dist/`; therefore canonical implementation must edit `content/**`/partials/assets, run the build, and verify generated `dist/**`. Existing Python tests and docs also read/describe checked-in root/legacy HTML directly, so implementation must either sync all checked-in non-`content/**`/non-`dist/**` HTML surfaces or update the test/build/docs contract to declare them non-authoritative.
- Found: `aceengineer-website/content/partials/footer.html:5` still uses `A&CE` as the footer heading; the same footer keeps the long-form legal/descriptive phrase at `footer.html:33`.
- Found: `aceengineer-website/index.html:10`, `index.html:18`, and `index.html:21` still use `A&CE` in Open Graph, Twitter, and title metadata.
- Found: `aceengineer-website/index.html:54-57` declares the organization as `Analytical & Computational Engineering`, `alternateName: A&CE`, and `logo: https://aceengineer.com/assets/img/logo.png`.
- Found: `aceengineer-website/assets/img/` contains demo/sample imagery only; no `logo.svg` or `logo.png` exists, so the JSON-LD logo URL is broken.
- Found: broader source/generated/static pages such as `content/about.html`, `content/faq.html`, root `about.html`/`faq.html`, and generated `dist/**` contain additional `A&CE` metadata, inline nav SVGs, JSON-LD `logo.png` references, footer headings, and visible consumer-facing body labels. Reviewer inspection found the footprint spans calculators, demos, methodology, blog, case studies, pricing, 404, FAQ, and legacy checked-in directories such as `blog/**`, `calculators/**`, `case-studies/**`, `demos/**`, and `samples/**`; existing `aceengineer-website/tests/python/test_wrk146_positioning.py` still asserts retired `A&CE`/long-form branding on root pages, so tests must be updated along with the brand contract.

### Issue / decision history

- Issue #2438 records the original bug: no canonical logo asset and conflicting treatments (`Achanta AceEngineer Inc.`, `AceEngineer`, `Analytical & Computational Engineering`, `A&CE`).
- Issue #2438 comment `2026-04-21T18:49:55Z` locks the naming hierarchy:
  - consumer-facing: `AceEngineer`
  - SEO/accessibility: `Analytical & Computational Engineering`
  - legal/contractual: `Achanta AceEngineer Inc.`
  - placeholder/historical: `A&CE`, retired for new work
- Issue #2440 comment `2026-04-21T18:49:44Z` locks visual DNA Option B: deliberately differentiate aceengineer.com from digitalmodel. Therefore this issue must not copy digitalmodel's navy/teal logo identity.
- Issue #2439 remains a separate broader Bootstrap/token consolidation issue; #2438 should create the canonical logo and fix brand identity surfaces needed for that logo, not attempt full color-token consolidation.

### Gaps

- No canonical AceEngineer logo source asset exists.
- No raster logo exists for JSON-LD/social consumers that require PNG.
- Static site surfaces still expose `A&CE` in visible brand, consumer-facing body labels, metadata, and schema across `content/**`, generated `dist/**`, root checked-in HTML, and legacy checked-in HTML directories outside both source and deploy output.
- There is no documented brand hierarchy file in `aceengineer-website` to prevent future drift.
- There is no lightweight regression check that fails when a checked-in HTML/partial surface reintroduces the retired visible `A&CE` brand or references a missing logo path; existing positioning tests also encode the old brand and must be revised.

### Scope split

In scope for #2438:
- create canonical AceEngineer logo assets
- create a minimal brand contract document
- replace visible brand/chrome/page-title/consumer-facing label/metadata/schema references across deployable `content/**` surfaces required to stop broken logo and retired visible `A&CE` usage; then rebuild and verify `dist/**`
- add/update tests/checks in the existing repo harness that verify logo assets exist, generated output references them correctly, old `A&CE` expectations are removed, and brand hierarchy rules are respected

Out of scope for #2438:
- full Bootstrap color-token consolidation (#2439); only minimal logo sizing/contrast CSS needed to render the canonical asset is in scope
- visual DNA ADR beyond the already locked Option B decision (#2440)
- full redesign of aceengineer.com templates (#2435/#2436)
- digitalmodel brand changes

Implementation-surface confidence: High after r2 plan tightening. The plan now explicitly covers the `content/` -> `dist/` build contract, the root/legacy checked-in HTML disposition, and the visible brand/body-label/metadata/schema scope that caused review blockers.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2438-aceengineer-brand-identity-logo-resolution.md` |
| Canonical SVG logo | `aceengineer-website/assets/img/logo.svg` |
| Raster logo for schema/social | `aceengineer-website/assets/img/logo.png` |
| Brand contract | `aceengineer-website/brand/BRAND.md` |
| Visible nav source | `aceengineer-website/content/partials/nav.html` |
| Visible footer source | `aceengineer-website/content/partials/footer.html` |
| Source page inventory | `aceengineer-website/content/**/*.html` |
| Generated deploy output | `aceengineer-website/dist/**/*.html` after `npm run build` |
| Legacy checked-in HTML outside source/deploy output | `aceengineer-website/*.html`, `aceengineer-website/blog/**/*.html`, `aceengineer-website/calculators/**/*.html`, `aceengineer-website/case-studies/**/*.html`, `aceengineer-website/demos/**/*.html`, `aceengineer-website/samples/**/*.html`, and any other checked-in HTML outside `content/**` and `dist/**` — must either be synced by implementation or explicitly excluded with updated tests/build contract; do not silently ignore because existing tests may read root/legacy pages |
| Existing build script | `aceengineer-website/build.js` |
| Existing deploy config | `aceengineer-website/vercel.json` |
| New regression tests/checks | `aceengineer-website/tests/python/test_brand_identity_assets.py` and/or an existing configured JS test file such as `aceengineer-website/tests/js/build.test.js` unless package.json is updated for a new Jest test |
| Existing tests requiring update | `aceengineer-website/tests/python/test_wrk146_positioning.py` and any other test asserting retired `A&CE` root-page branding |
| Build/deploy docs requiring update if root/legacy HTML is declared non-authoritative | `aceengineer-website/README.md`, `aceengineer-website/VERCEL_DEPLOY.md`, `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md`, `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` |

---

## Deliverable

A canonical AceEngineer brand identity baseline for aceengineer.com: reusable `logo.svg` + deterministic `logo.png`, documented brand hierarchy/allowlist, canonical `content/**` site chrome, visible consumer-facing labels, page titles, metadata, and schema aligned to `AceEngineer`/`Analytical & Computational Engineering` rules, generated `dist/**` verified after build, legacy checked-in HTML disposition resolved, and regression coverage preventing missing-logo or retired visible `A&CE` drift.

---

## Pseudocode

```text
step 1: create brand contract
  document allowed names by context and explicit allowlist:
    visible/chrome/consumer brand -> AceEngineer
    accessibility expansion, org description, selected schema name -> Analytical & Computational Engineering
    legal/copyright/contractual entity -> Achanta AceEngineer Inc. where a legal entity is required
    retired placeholder -> A&CE forbidden in visible chrome, page titles, OG/Twitter titles, schema alternateName, and consumer-facing body labels/headings such as contact forms, 404 links, case-study service labels, and CTAs unless a historical prose mention is explicitly allowlisted
  document visual DNA dependency:
    aceengineer.com deliberately differentiates from digitalmodel per #2440 Option B

step 2: create canonical logo assets
  design a simple text/mark SVG for AceEngineer that does not copy digitalmodel navy/teal identity
  export deterministic PNG at a documented web/schema-safe size using a recorded conversion command
  save to assets/img/logo.svg and assets/img/logo.png

step 3: update visible chrome
  replace inline nav placeholder SVG with img/logo asset plus accessible title/alt text
  replace footer visible A&CE heading with AceEngineer

step 4: update metadata/schema surfaces
  update canonical content/**/*.html sources and shared partials so visible brand labels/headings, titles, OG/Twitter metadata, JSON-LD name/alternateName/logo follow the brand hierarchy
  run the site build and verify generated dist/**/*.html matches the new identity
  keep Analytical & Computational Engineering only in the documented SEO/accessibility/schema allowlist
  remove A&CE from visible brand/chrome/page-title/consumer-facing body-label/OG/Twitter/schema surfaces unless explicitly marked as historical prose

step 5: resolve legacy checked-in HTML and old-test disposition
  either sync checked-in HTML outside content/** and dist/** where current tests/readers still depend on it
  or update tests/docs to declare those files non-authoritative and exclude them from brand identity scans
  update existing tests that assert old A&CE/root-page branding, especially tests/python/test_wrk146_positioning.py
  if adding JS tests, either extend an existing Jest test matched by package.json or update package.json testMatch deliberately

step 6: add regression checks
  assert logo.svg and logo.png exist and are non-empty
  assert JSON-LD/logo references point to existing assets in both source and built output
  scan content/partials, generated dist HTML, and any synced legacy HTML for retired visible A&CE patterns outside a precise allowlist
  assert nav/footer use AceEngineer-facing identity and accessible image text
  assert nested generated pages resolve logo paths correctly
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-website/assets/img/logo.svg` | canonical source logo asset |
| Create | `aceengineer-website/assets/img/logo.png` | raster logo for JSON-LD/social consumers |
| Create | `aceengineer-website/brand/BRAND.md` | durable brand hierarchy and Option B visual-DNA note |
| Update | `aceengineer-website/content/partials/nav.html` | replace inline `A&CE` placeholder with reusable asset and accessible brand text |
| Update | `aceengineer-website/content/partials/footer.html` | replace visible `A&CE` footer heading with `AceEngineer` |
| Update | `aceengineer-website/content/**/*.html` and shared partials | canonical source edits for visible/chrome/body-label/metadata/schema identity surfaces |
| Generate/verify | `aceengineer-website/dist/**/*.html` | deploy output must reflect the source changes after `npm run build` |
| Decide/sync or contract-update | checked-in HTML outside `content/**` and `dist/**`, including root `*.html`, `blog/**`, `calculators/**`, `case-studies/**`, `demos/**`, `samples/**` | either sync if current tests/workflows still read these pages, or update tests/docs to mark them non-authoritative and exclude them deliberately |
| Create | `aceengineer-website/tests/python/test_brand_identity_assets.py` | regression coverage for assets, source references, allowlist, and generated-output checks |
| Update | `aceengineer-website/tests/python/test_wrk146_positioning.py` | remove/replace old assertions that require retired `A&CE` root-page branding |
| Optional JS coverage | extend `aceengineer-website/tests/js/build.test.js` or update `package.json` testMatch before adding a new JS test file | avoid an unrun `tests/js/brand-identity.test.js` because Jest currently uses explicit testMatch entries |
| Conditional update | `aceengineer-website/README.md`, `VERCEL_DEPLOY.md`, `docs/WEBSITE_ARCHITECTURE.md`, `docs/DEPLOYMENT_GUIDE.md` | required if implementation declares root/legacy HTML non-authoritative rather than syncing it |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD / Verification List

| Check | Purpose |
|---|---|
| `test_logo_assets_exist_and_are_nonempty` | fails until `assets/img/logo.svg` and `assets/img/logo.png` exist and are non-empty |
| `test_schema_logo_references_existing_asset` | parses checked-in HTML/JSON-LD references to `/assets/img/logo.png` and verifies the asset exists |
| `test_existing_positioning_brand_expectations_updated` | updates existing positioning tests so they assert the locked `AceEngineer`/long-form/legal hierarchy instead of requiring retired `A&CE` branding |
| `test_nav_footer_visible_brand_uses_aceengineer` | verifies shared chrome no longer exposes `A&CE` as the visible brand and logo image has correct accessible text |
| `test_retired_acronym_allowlist` | scans visible chrome, page titles, consumer-facing body labels/headings/CTAs, OG/Twitter metadata, and JSON-LD schema contexts for `A&CE`, using a precise allowlist rather than arbitrary body-prose matching |
| `test_build_output_brand_identity` | runs or consumes `npm run build` output and verifies `dist/**` has copied logo assets, correct nested logo paths, and no forbidden visible/chrome/body-label/metadata/schema drift |
| `manual_visual_smoke_nav_logo` | open homepage and at least one nested page from built output to confirm logo path, sizing, and contrast work in browser |

---

## Acceptance Criteria

- [ ] `aceengineer-website/assets/img/logo.svg` exists and is the canonical source logo.
- [ ] `aceengineer-website/assets/img/logo.png` exists and satisfies current JSON-LD/social image references.
- [ ] `aceengineer-website/brand/BRAND.md` documents the locked brand hierarchy and #2440 Option B differentiation from digitalmodel.
- [ ] Shared nav/footer visible brand uses `AceEngineer`, not `A&CE`, and exposes correct logo alt/accessible text.
- [ ] Canonical `content/**` sources and generated `dist/**` visible brand/body-label/metadata/schema references no longer point to missing logo assets or retired visible `A&CE` brand surfaces.
- [ ] `npm run build` succeeds and regression checks fail before the assets/reference fixes and pass after implementation.
- [ ] Existing tests that require retired `A&CE` branding, especially `tests/python/test_wrk146_positioning.py`, are updated to the new hierarchy.
- [ ] Checked-in HTML outside `content/**` and `dist/**` is either synchronized for brand identity or explicitly declared non-authoritative with tests/docs updated so it cannot create false pass/fail ambiguity.
- [ ] If new JS brand tests are added, they are included by the existing Jest configuration or `package.json` is deliberately updated.
- [ ] #2439 remains the broader token/color cleanup and is not silently absorbed.
- [ ] #2440 remains the visual-DNA decision record and is not reopened by this implementation.

---

## Adversarial Review Summary

Delegated adversarial review r1 returned REQUEST_CHANGES. Revisions applied: source-of-truth/build contract, explicit source/dist/root surface split, exact test locations, site-wide visible/chrome/metadata/schema scope, allowlist policy, deterministic PNG command requirement, dist verification, nested path/accessibility checks, and minimal-CSS scope guardrail.

Fresh r2 delegated re-review returned REQUEST_CHANGES for two remaining blockers: (1) root/legacy checked-in HTML handling was still too narrow despite tests reading root pages, and (2) visible in-page `A&CE` consumer-facing body labels were outside the proposed scan scope. This plan resolves both by expanding the legacy checked-in HTML disposition to all non-`content/**`/non-`dist/**` HTML directories and expanding the brand cleanup/test scope to visible consumer-facing labels/headings/CTAs in addition to chrome, titles, metadata, and schema.

Final r3 consistency check returned MINOR only. It found no remaining blocker-level issue after the plan added explicit updates to existing tests (`tests/python/test_wrk146_positioning.py`) and conditional docs/contract surfaces. Residual note: broader markdown/template docs may still contain retired `A&CE` references, but those are outside this bounded site chrome/content/output/tests/docs-contract plan. Ready for `status:plan-review`; execution remains blocked until user approval.

---

## Risks and Open Questions

- Risk: PNG generation may introduce non-deterministic binary diffs. Implementation should use a stable conversion command and document it.
- Risk: checked-in legacy static pages outside `content/**`/`dist/**` may duplicate generated content; implementation must update canonical `content/**` sources, regenerate/verify `dist/**`, and explicitly either sync all checked-in legacy HTML surfaces that current tests/workflows read or update tests/docs to mark them non-authoritative.
- Risk: overly aggressive `A&CE` scanning could flag historical/legal prose. Limit automated checks to visible chrome, page titles, consumer-facing body labels/headings/CTAs, OG/Twitter metadata, JSON-LD/schema identity fields, and a narrow allowlist tied to `brand/BRAND.md`.
- Open: exact logo aesthetics should remain simple and production-safe; full design-system/token refinement belongs to #2439/#2435.

---

## Complexity: T2

T2 because the core change is bounded to assets, site chrome, metadata, documentation, and regression checks, but it spans multiple static surfaces and must preserve brand decisions from #2438/#2440 without absorbing #2439 token consolidation.
