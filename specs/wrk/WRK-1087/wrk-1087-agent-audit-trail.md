# WRK-1087 Agent Audit Trail — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Append-only SHA256-chained JSONL audit log of every significant agent action, queryable and verifiable.

**Architecture:** Three shell scripts (`log-action.sh`, `audit-query.sh`, `verify-chain.sh`) write to `logs/audit/agent-actions-YYYY-MM.jsonl`. Each entry hashes the previous raw line for tamper detection. Integration hooks are single-line additions to existing callers.

**Cross-review P1 findings addressed (Codex + Gemini):**
1. **flock locking** — `log-action.sh` uses `flock 9` on a per-file lock to prevent race conditions between concurrent writers.
2. **Cross-file chain** — first entry of each new month hashes the last line of the previous month's file (not "genesis"). Only the very first ever file uses "genesis". A `audit-chain-state.json` in `logs/audit/` records the running terminal hash.
3. **SHA256 spec** — hash is computed on the exact bytes appended to the file: `printf '%s\n' "$entry"` then `sha256sum`, stripping trailing newline-in-sha-output. Canonical: UTF-8, LF-terminated, no BOM.
4. **Fail-open with signal** — callers still use `|| true` to avoid blocking agent work, but `log-action.sh` writes a sentinel line `{"action":"log_failure",...}` to a separate `logs/audit/errors.log` when it fails, enabling detection.

**Tech Stack:** bash, sha256sum (coreutils), flock (util-linux), jq (already available), Python (exit_stage.py integration)

---

## Task 1: Core writer — `scripts/audit/log-action.sh`

**Files:**
- Create: `scripts/audit/log-action.sh`
- Create: `logs/audit/.gitkeep` (directory anchor)

**Step 1: Write the failing test**

Create `tests/quality/test_audit_trail.sh`:

```bash
#!/usr/bin/env bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_SCRIPT="${REPO_ROOT}/scripts/audit/log-action.sh"
PASS=0; FAIL=0
pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }
assert_contains() {
  local desc="$1" needle="$2" haystack="$3"
  if [[ "$haystack" == *"$needle"* ]]; then pass "$desc"
  else fail "$desc" "'${needle}' not in output"; fi
}

# Setup temp log dir
TMP=$(mktemp -d)
export AUDIT_LOG_DIR="$TMP"
export ACTIVE_WRK_FILE="$TMP/active-wrk"
export SESSION_STATE_FILE="$TMP/session-state.yaml"
echo "WRK-TEST" > "$TMP/active-wrk"
cat > "$TMP/session-state.yaml" <<'YAML'
session_id: "test-session-001"
YAML

# Test 1: creates log file and writes valid JSON
bash "$LOG_SCRIPT" file_write "src/foo.py" --wrk WRK-TEST
log_file="$TMP/agent-actions-$(date +%Y-%m).jsonl"
[[ -f "$log_file" ]] && pass "log file created" || fail "log file created" "file not found"
line=$(tail -1 "$log_file")
assert_contains "has action" '"action":"file_write"' "$line"
assert_contains "has target" '"target":"src/foo.py"' "$line"
assert_contains "has wrk_id" '"wrk_id":"WRK-TEST"' "$line"
assert_contains "has session_id" '"session_id":"test-session-001"' "$line"
assert_contains "has ts" '"ts":"' "$line"
assert_contains "has prev_hash" '"prev_hash":"' "$line"

# Test 2: second entry chains off first (spec: printf '%s\n' | sha256sum)
bash "$LOG_SCRIPT" stage_exit "stage-4" --wrk WRK-TEST
line2=$(tail -1 "$log_file")
first_hash=$(printf '%s\n' "$line" | sha256sum | awk '{print $1}')
assert_contains "chain links to prev" "\"prev_hash\":\"${first_hash}\"" "$line2"

# Test 3: first entry has prev_hash = "genesis"
first_line=$(head -1 "$log_file")
assert_contains "genesis hash" '"prev_hash":"genesis"' "$first_line"

# Test 4: --wrk flag overrides active-wrk
bash "$LOG_SCRIPT" script_run "scripts/foo.sh" --wrk WRK-OVERRIDE
line3=$(tail -1 "$log_file")
assert_contains "wrk override" '"wrk_id":"WRK-OVERRIDE"' "$line3"

rm -rf "$TMP"
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
```

