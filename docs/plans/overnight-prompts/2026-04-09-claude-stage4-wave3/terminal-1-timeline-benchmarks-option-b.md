We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2060 — Project Timeline Benchmarks from SubseaIQ
Status: Not started. Operator decision is locked in: Option B.

Operator decision:
- OPTION_CHOSEN = B
- Extract new logic to digitalmodel/src/digitalmodel/field_development/timeline.py
- Keep only SubseaProject timeline field additions in benchmarks.py

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
5. Create digitalmodel/src/digitalmodel/field_development/timeline.py and place these 3 functions there:
   - timeline_duration_stats(projects)
   - duration_stats_by_concept_type(projects)
   - schedule_distributions(projects)
6. Update digitalmodel/src/digitalmodel/field_development/__init__.py exports.
7. Create digitalmodel/tests/field_development/test_timeline_benchmarks.py with test classes for:
   - SubseaProject timeline fields
   - load_projects timeline parsing
   - inter-phase duration math
   - grouping by concept type
   - P10/P50/P90 schedule distributions
8. Run tests:
   - cd digitalmodel && uv run pytest tests/field_development/test_timeline_benchmarks.py -v
9. Post a gh issue comment on #2060 summarizing implementation and noting alias names are provisional pending first scrape.
10. Request Codex cross-review on the changed files after implementation.

Allowed write paths:
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
