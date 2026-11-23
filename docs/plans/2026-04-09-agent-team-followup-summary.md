# Agent team follow-up summary (2026-04-09)

Context:
- All 10 Claude planning dossiers completed under `docs/plans/overnight-prompts/2026-04-09-10claude/results/`.
- Parallel agent teams reviewed the completed dossiers to determine real execution readiness, sequencing, and hidden blockers.

## Executive summary

Most implementation-ready issues:
1. #2059 — Real vessel stability test cases from fleet data
2. #2063 — Drilling riser adapter into mooring/riser analysis
3. #2058 — Subsea architecture patterns

Governance sequence:
1. #2056 — runtime enforcement into hooks
2. #2057 — restore lost session infrastructure

Issue requiring refinement before implementation:
- #2055 — subsea cost benchmarking from SubseaIQ equipment counts

## Engineering implementation wave recommendation

### Wave 1
1. `#2059` — smallest delta, mostly test-oriented, highest confidence
   - likely files:
     - `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py`
     - possible small edit: `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`
   - note: depends on existing fleet adapter work already done

2. `#2063` — focused adapter slice with clear upstream/downstream boundaries
   - likely files:
     - `digitalmodel/src/digitalmodel/drilling_riser/adapter.py`
     - `digitalmodel/tests/drilling_riser/test_adapter_integration.py`
     - `digitalmodel/src/digitalmodel/drilling_riser/__init__.py`
     - `digitalmodel/tests/drilling_riser/conftest.py`

### Wave 2
3. `#2058` — additive analytics work, moderate data-normalization uncertainty
4. `#2060` — similar area as #2058, but more real-data uncertainty around milestone field coverage

### Defer last
5. `#2062` — drilling rig fleet adapter
   - hidden blocker: source data is sparse for draft/displacement geometry, so readiness is materially weaker than the dossier headline suggests

## Governance implementation recommendation

### First implement
`#2056` — Session governance Phase 2: wire runtime enforcement into hooks
- likely files:
  - `.claude/hooks/tool-call-ceiling.sh`
  - `.claude/hooks/error-loop-breaker.sh`
  - `.claude/settings.json`
  - `scripts/enforcement/require-review-on-push.sh`
  - `scripts/workflow/governance-checkpoints.yaml`
  - `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`
  - `docs/governance/SESSION-GOVERNANCE.md`
  - `tests/hooks/test_tool_call_ceiling.py`
  - `tests/hooks/test_error_loop_breaker.py`
- reason:
  - foundational runtime enforcement should land before Phase 3 skills/docs completion

### Then implement
`#2057` — Session governance Phase 3: restore lost session infrastructure
- mostly additive follow-up after #2056 stabilizes
- likely files:
  - `.claude/skills/workspace-hub/session-start-routine/SKILL.md`
  - `.claude/skills/workspace-hub/cross-review-policy/SKILL.md`
  - `tests/skills/test_session_start_routine_smoke.py`
  - `tests/skills/test_cross_review_policy_smoke.py`
  - related governance docs and broken links

## Field-development economics review

### `#2054` — decline curve cashflows
- status: READY AFTER LABEL UPDATE
- action: safe to implement once plan-approved

### `#2053` — concept selection matrix
- status: READY AFTER LABEL UPDATE
- action: implement with current GoM-scoped dataset; optionally clarify in the issue that 2 validation cases depend on future NCS data

### `#2055` — subsea cost benchmarking
- true status: NEEDS ISSUE REFINEMENT
- reason:
  - current SubseaIQ JSON lacks equipment-count fields
  - sanctioned cost schema lacks matching equipment-count fields
  - dependency “scraping with equipment count fields” is not actually met
- required refinement before approval:
  1. decide manual backfill vs waiting for real scrape
  2. decide band-level aggregation vs per-project join
  3. decide schema extension vs separate join table

## Recommended next approval set

If approving a small, high-confidence implementation batch next:
1. `#2059`
2. `#2063`
3. `#2056`

If approving a second batch after that:
4. `#2058`
5. `#2054`
6. `#2053`
7. `#2057`

Hold until refined:
- `#2055`
- `#2062` should be treated as lower-confidence and may benefit from issue clarification before implementation
