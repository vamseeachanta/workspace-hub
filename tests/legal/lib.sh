#!/usr/bin/env bash
# =============================================================================
# Shared helpers for legal-sanity-scan candidate-resolver tests.
#
# Every test builds a throwaway fake workspace (a copy of the scanner script
# anchored under <tmp>/.../workspace-hub) plus fake git-init'd repos under
# mktemp -d. Real repos are never scanned.
# =============================================================================
set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"
# Overridable so a reviewer can retro-check that these tests fail against an
# older scanner revision (e.g. LEGAL_SCAN_TEST_SCRIPT=/tmp/old-scan.sh).
SCRIPT_UNDER_TEST="${LEGAL_SCAN_TEST_SCRIPT:-$REPO_ROOT/scripts/legal/legal-sanity-scan.sh}"

fail() { echo "FAIL: $*" >&2; exit 1; }

# make_workspace <parent_dir>
# Creates <parent_dir>/workspace-hub containing a copy of the scanner and a
# minimal deny list; git-inits it (zero submodules). Echoes the fake
# workspace root path.
make_workspace() {
  local parent="$1"
  local ws="$parent/workspace-hub"
  mkdir -p "$ws/scripts/legal"
  cp "$SCRIPT_UNDER_TEST" "$ws/scripts/legal/legal-sanity-scan.sh"
  chmod +x "$ws/scripts/legal/legal-sanity-scan.sh"
  git -C "$ws" init -q
  cat > "$ws/.legal-deny-list.yaml" <<'EOF'
deny_patterns:
  - pattern: "FORBID_MARKER_X"
    case_sensitive: true
EOF
  printf '%s\n' "$ws"
}

# make_repo <path> [marker]
# git-inits a fake repo at <path>; when a marker is given, adds a file
# containing it (so a scan of that repo trips the deny list).
make_repo() {
  local path="$1"
  local marker="${2:-}"
  mkdir -p "$path"
  git -C "$path" init -q
  echo "clean content" > "$path/readme.txt"
  if [[ -n "$marker" ]]; then
    echo "$marker" > "$path/hit.txt"
  fi
  return 0
}

# run_scan <workspace_root> <args...>
# Runs the copied scanner; captures combined output in RUN_OUT and the exit
# code in RUN_RC (never aborts the test on non-zero).
run_scan() {
  local ws="$1"; shift
  set +e
  RUN_OUT="$("$ws/scripts/legal/legal-sanity-scan.sh" "$@" 2>&1)"
  RUN_RC=$?
  set -e
  return 0
}

# assert_contains <haystack> <needle> <message>
assert_contains() {
  local haystack="$1" needle="$2" message="$3"
  if ! printf '%s\n' "$haystack" | grep -F -- "$needle" >/dev/null; then
    fail "$message — expected to find '$needle' in output:
$haystack"
  fi
  return 0
}

# assert_not_contains <haystack> <needle> <message>
assert_not_contains() {
  local haystack="$1" needle="$2" message="$3"
  if printf '%s\n' "$haystack" | grep -F -- "$needle" >/dev/null; then
    fail "$message — did not expect '$needle' in output:
$haystack"
  fi
  return 0
}
