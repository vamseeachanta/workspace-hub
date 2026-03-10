#!/usr/bin/env bash
# test_skill_evals.sh — TAP-style tests for WRK-1009 skill eval tooling
# Usage: bash scripts/skills/tests/test_skill_evals.sh
# Exit 0 if all pass, 1 if any fail.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

PASS=0
FAIL=0
TEST_NUM=0
TMPDIR_ROOT="$(mktemp -d /tmp/test_skill_evals.XXXXXX)"

cleanup() {
    rm -rf "$TMPDIR_ROOT"
}
trap cleanup EXIT

ok() {
    TEST_NUM=$((TEST_NUM + 1))
    echo "ok ${TEST_NUM} - $1"
    PASS=$((PASS + 1))
}

not_ok() {
    TEST_NUM=$((TEST_NUM + 1))
    echo "not ok ${TEST_NUM} - $1"
    if [[ -n "${2:-}" ]]; then
        echo "  # $2"
    fi
    FAIL=$((FAIL + 1))
}

# ---------------------------------------------------------------------------
# test 1: test_valid_eval_dir_exits_0
# ---------------------------------------------------------------------------
test_valid_eval_dir_exits_0() {
    local tmpdir="${TMPDIR_ROOT}/t1"
    mkdir -p "${tmpdir}/specs/skills/evals"
    mkdir -p "${tmpdir}/.claude/state/skill-eval-results"
    mkdir -p "${tmpdir}/.claude/state/skill-eval-candidates"
    mkdir -p "${tmpdir}/.claude/skills/workspace-hub/test-skill"

    cat > "${tmpdir}/.claude/skills/workspace-hub/test-skill/SKILL.md" <<'EOF'
---
name: test-skill
description: Test skill for eval harness
version: 1.0.0
---
# Test Skill

## Quick Start

```bash
/test command
/test run
```

## Stage Contracts

All stages documented here.
EOF

    cat > "${tmpdir}/specs/skills/evals/test-skill.yaml" <<'EOF'
version: 1
wrk_id: WRK-1009
skill_name: test-skill
skill_path: .claude/skills/workspace-hub/test-skill/SKILL.md
evals:
  - eval_id: ts-cap-01
    eval_type: capability
    description: Quick start documented
    checks:
      required_commands:
        - "/test command"
        - "/test run"
  - eval_id: ts-proc-01
    eval_type: procedural
    description: Stage Contracts section present
    checks:
      required_sections:
        - "## Stage Contracts"
EOF

    local out
    out=$(cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/run_skill_evals.py" \
        --evals-dir specs/skills/evals \
        --results-dir .claude/state/skill-eval-results 2>&1)
    local rc=$?
    if [[ $rc -eq 0 ]]; then
        ok "test_valid_eval_dir_exits_0"
    else
        not_ok "test_valid_eval_dir_exits_0" "exit code $rc; output: $out"
    fi
}

# ---------------------------------------------------------------------------
# test 2: test_missing_skill_exits_nonzero
# ---------------------------------------------------------------------------
test_missing_skill_exits_nonzero() {
    local tmpdir="${TMPDIR_ROOT}/t2"
    mkdir -p "${tmpdir}/specs/skills/evals"
    mkdir -p "${tmpdir}/.claude/state/skill-eval-results"
    mkdir -p "${tmpdir}/.claude/state/skill-eval-candidates"

    cat > "${tmpdir}/specs/skills/evals/ghost-skill.yaml" <<'EOF'
version: 1
wrk_id: WRK-1009
skill_name: ghost-skill
skill_path: .claude/skills/nonexistent/ghost-skill/SKILL.md
evals:
  - eval_id: gs-cap-01
    eval_type: capability
    description: Some check
    checks:
      required_sections:
        - "## Some Section"
EOF

    local out
    out=$(cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/run_skill_evals.py" \
        --evals-dir specs/skills/evals \
        --results-dir .claude/state/skill-eval-results 2>&1)
    local rc=$?
    # Should exit nonzero because skill path doesn't exist — treated as FAIL
    if [[ $rc -ne 0 ]]; then
        ok "test_missing_skill_exits_nonzero"
    else
        not_ok "test_missing_skill_exits_nonzero" \
            "expected nonzero exit for missing skill; got $rc"
    fi
}

# ---------------------------------------------------------------------------
# test 3: test_jsonl_has_required_fields
# ---------------------------------------------------------------------------
test_jsonl_has_required_fields() {
    local tmpdir="${TMPDIR_ROOT}/t3"
    mkdir -p "${tmpdir}/specs/skills/evals"
    mkdir -p "${tmpdir}/.claude/state/skill-eval-results"
    mkdir -p "${tmpdir}/.claude/state/skill-eval-candidates"
    mkdir -p "${tmpdir}/.claude/skills/test/my-skill"

    cat > "${tmpdir}/.claude/skills/test/my-skill/SKILL.md" <<'EOF'
---
name: my-skill
version: 1.0.0
---
# My Skill

## Phase

Phase 1 documented.
EOF

    cat > "${tmpdir}/specs/skills/evals/my-skill.yaml" <<'EOF'
version: 1
wrk_id: WRK-1009
skill_name: my-skill
skill_path: .claude/skills/test/my-skill/SKILL.md
evals:
  - eval_id: ms-cap-01
    eval_type: capability
    description: Phase documented
    checks:
      required_sections:
        - "## Phase"
EOF

    cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/run_skill_evals.py" \
        --evals-dir specs/skills/evals \
        --results-dir .claude/state/skill-eval-results 2>&1 >/dev/null || true

    local jsonl_file
    jsonl_file=$(ls "${tmpdir}/.claude/state/skill-eval-results/"*.jsonl 2>/dev/null | head -1)

    if [[ -z "$jsonl_file" ]]; then
        not_ok "test_jsonl_has_required_fields" "no JSONL file produced"
        return
    fi

    local first_line
    first_line=$(head -1 "$jsonl_file")
    local missing=""
    for field in run_id skill_name skill_path eval_id eval_type result timestamp source_eval; do
        if ! echo "$first_line" | grep -q "\"${field}\""; then
            missing="${missing} ${field}"
        fi
    done

    if [[ -z "$missing" ]]; then
        ok "test_jsonl_has_required_fields"
    else
        not_ok "test_jsonl_has_required_fields" "missing fields:${missing}"
    fi
}

# ---------------------------------------------------------------------------
# test 4: test_duplicate_detection_flags
# ---------------------------------------------------------------------------
test_duplicate_detection_flags() {
    local tmpdir="${TMPDIR_ROOT}/t4"
    mkdir -p "${tmpdir}/.claude/skills/a/dup-skill"
    mkdir -p "${tmpdir}/.claude/skills/b/dup-skill"

    cat > "${tmpdir}/.claude/skills/a/dup-skill/SKILL.md" <<'EOF'
---
name: duplicated-skill-name
version: 1.0.0
---
# Dup A
EOF

    cat > "${tmpdir}/.claude/skills/b/dup-skill/SKILL.md" <<'EOF'
---
name: duplicated-skill-name
version: 1.0.0
---
# Dup B
EOF

    local out
    out=$(cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/detect_duplicate_skills.py" \
        --skills-dir .claude/skills 2>&1)

    if echo "$out" | grep -qi "DUPLICATE"; then
        ok "test_duplicate_detection_flags"
    else
        not_ok "test_duplicate_detection_flags" \
            "expected DUPLICATE in output; got: $out"
    fi
}

# ---------------------------------------------------------------------------
# test 5: test_retirement_flagged_when_below_threshold
# ---------------------------------------------------------------------------
test_retirement_flagged_when_below_threshold() {
    local tmpdir="${TMPDIR_ROOT}/t5"
    mkdir -p "${tmpdir}/.claude/state/skill-retirement-candidates"

    cat > "${tmpdir}/.claude/state/skill-scores.yaml" <<'EOF'
version: 1.0.0
skills:
  low-use-skill:
    baseline_usage_rate: 0.03
    calls_in_period: 5
    last_seen: "2026-01-01"
EOF

    local out
    out=$(cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/check_retirement_candidates.py" \
        --scores-file .claude/state/skill-scores.yaml \
        --output-dir .claude/state/skill-retirement-candidates 2>&1)

    if echo "$out" | grep -qi "RETIREMENT CANDIDATE"; then
        ok "test_retirement_flagged_when_below_threshold"
    else
        not_ok "test_retirement_flagged_when_below_threshold" \
            "expected RETIREMENT CANDIDATE; got: $out"
    fi
}

# ---------------------------------------------------------------------------
# test 6: test_retirement_not_flagged_above_threshold
# ---------------------------------------------------------------------------
test_retirement_not_flagged_above_threshold() {
    local tmpdir="${TMPDIR_ROOT}/t6"
    mkdir -p "${tmpdir}/.claude/state/skill-retirement-candidates"

    cat > "${tmpdir}/.claude/state/skill-scores.yaml" <<'EOF'
version: 1.0.0
skills:
  active-skill:
    baseline_usage_rate: 0.10
    calls_in_period: 20
    last_seen: "2026-01-01"
EOF

    local out
    out=$(cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/check_retirement_candidates.py" \
        --scores-file .claude/state/skill-scores.yaml \
        --output-dir .claude/state/skill-retirement-candidates 2>&1)

    if ! echo "$out" | grep -qi "RETIREMENT CANDIDATE"; then
        ok "test_retirement_not_flagged_above_threshold"
    else
        not_ok "test_retirement_not_flagged_above_threshold" \
            "should NOT flag; got: $out"
    fi
}

# ---------------------------------------------------------------------------
# test 7: test_retirement_skip_when_no_data
# ---------------------------------------------------------------------------
test_retirement_skip_when_no_data() {
    local tmpdir="${TMPDIR_ROOT}/t7"
    mkdir -p "${tmpdir}/.claude/state/skill-retirement-candidates"

    # skill-scores.yaml with entry missing both rate fields
    cat > "${tmpdir}/.claude/state/skill-scores.yaml" <<'EOF'
version: 1.0.0
skills:
  undocumented-skill:
    last_seen: "2026-01-01"
EOF

    local out
    out=$(cd "${tmpdir}" && \
        uv run --no-project python "${WS_HUB}/scripts/skills/check_retirement_candidates.py" \
        --scores-file .claude/state/skill-scores.yaml \
        --output-dir .claude/state/skill-retirement-candidates 2>&1)

    if echo "$out" | grep -qi "SKIP"; then
        ok "test_retirement_skip_when_no_data"
    else
        not_ok "test_retirement_skip_when_no_data" \
            "expected SKIP for missing data; got: $out"
    fi
}

# ---------------------------------------------------------------------------
# test 8: test_script_candidate_scan_produces_files
# ---------------------------------------------------------------------------
test_script_candidate_scan_produces_files() {
    local out
    out=$(cd "${WS_HUB}" && \
        bash scripts/skills/identify-script-candidates.sh 2>&1)
    local rc=$?

    local md_found=0
    local json_found=0

    [[ -f "${WS_HUB}/specs/skills/script-conversion-candidates.md" ]] && md_found=1
    ls "${WS_HUB}/.claude/state/skill-script-candidates/"*.json 2>/dev/null | grep -q . && json_found=1

    if [[ $md_found -eq 1 && $json_found -eq 1 ]]; then
        ok "test_script_candidate_scan_produces_files"
    else
        not_ok "test_script_candidate_scan_produces_files" \
            "md_found=$md_found json_found=$json_found rc=$rc"
    fi
}

# ---------------------------------------------------------------------------
# test 9: test_cron_integration
# ---------------------------------------------------------------------------
test_cron_integration() {
    local out
    out=$(cd "${WS_HUB}" && \
        bash scripts/cron/skill-curation-nightly.sh 2>&1)
    local rc=$?

    if echo "$out" | grep -qi "skill-curation"; then
        ok "test_cron_integration"
    else
        not_ok "test_cron_integration" \
            "expected 'skill-curation' in output; rc=$rc"
    fi
}

# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------
echo "TAP version 13"
echo "1..9"

test_valid_eval_dir_exits_0
test_missing_skill_exits_nonzero
test_jsonl_has_required_fields
test_duplicate_detection_flags
test_retirement_flagged_when_below_threshold
test_retirement_not_flagged_above_threshold
test_retirement_skip_when_no_data
test_script_candidate_scan_produces_files
test_cron_integration

echo ""
echo "# Results: $PASS passed, $FAIL failed out of $TEST_NUM tests"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
exit 0
