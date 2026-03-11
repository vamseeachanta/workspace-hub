#!/usr/bin/env bash
# test-provider-logging.sh — WRK-658 TDD tests (14 tests)
# Tests enforce gate+logging contract for Claude/Codex/Gemini agents.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
FIXTURES="${REPO_ROOT}/scripts/agents/tests/fixtures/wrk-fixture"
VERIFY="${REPO_ROOT}/scripts/work-queue/verify-gate-evidence.py"
CONTRACT="${REPO_ROOT}/.claude/docs/orchestrator-gate-contract.md"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# Helper: load vge module inline for python -c invocations
VGE_LOADER="import importlib.util; spec=importlib.util.spec_from_file_location('vge','${VERIFY}'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)"

echo "=== WRK-658 Provider Logging TDD Tests ==="

# T1: CODEX.md exists, ≤20 lines, refs wrappers + gate contract
t1_ok=true
[[ -f "${REPO_ROOT}/CODEX.md" ]] || { fail "T1: CODEX.md missing"; t1_ok=false; }
if [[ "$t1_ok" == true ]]; then
  lines=$(wc -l < "${REPO_ROOT}/CODEX.md")
  [[ "$lines" -le 20 ]] || { fail "T1: CODEX.md exceeds 20 lines (${lines})"; t1_ok=false; }
fi
if [[ "$t1_ok" == true ]]; then
  grep -q "session.sh\|work.sh\|execute.sh\|wrappers" "${REPO_ROOT}/CODEX.md" || \
    { fail "T1: CODEX.md missing wrapper reference"; t1_ok=false; }
fi
if [[ "$t1_ok" == true ]]; then
  grep -q "orchestrator-gate-contract\|gate.contract\|gate contract" "${REPO_ROOT}/CODEX.md" || \
    { fail "T1: CODEX.md missing gate contract reference"; t1_ok=false; }
fi
[[ "$t1_ok" == true ]] && pass "T1: CODEX.md exists ≤20 lines refs wrappers+gate-contract"

# T2: GEMINI.md exists, ≤20 lines, refs wrappers + gate contract
t2_ok=true
[[ -f "${REPO_ROOT}/GEMINI.md" ]] || { fail "T2: GEMINI.md missing"; t2_ok=false; }
if [[ "$t2_ok" == true ]]; then
  lines=$(wc -l < "${REPO_ROOT}/GEMINI.md")
  [[ "$lines" -le 20 ]] || { fail "T2: GEMINI.md exceeds 20 lines (${lines})"; t2_ok=false; }
fi
if [[ "$t2_ok" == true ]]; then
  grep -q "session.sh\|work.sh\|execute.sh\|wrappers" "${REPO_ROOT}/GEMINI.md" || \
    { fail "T2: GEMINI.md missing wrapper reference"; t2_ok=false; }
fi
if [[ "$t2_ok" == true ]]; then
  grep -q "orchestrator-gate-contract\|gate.contract\|gate contract" "${REPO_ROOT}/GEMINI.md" || \
    { fail "T2: GEMINI.md missing gate contract reference"; t2_ok=false; }
fi
[[ "$t2_ok" == true ]] && pass "T2: GEMINI.md exists ≤20 lines refs wrappers+gate-contract"

