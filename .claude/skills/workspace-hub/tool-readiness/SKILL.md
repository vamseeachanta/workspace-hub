---
name: tool-readiness
description: >
  Session-start readiness check for workspace-hub tooling — verifies CLI
  availability, data source freshness, statusline integrity, cross-OS
  script compatibility, and work queue accessibility.
version: 1.0.0
category: workspace-hub
last_updated: 2026-02-19
wrk_ref: WRK-224
invoke: /tool-readiness
trigger: session-start
auto_execute: false
related_skills:
  - workspace-hub/ecosystem-health
  - workspace-hub/session-start
  - workspace-hub/repo-sync
tags:
  - readiness
  - session-lifecycle
  - tooling
  - cli
  - quota
platforms: [all]
capabilities: []
requires: []
---

# /tool-readiness — Session-Start Readiness Check

Verifies workspace-hub tooling is available and healthy before beginning work.

## Usage

```
/tool-readiness        — run all 5 check groups
```

## When to Run

- At session start (triggered by `/session-start` skill)
- After a repo sync that may affect tooling
- When quota or statusline data looks stale

## Implementation

```bash
REPO="$(git rev-parse --show-toplevel)"

# Group 1 — CLI Availability
echo "=== Group 1: CLI Availability ==="
for cli in claude codex gemini; do
    command -v "$cli" >/dev/null 2>&1 \
        && echo "  [PASS] $cli in PATH" || echo "  [WARN] $cli not found"
done

# Group 2 — Data Source Health
echo "=== Group 2: Data Source Health ==="
QF="$REPO/config/ai-tools/agent-quota-latest.json"
if [ -f "$QF" ]; then
    mtime=$(date -r "$QF" +%s 2>/dev/null || stat -f %m "$QF" 2>/dev/null || echo 0)
    age=$(( $(date +%s) - mtime ))
    [ "$age" -lt 86400 ] \
        && echo "  [PASS] agent-quota-latest.json age: ${age}s" \
        || echo "  [WARN] agent-quota-latest.json stale: ${age}s (>= 24h)"
else
    echo "  [FAIL] agent-quota-latest.json not found: $QF"
fi
[ -f "$HOME/.cache/agent-quota.json" ] \
    && echo "  [PASS] ~/.cache/agent-quota.json exists" \
    || echo "  [WARN] ~/.cache/agent-quota.json not found"

# Group 3 — Statusline Integrity
echo "=== Group 3: Statusline Integrity ==="
SL="$REPO/.claude/statusline-command.sh"
[ -x "$SL" ] \
    && echo "  [PASS] statusline-command.sh: executable" \
    || echo "  [FAIL] statusline-command.sh: missing or not executable"
grep -q "agent-quota-latest.json" "$SL" 2>/dev/null \
    && echo "  [PASS] Reads agent-quota-latest.json" \
    || echo "  [WARN] May not read agent-quota-latest.json"
out=$("$SL" 2>/dev/null || echo "")
echo "$out" | grep -qv "100%" \
    && echo "  [PASS] Output non-trivial" \
    || echo "  [WARN] Output may be stale (all 100%): $out"

# Group 4 — Cross-OS Script Compatibility
echo "=== Group 4: Cross-OS Script Compatibility ==="
QS="$REPO/scripts/ai/assessment/query-quota.sh"
[ -f "$QS" ] && echo "  [PASS] query-quota.sh: found" \
    || echo "  [FAIL] query-quota.sh: not found"
grep -qE 'stat -c %Y' "$QS" 2>/dev/null \
    && echo "  [WARN] Non-portable stat -c %Y found" || echo "  [PASS] No bare stat -c %Y"
grep -qE 'date -d ' "$QS" 2>/dev/null \
    && echo "  [WARN] Non-portable date -d found" || echo "  [PASS] No bare date -d"

# Group 5 — Work Queue
echo "=== Group 5: Work Queue ==="
WQ="$REPO/.claude/work-queue"
for dir in pending working blocked; do
    [ -d "$WQ/$dir" ] \
        && echo "  [PASS] $dir/: $(find "$WQ/$dir" -name 'WRK-*.md' | wc -l | tr -d ' ') WRK files" \
        || echo "  [FAIL] $dir/: not found"
done
```

## Check Summary

| Group | Checks | Key Signals |
|-------|--------|-------------|
| 1 CLI Availability | claude, codex, gemini | [WARN] if not found |
| 2 Data Source Health | quota json age, cache file | [FAIL] missing, [WARN] stale |
| 3 Statusline Integrity | executable, correct source, output | [FAIL] not executable |
| 4 Cross-OS Compat | query-quota.sh portability | [WARN] non-portable stat/date |
| 5 Work Queue | pending/working/blocked dirs | [FAIL] dir missing |

## Related

- `/ecosystem-health` — deeper structural checks at session exit
- `/session-start` — parent skill that triggers this check
- `/repo-sync` — re-run after sync to verify tooling health
- `WRK-224` — tracking item for this skill