**Step 2: Run test to verify it fails**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: FAIL (scripts/audit/log-action.sh does not exist)

**Step 3: Implement `scripts/audit/log-action.sh`**

```bash
#!/usr/bin/env bash
# log-action.sh — Append-only SHA256-chained JSONL audit writer (WRK-1087)
# Usage: log-action.sh <action> <target> [--wrk <id>] [--provider <p>]
# Chain spec: SHA256(printf '%s\n' "$entry") — UTF-8, LF-terminated, no BOM.
# Cross-file continuity: logs/audit/audit-chain-state.json stores terminal hash.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

AUDIT_LOG_DIR="${AUDIT_LOG_DIR:-${REPO_ROOT}/logs/audit}"
ACTIVE_WRK_FILE="${ACTIVE_WRK_FILE:-${REPO_ROOT}/.claude/state/active-wrk}"
SESSION_STATE_FILE="${SESSION_STATE_FILE:-${REPO_ROOT}/.claude/work-queue/session-state.yaml}"

action="${1:-unknown}"
target="${2:-}"
shift 2 || shift || true

wrk_id=""
provider="${CLAUDE_PROVIDER:-claude}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wrk) wrk_id="$2"; shift 2 ;;
    --provider) provider="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$wrk_id" && -f "$ACTIVE_WRK_FILE" ]]; then
  wrk_id="$(tr -d '[:space:]' < "$ACTIVE_WRK_FILE" 2>/dev/null)"
fi
wrk_id="${wrk_id:-unknown}"

session_id="unknown"
if [[ -f "$SESSION_STATE_FILE" ]]; then
  session_id="$(awk -F': ' '/^session_id:/{gsub(/^"|"$/, "", $2); print $2; exit}' \
    "$SESSION_STATE_FILE" 2>/dev/null || true)"
fi
session_id="${session_id:-unknown}"

mkdir -p "$AUDIT_LOG_DIR"
month="$(date +%Y-%m)"
log_file="${AUDIT_LOG_DIR}/agent-actions-${month}.jsonl"
lock_file="${AUDIT_LOG_DIR}/.lock-${month}"
chain_state="${AUDIT_LOG_DIR}/audit-chain-state.json"
error_log="${AUDIT_LOG_DIR}/errors.log"

# Compress files older than 6 months (best-effort, non-blocking)
find "$AUDIT_LOG_DIR" -name "agent-actions-*.jsonl" -mtime +180 \
  -exec gzip -q {} \; 2>/dev/null || true

_log_error() {
  local msg="$1"
  printf '{"ts":"%s","event":"log_failure","reason":"%s"}\n' \
    "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$msg" >> "$error_log" 2>/dev/null || true
}

# Acquire exclusive lock (fd 9) — prevents concurrent chain corruption
exec 9>"$lock_file"
if ! flock -w 5 9; then
  _log_error "flock timeout"
  exit 1
fi

# Determine prev_hash with cross-file continuity
if [[ -f "$log_file" && -s "$log_file" ]]; then
  # Within same file: hash the last raw line (spec: printf '%s\n' last_line)
  prev_line="$(tail -1 "$log_file")"
  prev_hash="$(printf '%s\n' "$prev_line" | sha256sum | awk '{print $1}')"
elif [[ -f "$chain_state" ]]; then
  # New month file: carry forward terminal hash from chain-state
  prev_hash="$(jq -r '.terminal_hash // "genesis"' "$chain_state" 2>/dev/null || echo "genesis")"
else
  prev_hash="genesis"
fi

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
target_escaped="${target//\"/\\\"}"

entry="{\"ts\":\"${ts}\",\"session_id\":\"${session_id}\",\"wrk_id\":\"${wrk_id}\",\"action\":\"${action}\",\"target\":\"${target_escaped}\",\"provider\":\"${provider}\",\"prev_hash\":\"${prev_hash}\"}"

# Append (spec: LF-terminated)
printf '%s\n' "$entry" >> "$log_file"

# Update chain state with this entry's hash
entry_hash="$(printf '%s\n' "$entry" | sha256sum | awk '{print $1}')"
printf '{"terminal_hash":"%s","updated_at":"%s","file":"%s"}\n' \
  "$entry_hash" "$ts" "$(basename "$log_file")" > "$chain_state"

# Release lock
flock -u 9
exec 9>&-
```

