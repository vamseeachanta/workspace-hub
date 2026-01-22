# /today - Interactive Daily Productivity Review

You are guiding the user through their daily productivity review. This is an interactive session.

## Mode Detection

Determine the mode based on current time or user argument:
- **morning** (default before noon): Full review + priority setting
- **midday** (noon-5pm): Quick check-in + blockers
- **evening** (after 5pm or `--eod`): End-of-day wrap-up

## Step 1: Generate Report

First, run the daily report script to gather fresh data:

```bash
./scripts/productivity/daily_today.sh 2>/dev/null || echo "Script not found, gathering data manually"
```

Then read today's log file at `logs/daily/{TODAY}.md`.

## Step 2: Interactive Review by Mode

### Morning Mode

Walk through these sections interactively:

**A. Yesterday's Activity**
- Present git commits summary
- Ask: "Anything from yesterday you want to continue today?"

**B. Current State**
- Show open TODOs, active specs, branch status
- Ask: "Any of these blocked or need attention?"

**C. Set Priorities**
- Based on the data, suggest 3 priorities
- Ask user to confirm or modify using AskUserQuestion:
  ```
  Header: "Priority 1"
  Question: "What's your #1 priority today?"
  Options based on: open TODOs, in-progress work, suggestions
  ```
- Repeat for priorities 2 and 3

**D. Time Blocking (optional)**
- Ask: "Want to block focus time for deep work today?"
- If yes, suggest time blocks based on priorities

### Midday Mode

Quick 2-minute check-in:

**A. Progress Check**
- Ask: "How's priority #1 going?" with options: [On track, Blocked, Pivoted, Done]
- If blocked: "What's the blocker?" - log it

**B. Adjust if Needed**
- If pivoted or blocked, ask about reprioritizing
- Update the daily log with notes

### Evening Mode (--eod)

End-of-day wrap-up:

**A. Priority Review**
- For each morning priority, ask: [Completed, Partial, Blocked, Deferred]
- Log the status

**B. Capture Blockers**
- Ask: "Any blockers to log for tomorrow?"
- Add to daily log

**C. Tomorrow's Focus**
- Ask: "One thing you want to start with tomorrow?"
- Add to daily log

**D. Update Log**
- Mark `reviewed: true` in frontmatter
- Save all responses to the daily log file

## Step 3: Save Updates

After each interactive session, update the daily log file at `logs/daily/{TODAY}.md` with:
- Selected priorities (morning)
- Progress notes (midday)
- Completion status and tomorrow's focus (evening)

## Output Format

Keep responses conversational but concise. Use formatting:

```
## Morning Review - Jan 21, 2026

**Yesterday:** 11 commits across 8 repos - solid progress!

**Carrying forward:**
- Analytics dashboard (branch: feature/analytics)
- Mobile spec waiting on design review

**Suggested priorities:**
1. Complete analytics tests (high impact)
2. Review 2 open PRs (quick wins)
3. Follow up on mobile design review (unblock)

Ready to set your priorities?
```

## Arguments

- `/today` - Auto-detect mode by time
- `/today morning` - Force morning mode
- `/today midday` - Force midday check-in
- `/today --eod` or `/today evening` - Force end-of-day
- `/today --week` - Weekly review instead of daily
