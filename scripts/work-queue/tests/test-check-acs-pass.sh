#!/usr/bin/env bash
# TDD tests for check-acs-pass.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CHECK="$SCRIPT_DIR/check-acs-pass.sh"
TMPDIR_BASE=$(mktemp -d)
PASS=0
FAIL=0

cleanup() { rm -rf "$TMPDIR_BASE"; }
trap cleanup EXIT

assert_exit() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (expected exit $expected, got $actual)"
    FAIL=$((FAIL + 1))
  fi
}

assert_output_contains() {
  local desc="$1" pattern="$2" output="$3"
  if echo "$output" | grep -q "$pattern"; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (output missing '$pattern')"
    FAIL=$((FAIL + 1))
  fi
}

# --- Setup fake queue dirs ---
QUEUE="$TMPDIR_BASE/work-queue"
mkdir -p "$QUEUE/working" "$QUEUE/pending" "$QUEUE/blocked"

# --- Test 1: All ACs complete → exit 0 ---
cat > "$QUEUE/working/WRK-9901.md" <<'EOF'
---
id: WRK-9901
title: "test item all complete"
---
# Test Item

## Acceptance Criteria

- [x] First AC done
- [x] Second AC done
- [x] Third AC done
EOF

output=$("$CHECK" WRK-9901 --queue-dir "$QUEUE" 2>&1) || true
rc=$?
# Re-run to capture exit code properly
set +e
"$CHECK" WRK-9901 --queue-dir "$QUEUE" > /dev/null 2>&1
rc=$?
set -e
assert_exit "All ACs complete → exit 0" 0 "$rc"

# --- Test 2: Some ACs incomplete → exit 1 ---
cat > "$QUEUE/working/WRK-9902.md" <<'EOF'
---
id: WRK-9902
title: "test item incomplete"
---
# Test Item

## Acceptance Criteria

- [x] First AC done
- [ ] Second AC not done
- [x] Third AC done
EOF

set +e
output=$("$CHECK" WRK-9902 --queue-dir "$QUEUE" 2>&1)
rc=$?
set -e
assert_exit "Some ACs incomplete → exit 1" 1 "$rc"
assert_output_contains "Lists incomplete AC" "Second AC not done" "$output"

# --- Test 3: No AC section → exit 0 with warning ---
cat > "$QUEUE/pending/WRK-9903.md" <<'EOF'
---
id: WRK-9903
title: "test item no ACs"
---
# Test Item

## What

Just a description, no acceptance criteria section.
EOF

set +e
output=$("$CHECK" WRK-9903 --queue-dir "$QUEUE" 2>&1)
rc=$?
set -e
assert_exit "No AC section → exit 0" 0 "$rc"
assert_output_contains "Warning on missing ACs" "warning" "$output"

# --- Test 4: All ACs incomplete → exit 1 ---
cat > "$QUEUE/pending/WRK-9904.md" <<'EOF'
---
id: WRK-9904
title: "test item all incomplete"
---
# Test Item

## Acceptance Criteria

- [ ] First not done
- [ ] Second not done
EOF

set +e
output=$("$CHECK" WRK-9904 --queue-dir "$QUEUE" 2>&1)
rc=$?
set -e
assert_exit "All ACs incomplete → exit 1" 1 "$rc"
assert_output_contains "Lists first incomplete" "First not done" "$output"
assert_output_contains "Lists second incomplete" "Second not done" "$output"

# --- Test 5: WRK not found → exit 2 ---
set +e
output=$("$CHECK" WRK-9999 --queue-dir "$QUEUE" 2>&1)
rc=$?
set -e
assert_exit "WRK not found → exit 2" 2 "$rc"

# --- Test 6: Mixed checkbox styles (nested, bold) still detected ---
cat > "$QUEUE/working/WRK-9905.md" <<'EOF'
---
id: WRK-9905
title: "test mixed formatting"
---
# Test Item

## Acceptance Criteria

- [x] **Bold AC** done
- [ ] `Code AC` not done
- [x] Plain AC done
EOF

set +e
output=$("$CHECK" WRK-9905 --queue-dir "$QUEUE" 2>&1)
rc=$?
set -e
assert_exit "Mixed formatting incomplete → exit 1" 1 "$rc"
assert_output_contains "Detects code-formatted incomplete" "Code AC" "$output"

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