**Step 4: Run test to verify it passes**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: 8 passed, 0 failed

**Step 5: Create logs/audit directory anchor**

```bash
mkdir -p logs/audit
touch logs/audit/.gitkeep
```

**Step 6: Commit**

```bash
git add scripts/audit/log-action.sh logs/audit/.gitkeep tests/quality/test_audit_trail.sh
git commit -m "feat(WRK-1087): add log-action.sh — SHA256-chained JSONL audit writer"
```

---

## Task 2: Query tool — `scripts/audit/audit-query.sh`

**Files:**
- Create: `scripts/audit/audit-query.sh`

**Step 1: Extend test file with query tests**

Add to `tests/quality/test_audit_trail.sh` (after existing tests, before final summary):

```bash
# ---- audit-query.sh tests ----
QUERY_SCRIPT="${REPO_ROOT}/scripts/audit/audit-query.sh"

TMP2=$(mktemp -d)
export AUDIT_LOG_DIR="$TMP2"
export ACTIVE_WRK_FILE="$TMP2/active-wrk"
export SESSION_STATE_FILE="$TMP2/session-state.yaml"
echo "WRK-AAA" > "$TMP2/active-wrk"
printf 'session_id: "sess-A"\n' > "$TMP2/session-state.yaml"

bash "$LOG_SCRIPT" file_write "src/a.py" --wrk WRK-AAA
bash "$LOG_SCRIPT" file_write "src/b.py" --wrk WRK-BBB
bash "$LOG_SCRIPT" stage_exit "stage-4" --wrk WRK-AAA

out=$(bash "$QUERY_SCRIPT" --wrk WRK-AAA 2>&1)
assert_contains "query by wrk returns matches" "WRK-AAA" "$out"
# WRK-BBB should NOT appear in WRK-AAA query
if [[ "$out" == *"WRK-BBB"* ]]; then
  fail "query excludes other wrk" "WRK-BBB appeared in WRK-AAA results"
else
  pass "query excludes other wrk"
fi

out2=$(bash "$QUERY_SCRIPT" --session sess-A 2>&1)
assert_contains "query by session" "sess-A" "$out2"

rm -rf "$TMP2"
```

**Step 2: Run to verify new tests fail**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: query tests FAIL (audit-query.sh not found)

**Step 3: Implement `scripts/audit/audit-query.sh`**

