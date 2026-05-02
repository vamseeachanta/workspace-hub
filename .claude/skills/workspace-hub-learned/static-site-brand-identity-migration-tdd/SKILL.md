---
name: static-site-brand-identity-migration-tdd
description: Execute approved static-site brand identity/logo migrations with TDD across canonical content sources, generated deploy output, legacy checked-in HTML, existing stale tests, and build/docs contracts.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [static-site, frontend, branding, tdd, build-output, legacy-html, aceengineer]
---

# Static Site Brand Identity Migration TDD

Use when implementing an approved issue that changes a static site's canonical brand/logo identity, especially when the repo has:
- canonical source HTML under `content/**`
- generated deploy output under `dist/**`
- checked-in legacy/root HTML outside both source and deploy output
- existing tests that may read legacy/root pages
- metadata/schema/social references to logo or brand names

## Core lesson

Do not trust a clean canonical-source migration alone. A brand identity issue can still be wrong if:
- tests keep reading stale root/legacy HTML and pass by accident
- generated `dist/**` is not rebuilt/verified
- checked-in legacy HTML outside `content/**` and `dist/**` preserves retired visible branding
- existing tests still assert the old brand
- docs still describe the wrong source-of-truth contract

## Execution pattern

1. Confirm execution gate first
   - live issue has `status:plan-approved`
   - local `.planning/plan-approved/<issue>.md` exists in the checkout used for writes
   - commit the marker before implementation if hooks require it

2. Map the site contract before tests
   - read build script, e.g. `build.js`
   - read deploy config, e.g. `vercel.json`
   - identify canonical source, generated output, assets, and legacy checked-in pages
   - inspect test paths to see whether existing tests read `content/**`, `dist/**`, or root legacy files

3. TDD first
   - add a failing brand regression test before implementation
   - test at least:
     - logo assets exist and are non-empty
     - nav/footer use approved visible brand and accessible logo text
     - canonical source pages do not use retired brand in visible/chrome/title/metadata/schema contexts
     - built `dist/**` does not use retired brand after build
     - legacy checked-in HTML outside source/output does not preserve retired visible identity if tests/workflows read it
     - existing old-brand tests no longer require retired branding
   - run the targeted test and verify RED before implementation

4. Implement minimally
   - add canonical `assets/img/logo.svg`
   - add deterministic `assets/img/logo.png` or document the conversion command if generated externally
   - add a brand contract doc, e.g. `brand/BRAND.md`
   - update canonical source partials/pages under `content/**`
   - update or sync legacy checked-in HTML outside `content/**` and `dist/**` if tests or workflows still read it
   - update existing tests that encode the old brand, not just new tests
   - update README/deployment docs if they describe root HTML as authoritative while deploy actually serves generated output

5. Build and validate
   - run `npm run build` or equivalent
   - run targeted brand tests
   - run nearby existing tests that were touched
   - run broader Python/JS test suites when feasible
   - search for retired brand strings in `content/**/*.html`, `dist/**/*.html`, and checked-in legacy HTML

6. Adversarial review before commit
   - specifically ask reviewer to check for false confidence from tests reading stale legacy/root files
   - ask whether any old tests still pass by accepting long-form legacy strings instead of the new visible brand
   - ask whether generated output and legacy checked-in output are both covered or deliberately excluded

## Pitfalls caught live

- Updating `content/**` and building `dist/**` was not enough because existing tests still read root checked-in HTML.
- Loosening old tests to accept `Analytical` let stale root pages pass without proving the new `AceEngineer` visible brand.
- A reviewer found that checked-in HTML outside `content/**` and `dist/**` included root pages plus `blog/**`, `calculators/**`, `case-studies/**`, `demos/**`, `samples/**`, etc.; the plan had originally named only root `*.html`.
- A new Jest file may not run if `package.json` uses explicit `testMatch`; extend an existing matched JS test or update `package.json` deliberately.
- Broad markdown/template docs can still contain historical retired brand strings; decide whether they are in scope or future cleanup rather than silently absorbing them.

## Suggested regression test structure

For Python static checks:
- place tests under the repo's existing pytest tree, e.g. `tests/python/test_brand_identity_assets.py`
- define helpers for:
  - canonical source HTML: `content/**/*.html`
  - generated deploy output: `dist/**/*.html`
  - legacy checked-in HTML outside `content/**`, `dist/**`, `node_modules`, `.git`
- scan only identity contexts to avoid brittle prose checks:
  - visible chrome
  - headings / body labels / CTAs
  - page titles
  - OG/Twitter metadata
  - JSON-LD/schema identity fields such as `alternateName`

## Validation bundle example

```bash
npm run build
uv run pytest tests/python/test_brand_identity_assets.py tests/python/test_wrk146_positioning.py -q
uv run pytest tests/python -q
npm test -- --runInBand
```

## Closeout evidence to capture

- RED test failure before implementation
- build command and result
- targeted brand test result
- existing test suite result
- JS/build test result if applicable
- adversarial review verdict after fixes
- commit hash and push status
