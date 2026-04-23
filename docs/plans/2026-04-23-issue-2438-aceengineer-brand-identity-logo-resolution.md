# Plan for #2438: resolve AceEngineer canonical brand identity and ship real logo asset

> **Status:** draft — pending adversarial review
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2438
> **Review artifacts:** pending: `scripts/review/results/2026-04-23-plan-2438-{codex,gemini,claude}.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `aceengineer-website/content/partials/nav.html:9-14` still renders the visible brand as an inline placeholder SVG containing `A&CE`; this is not a reusable asset and conflicts with the 2026-04-21 decision that consumer-facing brand treatment is `AceEngineer`.
- Found: `aceengineer-website/content/partials/footer.html:5` still uses `A&CE` as the footer heading; the same footer keeps the long-form legal/descriptive phrase at `footer.html:33`.
- Found: `aceengineer-website/index.html:10`, `index.html:18`, and `index.html:21` still use `A&CE` in Open Graph, Twitter, and title metadata.
- Found: `aceengineer-website/index.html:54-57` declares the organization as `Analytical & Computational Engineering`, `alternateName: A&CE`, and `logo: https://aceengineer.com/assets/img/logo.png`.
- Found: `aceengineer-website/assets/img/` contains demo/sample imagery only; no `logo.svg` or `logo.png` exists, so the JSON-LD logo URL is broken.
- Found: broader generated/static pages such as `about.html` and `faq.html` contain additional `A&CE` metadata, inline nav SVGs, JSON-LD `logo.png` references, and footer headings. These may be generated from partials for some surfaces but are checked in as static files and must be audited before closeout.

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
- Static site surfaces still expose `A&CE` in visible brand, metadata, and schema.
- There is no documented brand hierarchy file in `aceengineer-website` to prevent future drift.
- There is no lightweight regression check that fails when a checked-in HTML/partial surface reintroduces the retired visible `A&CE` brand or references a missing logo path.

### Scope split

In scope for #2438:
- create canonical AceEngineer logo assets
- create a minimal brand contract document
- replace the nav/footer/homepage/blog/case-study/metadata references required to stop broken logo and retired visible `A&CE` usage
- add tests/checks that verify logo assets exist and brand hierarchy rules are respected

Out of scope for #2438:
- full Bootstrap color-token consolidation (#2439)
- visual DNA ADR beyond the already locked Option B decision (#2440)
- full redesign of aceengineer.com templates (#2435/#2436)
- digitalmodel brand changes

Implementation-surface confidence: Medium-High. The core surfaces are clear, but the exact static/generator boundary for all checked-in HTML pages must be audited during implementation.

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
| Homepage metadata/schema | `aceengineer-website/index.html` |
| Static page inventory | `aceengineer-website/**/*.html` |
| Regression tests/checks | `tests/aceengineer_website/test_brand_identity_assets.py` or equivalent repo-local test path chosen during implementation |

---

## Deliverable

A canonical AceEngineer brand identity baseline for aceengineer.com: reusable `logo.svg` + `logo.png`, documented brand hierarchy, visible site chrome and metadata aligned to `AceEngineer`/`Analytical & Computational Engineering` rules, and regression coverage preventing missing-logo or retired-`A&CE` drift.

---

## Pseudocode

```text
step 1: create brand contract
  document allowed names by context:
    visible/consumer brand -> AceEngineer
    accessibility/SEO expansion -> Analytical & Computational Engineering
    legal entity -> Achanta AceEngineer Inc.
    retired placeholder -> A&CE, do not use for new visible brand surfaces
  document visual DNA dependency:
    aceengineer.com deliberately differentiates from digitalmodel per #2440 Option B

step 2: create canonical logo assets
  design a simple text/mark SVG for AceEngineer that does not copy digitalmodel navy/teal identity
  export deterministic PNG at a web/schema-safe size
  save to assets/img/logo.svg and assets/img/logo.png

step 3: update visible chrome
  replace inline nav placeholder SVG with img/logo asset plus accessible title/alt text
  replace footer visible A&CE heading with AceEngineer

step 4: update metadata/schema surfaces
  update homepage and representative checked-in HTML pages so titles, OG/Twitter metadata, JSON-LD name/alternateName/logo follow the brand hierarchy
  keep Analytical & Computational Engineering only where long-form SEO/accessibility context is intended
  remove A&CE from visible new brand treatment unless explicitly marked as legacy/historical

step 5: add regression checks
  assert logo.svg and logo.png exist and are non-empty
  assert JSON-LD/logo references point to existing assets
  scan checked-in HTML/partials for retired visible A&CE patterns outside an allowlist
  assert nav/footer use AceEngineer-facing identity
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
| Update | `aceengineer-website/index.html` plus generated/static affected pages | fix visible metadata/schema references to align with brand hierarchy and existing logo paths |
| Create | `tests/aceengineer_website/test_brand_identity_assets.py` or nearest existing test location | regression coverage for assets, references, and retired placeholder drift |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD / Verification List

| Check | Purpose |
|---|---|
| `test_logo_assets_exist_and_are_nonempty` | fails until `assets/img/logo.svg` and `assets/img/logo.png` exist and are non-empty |
| `test_schema_logo_references_existing_asset` | parses checked-in HTML/JSON-LD references to `/assets/img/logo.png` and verifies the asset exists |
| `test_nav_footer_visible_brand_uses_aceengineer` | verifies shared chrome no longer exposes `A&CE` as the visible brand |
| `test_retired_acronym_allowlist` | scans HTML/partials for `A&CE` and allows only explicitly documented legacy or accessibility contexts, not new visible brand surfaces |
| `manual_visual_smoke_nav_logo` | open homepage and at least one nested page to confirm logo path, sizing, and contrast work in browser |

---

## Acceptance Criteria

- [ ] `aceengineer-website/assets/img/logo.svg` exists and is the canonical source logo.
- [ ] `aceengineer-website/assets/img/logo.png` exists and satisfies current JSON-LD/social image references.
- [ ] `aceengineer-website/brand/BRAND.md` documents the locked brand hierarchy and #2440 Option B differentiation from digitalmodel.
- [ ] Shared nav/footer visible brand uses `AceEngineer`, not `A&CE`.
- [ ] Homepage and affected static HTML metadata/schema references no longer point to missing logo assets.
- [ ] Regression checks fail before the assets/reference fixes and pass after implementation.
- [ ] #2439 remains the broader token/color cleanup and is not silently absorbed.
- [ ] #2440 remains the visual-DNA decision record and is not reopened by this implementation.

---

## Adversarial Review Summary

Pending. Required before `status:plan-review`.

---

## Risks and Open Questions

- Risk: PNG generation may introduce non-deterministic binary diffs. Implementation should use a stable conversion command and document it.
- Risk: checked-in static pages may duplicate partial content; implementation must update either the generator source plus generated outputs or the checked-in outputs explicitly, depending on the actual site build contract.
- Risk: overly aggressive `A&CE` scanning could flag historical/legal contexts. Use a narrow allowlist tied to `brand/BRAND.md`.
- Open: exact logo aesthetics should remain simple and production-safe; full design-system/token refinement belongs to #2439/#2435.

---

## Complexity: T2

T2 because the core change is bounded to assets, site chrome, metadata, documentation, and regression checks, but it spans multiple static surfaces and must preserve brand decisions from #2438/#2440 without absorbing #2439 token consolidation.
