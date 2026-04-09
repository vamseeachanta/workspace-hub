---
name: session-corpus-audit
description: Analyze session quality trends from session-signals JSONL files. Identifies high-churn patterns, reports wasted tool calls, flags sessions exceeding the 500-call threshold, and surfaces recurring failure modes across sessions.
version: 1.0.0
category: coordination
type: skill
trigger: manual
auto_execute: false
tools:
  - Bash
  - Read
  - Grep
  - Glob
tags:
  - session
  - governance
  - audit
  - quality
  - analytics
related_skills:
  - session-start-routine
  - comprehensive-learning
  - enforcement-audit-and-upgrade
issue_ref: "#2057"
---

# Session Corpus Audit

Analyze session quality trends from `.claude/state/session-signals/` JSONL files.
Identifies waste, high-churn patterns, and sessions that exceeded governance limits.

## When to Invoke

- Weekly review of session quality
- When investigating a session that felt wasteful or circular
- As input to the nightly comprehensive-learning pipeline
- After a burst of overnight batch runs to assess efficiency

## Data Source

Session signals are stored as newline-delimited JSON in:
```
.claude/state/session-signals/YYYY-MM-DD.jsonl
```

Each record contains: `session_id`, `transcript_path`, `cwd`, `permission_mode`,
`hook_event_name`, `stop_hook_active`, `last_assistant_message`.

Historical timestamped files (e.g., `2026-02-20-091148.jsonl`) also exist for
individual session events.

## Audit Procedure

### 1. Session Volume Summary

Count sessions per day over the last N days.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SIGNALS_DIR="$REPO_ROOT/.claude/state/session-signals"

echo "=== Session volume (last 7 days) ==="
for i in $(seq 0 6); do
  D=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null)
  FILE="$SIGNALS_DIR/$D.jsonl"
  if [[ -f "$FILE" ]]; then
    COUNT=$(wc -l < "$FILE")
    SESSIONS=$(jq -r '.session_id' "$FILE" 2>/dev/null | sort -u | wc -l)
    echo "  $D: $COUNT signals across $SESSIONS unique sessions"
  fi
done
```

### 2. High-Call Sessions

Flag sessions where the stop message mentions high tool-call counts or governance ceilings.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SIGNALS_DIR="$REPO_ROOT/.claude/state/session-signals"
TODAY=$(date +%Y-%m-%d)

echo "=== Sessions mentioning tool-call limits ==="
for FILE in "$SIGNALS_DIR"/${TODAY}*.jsonl "$SIGNALS_DIR"/$TODAY.jsonl; do
  [[ -f "$FILE" ]] || continue
  jq -r 'select(.last_assistant_message | test("tool.?call|ceiling|500|200|governance"; "i")) | "\(.session_id[0:8])... \(.last_assistant_message[0:120])"' "$FILE" 2>/dev/null || true
done
```

### 3. Session Churn Detection

Identify sessions that appear in the signals multiple times (restarts, repeated stops).

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SIGNALS_DIR="$REPO_ROOT/.claude/state/session-signals"
TODAY=$(date +%Y-%m-%d)

echo "=== Sessions with multiple stop signals (churn) ==="
if [[ -f "$SIGNALS_DIR/$TODAY.jsonl" ]]; then
  jq -r '.session_id' "$SIGNALS_DIR/$TODAY.jsonl" 2>/dev/null \
    | sort | uniq -c | sort -rn | head -10 \
    | while read count sid; do
        [[ "$count" -gt 2 ]] && echo "  CHURN: $sid appeared $count times"
      done
fi
```

### 4. Failure Pattern Extraction

Look for error-related keywords in session stop messages.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SIGNALS_DIR="$REPO_ROOT/.claude/state/session-signals"

echo "=== Recent failure patterns ==="
for i in $(seq 0 2); do
  D=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null)
  FILE="$SIGNALS_DIR/$D.jsonl"
  [[ -f "$FILE" ]] || continue
  jq -r 'select(.last_assistant_message | test("error|fail|block|denied|timeout"; "i")) | "\(.session_id[0:8])... [\(.hook_event_name)] \(.last_assistant_message[0:100])"' "$FILE" 2>/dev/null || true
done
```

### 5. Cross-Day Trend Analysis

Compare session counts and unique session IDs across days to detect workload spikes.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SIGNALS_DIR="$REPO_ROOT/.claude/state/session-signals"

echo "=== 14-day trend ==="
echo "Date        | Signals | Sessions"
echo "------------|---------|--------"
for i in $(seq 0 13); do
  D=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null)
  FILE="$SIGNALS_DIR/$D.jsonl"
  if [[ -f "$FILE" ]]; then
    SIGS=$(wc -l < "$FILE")
    SESS=$(jq -r '.session_id' "$FILE" 2>/dev/null | sort -u | wc -l)
    printf "%s | %7d | %7d\n" "$D" "$SIGS" "$SESS"
  fi
done
```

## Output Format

```
SESSION CORPUS AUDIT
====================
Period:           YYYY-MM-DD to YYYY-MM-DD
Total signals:    N
Unique sessions:  N
High-call (>200): N sessions
Churn (>2 stops): N sessions
Failure signals:  N
====================
Recommendations:  [list any patterns needing attention]
```

## Key Metrics

| Metric | Healthy | Warning | Action |
|--------|---------|---------|--------|
| Signals per session | 1-3 | 4-6 | >6 = investigate churn |
| Sessions per day | 2-8 | 9-15 | >15 = possible automation loop |
| Failure rate | <10% | 10-25% | >25% = systemic issue |
| High-call sessions | 0 | 1-2 | >2 = governance enforcement gap |

## Integration

- Fed into the comprehensive-learning nightly pipeline (Phase 1 insights)
- Referenced by `SESSION-GOVERNANCE.md` Phase 3
- Tool-call ceiling enforcement via `session-governor-check.sh` hook
