#!/usr/bin/env bash
# test-wrk1130-feature-tooling.sh — TDD tests for feature layer tooling scripts
# Tests: new-feature.sh, feature-status.sh, feature-close-check.sh
# Hermetic: all operations run inside a TMPDIR fixture; real queue is never touched.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
NEW_FEATURE="${REPO_ROOT}/scripts/work-queue/new-feature.sh"
FEAT_STATUS="${REPO_ROOT}/scripts/work-queue/feature-status.sh"
FEAT_CLOSE="${REPO_ROOT}/scripts/work-queue/feature-close-check.sh"

PASS=0; FAIL=0; TOTAL=0

# ── Fixture setup ─────────────────────────────────────────────────────────────
TMPDIR_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_ROOT"' EXIT

WQROOT="${TMPDIR_ROOT}/.claude/work-queue"
mkdir -p "${WQROOT}/pending" "${WQROOT}/working" "${WQROOT}/archived" "${WQROOT}/blocked"

# Synthetic spec file with ## Decomposition table (3 children, child-b depends on child-a)
SPEC_DIR="${TMPDIR_ROOT}/specs/wrk/WRK-9001"
mkdir -p "$SPEC_DIR"
SPEC_FILE="${SPEC_DIR}/feature-spec.md"
cat > "$SPEC_FILE" <<'SPEC'
# Synthetic Feature Spec for WRK-9001

## Mission

Test feature decomposition.

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Alpha task | Does the first thing | — | claude | |
| child-b | Beta task | Does the second thing | child-a | codex | |
| child-c | Gamma task | Does the third thing | child-a | gemini | |

### Child: child-a

**Acceptance Criteria:**
- [ ] Alpha done

### Child: child-b

**Acceptance Criteria:**
- [ ] Beta done

### Child: child-c

**Acceptance Criteria:**
- [ ] Gamma done
SPEC

# Synthetic feature WRK file
FEATURE_FILE="${WQROOT}/working/WRK-9001.md"
cat > "$FEATURE_FILE" <<'FEATURE'
---
id: WRK-9001
title: "Synthetic Feature for Testing"
type: feature
status: coordinating
priority: high
complexity: complex
created_at: "2026-03-11"
target_repos: [workspace-hub]
computer: ace-linux-1
category: harness
subcategory: testing
children: []
plan_reviewed: true
plan_approved: true
percent_complete: 0
---

## Mission

Synthetic feature for hermetic test fixture.
FEATURE
# Inject spec_ref pointing to our temp spec
echo "spec_ref: ${SPEC_FILE}" >> "$FEATURE_FILE"

# ── Helpers ───────────────────────────────────────────────────────────────────
pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); }

assert_exit() {
    local label="$1" expected="$2"; shift 2
    local actual=0
    "$@" >/dev/null 2>&1 || actual=$?
    TOTAL=$((TOTAL + 1))
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected exit=$expected, got exit=$actual)"
        FAIL=$((FAIL + 1))
    fi
}

assert_output_contains() {
    local label="$1" pattern="$2"; shift 2
    TOTAL=$((TOTAL + 1))
    local out
    out=$("$@" 2>&1) || true
    if echo "$out" | grep -qE "$pattern"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (pattern '$pattern' not found in output)"
        echo "    output: $out"
        FAIL=$((FAIL + 1))
    fi
}

# ── Verify scripts exist (pre-flight — these FAIL before implementation) ──────
echo ""
echo "=== Pre-flight: script existence checks ==="
for script in "$NEW_FEATURE" "$FEAT_STATUS" "$FEAT_CLOSE"; do
    TOTAL=$((TOTAL + 1))
    if [[ -x "$script" ]]; then
        echo "  PASS: $(basename "$script") exists and is executable"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $(basename "$script") missing or not executable"
        FAIL=$((FAIL + 1))
    fi
done

# Guard: if scripts don't exist, skip functional tests to keep output readable
if [[ ! -x "$NEW_FEATURE" || ! -x "$FEAT_STATUS" || ! -x "$FEAT_CLOSE" ]]; then
    echo ""
    echo "=== Skipping functional tests (scripts not yet implemented) ==="
    echo "Results: ${PASS} passed, ${FAIL} failed out of ${TOTAL}"
    exit 1
