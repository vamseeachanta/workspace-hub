---
phase: 04-client-acquisition-3-5-clients-broad-individual-user-base
plan: 03
subsystem: funnel
tags: [enterprise-funnel, ga4, scroll-tracking, github-issues, prospect-pipeline, cta-wiring]

# Dependency graph
requires:
  - phase: 04-01
    provides: "2 new case study pages (pipeline OBS, multi-code wall thickness) with CTAs"
  - phase: 04-02
    provides: "Calculator CTA buttons with cta_click tracking, contact form with project type selector"
provides:
  - "Calculator CTAs linked to specific matched case studies (not generic index)"
  - "Scroll depth tracking at 25/50/75/100% on both new case study pages"
  - "funnel_step GA4 events tracking calculator-to-case-study navigation"
  - "GitHub Issues prospect pipeline with 5 stage labels + 3 type labels + template issue"
affects: [client-outreach, ga4-reporting, enterprise-funnel-analytics]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "funnel_step GA4 event for cross-page navigation tracking"
    - "Scroll depth tracking with threshold-based firing (25/50/75/100%)"
    - "GitHub Issues label-based pipeline: pipeline:contacted -> responded -> pilot -> client -> lost"

key-files:
  created: []
  modified:
    - "aceengineer-website/content/calculators/on-bottom-stability.html"
    - "aceengineer-website/content/calculators/wall-thickness.html"
    - "aceengineer-website/content/case-studies/pipeline-on-bottom-stability-assessment.html"
    - "aceengineer-website/content/case-studies/multi-code-wall-thickness-comparison.html"

key-decisions:
  - "Used funnel_step event (not cta_click) for calculator-to-case-study links to distinguish funnel progression from generic CTA clicks"
  - "Scroll tracking uses var and default (non-passive) scroll listener for browser compat"
  - "GitHub Issues pipeline in workspace-hub repo (private) rather than separate tool"

patterns-established:
  - "Enterprise funnel flow: calculator -> specific case study -> contact form"
  - "Scroll depth tracking: threshold array with fired map, case_study_scroll event"
  - "Prospect pipeline: GitHub Issues with pipeline:* and type:* label taxonomy"

requirements-completed: [D-01, D-03, D-07, D-09, D-11, D-13, D-16]

# Metrics
duration: 5min
completed: 2026-03-27
---

# Phase 04 Plan 03: Enterprise Funnel Wiring and Prospect Pipeline Summary

**Calculator CTAs wired to specific case studies with funnel_step tracking, scroll depth analytics on case study pages, and GitHub Issues prospect pipeline with 8 labels**

## Performance

- **Duration:** 5 min (execution across checkpoint)
- **Started:** 2026-03-27T06:12:33Z
- **Completed:** 2026-03-28T03:30:00Z
- **Tasks:** 3 (2 auto + 1 human-verify checkpoint)
- **Files modified:** 4

## Accomplishments
- Wired OBS calculator secondary CTA to the specific pipeline OBS case study (replacing generic case-studies index link) with funnel_step GA4 event tracking the calculator-to-case-study navigation
- Wired wall thickness calculator secondary CTA to the specific multi-code wall thickness case study with funnel_step GA4 event
- Added scroll depth tracking to both new case study pages firing case_study_scroll at 25%, 50%, 75%, 100% thresholds with case_study_name parameter
- Created GitHub Issues prospect pipeline with 5 stage labels (contacted, responded, pilot, client, lost), 3 type labels (consultancy, operator, individual), and template issue #1465
- User verified complete enterprise funnel flow: calculator -> case study -> contact form

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire calculator CTAs to specific case studies and add scroll depth tracking** - `f1b43a3` (feat, aceengineer-website)
2. **Task 2: Set up GitHub Issues prospect pipeline with labels and issue template** - GitHub API only (no file commit; 5 pipeline labels + 3 type labels + issue #1465 created via gh CLI)
3. **Task 3: Verify enterprise funnel and GA4 tracking** - Checkpoint: human-verify (approved)

## Files Created/Modified
- `aceengineer-website/content/calculators/on-bottom-stability.html` - Secondary CTA updated from generic case-studies/ to specific pipeline-on-bottom-stability-assessment.html, added funnel_step GA4 event
- `aceengineer-website/content/calculators/wall-thickness.html` - Secondary CTA updated from generic case-studies/ to specific multi-code-wall-thickness-comparison.html, added funnel_step GA4 event
- `aceengineer-website/content/case-studies/pipeline-on-bottom-stability-assessment.html` - Added scroll depth tracking script (case_study_scroll at 25/50/75/100%)
- `aceengineer-website/content/case-studies/multi-code-wall-thickness-comparison.html` - Added scroll depth tracking script (case_study_scroll at 25/50/75/100%)

## GitHub Resources Created
- 5 pipeline stage labels: pipeline:contacted, pipeline:responded, pipeline:pilot, pipeline:client, pipeline:lost
- 3 prospect type labels: type:consultancy, type:operator, type:individual
- Template issue #1465: "[Template] Prospect - [Company Name] - [Contact Name]"

## Decisions Made
- Used `funnel_step` as the GA4 event name for calculator-to-case-study links (distinct from `cta_click` used for generic CTA tracking) to enable funnel analysis in GA4
- Scroll tracking uses `var` (not const/let) throughout, matching existing codebase browser compatibility pattern
- Used default (non-passive) scroll listener since the handler does not call preventDefault() -- passive would also work but default is simpler and the handler is lightweight
- GitHub Issues pipeline placed in workspace-hub repo (private) since it already hosts planning data and is the natural home for prospect tracking

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required

**GA4 Custom Dimensions:** Register 8 event-scoped custom dimensions in GA4 Admin > Custom definitions for full reporting:
1. cta_text (from cta_click event)
2. cta_location (from cta_click event)
3. page_type (from cta_click event)
4. calculator_name (from cta_click, calculator_use events)
5. case_study_name (from case_study_view, case_study_scroll events)
6. project_type (from contact_project_type, contact_form_submission events)
7. percent_scrolled (from case_study_scroll event)
8. input_count (from calculator_use event)

Note: Events will appear in GA4 Realtime immediately. Custom dimensions need registration for standard reports and explorations.

## Known Stubs
None - all CTAs link to real pages, scroll tracking fires real GA4 events, and GitHub Issues pipeline is operational.

## Next Phase Readiness
- Complete enterprise funnel operational: calculator -> specific case study -> contact form
- GA4 event taxonomy covers full user journey (page views, calculator use, CTA clicks, funnel steps, scroll depth, contact form submission)
- Prospect pipeline ready for manual outreach tracking via GitHub Issues
- Phase 04 complete (all 3 plans done)
- Site builds successfully (36 pages) and all 118 tests pass

## Self-Check: PASSED

- All 4 modified files exist in aceengineer-website
- Commit f1b43a3 verified in aceengineer-website git log
- 5 pipeline labels and 3 type labels confirmed via gh CLI
- Template issue #1465 confirmed

---
*Phase: 04-client-acquisition-3-5-clients-broad-individual-user-base*
*Completed: 2026-03-27*
