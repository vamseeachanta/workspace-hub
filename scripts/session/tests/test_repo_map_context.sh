#!/usr/bin/env bash
# test_repo_map_context.sh — TDD tests for repo-map-context.sh
# Usage: bash scripts/session/tests/test_repo_map_context.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${SCRIPT_DIR}/../repo-map-context.sh"
FIXTURES="${SCRIPT_DIR}/fixtures/repo_map"
PASS=0; FAIL=0

mkdir -p "$FIXTURES"

# Minimal repo-map.yaml fixture
cat > "$FIXTURES/repo-map.yaml" << 'EOF'
repos:
- name: digitalmodel
  path: digitalmodel
  purpose: "Engineering digital twin"
  test_command: PYTHONPATH=src uv run python -m pytest
- name: assetutilities
  path: assetutilities
  purpose: "Shared engineering utilities"
  test_command: uv run python -m pytest tests/
EOF

# WRK fixture with known target_repos
cat > "$FIXTURES/WRK-9901.md" << 'EOF'
---
id: WRK-9901
title: "test wrk"
status: working
target_repos:
  - digitalmodel
---
## Mission
Test fixture
EOF

# WRK fixture with workspace-hub (not in repo-map)
cat > "$FIXTURES/WRK-9902.md" << 'EOF'
---
id: WRK-9902
title: "hub wrk"
status: working
target_repos:
  - workspace-hub
---
## Mission
Test fixture
EOF

# WRK fixture with no target_repos
cat > "$FIXTURES/WRK-9903.md" << 'EOF'
---
id: WRK-9903
title: "no repos"
status: working
---
## Mission
Test fixture
EOF

# WRK fixture with unknown repo
cat > "$FIXTURES/WRK-9904.md" << 'EOF'
---
id: WRK-9904
title: "unknown repo"
status: working
target_repos:
  - unknownrepo
---
## Mission
Test fixture
EOF

run_test() {
    local name="$1" wrk_file="$2" expected_pattern="$3" expect_match="$4"
    local out exit_code=0
    out=$(bash "$SCRIPT" --wrk-file "$wrk_file" --repo-map "$FIXTURES/repo-map.yaml" 2>/dev/null) || exit_code=$?
    if [[ "$expect_match" == "yes" ]]; then
        if echo "$out" | grep -qE "$expected_pattern"; then
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        else
            echo "  FAIL: $name — pattern '$expected_pattern' not in: '$out'"
            FAIL=$((FAIL + 1))
        fi
    else
        if echo "$out" | grep -qE "$expected_pattern" && [[ -n "$expected_pattern" ]]; then
            echo "  FAIL: $name — unexpected pattern '$expected_pattern' in: '$out'"
            FAIL=$((FAIL + 1))
        else
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        fi
    fi
}

run_exit_test() {
    local name="$1" wrk_file="$2" expected_exit="$3"
    local exit_code=0
    bash "$SCRIPT" --wrk-file "$wrk_file" --repo-map "$FIXTURES/repo-map.yaml" >/dev/null 2>/dev/null || exit_code=$?
    if [[ "$exit_code" == "$expected_exit" ]]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name — expected exit $expected_exit, got $exit_code"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== test_repo_map_context.sh ==="

run_test      "known_repo"         "$FIXTURES/WRK-9901.md" "digitalmodel"  "yes"
run_test      "workspace_hub_noop" "$FIXTURES/WRK-9902.md" "digitalmodel"  "no"
run_test      "no_target_repos"    "$FIXTURES/WRK-9903.md" "."             "no"
run_test      "unknown_repo_note"  "$FIXTURES/WRK-9904.md" "[Nn]ot.found|not in repo-map" "yes"
run_exit_test "always_exits_0"     "$FIXTURES/WRK-9901.md" 0
run_exit_test "missing_wrk_exits_0" "/nonexistent/WRK.md"  0

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