fi

# ── T1: new-feature.sh exits 0 on valid feature WRK ──────────────────────────
echo ""
echo "=== T1: new-feature.sh creates child WRK files ==="
output=$(WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9001 2>&1) || {
    echo "  FAIL: new-feature.sh exited non-zero"
    echo "    output: $output"
    FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1))
}

# Count child files created in pending/
child_count=$(ls "${WQROOT}/pending/WRK-"*.md 2>/dev/null | wc -l || echo 0)
TOTAL=$((TOTAL + 1))
if [[ "$child_count" -eq 3 ]]; then
    pass "T1a: 3 child WRK files created in pending/"
else
    fail "T1a: expected 3 child files, found $child_count"
fi

# ── T2: child WRKs have correct parent and category ──────────────────────────
echo ""
echo "=== T2: child WRK frontmatter correctness ==="
FIRST_CHILD=$(ls "${WQROOT}/pending/WRK-"*.md 2>/dev/null | head -1)
TOTAL=$((TOTAL + 1))
if [[ -n "$FIRST_CHILD" ]] && grep -q "^parent: WRK-9001" "$FIRST_CHILD"; then
    pass "T2a: first child has parent: WRK-9001"
else
    fail "T2a: first child missing parent: WRK-9001"
fi

TOTAL=$((TOTAL + 1))
if [[ -n "$FIRST_CHILD" ]] && grep -q "^category: harness" "$FIRST_CHILD"; then
    pass "T2b: first child inherits category: harness from feature"
else
    fail "T2b: first child missing inherited category: harness"
fi

# ── T3: blocked_by resolution — child-b should reference concrete WRK-ID ─────
echo ""
echo "=== T3: blocked_by resolved to concrete WRK-IDs ==="
# child-b depends on child-a; after resolution blocked_by should be WRK-NNNN not "child-a"
CHILD_B_FILE=$(grep -l "^title: \"Beta task\"" "${WQROOT}/pending/WRK-"*.md 2>/dev/null | head -1 || true)
TOTAL=$((TOTAL + 1))
if [[ -n "$CHILD_B_FILE" ]]; then
    blocked_val=$(grep "^blocked_by:" "$CHILD_B_FILE" | head -1)
    # should be WRK-NNNN form, not symbolic key
    if echo "$blocked_val" | grep -qE "WRK-[0-9]+"; then
        pass "T3a: child-b blocked_by contains concrete WRK-ID: $blocked_val"
    else
        fail "T3a: child-b blocked_by not resolved to WRK-ID: $blocked_val"
    fi
else
    fail "T3a: could not find child-b file (Beta task)"
fi

# child-c also depends on child-a — same check
CHILD_C_FILE=$(grep -l "^title: \"Gamma task\"" "${WQROOT}/pending/WRK-"*.md 2>/dev/null | head -1 || true)
TOTAL=$((TOTAL + 1))
if [[ -n "$CHILD_C_FILE" ]]; then
    blocked_val=$(grep "^blocked_by:" "$CHILD_C_FILE" | head -1)
    if echo "$blocked_val" | grep -qE "WRK-[0-9]+"; then
        pass "T3b: child-c blocked_by contains concrete WRK-ID: $blocked_val"
    else
        fail "T3b: child-c blocked_by not resolved to WRK-ID: $blocked_val"
    fi
else
    fail "T3b: could not find child-c file (Gamma task)"
fi

# child-a has no deps; blocked_by should be empty list
CHILD_A_FILE=$(grep -l "^title: \"Alpha task\"" "${WQROOT}/pending/WRK-"*.md 2>/dev/null | head -1 || true)
TOTAL=$((TOTAL + 1))
if [[ -n "$CHILD_A_FILE" ]]; then
    blocked_val=$(grep "^blocked_by:" "$CHILD_A_FILE" | head -1)
    if echo "$blocked_val" | grep -qE "blocked_by: \[\]"; then
        pass "T3c: child-a has blocked_by: []"
    else
        fail "T3c: child-a blocked_by not empty: $blocked_val"
    fi
