# Variation Tests — WRK-659
wrk_id: WRK-659
run_date: 2026-03-01
runner: claude (inline)

## Test 1: session.sh show
command: `bash scripts/agents/session.sh show`
result: PASS
evidence: output contains `orchestrator_agent: claude`

## Test 2: log-gate-event.sh creates log file
command: `bash scripts/work-queue/log-gate-event.sh WRK-659 tdd smoke-test claude "variation test probe"`
result: PASS
evidence: `.claude/work-queue/logs/WRK-659-tdd.log` created with correct YAML structure

## Test 3: verify-gate-evidence.py WRK-659
command: `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-659`
result: PASS
evidence: All 5 gates OK (plan, workstation, cross-review, TDD, legal) → "All orchestrator gates have documented evidence."

## Test 4: plan.sh --skip-ensemble passes after ## Plan section present
command: `bash scripts/agents/plan.sh --provider claude --skip-ensemble WRK-659`
result: PASS
evidence: exit 0, "Plan gate passed for WRK-659 under orchestrator 'claude'."
note: exit 3 (no ## Plan section) resolved by adding ## Plan section to WRK body

## Test 5: set-active-wrk roundtrip
command: `bash scripts/work-queue/set-active-wrk.sh WRK-659` then `cat .claude/state/active-wrk`
result: PASS
evidence: active-wrk reads "WRK-659"

## Summary
5/5 tests passed. All gate scripts behave correctly.
