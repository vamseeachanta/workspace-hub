We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2058 — Subsea architecture patterns — flowline trends and layout classification
Status: Ready only after the operator confirms Wave 3 is landed, there is no active contention on benchmarks.py / SubseaProject, and the issue is already labeled status:plan-approved.

Hard gate before any implementation write:
- Read CLAUDE.md and AGENTS.md planning rules first.
- Verify issue #2058 is already status:plan-approved by a human. Do NOT self-approve, do NOT create approval markers, and do NOT edit GitHub labels.
- If plan approval is missing, or if another session is still editing benchmarks.py / normalize.py / SubseaProject-related files, stop immediately and return a blocked summary with zero implementation writes.

Tasks:
1. Read current state:
   - CLAUDE.md lines 8-12
   - AGENTS.md lines 5-8
   - digitalmodel/src/digitalmodel/field_development/benchmarks.py
   - worldenergydata/subseaiq/analytics/normalize.py
2. Follow TDD first.
3. In digitalmodel/tests/field_development/test_benchmarks.py:
   - extend 4+ fixture records with flowline_diameter_in, flowline_material, and layout_type
   - add TestSubseaProjectNewFields covering field loading and None defaults for sparse records
4. Create digitalmodel/tests/field_development/test_architecture_patterns.py with tests for:
   - layout_distribution
   - tieback_stats_segmented
   - equipment_stats_by_concept
   - flowline_trends_by_depth
   Include empty-input and missing-field cases.
5. Add or update normalize tests under worldenergydata to cover the 3 new fields:
   - flowline_diameter_in float coercion
   - flowline_material passthrough
   - layout_type passthrough / alias mapping
6. Implement worldenergydata/subseaiq/analytics/normalize.py changes:
   - add alias groups for flowline_diameter_in, flowline_material, layout_type
   - add float coercion for flowline_diameter_in in normalize_project()
7. Implement digitalmodel/src/digitalmodel/field_development/benchmarks.py changes only for shared data model plumbing:
   - add optional SubseaProject fields flowline_diameter_in, flowline_material, layout_type
   - update load_projects() to map those fields
   - do not add the new analytics functions here
8. Create digitalmodel/src/digitalmodel/field_development/architecture_patterns.py and implement:
   - layout_distribution(projects) -> dict[str, dict[str, int]]
   - tieback_stats_segmented(projects) -> dict[str, dict[str, dict[str, float]]]
   - equipment_stats_by_concept(projects) -> dict[str, dict[str, dict[str, float]]]
   - flowline_trends_by_depth(projects) -> dict[str, dict[str, object]]
   Reuse benchmark helpers where sensible.
9. Keep the architecture split mandatory:
   - benchmarks.py should receive only dataclass + load_projects changes
   - new analytical functions must live in architecture_patterns.py
10. Run verification:
   - cd digitalmodel && PYTHONPATH=src uv run python -m pytest tests/field_development/test_benchmarks.py tests/field_development/test_architecture_patterns.py -v
   - cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest
     (if a narrower normalize test target exists, use it and note it explicitly)
11. Post a gh issue comment on #2058 summarizing implementation, tests run, and the mandatory file split.
12. Request Codex cross-review on the changed files after implementation.

Allowed write paths:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/architecture_patterns.py
- digitalmodel/tests/field_development/test_benchmarks.py
- digitalmodel/tests/field_development/test_architecture_patterns.py
- worldenergydata/subseaiq/analytics/normalize.py
- worldenergydata/tests/** only if needed for normalize-field coverage

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT touch:
  - digitalmodel/src/digitalmodel/field_development/economics.py
  - digitalmodel/src/digitalmodel/field_development/concept_selection.py
  - digitalmodel/src/digitalmodel/field_development/timeline.py
  - digitalmodel/src/digitalmodel/naval_architecture/
  - digitalmodel/src/digitalmodel/drilling_riser/
  - docs/
  - scripts/
  - .claude/
  - .planning/
  - any Git metadata or labels

Verification:
- cd /mnt/local-analysis/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/field_development/test_benchmarks.py tests/field_development/test_architecture_patterns.py -v
- cd /mnt/local-analysis/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -c "from digitalmodel.field_development.architecture_patterns import layout_distribution, tieback_stats_segmented, equipment_stats_by_concept, flowline_trends_by_depth; print('architecture_patterns imports OK')"
- cd /mnt/local-analysis/workspace-hub && wc -l digitalmodel/src/digitalmodel/field_development/benchmarks.py digitalmodel/src/digitalmodel/field_development/architecture_patterns.py worldenergydata/subseaiq/analytics/normalize.py
- gh issue view 2058 --repo vamseeachanta/workspace-hub --json comments --jq '.comments[-1].body'