# T3: check_agent_log_gate(valid-logs, WRK-700, close, frontmatter=new) PASSES
t3_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/valid-logs'), 'WRK-700', 'close',
    wrk_frontmatter={'id': 'WRK-700', 'created_at': '2026-03-10T00:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if ok else 1)
" 2>&1) && pass "T3: check_agent_log_gate(valid-logs, WRK-700, close, new-frontmatter) PASSES" \
           || fail "T3: expected PASS — got: ${t3_result}"

# T4: check_agent_log_gate(new-wrk, WRK-700, close, frontmatter=new) FAILS
t4_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/new-wrk'), 'WRK-700', 'close',
    wrk_frontmatter={'id': 'WRK-700', 'created_at': '2026-03-10T00:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if not ok else 1)
" 2>&1) && pass "T4: check_agent_log_gate(new-wrk, WRK-700, close, new-frontmatter) FAILS" \
           || fail "T4: expected FAIL — got: ${t4_result}"

# T5: check_agent_log_gate(legacy-wrk, WRK-001, close, legacy frontmatter) PASSES (id < 658)
t5_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/legacy-wrk'), 'WRK-001', 'close',
    wrk_frontmatter={'id': 'WRK-001', 'created_at': '2025-01-01T00:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if ok else 1)
" 2>&1) && pass "T5: check_agent_log_gate(legacy-wrk, WRK-001, legacy id<658) PASSES" \
           || fail "T5: expected PASS — got: ${t5_result}"

# T6: check_agent_log_gate(new-wrk, WRK-700, at-cutoff created_at) FAILS
# boundary equality: created_at=2026-03-09T00:00:00Z equals cutoff, not before → FAIL
t6_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/new-wrk'), 'WRK-700', 'close',
    wrk_frontmatter={'id': 'WRK-700', 'created_at': '2026-03-09T00:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if not ok else 1)
" 2>&1) && pass "T6: check_agent_log_gate(at-cutoff created_at) FAILS (boundary equality)" \
           || fail "T6: expected FAIL — got: ${t6_result}"

# T7: check_agent_log_gate with malformed created_at and id>=658 → FAILS
t7_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/new-wrk'), 'WRK-700', 'close',
    wrk_frontmatter={'id': 'WRK-700', 'created_at': 'not-a-date'}
)
print(ok, msg)
import sys; sys.exit(0 if not ok else 1)
" 2>&1) && pass "T7: check_agent_log_gate(malformed created_at, id>=658) FAILS" \
           || fail "T7: expected FAIL — got: ${t7_result}"

# T8: check_agent_log_gate(legacy-wrk, WRK-001, absent created_at) PASSES
t8_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/legacy-wrk'), 'WRK-001', 'close',
    wrk_frontmatter={'id': 'WRK-001'}
)
print(ok, msg)
import sys; sys.exit(0 if ok else 1)
" 2>&1) && pass "T8: check_agent_log_gate(WRK-001, absent created_at, id<658) PASSES" \
           || fail "T8: expected PASS — got: ${t8_result}"

# T9: check_agent_log_gate with non-numeric id (WRK-TEST) → FAILS
t9_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/new-wrk'), 'WRK-TEST', 'close',
    wrk_frontmatter={'id': 'WRK-TEST', 'created_at': '2026-03-10T00:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if not ok else 1)
" 2>&1) && pass "T9: check_agent_log_gate(non-numeric id WRK-TEST) FAILS" \
           || fail "T9: expected FAIL — got: ${t9_result}"

# T10: orchestrator-gate-contract.md documents log schema + required action names per phase
t10_ok=true
[[ -f "$CONTRACT" ]] || { fail "T10: orchestrator-gate-contract.md missing"; t10_ok=false; }
if [[ "$t10_ok" == true ]]; then
  grep -q "timestamp.*wrk_id.*stage.*action\|log schema\|{timestamp" "$CONTRACT" || \
    { fail "T10: gate-contract missing log schema"; t10_ok=false; }
fi
if [[ "$t10_ok" == true ]]; then
  grep -q "work_queue_skill\|plan_draft_complete" "$CONTRACT" || \
    { fail "T10: gate-contract missing required action names"; t10_ok=false; }
fi
[[ "$t10_ok" == true ]] && pass "T10: gate-contract documents log schema + required action names per phase"

# T11: check_agent_log_gate(backfill-wrk, WRK-700, backfill frontmatter) PASSES
# backfill: id>=658 but created_at < cutoff → skip gate
t11_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/backfill-wrk'), 'WRK-700', 'close',
    wrk_frontmatter={'id': 'WRK-700', 'created_at': '2026-01-01T00:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if ok else 1)
" 2>&1) && pass "T11: check_agent_log_gate(backfill id>=658 created_at<cutoff) PASSES" \
           || fail "T11: expected PASS — got: ${t11_result}"

# T12: check_agent_log_gate(boundary-wrk, WRK-658, boundary frontmatter) FAILS
# id=658 Tier1 skips (not < 658), Tier2: created_at=2026-03-09T12:00:00Z > cutoff → FAIL
t12_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/boundary-wrk'), 'WRK-658', 'close',
    wrk_frontmatter={'id': 'WRK-658', 'created_at': '2026-03-09T12:00:00Z'}
)
print(ok, msg)
import sys; sys.exit(0 if not ok else 1)
" 2>&1) && pass "T12: check_agent_log_gate(WRK-658 Tier2, date after cutoff) FAILS" \
           || fail "T12: expected FAIL — got: ${t12_result}"

# T13: inline wrk_frontmatter param — legacy WRK-001 id<658 skips gate
t13_result=$(uv run --no-project python -c "
${VGE_LOADER}
from pathlib import Path
ok, msg = m.check_agent_log_gate(
    Path('${FIXTURES}/legacy-wrk'), 'WRK-001', 'close',
    wrk_frontmatter={'id': 'WRK-001'}
)
print(ok, msg)
import sys; sys.exit(0 if ok else 1)
" 2>&1) && pass "T13: check_agent_log_gate(legacy-wrk, WRK-001, wrk_frontmatter={'id':'WRK-001'}) PASSES" \
           || fail "T13: expected PASS — got: ${t13_result}"

# T14: get_field(parse_frontmatter(wrk_stub), 'id') returns 'WRK-001'
t14_result=$(uv run --no-project python -c "
${VGE_LOADER}
stub = '---\nid: WRK-001\ncreated_at: 2026-01-01\n---\n'
fm = m.parse_frontmatter(stub)
val = m.get_field(fm, 'id')
print(repr(val))
import sys; sys.exit(0 if val == 'WRK-001' else 1)
" 2>&1) && pass "T14: get_field(parse_frontmatter(stub), 'id') returns 'WRK-001'" \
           || fail "T14: expected 'WRK-001' — got: ${t14_result}"

echo ""
echo "=== Results: ${PASS} PASS, ${FAIL} FAIL ==="
[[ "$FAIL" -eq 0 ]] && echo "All tests PASS" && exit 0
echo "Some tests FAILED" && exit 1
