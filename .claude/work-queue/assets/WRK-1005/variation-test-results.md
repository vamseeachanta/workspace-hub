# Variation Tests — WRK-1005
wrk_id: WRK-1005
run_date: 2026-03-05T05:45:00Z
runner: claude

## Test 1: parse-session-logs.sh
command: `bash scripts/work-queue/parse-session-logs.sh WRK-1002 WRK-1003 WRK-1004`
result: PASS
evidence: |
  Session log review generated for 3 WRKs × 3 providers.
  Claude: session_20260304.jsonl present (17h session)
  Codex: session_20260304.log present (55s, 2 WRK refs)
  Gemini: no named log (native store present)
  Output: .claude/work-queue/assets/WRK-1004/session-log-review.md

## Test 2: verify-gate-evidence.py WRK-1002
command: `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1002`
result: PASS
evidence: 15 PASS, 1 WARN (reclaim) — all gates documented

## Test 3: verify-gate-evidence.py WRK-1003
command: `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1003`
result: PASS
evidence: 15 PASS, 1 WARN (reclaim) — all gates documented

## Test 4: verify-gate-evidence.py WRK-1004
command: `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1004`
result: PASS
evidence: 15 PASS, 1 WARN (reclaim) — all gates documented

## Test 5: pytest spec divergence check
command: `uv run --no-project python -m pytest tests/unit/test_circle.py -v`
result: PASS
evidence: 5/5 pass — no divergence across Claude/Codex/Gemini runs

## Summary
5/5 tests passed. All provider lifecycles verified; session logs parsed; spec contract intact.
