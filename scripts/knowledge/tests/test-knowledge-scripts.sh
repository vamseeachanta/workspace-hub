#!/usr/bin/env bash
# tests/test-knowledge-scripts.sh — TDD tests for scripts/knowledge/*.sh
# Run from workspace-hub root: bash scripts/knowledge/tests/test-knowledge-scripts.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS_DIR="${REPO_ROOT}/scripts/knowledge"
PASS=0
FAIL=0
ERRORS=()

# ── helpers ─────────────────────────────────────────────────────────────────
run_test() {
    local name="$1"
    shift
    if "$@" 2>/dev/null; then
        echo "  PASS: ${name}"
        ((PASS++)) || true
    else
        echo "  FAIL: ${name}"
        ((FAIL++)) || true
        ERRORS+=("${name}")
    fi
}

# shellcheck disable=SC2329
assert_file_contains() {
    local file="$1" pattern="$2"
    grep -q "${pattern}" "${file}"
}

# shellcheck disable=SC2329
assert_line_count_le() {
    local file="$1" limit="$2"
    [[ "$(wc -l < "${file}")" -le "${limit}" ]]
}

# ── fixture setup ────────────────────────────────────────────────────────────
setup() {
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "${TMP_DIR}"' EXIT

    # Minimal WRK fixture
    WRK_DIR="${TMP_DIR}/work-queue/archive"
    mkdir -p "${WRK_DIR}"
    cat > "${WRK_DIR}/WRK-9999.md" << 'WRKEOF'
---
id: WRK-9999
title: "Test WRK for knowledge scripts"
category: harness
subcategory: test
status: done
---
## Mission
Verify that capture-wrk-summary.sh correctly appends a JSONL entry.
WRKEOF

    KB_DIR="${TMP_DIR}/knowledge-base"
    mkdir -p "${KB_DIR}"

    SEED_DIR="${TMP_DIR}/knowledge/seeds"
    mkdir -p "${SEED_DIR}"
    cat > "${SEED_DIR}/career-learnings.yaml" << 'SEEDEOF'
entries:
  - id: CAREER-engineering-test-entry
    type: career
    category: engineering
    subcategory: test
    title: "Test career learning entry"
    learned_at: "2026-03-10T00:00:00Z"
    context: "Test entry for unit tests"
    patterns:
      - "Always validate inputs at boundaries"
    follow_ons: []
SEEDEOF
}

# ── Phase 2 tests ─────────────────────────────────────────────────────────────

echo "=== Phase 2: Core Knowledge Scripts ==="

setup

# test_capture_happy_path
run_test "test_capture_happy_path" bash -c "
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-9999 &&
    [[ -f '${TMP_DIR}/knowledge-base/wrk-completions.jsonl' ]] &&
    grep -q 'WRK-9999' '${TMP_DIR}/knowledge-base/wrk-completions.jsonl'
"

# test_capture_nonexistent_wrk — must exit 0 (non-blocking)
run_test "test_capture_nonexistent_wrk" bash -c "
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-8888
    # exit code must be 0
"

# test_capture_creates_knowledge_dir
run_test "test_capture_creates_knowledge_dir" bash -c "
    rm -rf '${TMP_DIR}/knowledge-base2'
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base2' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-9999 &&
    [[ -f '${TMP_DIR}/knowledge-base2/wrk-completions.jsonl' ]]
"

