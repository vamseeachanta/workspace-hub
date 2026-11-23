---
name: session-corpus-audit
description: Analyze session quality trends — identify high-churn patterns, report waste, flag sessions exceeding 500 tool calls
version: 1.0.0
category: coordination
tags: [session, audit, quality, signals]
related_skills:
  - session-start-routine
  - comprehensive-learning
---

# Session Corpus Audit

Analyze session signals to identify quality trends and waste patterns.

## Data source

Session signals live at `.claude/state/session-signals/YYYY-MM-DD.jsonl`.
Each line is a JSON object with: session_id, transcript_path, cwd, permission_mode, hook_event_name, stop_hook_active, last_assistant_message.

## Audit procedure

### 1. Collect recent signals
```bash
# Last 7 days of session signals
for f in $(ls -t .claude/state/session-signals/*.jsonl | head -7); do
  echo "=== $(basename $f) ==="
  wc -l "$f"
  cat "$f"
done
```

### 2. Identify high-churn sessions
- Sessions that fired multiple Stop hooks (restarts/crashes)
- Sessions with last_assistant_message indicating errors or blocks
- Sessions ending with permission denials

### 3. Estimate tool-call volume
- Check `.claude/state/session-governor/tool-call-count` for daily totals
- Flag any day exceeding 500 tool calls (potential runaway session)

### 4. Detect recurring patterns
- Same error messages across sessions (systemic issues)
- Sessions that ended mid-task (unreleased wip labels, uncommitted changes)
- Permission mode patterns (bypassPermissions vs default)

### 5. Produce quality report
Output a markdown report with:
- Session count by day (last 7 days)
- High-churn sessions with root cause
- Recurring error patterns
- Waste estimate (sessions that produced no commits)
- Recommendations for workflow improvement

## When to use
- Weekly quality review
- After a day with many session restarts
- When investigating tool-call ceiling hits
- When a product/chatbot already has rated conversation examples and the user asks to review provider sessions to catch up on inconsistencies

## Conversation-rating provider catch-up

When auditing Claude/Codex/Hermes/Gemini sessions for a chatbot or product with existing conversation ratings, **load the rated baseline first** and treat provider logs as meta-evidence. Do not restart the rubric. Review provider sessions for workflow defects that explain or predict conversation-quality failures: delivery-state overclaims, internal/tool leakage, canary-before-live drift, channel/scope/domain terminology confusion, and user-blame before log inspection.

Use `references/conversation-rating-provider-catchup.md` for the detailed procedure and output shape.
