---
phase: 04-client-acquisition-3-5-clients-broad-individual-user-base
plan: 02
subsystem: analytics
tags: [ga4, gtag, web3forms, contact-form, cta-tracking, bootstrap3]

# Dependency graph
requires:
  - phase: 03-gtm-marketing
    provides: Calculator pages, contact form, pricing page, GA4 integration
provides:
  - Contact form project type selector with 7 analysis type options
  - GA4 cta_click events on all 5 calculator page CTA buttons
  - GA4 pricing_cta_click events on all pricing page CTA buttons
  - Enhanced calculator_use events with input_count on 3 calculator pages
  - GA4 contact_project_type event on project type selection
affects: [04-client-acquisition-3-5-clients-broad-individual-user-base]

# Tech tracking
tech-stack:
  added: []
  patterns: [inline onclick GA4 event handlers with typeof gtag guard, sessionCalculationCount for input tracking]

key-files:
  created: []
  modified:
    - aceengineer-website/content/contact.html
    - aceengineer-website/content/calculators/on-bottom-stability.html
    - aceengineer-website/content/calculators/wall-thickness.html
    - aceengineer-website/content/calculators/fatigue-life-calculator.html
    - aceengineer-website/content/calculators/fatigue-sn-curve.html
    - aceengineer-website/content/calculators/npv-field-development.html
    - aceengineer-website/content/pricing.html

key-decisions:
  - "Used var throughout new JS code for browser compatibility matching existing codebase pattern"
  - "All GA4 event calls guarded with typeof gtag !== undefined to prevent errors when analytics blocked"
  - "Added typeof gtag guard to fatigue-life calculator_use event that was missing it (Rule 1 bug fix)"
  - "Added pricing_cta_click tracking to bottom CTA in addition to 3 tier CTAs"

patterns-established:
  - "CTA click tracking: inline onclick with typeof gtag guard firing cta_click event"
  - "Session calculation counting: var sessionCalculationCount incremented before gtag call"
  - "Pricing tier tracking: pricing_cta_click event with tier_clicked parameter"

requirements-completed: [D-02, D-05, D-06, D-10, D-12, D-14, D-15]

# Metrics
duration: 5min
completed: 2026-03-27
---

# Phase 04 Plan 02: Contact Form Enhancement and GA4 CTA Tracking Summary

**Project type selector on contact form with 7 options, cta_click events on all 5 calculator pages, pricing_cta_click events on pricing page, and input_count session tracking on 3 calculator pages**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-27T06:02:50Z
- **Completed:** 2026-03-27T06:08:23Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Contact form enhanced with project type selector (Pipeline Stability, Wall Thickness, Fatigue Assessment, Riser/Mooring, Full Engineering Study, Data/Analytics, Other) that web3forms delivers automatically in submission emails
- GA4 cta_click events fire on all 5 calculator page "Discuss Your Project" CTA buttons with calculator_name, cta_location, and page_type parameters
- GA4 pricing_cta_click events fire on all 4 pricing page CTA buttons with tier_clicked parameter (free, professional, enterprise, general)
- Enhanced calculator_use events with sessionCalculationCount-based input_count on OBS, wall-thickness, and fatigue-life calculator pages
- GA4 contact_project_type event fires when user selects a project type on the contact form

## Task Commits

Each task was committed atomically:

1. **Task 1: Add project type selector to contact form and enhanced GA4 events** - `a813cf2` (feat)
2. **Task 2: Add GA4 CTA click tracking and enhanced calculator_use events to all calculator pages** - `f0e198d` (feat)

## Files Created/Modified
- `aceengineer-website/content/contact.html` - Added project type select field, contact_project_type GA4 event, enhanced form submission tracking with project_type parameter, URL parameter support for project_type
- `aceengineer-website/content/calculators/on-bottom-stability.html` - Added cta_click onclick handler on CTA, sessionCalculationCount with input_count in calculator_use event, ?vertical=offshore on CTA href
- `aceengineer-website/content/calculators/wall-thickness.html` - Added cta_click onclick handler on CTA, sessionCalculationCount with input_count in calculator_use event, ?vertical=offshore on CTA href
- `aceengineer-website/content/calculators/fatigue-life-calculator.html` - Added cta_click onclick handler on CTA, sessionCalculationCount with input_count in calculator_use event, typeof gtag guard added to calculator_use event, ?vertical=fatigue on CTA href
- `aceengineer-website/content/calculators/fatigue-sn-curve.html` - Added cta_click onclick handler on CTA
- `aceengineer-website/content/calculators/npv-field-development.html` - Added cta_click onclick handler on CTA
- `aceengineer-website/content/pricing.html` - Added pricing_cta_click onclick handlers on all 4 CTA buttons (free, professional, enterprise tiers + bottom CTA)

## Decisions Made
- Used `var` throughout new JavaScript code for browser compatibility, matching existing codebase pattern (no const/let in new code)
- All new GA4 event calls guarded with `typeof gtag !== 'undefined'` to prevent errors when analytics is blocked by ad blockers
- Added typeof gtag guard to the existing fatigue-life calculator_use event that was missing it (auto-fixed, Rule 1)
- Added pricing_cta_click tracking to the bottom "Discuss Your Project" CTA on pricing page in addition to the 3 tier-specific CTAs, using tier_clicked='general' to distinguish it

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added missing typeof gtag guard on fatigue-life calculator_use event**
- **Found during:** Task 2 (fatigue-life-calculator.html editing)
- **Issue:** The existing calculator_use gtag call at line 594 had no typeof gtag guard, which would throw an error if gtag is not loaded
- **Fix:** Wrapped the existing gtag call in `if (typeof gtag !== 'undefined')` guard
- **Files modified:** aceengineer-website/content/calculators/fatigue-life-calculator.html
- **Verification:** Build passes, tests pass
- **Committed in:** f0e198d (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Minor fix for consistency and error prevention. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required. Note: For GA4 custom event parameters to appear in standard reports (not just Realtime), the following custom dimensions should be registered in GA4 Admin > Custom definitions: project_type, calculator_name, cta_text, cta_location, page_type, tier_clicked, input_count.

## Known Stubs
None - all data sources are wired (web3forms receives project_type field automatically, GA4 receives all custom events via gtag).

## Next Phase Readiness
- Contact form project type data will flow into web3forms email submissions immediately on deployment
- GA4 events are instrumented and will fire on production once deployed
- Custom dimensions need manual registration in GA4 Admin console for full reporting (see User Setup Required)
- Ready for Plan 03 (case studies and pipeline setup)

---
*Phase: 04-client-acquisition-3-5-clients-broad-individual-user-base*
*Completed: 2026-03-27*

## Self-Check: PASSED

- All 7 modified files exist
- Both commit hashes verified (a813cf2, f0e198d)
- SUMMARY.md created
