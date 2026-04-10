We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2060 — Project Timeline Benchmarks from SubseaIQ
Status: Not started. Depends on operator file-size policy decision for benchmarks.py.

OPERATOR MUST CHOOSE BEFORE DISPATCH:
- Option A: accept growth in benchmarks.py to ~700 lines
- Option B: extract new logic to digitalmodel/src/digitalmodel/field_development/timeline.py
Replace OPTION_CHOSEN below before dispatch.

Tasks:
1. Read current state:
   - digitalmodel/src/digitalmodel/field_development/benchmarks.py lines 1-30
   - worldenergydata/subseaiq/analytics/normalize.py lines 25-60
2. Extend SubseaProject with 4 optional fields:
   - year_concept
   - year_feed
   - year_fid
   - year_first_oil
3. Update load_projects() to parse the 4 fields via _opt_int().
4. Add 4 alias groups to worldenergydata/subseaiq/analytics/normalize.py for the timeline fields.
5. If OPTION_CHOSEN == A:
   - add timeline_duration_stats(projects)
   - add duration_stats_by_concept_type(projects)
   - add schedule_distributions(projects)
   inside benchmarks.py
6. If OPTION_CHOSEN == B:
   - create digitalmodel/src/digitalmodel/field_development/timeline.py
   - place the same 3 functions there
   - keep only dataclass field additions in benchmarks.py
7. Update digitalmodel/src/digitalmodel/field_development/__init__.py exports.
8. Create digitalmodel/tests/field_development/test_timeline_benchmarks.py with test classes for:
   - SubseaProject timeline fields
   - load_projects timeline parsing
   - inter-phase duration math
   - grouping by concept type
   - P10/P50/P90 schedule distributions
9. Run tests:
   - cd digitalmodel && uv run pytest tests/field_development/test_timeline_benchmarks.py -v
10. Post a gh issue comment on #2060 summarizing implementation and noting alias names are provisional pending first scrape.
11. Request Codex cross-review on the changed files after implementation.

Allowed write paths (Option A):
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_timeline_benchmarks.py
- worldenergydata/subseaiq/analytics/normalize.py

Allowed write paths (Option B):
- digitalmodel/src/digitalmodel/field_development/timeline.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_timeline_benchmarks.py
- worldenergydata/subseaiq/analytics/normalize.py
- digitalmodel/src/digitalmodel/field_development/benchmarks.py (SubseaProject fields only)

Negative write boundaries:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/src/digitalmodel/field_development/concept_selection.py
- digitalmodel/src/digitalmodel/naval_architecture/
- digitalmodel/src/digitalmodel/drilling_riser/
- scripts/
- .claude/
- docs/

Verification:
- cd digitalmodel && uv run pytest tests/field_development/test_timeline_benchmarks.py -v
- cd digitalmodel && uv run python -c "from digitalmodel.field_development import timeline_duration_stats, duration_stats_by_concept_type, schedule_distributions; print('All 3 exports OK')"
- cd digitalmodel && wc -l src/digitalmodel/field_development/benchmarks.py
