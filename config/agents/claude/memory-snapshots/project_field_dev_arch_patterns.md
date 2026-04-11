---
name: Field-dev architecture patterns (#2058)
description: Architecture pattern analytics added to field_development; new module and normalize aliases
type: project
originSessionId: ca73fd20-2b86-4256-9c02-83a2d9c418fd
---
Architecture pattern benchmark analytics for #2058 are fully implemented and pushed.

**Why:** Extension of #1861 SubseaIQ scaffold to add richer segmented analytics.

**How to apply:** If touching architecture_patterns.py or normalize.py flowline/layout aliases, the foundation is solid — extend rather than rewrite.

## State
- `digitalmodel`: `architecture_patterns.py` (4 functions) live on main @ `de2625aa`
- `worldenergydata`: `normalize.py` flowline/layout aliases live on main @ `2d9dbe2`
- Tests: 77 passed in digitalmodel field_development suite
- Follow-up issues: #2082 (sparse tests), #2084 (regional segmentation), #2086 (year validation)

## Key design decisions
- All 4 analytics functions skip None fields silently — no inference
- `tieback_stats_segmented` returns `by_depth_band` + `by_fluid_type` (not `by_region` yet — #2084)
- `flowline_trends_by_depth` emits only bands with at least one data point
- `_classify_depth` from benchmarks.py is shared by architecture_patterns.py (internal import)
