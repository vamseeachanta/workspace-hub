#!/usr/bin/env bash
# run-skill-integration-tests.sh — Integration test runner for skills
#
# Reads test specs from .planning/skills/integration-tests/*.yaml
# For each spec: validates skill exists, optionally runs claude -p, checks patterns.
#
# Usage:
#   bash scripts/skills/run-skill-integration-tests.sh [--dry-run] [--specs-dir DIR] [--verbose]
#
# Modes:
#   --dry-run   Validate specs and skill paths without invoking claude CLI
#   (default)   Live mode — invokes claude -p with skill content + test prompt
#
# Exit codes:
#   0  All tests pass (or skip in dry-run)
#   1  One or more tests fail

set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────
SPECS_DIR=".planning/skills/integration-tests"
DRY_RUN=false
VERBOSE=false
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# ── Parse arguments ─────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)   DRY_RUN=true; shift ;;
    --specs-dir) SPECS_DIR="$2"; shift 2 ;;
    --verbose)   VERBOSE=true; shift ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--specs-dir DIR] [--verbose]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

cd "$REPO_ROOT"

# ── Counters ────────────────────────────────────────────────────────────
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
TOTAL_COUNT=0
declare -a ERROR_MSGS=()

# ── Color helpers (if terminal) ─────────────────────────────────────────
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  CYAN='\033[0;36m'
  RESET='\033[0m'
else
  GREEN='' RED='' YELLOW='' CYAN='' RESET=''
fi

# ── Python-based YAML parser helper ────────────────────────────────────
# Instead of parsing YAML in bash (fragile), we use a tiny inline Python
# to convert each spec into a simple line-based format that bash can read.
yaml_to_lines() {
  local file="$1"
  python3 - "$file" <<'PYEOF'
import sys, json
try:
    import yaml
    data = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
except ImportError:
    # Minimal fallback without PyYAML
    import re
    text = open(sys.argv[1], encoding="utf-8").read()
    data = {}
    # Very simple extraction
    m = re.search(r'^skill_name:\s*(.+)', text, re.M)
    if m: data['skill_name'] = m.group(1).strip().strip("'\"")
    m = re.search(r'^skill_path:\s*(.+)', text, re.M)
    if m: data['skill_path'] = m.group(1).strip().strip("'\"")
    data['tests'] = []
    # Split on test entries
    parts = re.split(r'\n\s+-\s+test_id:', text)
    for i, part in enumerate(parts):
        if i == 0: continue
        t = {}
        m = re.match(r'\s*(\S+)', part)
        if m: t['test_id'] = m.group(1)
        m = re.search(r'description:\s*(.+)', part)
        if m: t['description'] = m.group(1).strip().strip("'\"")
        m = re.search(r'prompt:\s*>?\s*\n((?:\s+.+\n?)+)', part)
        if m: t['prompt'] = ' '.join(m.group(1).split())
        else:
            m = re.search(r'prompt:\s*(.+)', part)
            if m: t['prompt'] = m.group(1).strip().strip("'\"")
        t['expected_patterns'] = re.findall(r'expected_patterns:\s*\n((?:\s+-\s+.+\n?)+)', part)
        if t['expected_patterns']:
            t['expected_patterns'] = [x.strip().strip("'\"") for x in re.findall(r'-\s+(.+)', t['expected_patterns'][0])]
        else:
            t['expected_patterns'] = []
        t['unexpected_patterns'] = re.findall(r'unexpected_patterns:\s*\n((?:\s+-\s+.+\n?)+)', part)
        if t['unexpected_patterns']:
            t['unexpected_patterns'] = [x.strip().strip("'\"") for x in re.findall(r'-\s+(.+)', t['unexpected_patterns'][0])]
        else:
            t['unexpected_patterns'] = []
        m = re.search(r'timeout:\s*(\d+)', part)
        t['timeout'] = int(m.group(1)) if m else 60
        data['tests'].append(t)

if not data:
    sys.exit(1)

# Output in simple line-based format
print("SKILL_NAME=" + str(data.get('skill_name', '')))
print("SKILL_PATH=" + str(data.get('skill_path', '')))
tests = data.get('tests', [])
print("TEST_COUNT=" + str(len(tests)))
for idx, t in enumerate(tests):
    print(f"TEST_{idx}_ID=" + str(t.get('test_id', '')))
    print(f"TEST_{idx}_DESC=" + str(t.get('description', '')))
    print(f"TEST_{idx}_PROMPT=" + str(t.get('prompt', '')))
    print(f"TEST_{idx}_TIMEOUT=" + str(t.get('timeout', 60)))
    ep = t.get('expected_patterns', [])
    print(f"TEST_{idx}_EXPECTED_COUNT=" + str(len(ep)))
    for j, p in enumerate(ep):
        print(f"TEST_{idx}_EXPECTED_{j}=" + str(p))
    up = t.get('unexpected_patterns', [])
    print(f"TEST_{idx}_UNEXPECTED_COUNT=" + str(len(up)))
    for j, p in enumerate(up):
        print(f"TEST_{idx}_UNEXPECTED_{j}=" + str(p))
PYEOF
}

