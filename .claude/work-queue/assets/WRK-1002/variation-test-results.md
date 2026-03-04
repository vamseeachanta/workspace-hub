# Variation Tests — WRK-1002
wrk_id: WRK-1002
run_date: 2026-03-04T23:37:15Z
runner: claude

## Test 1: uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1002
command: `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1002`
result: FAIL (exit 1)
evidence: |
  → Gate evidence incomplete. Please collect the missing artifacts before claiming.
  Gate evidence for WRK-1002 (phase=close, assets: /mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1002):
    - Plan gate: OK (reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed)
    - Workstation contract gate: OK (plan_workstations=[ace-linux-1], execution_workstations=[ace-linux-1])
    - Stage evidence gate: MISSING (stage-evidence.yaml: stage order 5 must be done|n/a before close (found pending))
    - Resource-intelligence gate: OK (resource-intelligence.yaml: completion_status=continue_to_planning, p1_count=0, core_skills=3)
    - Activation gate: OK (activation.yaml: activation evidence OK)
    - User-review HTML-open gate: MISSING (user-review-browser-open.yaml: missing required stages ['close_review'])
    - User-review publish gate: MISSING (user-review-publish.yaml: missing required stages ['close_review'])
    - Cross-review gate: OK (artifact=/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/WRK-1002/review.html)
    - TDD gate: OK (test files=['variation-test-results.md'])
    - Integrated test gate: OK (execute.yaml: integrated_repo_tests=5 (all passing))
    - Legal gate: MISSING (artifact=missing, none)
    - Claim gate: OK (claim-evidence.yaml: version=1, owner=claude, quota=available(null))
    - Future-work gate: MISSING (future-work evidence absent (legacy item — WARN))
    - Resource-intelligence update gate: MISSING (resource-intelligence-update.yaml missing)
    - User-review close gate: MISSING (user-review-close.yaml: missing fields: ['reviewed_at'])
    - Reclaim gate: WARN (reclaim.yaml absent (no reclaim triggered — WARN))

## Test 2: uv run --no-project python -m pytest tests/unit/test_circle.py -v
command: `uv run --no-project python -m pytest tests/unit/test_circle.py -v`
result: PASS
evidence: |
  ============================= test session starts ==============================
  platform linux -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0 -- /mnt/local-analysis/workspace-hub/.venv/bin/python3
  cachedir: .pytest_cache
  rootdir: /mnt/local-analysis/workspace-hub
  configfile: pyproject.toml
  collecting ... collected 5 items
  
  tests/unit/test_circle.py::test_calculate_circle_area PASSED             [ 20%]
  tests/unit/test_circle.py::test_calculate_circle_circumference PASSED    [ 40%]
  tests/unit/test_circle.py::test_calculate_circle_zero_radius PASSED      [ 60%]
  tests/unit/test_circle.py::test_calculate_circle_returns_dict PASSED     [ 80%]
  tests/unit/test_circle.py::test_calculate_circle_unit_radius PASSED      [100%]
  
  ============================== 5 passed in 0.08s ===============================

## Summary
1/2 tests passed.
⚠ 1 test(s) failed — review evidence above.
