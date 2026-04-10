We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2053 — Concept Selection Probability Matrix & Decision Tree
Status: 4 of 5 scope items are already implemented. Remaining `production_rate_bopd` work should be split to follow-up.

Validated precondition:
- `cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py tests/field_development/test_concept_probability.py -q` already passed in this session.

Tasks:
1. Run the full field development test suite:
   - `cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short`
2. If Norwegian case-study tests fail due to missing NCS data, add `pytest.skip` markers with reason `NCS data dependency not yet available`.
   - Do NOT delete tests.
3. Create a follow-up draft issue file for the remaining scope item:
   - `docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave1/results/2053-followup-draft.md`
   - Title: `Add production_rate_bopd correlation to concept selection benchmarks`
4. Post a GitHub issue comment on #2053 summarizing: 4/5 scope items done, tests passing, remaining scope split to follow-up, Norwegian cases deferred if applicable.
5. Add a second GitHub comment noting Codex cross-review is requested per engineering gate.
6. Do NOT close the issue.

Allowed write paths:
- `digitalmodel/tests/field_development/test_benchmarks.py` (skip markers only if needed)
- `digitalmodel/tests/field_development/test_concept_probability.py` (skip markers only if needed)
- `docs/plans/overnight-prompts/2026-04-09-claude-stage4-wave1/results/2053-followup-draft.md`

Negative write boundaries:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/src/digitalmodel/field_development/concept_selection.py`
- any file outside `digitalmodel/tests/` and the single allowed docs result path
- `worldenergydata/`

Cross-review: yes, request Codex in the issue comment.

End state:
- tests run
- follow-up draft file exists
- issue comments posted
