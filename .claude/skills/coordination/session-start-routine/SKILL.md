---
name: session-start-routine
description: Pre-flight checks at session start — load context, check prior state, validate environment, detect in-flight work from other terminals. Ensures sessions begin with full awareness of current ecosystem state.
version: 1.0.0
category: coordination
type: skill
trigger: session-start
auto_execute: false
tools:
  - Bash
  - Read
  - Grep
  - Glob
tags:
  - session
  - governance
  - pre-flight
  - context-loading
related_skills:
  - comprehensive-learning
  - enforcement-audit-and-upgrade
issue_ref: "#2057"
---

# Session Start Routine

Pre-flight checks that run at the beginning of every interactive session. Ensures the
agent starts with full context awareness and does not collide with in-flight work.

## When to Invoke

- At the start of every interactive Claude Code session
- After a long pause (>2 hours) within the same session
- When resuming work from a previous day

## Pre-Flight Checklist

### 1. Load Prior Session State

Read the most recent session signals to understand where the last session left off.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SIGNALS_DIR="$REPO_ROOT/.claude/state/session-signals"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Check today's signals first, fall back to yesterday
if [[ -f "$SIGNALS_DIR/$TODAY.jsonl" ]]; then
  echo "=== Today's session signals ==="
  tail -5 "$SIGNALS_DIR/$TODAY.jsonl"
elif [[ -f "$SIGNALS_DIR/$YESTERDAY.jsonl" ]]; then
  echo "=== Yesterday's session signals ==="
  tail -3 "$SIGNALS_DIR/$YESTERDAY.jsonl"
else
  echo "WARNING: No recent session signals found"
fi
```

### 2. Check for In-Flight Work from Other Terminals

Scan for `wip:` labels on GitHub issues to detect work in progress on any machine.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "=== In-flight work (wip labels) ==="
gh issue list --label "wip:ace-linux-1" --state open --json number,title \
  --jq '.[] | "#\(.number) \(.title)"' 2>/dev/null || echo "  (gh unavailable)"
gh issue list --label "wip:ace-linux-2" --state open --json number,title \
  --jq '.[] | "#\(.number) \(.title)"' 2>/dev/null || true
gh issue list --label "wip:licensed-win-1" --state open --json number,title \
  --jq '.[] | "#\(.number) \(.title)"' 2>/dev/null || true

# Check for local worktrees with uncommitted changes
echo ""
echo "=== Active worktrees ==="
git worktree list 2>/dev/null | grep -v "(bare)" || echo "  No worktrees found"
```

### 3. Validate Environment

Confirm required tools are available and the repo is in a clean state.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "=== Environment validation ==="

# Check git status
DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
if [[ "$DIRTY" -gt 0 ]]; then
  echo "WARNING: $DIRTY uncommitted changes in working tree"
  git status --short | head -10
else
  echo "  Git working tree: clean"
fi

# Check branch
BRANCH=$(git branch --show-current)
echo "  Current branch: $BRANCH"

# Check required tools
for tool in gh node; do
  if command -v "$tool" &>/dev/null; then
    echo "  $tool: available"
  else
    echo "  WARNING: $tool not found on PATH"
  fi
done

# Check governance state
GOVERNOR="$REPO_ROOT/scripts/workflow/session_governor.py"
if [[ -f "$GOVERNOR" ]]; then
  python3 "$GOVERNOR" --list 2>/dev/null | head -5 \
    || echo "  Governor: script exists but failed to run"
else
  echo "  WARNING: session_governor.py not found"
fi
```

### 4. Check Plan Approval State

Verify whether any plan approvals are active for the current session.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
APPROVAL_DIR="$REPO_ROOT/.planning/plan-approved"

echo "=== Plan approval state ==="
if [[ -d "$APPROVAL_DIR" ]]; then
  APPROVALS=$(ls "$APPROVAL_DIR"/*.md 2>/dev/null | wc -l)
  if [[ "$APPROVALS" -gt 0 ]]; then
    echo "  Active approvals: $APPROVALS"
    ls "$APPROVAL_DIR"/*.md 2>/dev/null | while read f; do
      echo "    - $(basename "$f" .md)"
    done
  else
    echo "  No active plan approvals — implementation gated until a plan is approved"
  fi
else
  echo "  Approval directory does not exist"
fi
```

### 5. Load Context Files

Verify that repo-committed memory files exist in the `.claude/memory/` directory.
These are the three core files that provide session context:

- `context.md` — machine conventions, paths, workspace layout
- The agent profile file — user profile, AI subscriptions, workflow rules
- `KNOWLEDGE.md` — engineering lessons, tool quirks

Also check for the most recent learning report in `.claude/state/learning-reports/`.

The agent should Read any missing files and flag them for repair.

## Output Format

The routine produces a brief status summary:

```
SESSION PRE-FLIGHT
==================
Prior state:    [loaded / not found]
In-flight work: [N issues with wip labels]
Environment:    [clean / N warnings]
Plan approvals: [N active / none]
Context:        [loaded / N files missing]
==================
Ready to proceed: [YES / NO — resolve warnings first]
```

## Failure Modes

| Condition | Action |
|-----------|--------|
| `wip:` label found on current machine | WARN — another terminal may be working; confirm before proceeding |
| Dirty working tree with >20 files | WARN — consider stashing or committing before new work |
| `gh` CLI unavailable | SKIP in-flight check; note in summary |
| Governor script missing | WARN — governance enforcement may not be active |
| No session signals in last 48 hours | INFO — first session in a while; check cron health |

## Integration

This skill is referenced by:
- `SESSION-GOVERNANCE.md` Phase 3 — session infrastructure rebuild
- The `/daily-brief` and `/today` skills for morning startup routines
- Hook: `session-governor-check.sh` validates runtime limits (separate concern)