# ── Run a single test (dry-run) ────────────────────────────────────────
run_test_dry() {
  local test_id="$1"
  local desc="$2"
  local prompt="$3"
  local skill_path="$4"
  local expected_count="$5"
  local unexpected_count="$6"

  TOTAL_COUNT=$((TOTAL_COUNT + 1))

  # Validate skill file exists
  if [[ ! -f "$skill_path" ]]; then
    echo -e "  ${RED}FAIL${RESET} [$test_id] $desc — skill file not found: $skill_path"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    ERROR_MSGS+=("$test_id: skill file not found: $skill_path")
    return
  fi

  # Validate spec has required fields
  if [[ -z "$test_id" || -z "$prompt" ]]; then
    echo -e "  ${RED}FAIL${RESET} [$test_id] $desc — missing test_id or prompt"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    ERROR_MSGS+=("$test_id: missing required fields")
    return
  fi

  # Check patterns arrays are not empty
  if [[ "$expected_count" -eq 0 ]]; then
    echo -e "  ${YELLOW}SKIP${RESET} [$test_id] $desc — no expected_patterns defined"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    return
  fi

  echo -e "  ${GREEN}PASS${RESET} [$test_id] $desc (dry-run: spec valid, skill exists)"
  PASS_COUNT=$((PASS_COUNT + 1))
}

