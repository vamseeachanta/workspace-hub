#!/usr/bin/env bash
# test_gsd_researcher_nightly.sh — behavioral tests for gsd-researcher-nightly.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="${SCRIPT_DIR}/../gsd-researcher-nightly.sh"

pass_count=0
fail_count=0
total_count=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  total_count=$((total_count + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label}"
    echo "        expected: ${expected}"
    echo "        actual:   ${actual}"
    fail_count=$((fail_count + 1))
  fi
}

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  total_count=$((total_count + 1))
  if printf '%s' "$haystack" | grep -qF "$needle"; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label}"
    echo "        expected to contain: ${needle}"
    echo "        actual: ${haystack}"
    fail_count=$((fail_count + 1))
  fi
}

assert_file_exists() {
  local label="$1" path="$2"
  total_count=$((total_count + 1))
  if [[ -f "$path" ]]; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label} — file not found: ${path}"
    fail_count=$((fail_count + 1))
  fi
}

assert_not_exists() {
  local label="$1" path="$2"
  total_count=$((total_count + 1))
  if [[ ! -e "$path" ]]; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label} — unexpected path exists: ${path}"
    fail_count=$((fail_count + 1))
  fi
}

TMP_ROOT=$(mktemp -d)
trap 'rm -rf "$TMP_ROOT"' EXIT

setup_workspace() {
  local ws="$TMP_ROOT/ws"
  local bindir="$TMP_ROOT/bin"
  rm -rf "$ws" "$bindir"
  mkdir -p "$ws/scripts/cron" "$ws/scripts/lib" "$ws/scripts" "$ws/.planning/research" "$ws/logs/research" "$ws/logs/notifications" "$bindir"
  cp "$SOURCE_SCRIPT" "$ws/scripts/cron/gsd-researcher-nightly.sh"
  chmod +x "$ws/scripts/cron/gsd-researcher-nightly.sh"

  cat > "$ws/.planning/PROJECT.md" <<'EOF'
# Project
Useful project context.
EOF
  cat > "$ws/.planning/ROADMAP.md" <<'EOF'
# Roadmap
Useful roadmap context.
EOF

  cat > "$ws/scripts/lib/workstation-lib.sh" <<'EOF'
#!/usr/bin/env bash
ws_is() {
  [[ "$1" == "full" ]]
}
ws_variant() {
  echo "full"
}
EOF
  chmod +x "$ws/scripts/lib/workstation-lib.sh"

  cat > "$ws/scripts/notify.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$REPO_ROOT/logs/notifications"
printf '{"source":"%s","job":"%s","status":"%s","details":"%s"}\n' "${1:-}" "${2:-}" "${3:-}" "${4:-}" >> "$REPO_ROOT/logs/notifications/notify.jsonl"
EOF
  chmod +x "$ws/scripts/notify.sh"

  cat > "$bindir/date" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "+%u" ]]; then
  printf '%s\n' "${MOCK_DAY_NUM:-3}"
  exit 0
fi
if [[ "${1:-}" == "-u" && "${2:-}" == "+%Y-%m-%d" ]]; then
  printf '%s\n' "${MOCK_DATE:-2026-04-02}"
  exit 0
fi
if [[ "${1:-}" == "-u" && "${2:-}" == "+%H:%M:%S" ]]; then
  printf '%s\n' "06:35:00"
  exit 0
fi
if [[ "${1:-}" == "-d" ]]; then
  printf '%s\n' "1743552000"
  exit 0
fi
exec /bin/date "$@"
EOF
  chmod +x "$bindir/date"

  cat > "$bindir/hostname" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "-s" ]]; then
  printf '%s\n' "ace-linux-1"
else
  printf '%s\n' "ace-linux-1"
fi
EOF
  chmod +x "$bindir/hostname"

  cat > "$bindir/flock" <<'EOF'
#!/usr/bin/env bash
# BUG FIX I-2: Mock flock must handle BOTH patterns used by the real code:
#   fd-based:      flock --timeout 120 9        (git-safe.sh uses this)
#   command-based: flock -w 120 /path cmd args  (legacy pattern)
# For fd-based: args are [--timeout N fd] — just succeed (lock acquired)
# For command-based: args are [-w N lockfile cmd...] — exec the command

# Handle --timeout (fd-based locking — git-safe.sh pattern)
if [[ "${1:-}" == "--timeout" ]]; then
  # flock --timeout SECONDS FD — just succeed, fd is already open by caller
  exit 0
fi
# Handle -u (unlock fd) — just succeed
if [[ "${1:-}" == "-u" ]]; then
  exit 0
fi
# Handle -w (command-based locking — legacy pattern)
if [[ "${1:-}" == "-w" ]]; then
  shift 3  # skip -w, timeout, lockfile
  exec "$@"
fi
# Fallback — just succeed
exit 0
EOF
  chmod +x "$bindir/flock"

  cat > "$bindir/git" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
LOG_FILE="${MOCK_GIT_LOG:-/tmp/mock-git.log}"
printf '%s\n' "$*" >> "$LOG_FILE"
case "${1:-}" in
  status|add|diff|commit|pull|push|read-tree)
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
EOF
  chmod +x "$bindir/git"

  cat > "$bindir/claude" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
COUNT_FILE="${MOCK_CLAUDE_COUNT_FILE:-/tmp/mock-claude-count}"
count=0
[[ -f "$COUNT_FILE" ]] && count=$(cat "$COUNT_FILE")
count=$((count + 1))
printf '%s' "$count" > "$COUNT_FILE"
mode="${MOCK_CLAUDE_MODE:-valid}"
if [[ "$mode" == "timeout-then-valid" && "$count" -eq 1 ]]; then
  exit 1
