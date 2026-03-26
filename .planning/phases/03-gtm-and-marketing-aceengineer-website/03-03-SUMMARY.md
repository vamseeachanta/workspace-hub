---
phase: 03-gtm-and-marketing-aceengineer-website
plan: 03
subsystem: ui
tags: [html, plotly, calculator, dnv-rp-f109, asme-b31.4, seo, schema-org, ga4]

requires:
  - phase: 03-gtm-and-marketing-aceengineer-website
    plan: 01
    provides: "obs-calculator-engine.js and wall-thickness-engine.js"
  - phase: 03-gtm-and-marketing-aceengineer-website
    plan: 02
    provides: "Landing page, pricing page, navigation updates"
provides:
  - "On-bottom stability calculator HTML page with DNV-RP-F109 method"
  - "Wall thickness calculator HTML page with ASME B31.4 burst/collapse checks"
  - "Updated calculator index with 5 entries and Schema.org ItemList"
  - "Updated sitemap with new calculator and pricing URLs"
affects: [aceengineer-website, seo, calculator-suite]

tech-stack:
  added: [plotly-2.27.0]
  patterns: [calculator-page-template, ga4-event-tracking, schema-org-webapplication]

key-files:
  created:
    - "aceengineer-website/content/calculators/on-bottom-stability.html"
    - "aceengineer-website/content/calculators/wall-thickness.html"
  modified:
    - "aceengineer-website/content/calculators/index.html"
    - "aceengineer-website/sitemap.xml"

key-decisions:
  - "Followed exact fatigue-life-calculator.html template pattern for consistency"
  - "Added green/red zone fills on OBS velocity sweep chart for visual clarity"
  - "Removed Coming Soon placeholder cards in favor of actual new calculators"

patterns-established:
  - "Calculator page pattern: PostHTML front matter, Schema.org WebApplication, Plotly charts, GA4 tracking, D-06 disclaimer, consulting CTA"

requirements-completed: [D-01, D-02, D-03, D-04, D-05, D-06, D-10, D-11, D-12]

duration: 17min
completed: 2026-03-26
---

# Phase 03 Plan 03: Calculator Pages Summary

**Two interactive calculator HTML pages (OBS + wall thickness) with Plotly charts, GA4 tracking, Schema.org SEO, and updated index listing 5 calculators**

## Performance

- **Duration:** 17 min (7 min auto tasks + 10 min checkpoint verification)
- **Started:** 2026-03-26T21:40:35Z
- **Completed:** 2026-03-26T21:57:06Z
- **Tasks:** 4/4 (3 auto + 1 checkpoint verified)
- **Files modified:** 4

## Accomplishments

- Created 524-line on-bottom stability calculator page with 13 inputs, velocity sweep chart, and DNV-RP-F109 SEO content
- Created 492-line wall thickness calculator page with 9 inputs, burst/collapse bar chart, and ASME B31.4 SEO content
- Updated calculator index to list all 5 calculators with Schema.org ItemList (positions 1-5) and removed Coming Soon placeholders
- Updated sitemap with 3 new URLs (OBS, wall thickness, pricing)
- Full build passes (34 pages), all 118 tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: On-bottom stability calculator page** - `5ad7bda` (feat)
2. **Task 2: Wall thickness calculator page** - `33e9d84` (feat)
3. **Task 3: Calculator index update and sitemap** - `0f72959` (feat)
4. **Task 4: Visual and functional verification** - user approved (checkpoint)

## Files Created/Modified

- `aceengineer-website/content/calculators/on-bottom-stability.html` - OBS calculator with 13 form inputs, Plotly velocity sweep, GA4 tracking
- `aceengineer-website/content/calculators/wall-thickness.html` - Wall thickness calculator with 9 inputs, burst/collapse checks, bar chart
- `aceengineer-website/content/calculators/index.html` - Updated with 2 new cards, 5-item Schema.org ItemList, new standards
- `aceengineer-website/sitemap.xml` - Added OBS, wall thickness, and pricing URLs

## Decisions Made

- Followed fatigue-life-calculator.html template exactly for structural consistency
- Added green/red zone background fills on OBS chart for immediate visual pass/fail indication
- Removed Coming Soon cards (SCF and Pressure Vessel) since they are now replaced by actual pipeline calculators
- Wrapped GA4 calls in `typeof gtag !== 'undefined'` guard to prevent errors when GA not loaded

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- JS engine files (obs-calculator-engine.js, wall-thickness-engine.js) do not yet exist in the aceengineer-website repo, as Plan 01 runs in parallel. The HTML pages reference them via script tags and will be functional once Plan 01 commits are merged.

## Known Stubs

- `on-bottom-stability.html` references `obs-calculator-engine.js` which is created by Plan 03-01 (parallel execution)
- `wall-thickness.html` references `wall-thickness-engine.js` which is created by Plan 03-01 (parallel execution)

Both stubs are intentional: the engine JS files are delivered by a dependency plan running concurrently. Once Plan 01 completes, calculators will be fully functional.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Task 4 visual/functional verification approved by user
- Once Plan 01 engines are merged, calculators are fully production-ready
- Build and test suite both pass with all 118 tests
- Plan 03-03 complete; remaining Phase 03 plans (01, 02) run in parallel

## Self-Check: PASSED

- FOUND: `.planning/phases/03-gtm-and-marketing-aceengineer-website/03-03-SUMMARY.md`
- FOUND: Cherry-picked commit `4e692335` (original: `f6f5ca3d`) containing all task work
- Note: Individual task hashes (5ad7bda, 33e9d84, 0f72959) were from original execution agent's worktree branch; consolidated in docs commit f6f5ca3d
- User verification: approved at checkpoint

---
*Phase: 03-gtm-and-marketing-aceengineer-website*
*Completed: 2026-03-26*