```bash
#!/usr/bin/env bash
# audit-query.sh — Query agent audit log (WRK-1087)
# Usage: audit-query.sh [--wrk WRK-NNN] [--session <id>] [--date YYYY-MM-DD]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AUDIT_LOG_DIR="${AUDIT_LOG_DIR:-${REPO_ROOT}/logs/audit}"

filter_wrk=""
filter_session=""
filter_date=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wrk) filter_wrk="$2"; shift 2 ;;
    --session) filter_session="$2"; shift 2 ;;
    --date) filter_date="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -d "$AUDIT_LOG_DIR" ]]; then
  echo "No audit logs found at $AUDIT_LOG_DIR" >&2
  exit 0
fi

shopt -s nullglob
files=("${AUDIT_LOG_DIR}"/agent-actions-*.jsonl)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No audit log files found."
  exit 0
fi

printf "%-25s %-20s %-12s %-14s %-10s %s\n" "TIMESTAMP" "SESSION" "WRK" "ACTION" "PROVIDER" "TARGET"
printf '%s\n' "$(printf '%.0s-' {1..90})"

for f in "${files[@]}"; do
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    ts=$(echo "$line" | jq -r '.ts // ""' 2>/dev/null)
    sid=$(echo "$line" | jq -r '.session_id // ""' 2>/dev/null)
    wid=$(echo "$line" | jq -r '.wrk_id // ""' 2>/dev/null)
    act=$(echo "$line" | jq -r '.action // ""' 2>/dev/null)
    tgt=$(echo "$line" | jq -r '.target // ""' 2>/dev/null)
    prv=$(echo "$line" | jq -r '.provider // ""' 2>/dev/null)

    [[ -n "$filter_wrk" && "$wid" != "$filter_wrk" ]] && continue
    [[ -n "$filter_session" && "$sid" != "$filter_session" ]] && continue
    [[ -n "$filter_date" && "$ts" != "${filter_date}"* ]] && continue

    printf "%-25s %-20s %-12s %-14s %-10s %s\n" \
      "${ts:0:19}" "${sid:0:19}" "${wid:0:11}" "${act:0:13}" "${prv:0:9}" "${tgt:0:40}"
  done < "$f"
done
```

**Step 4: Run tests to verify pass**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: all query tests pass

**Step 5: Commit**

```bash
git add scripts/audit/audit-query.sh tests/quality/test_audit_trail.sh
git commit -m "feat(WRK-1087): add audit-query.sh — filter by wrk/session/date"
```

---

## Task 3: Chain verifier — `scripts/audit/verify-chain.sh`

**Files:**
- Create: `scripts/audit/verify-chain.sh`

**Step 1: Add verify-chain tests to test file**

```bash
# ---- verify-chain.sh tests ----
VERIFY_SCRIPT="${REPO_ROOT}/scripts/audit/verify-chain.sh"

TMP3=$(mktemp -d)
export AUDIT_LOG_DIR="$TMP3"
export ACTIVE_WRK_FILE="$TMP3/active-wrk"
export SESSION_STATE_FILE="$TMP3/session-state.yaml"
echo "WRK-VFY" > "$TMP3/active-wrk"
printf 'session_id: "sess-V"\n' > "$TMP3/session-state.yaml"

bash "$LOG_SCRIPT" file_write "src/x.py"
bash "$LOG_SCRIPT" stage_exit "stage-3"
bash "$LOG_SCRIPT" wrk_close "WRK-VFY"
vfy_log="$TMP3/agent-actions-$(date +%Y-%m).jsonl"

bash "$VERIFY_SCRIPT" "$vfy_log" 2>&1 | grep -q "OK" && pass "clean chain verifies OK" || fail "clean chain verifies OK" "verify failed on valid chain"

# Tamper: modify middle line
lines=$(wc -l < "$vfy_log")
if [[ "$lines" -ge 2 ]]; then
  tmpf=$(mktemp)
  awk 'NR==2 {sub(/"action":"[^"]*"/, "\"action\":\"TAMPERED\"")} {print}' "$vfy_log" > "$tmpf"
  mv "$tmpf" "$vfy_log"
  bash "$VERIFY_SCRIPT" "$vfy_log" 2>&1 | grep -qi "broken\|invalid\|tamper\|mismatch" \
    && pass "tampered chain detected" \
    || fail "tampered chain detected" "verify did not detect tampering"
fi

rm -rf "$TMP3"
```

**Step 2: Run to verify tests fail**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: verify-chain tests FAIL

**Step 3: Implement `scripts/audit/verify-chain.sh`**