fi
if [[ "$mode" == "invalid-then-valid" && "$count" -eq 1 ]]; then
  cat <<'OUT'
# Research: ai-tooling — 2026-04-02

## Key Findings
- Missing sections on purpose
OUT
  exit 0
fi
if [[ "$mode" == "synthesis-valid" ]]; then
  cat <<'OUT'
# Weekly Research Synthesis — 2026-04-04

## Action Table
| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Example | High | Monitor | Pending |

## Top 3 Insights for PROJECT.md
1. Insight
2. Insight
3. Insight

## Cross-Domain Connections
- Connection

## Detailed Action Items
- [ ] Monitor: finding to watch next week
OUT
  exit 0
fi
cat <<'OUT'
# Research: ai-tooling — 2026-04-02

## Key Findings
- Valid finding

## Relevance to Project
- Valid relevance

## Recommended Actions
- [ ] Valid action
OUT
EOF
  chmod +x "$bindir/claude"

  printf '%s\n' "$ws"
}

run_script() {
  local ws="$1"
  shift
  PATH="$TMP_ROOT/bin:$PATH" \
  MOCK_GIT_LOG="$TMP_ROOT/git.log" \
  MOCK_CLAUDE_COUNT_FILE="$TMP_ROOT/claude.count" \
  bash "$ws/scripts/cron/gsd-researcher-nightly.sh" "$@"
}

echo "--- Test 1: Script exists ---"
assert_file_exists "source script exists" "$SOURCE_SCRIPT"

echo "--- Test 2: Weekend skip does not invoke Claude (Sunday = day 7) ---"
WS=$(setup_workspace)
: > "$TMP_ROOT/git.log"
rm -f "$TMP_ROOT/claude.count"
# BUG FIX I-1: Script skips day 7 (Sunday), NOT day 6 (Saturday).
# Day 6 = Saturday = skill-design domain (runs normally).
# Must test day 7 to verify the weekend skip path.
OUTPUT=$(MOCK_DAY_NUM=7 MOCK_DATE=2026-04-06 run_script "$WS" 2>&1)
assert_eq "sunday skip exit code" "0" "$?"
CLAUDE_CALLS=$(cat "$TMP_ROOT/claude.count" 2>/dev/null || echo "0")
assert_eq "sunday claude calls" "0" "$CLAUDE_CALLS"
assert_not_exists "sunday output file not written" "$WS/.planning/research/2026-04-06-synthesis.md"

echo "--- Test 2b: Saturday (day 6) DOES run skill-design domain ---"
WS=$(setup_workspace)
: > "$TMP_ROOT/git.log"
rm -f "$TMP_ROOT/claude.count"
OUTPUT=$(MOCK_DAY_NUM=6 MOCK_DATE=2026-04-05 run_script "$WS" 2>&1)
assert_eq "saturday exit code" "0" "$?"
CLAUDE_CALLS=$(cat "$TMP_ROOT/claude.count" 2>/dev/null || echo "0")
assert_eq "saturday claude calls" "1" "$CLAUDE_CALLS"
assert_file_exists "saturday skill-design output written" "$WS/.planning/research/2026-04-05-skill-design.md"

echo "--- Test 3: Claude failure retries with reduced path to success ---"
WS=$(setup_workspace)
: > "$TMP_ROOT/git.log"
rm -f "$TMP_ROOT/claude.count"
OUTPUT_FILE="$WS/.planning/research/2026-04-02-ai-tooling.md"
OUTPUT=$(MOCK_DAY_NUM=3 MOCK_DATE=2026-04-02 MOCK_CLAUDE_MODE=timeout-then-valid run_script "$WS" 2>&1)
assert_eq "timeout-then-valid exit code" "0" "$?"
assert_file_exists "output file written after retry" "$OUTPUT_FILE"
CLAUDE_CALLS=$(cat "$TMP_ROOT/claude.count" 2>/dev/null || echo "0")
assert_eq "claude called twice after failure" "2" "$CLAUDE_CALLS"
RESEARCH_CONTENT=$(cat "$OUTPUT_FILE")
assert_contains "retry output has recommendations" "## Recommended Actions" "$RESEARCH_CONTENT"


echo "--- Test 4: Synthesis output is accepted without false retry ---"
WS=$(setup_workspace)
: > "$TMP_ROOT/git.log"
rm -f "$TMP_ROOT/claude.count"
OUTPUT_FILE="$WS/.planning/research/2026-04-04-synthesis.md"
OUTPUT=$(MOCK_DAY_NUM=5 MOCK_DATE=2026-04-04 MOCK_CLAUDE_MODE=synthesis-valid run_script "$WS" 2>&1)
assert_eq "synthesis exit code" "0" "$?"
assert_file_exists "synthesis output written" "$OUTPUT_FILE"
CLAUDE_CALLS=$(cat "$TMP_ROOT/claude.count" 2>/dev/null || echo "0")
assert_eq "synthesis claude calls" "1" "$CLAUDE_CALLS"
SYNTHESIS_CONTENT=$(cat "$OUTPUT_FILE")
assert_contains "synthesis contains action table" "## Action Table" "$SYNTHESIS_CONTENT"


echo "--- Summary ---"
if [[ "$fail_count" -eq 0 ]]; then
  echo "ALL TESTS PASSED (${pass_count}/${total_count})"
  exit 0
else
  echo "FAILURES: ${fail_count}/${total_count} tests failed"
  exit 1
fi