# ── Run a single test (live) ──────────────────────────────────────────
run_test_live() {
  local test_id="$1"
  local desc="$2"
  local prompt="$3"
  local skill_path="$4"
  local timeout_sec="$5"
  # Expected/unexpected patterns passed via temp files

  TOTAL_COUNT=$((TOTAL_COUNT + 1))

  if [[ ! -f "$skill_path" ]]; then
    echo -e "  ${RED}FAIL${RESET} [$test_id] $desc — skill file not found: $skill_path"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    ERROR_MSGS+=("$test_id: skill file not found: $skill_path")
    return
  fi

  if ! command -v claude &>/dev/null; then
    echo -e "  ${YELLOW}SKIP${RESET} [$test_id] $desc — claude CLI not found"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    return
  fi

  # Read skill content
  local skill_content
  skill_content="$(cat "$skill_path")"

  local full_prompt="Here is a skill definition:

---SKILL START---
${skill_content}
---SKILL END---

Based on this skill, respond to the following:
${prompt}"

  # Run claude
  local output exit_code=0
  output=$(timeout "${timeout_sec}" claude -p "$full_prompt" --print 2>&1) || exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    echo -e "  ${RED}FAIL${RESET} [$test_id] $desc — claude CLI exited with code $exit_code"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    ERROR_MSGS+=("$test_id: claude CLI failed (exit=$exit_code)")
    return
  fi

  local all_match=true

  # Check expected patterns (from temp file)
  while IFS= read -r pattern; do
    [[ -z "$pattern" ]] && continue
    if ! echo "$output" | grep -qiE "$pattern"; then
      echo -e "  ${RED}FAIL${RESET} [$test_id] Expected pattern not found: '$pattern'"
      all_match=false
      ERROR_MSGS+=("$test_id: expected pattern missing: $pattern")
    fi
  done < "$EXPECTED_TMP"

  # Check unexpected patterns (from temp file)
  while IFS= read -r pattern; do
    [[ -z "$pattern" ]] && continue
    if echo "$output" | grep -qiE "$pattern"; then
      echo -e "  ${RED}FAIL${RESET} [$test_id] Unexpected pattern found: '$pattern'"
      all_match=false
      ERROR_MSGS+=("$test_id: unexpected pattern present: $pattern")
    fi
  done < "$UNEXPECTED_TMP"

  if $all_match; then
    echo -e "  ${GREEN}PASS${RESET} [$test_id] $desc"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# ── Main ────────────────────────────────────────────────────────────────
echo "=================================================="
echo " Skill Integration Test Runner"
echo "=================================================="
echo "Specs dir:  $SPECS_DIR"
echo "Mode:       $(if $DRY_RUN; then echo 'dry-run'; else echo 'live'; fi)"
echo "Repo root:  $REPO_ROOT"
echo ""

# Find all YAML spec files
mapfile -t spec_files < <(find "$SPECS_DIR" -name '*.yaml' -o -name '*.yml' 2>/dev/null | sort)

if [[ ${#spec_files[@]} -eq 0 ]]; then
  echo -e "${RED}ERROR${RESET}: No spec files found in $SPECS_DIR"
  exit 1
fi

echo "Found ${#spec_files[@]} spec file(s)"
echo ""

# Temp files for pattern passing in live mode
EXPECTED_TMP=$(mktemp)
UNEXPECTED_TMP=$(mktemp)
trap 'rm -f "$EXPECTED_TMP" "$UNEXPECTED_TMP"' EXIT

# Process each spec file
for spec_file in "${spec_files[@]}"; do
  echo -e "${CYAN}── $(basename "$spec_file") ──${RESET}"

  # Parse YAML via Python helper into line-based format
  declare -A SPEC_DATA=()
  while IFS='=' read -r key value; do
    [[ -z "$key" ]] && continue
    SPEC_DATA["$key"]="$value"
  done < <(yaml_to_lines "$spec_file")

  local_skill_name="${SPEC_DATA[SKILL_NAME]:-unknown}"
  local_skill_path="${SPEC_DATA[SKILL_PATH]:-}"
  local_test_count="${SPEC_DATA[TEST_COUNT]:-0}"

  echo "  Skill: $local_skill_name ($local_skill_path)"
  echo "  Tests: $local_test_count"

  for i in $(seq 0 $((local_test_count - 1))); do
    local_id="${SPEC_DATA[TEST_${i}_ID]:-}"
    local_desc="${SPEC_DATA[TEST_${i}_DESC]:-}"
    local_prompt="${SPEC_DATA[TEST_${i}_PROMPT]:-}"
    local_timeout="${SPEC_DATA[TEST_${i}_TIMEOUT]:-60}"
    local_exp_count="${SPEC_DATA[TEST_${i}_EXPECTED_COUNT]:-0}"
    local_unexp_count="${SPEC_DATA[TEST_${i}_UNEXPECTED_COUNT]:-0}"

    if $DRY_RUN; then
      run_test_dry "$local_id" "$local_desc" "$local_prompt" "$local_skill_path" "$local_exp_count" "$local_unexp_count"
    else
      # Write patterns to temp files for live mode
      : > "$EXPECTED_TMP"
      for j in $(seq 0 $((local_exp_count - 1))); do
        echo "${SPEC_DATA[TEST_${i}_EXPECTED_${j}]:-}" >> "$EXPECTED_TMP"
      done
      : > "$UNEXPECTED_TMP"
      for j in $(seq 0 $((local_unexp_count - 1))); do
        echo "${SPEC_DATA[TEST_${i}_UNEXPECTED_${j}]:-}" >> "$UNEXPECTED_TMP"
      done
      run_test_live "$local_id" "$local_desc" "$local_prompt" "$local_skill_path" "$local_timeout"
    fi
  done
  echo ""
done

# ── Summary ─────────────────────────────────────────────────────────────
echo "=================================================="
echo " Summary"
echo "=================================================="
echo -e "  Total:  $TOTAL_COUNT"
echo -e "  ${GREEN}Pass:   $PASS_COUNT${RESET}"
echo -e "  ${RED}Fail:   $FAIL_COUNT${RESET}"
echo -e "  ${YELLOW}Skip:   $SKIP_COUNT${RESET}"
echo ""

if [[ ${#ERROR_MSGS[@]} -gt 0 ]]; then
  echo "Errors:"
  for err in "${ERROR_MSGS[@]}"; do
    echo "  - $err"
  done
  echo ""
fi

if [[ $FAIL_COUNT -gt 0 ]]; then
  echo -e "${RED}RESULT: FAILED${RESET}"
  exit 1
else
  echo -e "${GREEN}RESULT: PASSED${RESET}"
  exit 0
fi