```bash
#!/usr/bin/env bash
# verify-chain.sh — Validate SHA256 chain integrity of an audit log (WRK-1087)
# Usage: verify-chain.sh [file] [--prev-hash <hash>]
#   If no file given, verifies current month's log.
#   --prev-hash <hash>: seed hash for first entry (default: "genesis" or from chain-state)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AUDIT_LOG_DIR="${AUDIT_LOG_DIR:-${REPO_ROOT}/logs/audit}"

log_file=""
seed_hash=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prev-hash) seed_hash="$2"; shift 2 ;;
    *) log_file="$1"; shift ;;
  esac
done

if [[ -z "$log_file" ]]; then
  log_file="${AUDIT_LOG_DIR}/agent-actions-$(date +%Y-%m).jsonl"
fi

if [[ ! -f "$log_file" ]]; then
  echo "No log file: $log_file" >&2
  exit 1
fi

# Determine starting prev_hash
if [[ -z "$seed_hash" ]]; then
  seed_hash="genesis"
fi

prev_hash="$seed_hash"
line_no=0
errors=0

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  line_no=$((line_no + 1))
  entry_prev=$(printf '%s' "$line" | jq -r '.prev_hash // ""' 2>/dev/null)
  if [[ "$entry_prev" != "$prev_hash" ]]; then
    echo "BROKEN at line ${line_no}: expected prev_hash='${prev_hash}', got '${entry_prev}'"
    errors=$((errors + 1))
  fi
  # Spec: hash of printf '%s\n' "$line" (LF-terminated)
  prev_hash="$(printf '%s\n' "$line" | sha256sum | awk '{print $1}')"
done < "$log_file"

if [[ "$errors" -eq 0 ]]; then
  echo "OK — chain valid (${line_no} entries, terminal_hash=${prev_hash})"
  exit 0
else
  echo "INVALID — ${errors} broken link(s) in ${line_no} entries"
  exit 1
fi
```

**Step 4: Run tests to verify pass**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: all tests pass

**Step 5: Commit**

```bash
git add scripts/audit/verify-chain.sh tests/quality/test_audit_trail.sh
git commit -m "feat(WRK-1087): add verify-chain.sh — SHA256 chain integrity check"
```

---

## Task 4: Integration — `scripts/agents/session.sh`

**Files:**
- Modify: `scripts/agents/session.sh`

Add `log-action.sh` calls at session init and end. The `end` subcommand needs to be located (or added if missing).

**Step 1: Locate init and end blocks**

```bash
grep -n "case.*cmd\|init)\|end)" scripts/agents/session.sh | head -20
```

**Step 2: Add log-action.sh call after session_set_scalar in init block**

After the line `session_set_scalar "session_id" "$sid"`, add:

```bash
        LOG_ACTION="${REPO_ROOT:-$(git rev-parse --show-toplevel)}/scripts/audit/log-action.sh"
        [[ -x "$LOG_ACTION" ]] && bash "$LOG_ACTION" session_start "init" --wrk "WRK-SESSION" --provider "$provider" 2>/dev/null || true
```

**Step 3: Add log-action.sh call in end block**

Find the `end)` case (or `session end` handler) and add before the case closes:

```bash
        LOG_ACTION="${AGENTS_DIR}/../../scripts/audit/log-action.sh"
        [[ -x "$LOG_ACTION" ]] && bash "$LOG_ACTION" session_end "end" 2>/dev/null || true
```

**Step 4: Verify session.sh still works**

```bash
bash scripts/agents/session.sh init --provider claude --session-id test-$(date +%s) 2>&1 | head -5
bash scripts/agents/session.sh show 2>&1 | head -5
```

**Step 5: Commit**

```bash
git add scripts/agents/session.sh
git commit -m "feat(WRK-1087): wire log-action.sh into session init/end"
```

---

## Task 5: Integration — `scripts/work-queue/exit_stage.py`

**Files:**
- Modify: `scripts/work-queue/exit_stage.py`

**Step 1: Add subprocess call at the end of main exit validation**

Find the location just before the STAGE_GATE banner is printed. Add:

```python
import subprocess as _sp
_log = os.path.join(repo_root, "scripts", "audit", "log-action.sh")
if os.path.isfile(_log):
    _sp.run(
        ["bash", _log, "stage_exit", f"stage-{stage}"],
        capture_output=True, timeout=5
    )
```