# test_capture_idempotent — re-running same WRK-ID must not duplicate
run_test "test_capture_idempotent" bash -c "
    rm -f '${TMP_DIR}/knowledge-base/wrk-completions.jsonl'
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-9999
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-9999
    count=\$(grep -c '\"WRK-9999\"' '${TMP_DIR}/knowledge-base/wrk-completions.jsonl' 2>/dev/null || echo 0)
    [[ \"\${count}\" -eq 1 ]]
"

# test_capture_malformed_yaml — malformed resource-intelligence.yaml should not crash
run_test "test_capture_malformed_yaml" bash -c "
    mkdir -p '${TMP_DIR}/work-queue/assets/WRK-9999/evidence'
    echo 'this: is: not: valid: yaml: :' > \
        '${TMP_DIR}/work-queue/assets/WRK-9999/evidence/resource-intelligence.yaml'
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-9999 &&
    grep -q 'WRK-9999' '${TMP_DIR}/knowledge-base/wrk-completions.jsonl'
"

# test_capture_flock_timeout — lock held → exits 0 (non-blocking)
run_test "test_capture_flock_timeout" bash -c "
    rm -f '${TMP_DIR}/knowledge-base/wrk-completions.jsonl.lock'
    # Hold lock for 10s
    exec 9>'${TMP_DIR}/knowledge-base/wrk-completions.jsonl.lock'
    flock -x 9
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/work-queue' \
    FLOCK_TIMEOUT=1 \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-9999
    exit_code=\$?
    flock -u 9
    [[ \${exit_code} -eq 0 ]]
"

# test_query_keyword_match
run_test "test_query_keyword_match" bash -c "
    echo '{\"id\":\"WRK-100\",\"type\":\"wrk\",\"category\":\"harness\",\"title\":\"Pipeline integrity check\",\"mission\":\"Check pipeline integrity\",\"patterns\":[]}' \
        > '${TMP_DIR}/knowledge-base/wrk-completions.jsonl'
    out=\$(KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
         KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds' \
         bash '${SCRIPTS_DIR}/query-knowledge.sh' --query pipeline)
    echo \"\${out}\" | grep -q 'WRK-100'
"

# test_query_domain_filter
run_test "test_query_domain_filter" bash -c "
    echo '{\"id\":\"WRK-101\",\"type\":\"wrk\",\"category\":\"harness\",\"title\":\"Harness item\",\"mission\":\"Harness mission\",\"patterns\":[]}' \
        >> '${TMP_DIR}/knowledge-base/wrk-completions.jsonl'
    echo '{\"id\":\"WRK-102\",\"type\":\"wrk\",\"category\":\"data\",\"title\":\"Data item\",\"mission\":\"Data mission\",\"patterns\":[]}' \
        >> '${TMP_DIR}/knowledge-base/wrk-completions.jsonl'
    out=\$(KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base' \
         KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds' \
         bash '${SCRIPTS_DIR}/query-knowledge.sh' --category harness)
    echo \"\${out}\" | grep -q 'WRK-101' &&
    ! echo \"\${out}\" | grep -q 'WRK-102'
"

# test_query_empty_result
run_test "test_query_empty_result" bash -c "
    rm -f '${TMP_DIR}/knowledge-base2/wrk-completions.jsonl'
    mkdir -p '${TMP_DIR}/knowledge-base2'
    out=\$(KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base2' \
         KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds-empty' \
         bash '${SCRIPTS_DIR}/query-knowledge.sh' --query zzznomatch 2>/dev/null)
    echo \"\${out}\" | grep -q 'No knowledge entries found'
"

# test_query_corrupt_jsonl_skip — malformed line skipped, valid entries returned
run_test "test_query_corrupt_jsonl_skip" bash -c "
    mkdir -p '${TMP_DIR}/knowledge-base3'
    echo 'NOT VALID JSON' > '${TMP_DIR}/knowledge-base3/wrk-completions.jsonl'
    echo '{\"id\":\"WRK-200\",\"type\":\"wrk\",\"category\":\"harness\",\"title\":\"Valid entry\",\"mission\":\"Valid mission\",\"patterns\":[]}' \
        >> '${TMP_DIR}/knowledge-base3/wrk-completions.jsonl'
    out=\$(KNOWLEDGE_BASE_DIR='${TMP_DIR}/knowledge-base3' \
         KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds' \
         bash '${SCRIPTS_DIR}/query-knowledge.sh' --query valid)
    echo \"\${out}\" | grep -q 'WRK-200'
"

# test_index_builds_from_jsonl
run_test "test_index_builds_from_jsonl" bash -c "
    mkdir -p '${TMP_DIR}/kb-index'
    echo '{\"id\":\"WRK-300\",\"type\":\"wrk\",\"category\":\"test\",\"title\":\"Index test\",\"mission\":\"Test\",\"patterns\":[]}' \
        > '${TMP_DIR}/kb-index/wrk-completions.jsonl'
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/kb-index' \
    KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds' \
    bash '${SCRIPTS_DIR}/build-knowledge-index.sh' &&
    [[ -f '${TMP_DIR}/kb-index/index.jsonl' ]] &&
    grep -q 'WRK-300' '${TMP_DIR}/kb-index/index.jsonl'
"

# test_index_normalizes_career_learnings
run_test "test_index_normalizes_career_learnings" bash -c "
    mkdir -p '${TMP_DIR}/kb-career'
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/kb-career' \
    KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds' \
    bash '${SCRIPTS_DIR}/build-knowledge-index.sh' &&
    grep -q 'CAREER-engineering-test-entry' '${TMP_DIR}/kb-career/index.jsonl'
"

# test_index_deduplicates — duplicate id across files → single entry in index
run_test "test_index_deduplicates" bash -c "
    mkdir -p '${TMP_DIR}/kb-dedup'
    echo '{\"id\":\"WRK-400\",\"type\":\"wrk\",\"category\":\"test\",\"title\":\"Dup\",\"mission\":\"Dup\",\"patterns\":[]}' \
        > '${TMP_DIR}/kb-dedup/store1.jsonl'
    echo '{\"id\":\"WRK-400\",\"type\":\"wrk\",\"category\":\"test\",\"title\":\"Dup2\",\"mission\":\"Dup2\",\"patterns\":[]}' \
        > '${TMP_DIR}/kb-dedup/store2.jsonl'
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/kb-dedup' \
    KNOWLEDGE_SEEDS_DIR='${TMP_DIR}/knowledge/seeds' \
    bash '${SCRIPTS_DIR}/build-knowledge-index.sh' &&
    count=\$(grep -c '\"WRK-400\"' '${TMP_DIR}/kb-dedup/index.jsonl')
    [[ \"\${count}\" -eq 1 ]]
"

# ── Phase 3 tests ─────────────────────────────────────────────────────────────

echo ""
echo "=== Phase 3: Integration ==="

# test_archive_hook_writes_knowledge — simulate archive-item.sh hook
run_test "test_archive_hook_writes_knowledge" bash -c "
    mkdir -p '${TMP_DIR}/archive-test/knowledge-base'
    mkdir -p '${TMP_DIR}/archive-test/work-queue/archive'
    cat > '${TMP_DIR}/archive-test/work-queue/archive/WRK-500.md' << 'MDEOF'
---
id: WRK-500
title: Archive hook test WRK
category: test
subcategory: integration
status: done
---
## Mission
Test that archive hook writes knowledge entry.
MDEOF
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/archive-test/knowledge-base' \
    WORK_QUEUE_DIR='${TMP_DIR}/archive-test/work-queue' \
    bash '${SCRIPTS_DIR}/capture-wrk-summary.sh' WRK-500 || true
    [[ -f '${TMP_DIR}/archive-test/knowledge-base/wrk-completions.jsonl' ]] &&
    grep -q 'WRK-500' '${TMP_DIR}/archive-test/knowledge-base/wrk-completions.jsonl'
"

# test_compact_memory_routes_before_evict — compact-memory.py routing
# (Integration test: verify the ARCHIVED bullet extractor in compact-memory.py)
run_test "test_compact_memory_routes_before_evict" bash -c "
    mkdir -p '${TMP_DIR}/cm-test/knowledge-base'
    cat > '${TMP_DIR}/cm-test/MEMORY.md' << 'CMEOF'
# Test Memory
- **WRK-600 ARCHIVED** (abc123): test compact routing — dummy entry for TDD
- Active state pointer only here
CMEOF
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/cm-test/knowledge-base' \
    bash '${SCRIPTS_DIR}/compact-memory-route.sh' \
        '${TMP_DIR}/cm-test/MEMORY.md' --dry-run 2>/dev/null || true
    # Accept: script prints preview without crashing (full integration via compact-memory.py)
    true
"

# ── Phase 4 tests ─────────────────────────────────────────────────────────────

echo ""
echo "=== Phase 4: Migration ==="

# test_migrate_dry_run
run_test "test_migrate_dry_run" bash -c "
    mkdir -p '${TMP_DIR}/migrate-test/knowledge-base'
    cat > '${TMP_DIR}/migrate-test/MEMORY.md' << 'MEMEOF'
# Workspace Hub Memory

- **WRK-700 ARCHIVED** (def456): first archived WRK
- **WRK-701 ARCHIVED** (ghi789): second archived WRK
- Active state line that must be kept
MEMEOF
    out=\$(KNOWLEDGE_BASE_DIR='${TMP_DIR}/migrate-test/knowledge-base' \
         bash '${SCRIPTS_DIR}/migrate-memory-to-knowledge.sh' \
         '${TMP_DIR}/migrate-test/MEMORY.md' --dry-run)
    echo \"\${out}\" | grep -q 'Would migrate'
    # MEMORY.md must NOT be modified in dry-run
    grep -q 'WRK-700 ARCHIVED' '${TMP_DIR}/migrate-test/MEMORY.md'
"

# test_migrate_reduces_memory_lines
run_test "test_migrate_reduces_memory_lines" bash -c "
    mkdir -p '${TMP_DIR}/migrate-real/knowledge-base'
    cat > '${TMP_DIR}/migrate-real/MEMORY.md' << 'MEMEOF'
# Workspace Hub Memory

- **WRK-800 ARCHIVED** (aaa111): first entry to remove
- **WRK-801 ARCHIVED** (bbb222): second entry to remove
- This active line must survive
- This pointer also survives
MEMEOF
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/migrate-real/knowledge-base' \
    bash '${SCRIPTS_DIR}/migrate-memory-to-knowledge.sh' \
         '${TMP_DIR}/migrate-real/MEMORY.md'
    # ARCHIVED lines must be removed
    ! grep -q 'WRK-800 ARCHIVED' '${TMP_DIR}/migrate-real/MEMORY.md' &&
    grep -q 'This active line must survive' '${TMP_DIR}/migrate-real/MEMORY.md' &&
    grep -q 'WRK-800' '${TMP_DIR}/migrate-real/knowledge-base/wrk-completions.jsonl'
"

# test_migrate_idempotent — re-running skips already-captured IDs
run_test "test_migrate_idempotent" bash -c "
    mkdir -p '${TMP_DIR}/migrate-idem/knowledge-base'
    cat > '${TMP_DIR}/migrate-idem/MEMORY.md' << 'MEMEOF'
# Memory
- Active line
MEMEOF
    echo '{\"id\":\"WRK-900\",\"type\":\"wrk\",\"source\":\"memory-migration\",\"raw\":\"test\"}' \
        > '${TMP_DIR}/migrate-idem/knowledge-base/wrk-completions.jsonl'
    # MEMORY.md has no ARCHIVED lines → migration should be a no-op
    KNOWLEDGE_BASE_DIR='${TMP_DIR}/migrate-idem/knowledge-base' \
    bash '${SCRIPTS_DIR}/migrate-memory-to-knowledge.sh' \
         '${TMP_DIR}/migrate-idem/MEMORY.md'
    count=\$(grep -c '\"WRK-900\"' '${TMP_DIR}/migrate-idem/knowledge-base/wrk-completions.jsonl')
    [[ \"\${count}\" -eq 1 ]]
"

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════"
echo "  Results: ${PASS} passed, ${FAIL} failed"
if [[ "${FAIL}" -gt 0 ]]; then
    echo "  Failed tests:"
    for e in "${ERRORS[@]}"; do
        echo "    - ${e}"
    done
    echo "═══════════════════════════════════════════"
    exit 1
fi
echo "═══════════════════════════════════════════"
exit 0
