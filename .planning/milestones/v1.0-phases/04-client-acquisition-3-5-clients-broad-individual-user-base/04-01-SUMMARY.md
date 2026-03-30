---
phase: 04-client-acquisition-3-5-clients-broad-individual-user-base
plan: 01
subsystem: content
tags: [case-study, html, schema.org, seo, dnv-rp-f109, asme-b31.4, api-1111, dnv-st-f101, ga4]

# Dependency graph
requires:
  - phase: 03-gtm-and-marketing-aceengineer-website
    provides: "Calculator pages (OBS, wall thickness), PostHTML build system, GA4 tracking, existing case study pattern"
provides:
  - "Pipeline OBS case study page with Schema.org, OG tags, GA4, CTA"
  - "Multi-code wall thickness case study page with Schema.org, OG tags, GA4, CTA"
  - "Updated case study index with 8 entries"
  - "Updated sitemap with 2 new case study URLs"
affects: [04-02, 04-03, enterprise-funnel]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BreadcrumbList JSON-LD schema on case study pages"
    - "case_study_view GA4 event with referrer_type classification"
    - "info-section CTA pattern with btn-success primary and btn-default secondary"

key-files:
  created:
    - "aceengineer-website/content/case-studies/pipeline-on-bottom-stability-assessment.html"
    - "aceengineer-website/content/case-studies/multi-code-wall-thickness-comparison.html"
  modified:
    - "aceengineer-website/content/case-studies/index.html"
    - "aceengineer-website/sitemap.xml"

key-decisions:
  - "Added BreadcrumbList JSON-LD to new case studies (not present in existing ones) per plan spec"
  - "Used indexOf instead of includes for browser compat in GA4 referrer detection"
  - "Removed Subsea Pipeline Integrity from coming-soon list since pipeline stability is now covered"

patterns-established:
  - "Case study CTA: info-section with btn-success to contact + btn-default to paired calculator"
  - "GA4 case_study_view event fires on DOMContentLoaded with typeof gtag guard"

requirements-completed: [D-04, D-08, D-09, D-12]

# Metrics
duration: 7min
completed: 2026-03-27
---

# Phase 04 Plan 01: Case Studies Summary

**2 engineering case studies (pipeline OBS + multi-code wall thickness) with Schema.org markup, GA4 tracking, calculator cross-links, and enterprise CTA funnel**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-27T06:03:19Z
- **Completed:** 2026-03-27T06:10:22Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Created pipeline on-bottom stability assessment case study with DNV-RP-F109 methodology, 60% time reduction narrative, and CTA linking to OBS calculator
- Created multi-code wall thickness comparison case study covering ASME B31.4 vs API 1111 vs DNV-ST-F101 with cross-over effect finding and $1.2M savings narrative
- Updated case study index to 8 entries with metrics cards and compliance tags, updated sitemap with both new URLs

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Pipeline OBS Assessment case study** - `7370d16` (feat)
2. **Task 2: Create Multi-Code Wall Thickness Comparison case study** - `f6b4cb6` (feat)
3. **Task 3: Update case study index and sitemap** - `de2479f` (feat)

## Files Created/Modified
- `aceengineer-website/content/case-studies/pipeline-on-bottom-stability-assessment.html` - OBS case study with Schema.org Article + BreadcrumbList, OG tags, GA4 event, CTA to contact and OBS calculator
- `aceengineer-website/content/case-studies/multi-code-wall-thickness-comparison.html` - Wall thickness case study with Schema.org Article + BreadcrumbList, OG tags, GA4 event, CTA to contact and WT calculator
- `aceengineer-website/content/case-studies/index.html` - Added 2 new case study cards (8 total), removed Subsea Pipeline Integrity from coming-soon
- `aceengineer-website/sitemap.xml` - Added 2 new case study URLs with 2026-03-26 lastmod

## Decisions Made
- Added BreadcrumbList JSON-LD to new case studies (existing case studies do not have it) per plan specification -- enhances SEO for new pages
- Used `indexOf` instead of `includes` for browser compatibility in the GA4 referrer_type detection, consistent with Phase 3 established `var`-based pattern
- Removed "Subsea Pipeline Integrity" from the coming-soon section since pipeline on-bottom stability now covers this topic area

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - both case studies contain complete content, all CTAs link to existing pages (contact form, calculators), and GA4 tracking is wired to the existing gtag infrastructure.

## Next Phase Readiness
- Case studies ready for enterprise funnel: calculator -> case study -> contact form
- Both new pages build successfully (36 total pages) and all 118 tests pass
- Index page now shows 8 case studies with consistent card format
- Sitemap updated for search engine discovery

## Self-Check: PASSED

All files verified present, all 3 commits confirmed in git log.

---
*Phase: 04-client-acquisition-3-5-clients-broad-individual-user-base*
*Completed: 2026-03-27*
