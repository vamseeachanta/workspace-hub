---
phase: 03-gtm-and-marketing-aceengineer-website
plan: 02
subsystem: ui
tags: [html, posthtml, seo, pricing, navigation, landing-page]

# Dependency graph
requires:
  - phase: 03-gtm-and-marketing-aceengineer-website
    provides: "Existing site structure, PostHTML build pipeline, calculator pages"
provides:
  - "Updated site-wide navigation with Calculators link and Request Pricing CTA"
  - "Landing page value proposition with 'single source of truth' theme"
  - "Calculator showcase section highlighting 3 engineering calculators"
  - "Display-only pricing page with Free/Pro/Enterprise tiers"
  - "Footer with Pricing link and contact form with Request Pricing option"
affects: [03-gtm-and-marketing-aceengineer-website]

# Tech tracking
tech-stack:
  added: []
  patterns: [pricing-card-component, showcase-card-component, display-only-pricing-page]

key-files:
  created:
    - aceengineer-website/content/pricing.html
  modified:
    - aceengineer-website/content/partials/nav.html
    - aceengineer-website/content/partials/footer.html
    - aceengineer-website/content/contact.html
    - aceengineer-website/content/index.html

key-decisions:
  - "All pricing CTAs route to contact.html -- no payment infrastructure per D-07"
  - "Added inline CSS for showcase and pricing cards rather than modifying global stylesheet"
  - "rootPath set to empty string for pricing.html since it is at content root level"

patterns-established:
  - "pricing-card: Reusable card component with hover shadow, checkmark list, and CTA button"
  - "showcase-card: Calculator preview card with title, description, and Try Calculator CTA"

requirements-completed: [D-07, D-08, D-09, D-13, D-14]

# Metrics
duration: 6min
completed: 2026-03-26
---

# Phase 03 Plan 02: Navigation, Landing Page, and Pricing Summary

**Updated site-wide nav with Calculators link and Request Pricing CTA, redesigned landing page hero around 'single source of truth' theme with calculator showcase, and created display-only 3-tier pricing page**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-26T21:38:15Z
- **Completed:** 2026-03-26T21:44:39Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Site-wide navigation now includes Calculators link between Energy Data and Case Studies, with Request Pricing CTA replacing Get a Quote
- Landing page hero communicates "Engineering Calculations You Can Trust" value prop with "single source of truth" theme per D-13/D-14
- Calculator showcase section highlights 3 engineering tools (pipeline stability, wall thickness, fatigue life) as lead generation
- Display-only pricing page with Free/Professional/Enterprise tiers, all CTAs routing to contact.html per D-07/D-09
- Footer updated with Pricing link and contact form now includes Request Pricing subject option

## Task Commits

Each task was committed atomically:

1. **Task 1: Navigation, footer, and contact form updates** - `f6694e7` (feat)
2. **Task 2: Landing page value proposition and calculator showcase** - `c973795` (feat)
3. **Task 3: Pricing page (display-only)** - `8857b32` (feat)

## Files Created/Modified
- `aceengineer-website/content/partials/nav.html` - Added Calculators link, changed CTA to Request Pricing
- `aceengineer-website/content/partials/footer.html` - Added Pricing link to Quick Links
- `aceengineer-website/content/contact.html` - Added Request Pricing subject option
- `aceengineer-website/content/index.html` - Updated hero, meta tags, added calculator showcase section
- `aceengineer-website/content/pricing.html` - New display-only pricing page with 3 tiers

## Decisions Made
- All pricing tier CTAs route to contact.html per D-07 (consultation-based pricing, no payment infrastructure)
- Used inline `<style>` blocks for showcase and pricing card CSS rather than modifying global stylesheet (follows existing pattern in contact.html)
- Set `rootPath: ""` for pricing.html since it sits at content root level (same as index.html, contact.html)
- Added Schema.org Service type for pricing page structured data (consistent with existing JSON-LD patterns)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all data is wired and functional. Calculator showcase links point to calculator pages (some may be created by other plans in this phase).

## Next Phase Readiness
- Navigation, landing page, and pricing page are complete and building successfully
- All 110 existing tests continue to pass
- Build pipeline produces all 33 pages without errors
- Ready for Plan 03 (calculator implementations) and any remaining phase 03 plans

## Self-Check: PASSED

- All 5 files verified present (1 created, 4 modified)
- All 3 task commits verified in git log
- Build pipeline produces 33 pages without errors
- All 110 existing tests pass

---
*Phase: 03-gtm-and-marketing-aceengineer-website*
*Completed: 2026-03-26*