**Step 2: Verify exit_stage.py still works**

```bash
uv run --no-project python scripts/work-queue/exit_stage.py WRK-1087 4 2>&1 | head -5
```
(May show artifacts missing — that's expected; confirm no crash)

**Step 3: Check audit log was written**

```bash
tail -2 logs/audit/agent-actions-$(date +%Y-%m).jsonl 2>/dev/null | jq .
```
Expected: entry with `"action":"stage_exit"`

**Step 4: Commit**

```bash
git add scripts/work-queue/exit_stage.py
git commit -m "feat(WRK-1087): wire log-action.sh into exit_stage.py"
```

---

## Task 6: Integration — `scripts/work-queue/close-item.sh` + post-commit hook

**Files:**
- Modify: `scripts/work-queue/close-item.sh`
- Modify: `.git/hooks/post-commit`

**Step 1: Add to close-item.sh just before final exit**

Find the closing section in `close-item.sh` and add:

```bash
LOG_ACTION="${SCRIPT_DIR}/../../scripts/audit/log-action.sh"
if [[ -x "$LOG_ACTION" ]]; then
  bash "$LOG_ACTION" wrk_close "$WRK_ID" --wrk "$WRK_ID" 2>/dev/null || true
fi
```

**Step 2: Add commit hook entry to `.git/hooks/post-commit`**

Append to the existing `.git/hooks/post-commit`:

```bash
# Audit trail (WRK-1087)
REPO_ROOT_AUD="$(git rev-parse --show-toplevel)"
LOG_ACTION="${REPO_ROOT_AUD}/scripts/audit/log-action.sh"
if [[ -x "$LOG_ACTION" ]]; then
  COMMIT_HASH="$(git rev-parse HEAD)"
  bash "$LOG_ACTION" commit "$COMMIT_HASH" 2>/dev/null || true
fi
```

**Step 3: Verify commit writes to audit log**

```bash
git commit --allow-empty -m "test: verify audit hook"
tail -1 logs/audit/agent-actions-$(date +%Y-%m).jsonl | jq .
```
Expected: entry with `"action":"commit"`

**Step 4: Revert test commit**

```bash
git reset --soft HEAD~1
```

**Step 5: Commit close-item.sh change**

```bash
git add scripts/work-queue/close-item.sh
git commit -m "feat(WRK-1087): wire log-action.sh into close-item.sh + post-commit hook"
```

---

## Task 7: Stop hook integration

**Files:**
- Modify: `.claude/settings.json` (Stop hook)

**Step 1: Add log-action.sh call to Stop hooks array in `.claude/settings.json`**

In the `"Stop"` array, add a new hook entry:

```json
{
  "type": "command",
  "command": "bash \"${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}/scripts/audit/log-action.sh\" session_end \"stop\" 2>/dev/null || true",
  "statusMessage": "Audit: session_end"
}
```

**Step 2: Verify settings.json is valid JSON**

```bash
jq . /mnt/local-analysis/workspace-hub/.claude/settings.json > /dev/null && echo "JSON valid"
```

**Step 3: Commit**

```bash
git add .claude/settings.json
git commit -m "feat(WRK-1087): add session_end to Stop hook for audit trail"
```

---

## Task 8: Final verification

**Step 1: Run full test suite**

```bash
bash tests/quality/test_audit_trail.sh
```
Expected: all pass, 0 failed

**Step 2: Run end-to-end smoke test**

```bash
bash scripts/audit/log-action.sh file_write "src/test.py" --wrk WRK-1087
bash scripts/audit/log-action.sh stage_exit "stage-10" --wrk WRK-1087
bash scripts/audit/audit-query.sh --wrk WRK-1087
bash scripts/audit/verify-chain.sh
```

**Step 3: Verify gate evidence**

```bash
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1087
```

**Step 4: Prepare cross-review input**

Write `scripts/review/results/wrk-1087-phase-1-review-input.md` and submit to Codex.