else
    fail "T3c: could not find child-a file (Alpha task)"
fi

# ── T4: feature WRK children: field updated ───────────────────────────────────
echo ""
echo "=== T4: feature WRK children: list populated ==="
TOTAL=$((TOTAL + 1))
children_line=$(grep "^children:" "$FEATURE_FILE" | head -1)
if echo "$children_line" | grep -qE "WRK-[0-9]+"; then
    pass "T4: feature WRK children: populated with WRK IDs"
else
    fail "T4: feature WRK children: not updated: $children_line"
fi

# ── T5: feature-status.sh — set up 1 archived child, 2 pending ────────────────
echo ""
echo "=== T5: feature-status.sh shows correct completion ==="

# Mark one child as archived by creating it in archived/ dir and updating status
CHILD_IDS=($(ls "${WQROOT}/pending/WRK-"*.md 2>/dev/null | xargs -I{} basename {} .md))
if [[ ${#CHILD_IDS[@]} -ge 1 ]]; then
    ARCHIVE_CHILD="${CHILD_IDS[0]}"
    ARCHIVE_FILE="${WQROOT}/archived/${ARCHIVE_CHILD}.md"
    # Copy the pending file to archived and update status
    cp "${WQROOT}/pending/${ARCHIVE_CHILD}.md" "$ARCHIVE_FILE"
    # Update status in the archived copy
    sed -i 's/^status: .*/status: archived/' "$ARCHIVE_FILE"
    # Remove from pending (archived takes priority)
    rm "${WQROOT}/pending/${ARCHIVE_CHILD}.md"
fi

STATUS_OUTPUT=$(WORK_QUEUE_ROOT="$WQROOT" bash "$FEAT_STATUS" WRK-9001 2>&1) || true

TOTAL=$((TOTAL + 1))
if echo "$STATUS_OUTPUT" | grep -qE "1/3 archived \(33%\)"; then
    pass "T5a: feature-status.sh shows '1/3 archived (33%)'"
else
    fail "T5a: expected '1/3 archived (33%)'; got: $STATUS_OUTPUT"
fi

# ── T6: feature-close-check.sh exits 1 (not all archived) ────────────────────
echo ""
echo "=== T6: feature-close-check.sh exits 1 when not all archived ==="
assert_exit "T6: close-check exits 1 (children not done)" 1 \
    env WORK_QUEUE_ROOT="$WQROOT" bash "$FEAT_CLOSE" WRK-9001

# ── T7: feature-close-check.sh exits 0 when all archived ─────────────────────
echo ""
echo "=== T7: feature-close-check.sh exits 0 when all archived ==="
# Archive all remaining pending children
for child_file in "${WQROOT}/pending/WRK-"*.md; do
    [[ -f "$child_file" ]] || continue
    child_id=$(basename "$child_file" .md)
    cp "$child_file" "${WQROOT}/archived/${child_id}.md"
    sed -i 's/^status: .*/status: archived/' "${WQROOT}/archived/${child_id}.md"
    rm "$child_file"
done
assert_exit "T7: close-check exits 0 (all archived)" 0 \
    env WORK_QUEUE_ROOT="$WQROOT" bash "$FEAT_CLOSE" WRK-9001

# ── T8: new-feature.sh exits 1 when no children parsed ───────────────────────
echo ""
echo "=== T8: new-feature.sh exits 1 when no children in spec ==="
EMPTY_SPEC="${TMPDIR_ROOT}/specs/wrk/WRK-9002/empty-spec.md"
mkdir -p "$(dirname "$EMPTY_SPEC")"
cat > "$EMPTY_SPEC" <<'EMPTYSPEC'
# Empty Feature Spec

## Mission

No decomposition table here.

## Acceptance Criteria

- [ ] nothing
EMPTYSPEC

EMPTY_WRK="${WQROOT}/working/WRK-9002.md"
cat > "$EMPTY_WRK" <<EMPTYWRK
---
id: WRK-9002
title: "Empty feature"
type: feature
status: coordinating
children: []
category: harness
subcategory: testing
spec_ref: ${EMPTY_SPEC}
---
EMPTYWRK

assert_exit "T8: new-feature.sh exits 1 when no children parsed" 1 \
    env WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9002

# ── T9: Edge — block-list children: YAML parses correctly ────────────────────
echo ""
echo "=== T9: block-list children: YAML format parses correctly ==="
# feature-status.sh must handle block-list YAML format:
#   children:
#     - WRK-1001
#     - WRK-1002
BLOCK_LIST_WRK="${WQROOT}/working/WRK-9003.md"
DUMMY_CHILD1="${WQROOT}/archived/WRK-9090.md"
DUMMY_CHILD2="${WQROOT}/pending/WRK-9091.md"
cat > "$DUMMY_CHILD1" <<'DC'
---
id: WRK-9090
status: archived
---
DC
cat > "$DUMMY_CHILD2" <<'DC'
---
id: WRK-9091
status: pending
---
DC
cat > "$BLOCK_LIST_WRK" <<'BLWRK'
---
id: WRK-9003
title: "Block-list children format test"
type: feature
status: coordinating
children:
  - WRK-9090
  - WRK-9091
category: harness
subcategory: testing
BLWRK

BL_OUTPUT=$(WORK_QUEUE_ROOT="$WQROOT" bash "$FEAT_STATUS" WRK-9003 2>&1) || true
TOTAL=$((TOTAL + 1))
if echo "$BL_OUTPUT" | grep -qE "1/2 archived \(50%\)"; then
    pass "T9: block-list children: parsed correctly, shows '1/2 archived (50%)'"
else
    fail "T9: block-list parsing failed; expected '1/2 archived (50%)'; got: $BL_OUTPUT"
fi

# ── T10: Adoption — parent matches → no-op (idempotent) ──────────────────────
echo ""
echo "=== T10: adoption when parent: matches feature → no-op ==="
ADOPT_SPEC="${TMPDIR_ROOT}/specs/wrk/WRK-9004/adopt-spec.md"
mkdir -p "$(dirname "$ADOPT_SPEC")"
# Create a target WRK that already has parent: WRK-9004
EXISTING_ADOPT="${WQROOT}/pending/WRK-9099.md"
cat > "$EXISTING_ADOPT" <<'EWS'
---
id: WRK-9099
title: "Existing WRK to be adopted"
status: pending
parent: WRK-9004
blocked_by: []
category: harness
subcategory: testing
---
EWS
cat > "$ADOPT_SPEC" <<ASPEC
# Adopt Spec

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| adopt-a | Adopt task | Adopts existing | — | claude | WRK-9099 |

ASPEC

ADOPT_WRK="${WQROOT}/working/WRK-9004.md"
cat > "$ADOPT_WRK" <<AWRK
---
id: WRK-9004
title: "Adopt feature"
type: feature
status: coordinating
children: []
category: harness
subcategory: testing
spec_ref: ${ADOPT_SPEC}
---
AWRK

ADOPT_OUT=$(WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9004 2>&1)
exit_code=$?
TOTAL=$((TOTAL + 1))
if [[ $exit_code -eq 0 ]]; then
    pass "T10a: adoption of already-parented WRK → exit 0 (no-op)"
else
    fail "T10a: adoption idempotency failed, exit $exit_code; output: $ADOPT_OUT"
fi
# Verify parent field is unchanged (still WRK-9004)
TOTAL=$((TOTAL + 1))
if grep -q "^parent: WRK-9004" "$EXISTING_ADOPT"; then
    pass "T10b: adopted WRK parent: field unchanged"
else
    fail "T10b: parent field changed unexpectedly: $(grep parent "$EXISTING_ADOPT")"
fi

# ── T11: Adoption — parent: differs → hard exit 1 ────────────────────────────
echo ""
echo "=== T11: adoption when parent: differs → hard exit 1 ==="
DIFF_ADOPT_SPEC="${TMPDIR_ROOT}/specs/wrk/WRK-9005/diff-adopt-spec.md"
mkdir -p "$(dirname "$DIFF_ADOPT_SPEC")"
# Create a target WRK with a DIFFERENT parent
EXISTING_DIFF="${WQROOT}/pending/WRK-9098.md"
cat > "$EXISTING_DIFF" <<'EWD'
---
id: WRK-9098
title: "WRK belonging to a different feature"
status: pending
parent: WRK-8888
blocked_by: []
category: harness
subcategory: testing
---
EWD
cat > "$DIFF_ADOPT_SPEC" <<DSPEC
# Diff-parent Adopt Spec

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| diff-a | Conflict adopt | Tries to adopt WRK with different parent | — | claude | WRK-9098 |

DSPEC

DIFF_WRK="${WQROOT}/working/WRK-9005.md"
cat > "$DIFF_WRK" <<DWRK
---
id: WRK-9005
title: "Diff-parent feature"
type: feature
status: coordinating
children: []
category: harness
subcategory: testing
spec_ref: ${DIFF_ADOPT_SPEC}
---
DWRK

assert_exit "T11: adoption with different parent → exit 1" 1 \
    env WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9005

# ── T12: Unresolved symbolic Depends on key → exit 1 ─────────────────────────
echo ""
echo "=== T12: unresolved Depends on key → exit 1 ==="
UNRES_SPEC="${TMPDIR_ROOT}/specs/wrk/WRK-9006/unresolved-spec.md"
mkdir -p "$(dirname "$UNRES_SPEC")"
cat > "$UNRES_SPEC" <<'USPEC'
# Unresolved Dep Spec

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| first | First task | Does first | — | claude | |
| second | Second task | Depends on ghost key | ghost-key | claude | |

USPEC

UNRES_WRK="${WQROOT}/working/WRK-9006.md"
cat > "$UNRES_WRK" <<UWRK
---
id: WRK-9006
title: "Unresolved-dep feature"
type: feature
status: coordinating
children: []
category: harness
subcategory: testing
spec_ref: ${UNRES_SPEC}
---
UWRK

assert_exit "T12: unresolved symbolic dep key → exit 1" 1 \
    env WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9006

# ── T13: dep_graph.py --feature exits 0 and prints feature tree ───────────────
echo ""
echo "=== T13: dep_graph.py --feature exits 0 and prints tree ==="
DEP_GRAPH="${REPO_ROOT}/scripts/work-queue/dep_graph.py"

# Build hermetic queue with a feature + 2 children
DG_ROOT="${TMPDIR_ROOT}/dg-queue/.claude/work-queue"
mkdir -p "${DG_ROOT}/pending" "${DG_ROOT}/working" "${DG_ROOT}/archived"

cat > "${DG_ROOT}/working/WRK-8001.md" <<'FWRK'
---
id: WRK-8001
title: "DG Test Feature"
type: feature
status: coordinating
children: [WRK-8002, WRK-8003]
---
FWRK

cat > "${DG_ROOT}/archived/WRK-8002.md" <<'CWA'
---
id: WRK-8002
title: "DG Child A"
status: archived
orchestrator: claude
blocked_by: []
parent: WRK-8001
---
CWA

cat > "${DG_ROOT}/pending/WRK-8003.md" <<'CWB'
---
id: WRK-8003
title: "DG Child B"
status: pending
orchestrator: codex
blocked_by: [WRK-8002]
parent: WRK-8001
---
CWB

DG_OUT=$(uv run --no-project python "$DEP_GRAPH" \
    --feature WRK-8001 \
    --queue-root "${DG_ROOT}" 2>&1)
DG_EXIT=$?

TOTAL=$((TOTAL + 1))
if [[ $DG_EXIT -eq 0 ]]; then
    pass "T13a: dep_graph.py --feature exits 0"
else
    fail "T13a: dep_graph.py --feature exited $DG_EXIT; output: $DG_OUT"
fi

TOTAL=$((TOTAL + 1))
if echo "$DG_OUT" | grep -q "WRK-8001"; then
    pass "T13b: output contains feature WRK-8001"
else
    fail "T13b: output missing WRK-8001; got: $DG_OUT"
fi

TOTAL=$((TOTAL + 1))
if echo "$DG_OUT" | grep -q "WRK-8002"; then
    pass "T13c: output contains child WRK-8002"
else
    fail "T13c: output missing WRK-8002; got: $DG_OUT"
fi

TOTAL=$((TOTAL + 1))
if echo "$DG_OUT" | grep -q "WRK-8003"; then
    pass "T13d: output contains child WRK-8003"
else
    fail "T13d: output missing WRK-8003; got: $DG_OUT"
fi

# ── T14: missing child → [missing] placeholder, still exits 0 ────────────────
echo ""
echo "=== T14: missing child → [missing] placeholder, exits 0 ==="
cat > "${DG_ROOT}/working/WRK-8010.md" <<'FWRK2'
---
id: WRK-8010
title: "Feature with ghost child"
type: feature
status: coordinating
children: [WRK-8011, WRK-9999]
---
FWRK2

cat > "${DG_ROOT}/pending/WRK-8011.md" <<'RWA'
---
id: WRK-8011
title: "Real Child"
status: pending
orchestrator: claude
blocked_by: []
parent: WRK-8010
---
RWA

MISS_OUT=$(uv run --no-project python "$DEP_GRAPH" \
    --feature WRK-8010 \
    --queue-root "${DG_ROOT}" 2>&1)
MISS_EXIT=$?

TOTAL=$((TOTAL + 1))
if [[ $MISS_EXIT -eq 0 ]]; then
    pass "T14a: missing child does not crash, exits 0"
else
    fail "T14a: missing child caused non-zero exit $MISS_EXIT; output: $MISS_OUT"
fi

TOTAL=$((TOTAL + 1))
if echo "$MISS_OUT" | grep -qiE "missing|WRK-9999"; then
    pass "T14b: missing child shows placeholder (WRK-9999 or [missing])"
else
    fail "T14b: missing child placeholder not shown; got: $MISS_OUT"
fi

# ── T15: --feature does not affect existing dep_graph behavior ────────────────
echo ""
echo "=== T15: existing dep_graph --summary still works (no regression) ==="
SUMM_OUT=$(uv run --no-project python "$DEP_GRAPH" \
    --summary \
    --queue-root "${DG_ROOT}" 2>&1)
SUMM_EXIT=$?

TOTAL=$((TOTAL + 1))
if [[ $SUMM_EXIT -eq 0 ]]; then
    pass "T15a: --summary exits 0 after --feature implementation"
else
    fail "T15a: --summary exited $SUMM_EXIT; output: $SUMM_OUT"
fi

TOTAL=$((TOTAL + 1))
if echo "$SUMM_OUT" | grep -q "dep-graph"; then
    pass "T15b: --summary output contains [dep-graph] prefix"
else
    fail "T15b: --summary output missing [dep-graph]; got: $SUMM_OUT"
fi

# ── T16: block-list children: YAML format in dep_graph.py --feature ───────────
echo ""
echo "=== T16: block-list children: YAML format parses in dep_graph --feature ==="
cat > "${DG_ROOT}/working/WRK-8020.md" <<'FWRK3'
---
id: WRK-8020
title: "Block-list children feature"
type: feature
status: coordinating
children:
  - WRK-8021
  - WRK-8022
---
FWRK3

cat > "${DG_ROOT}/pending/WRK-8021.md" <<'BLA'
---
id: WRK-8021
title: "Block-list child A"
status: pending
orchestrator: claude
blocked_by: []
parent: WRK-8020
---
BLA

cat > "${DG_ROOT}/pending/WRK-8022.md" <<'BLB'
---
id: WRK-8022
title: "Block-list child B"
status: pending
orchestrator: codex
blocked_by: [WRK-8021]
parent: WRK-8020
---
BLB

BL16_OUT=$(uv run --no-project python "$DEP_GRAPH" \
    --feature WRK-8020 \
    --queue-root "${DG_ROOT}" 2>&1)
BL16_EXIT=$?

TOTAL=$((TOTAL + 1))
if [[ $BL16_EXIT -eq 0 ]]; then
    pass "T16a: block-list children parsed correctly, exits 0"
else
    fail "T16a: block-list parse failed, exit $BL16_EXIT; output: $BL16_OUT"
fi

TOTAL=$((TOTAL + 1))
if echo "$BL16_OUT" | grep -q "WRK-8021" && echo "$BL16_OUT" | grep -q "WRK-8022"; then
    pass "T16b: both block-list children appear in output"
else
    fail "T16b: block-list children missing from output; got: $BL16_OUT"
fi

# ── T17: re-run guard exits 1 when children already populated ─────────────────
echo ""
echo "=== T17: new-feature.sh re-run guard exits 1 when children already populated ==="
RERUN_SPEC="${TMPDIR_ROOT}/specs/wrk/WRK-9007/rerun-spec.md"
mkdir -p "$(dirname "$RERUN_SPEC")"
cat > "$RERUN_SPEC" <<'RSPEC'
# Rerun Guard Spec

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| rerun-a | Rerun task | Does a thing | — | claude | |

RSPEC

# Feature WRK with children: already populated (non-empty)
RERUN_WRK="${WQROOT}/working/WRK-9007.md"
cat > "$RERUN_WRK" <<RWRK
---
id: WRK-9007
title: "Rerun guard test feature"
type: feature
status: coordinating
children: [WRK-001]
category: harness
subcategory: testing
spec_ref: ${RERUN_SPEC}
---
RWRK

assert_exit "T17a: new-feature.sh exits 1 when children already populated" 1 \
    env WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9007

# Verify children: field is unchanged after the guard fires
TOTAL=$((TOTAL + 1))
children_after=$(grep "^children:" "$RERUN_WRK" | head -1)
if echo "$children_after" | grep -qE "WRK-001"; then
    pass "T17b: children: field unchanged after re-run guard fired"
else
    fail "T17b: children: field changed unexpectedly: $children_after"
fi

# ── T18: children: written inside frontmatter when key was absent ─────────────
echo ""
echo "=== T18: children: inserted inside frontmatter (not after closing ---) ==="
T18_SPEC="${TMPDIR_ROOT}/specs/wrk/WRK-9008/t18-spec.md"
mkdir -p "$(dirname "$T18_SPEC")"
cat > "$T18_SPEC" <<'T18SPEC'
## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| t18-a | T18 task | Single child for T18 | — | claude | |

T18SPEC

# Feature WRK with NO children: field in frontmatter at all
T18_WRK="${WQROOT}/working/WRK-9008.md"
cat > "$T18_WRK" <<T18WRK
---
id: WRK-9008
title: "T18 no-children-key feature"
type: feature
status: coordinating
priority: high
complexity: medium
created_at: "2026-03-11"
target_repos: [workspace-hub]
computer: ace-linux-1
category: harness
subcategory: testing
spec_ref: ${T18_SPEC}
---

## Mission

Feature with no children: key — tests frontmatter insertion.
T18WRK

T18_OUT=$(WORK_QUEUE_ROOT="$WQROOT" bash "$NEW_FEATURE" WRK-9008 2>&1)
T18_EXIT=$?
TOTAL=$((TOTAL + 1))
if [[ $T18_EXIT -eq 0 ]]; then
    pass "T18a: new-feature.sh exits 0 for feature with no children: key"
else
    fail "T18a: new-feature.sh exited $T18_EXIT; output: $T18_OUT"
fi

# children: must appear INSIDE the frontmatter (before the closing ---)
TOTAL=$((TOTAL + 1))
if python3 - "$T18_WRK" <<'PYCHECK'
import re, sys
with open(sys.argv[1]) as f:
    content = f.read()
m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not m:
    print("no frontmatter found"); sys.exit(1)
fm_body = m.group(1)
if re.search(r'^children:\s*\[WRK-', fm_body, re.MULTILINE):
    sys.exit(0)
print("children: not found inside frontmatter")
print("frontmatter body:", repr(fm_body))
sys.exit(1)
PYCHECK
then
    pass "T18b: children: appears inside YAML frontmatter block"
else
    fail "T18b: children: not inside frontmatter"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Results ==="
echo "Total: ${TOTAL}  |  PASS: ${PASS}  |  FAIL: ${FAIL}"
[[ $FAIL -eq 0 ]] && echo "ALL TESTS PASSED" || echo "SOME TESTS FAILED"
[[ $FAIL -eq 0 ]]
