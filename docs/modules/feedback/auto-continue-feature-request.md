# Feature Request: Auto-Continue After Rate Limit Reset

## Problem

When Claude Code hits a rate limit mid-task, it stops completely and requires manual intervention. This breaks workflow for long-running tasks, background agents, and unattended operations.

## Proposed Solution

Add an option to automatically wait and resume:

- **Flag:** `--auto-continue` or `--wait-on-limit`
- **Setting:** `autoResumeOnRateLimit` in settings.json
- **Environment variable:** `CLAUDE_AUTO_CONTINUE=1`

## Desired Behavior

- Detect rate limit error
- Display countdown timer until reset
- Auto-resume once limit resets
- Preserve full context and state

## Use Cases

- Overnight multi-file refactors
- Automated CI/CD code review pipelines
- Long research tasks with subagents
- Batch processing across repositories

## Alternatives Considered

- External wrapper scripts (fragile, loses context)
- Manual monitoring (not scalable)

---

**To submit:** Run `/feedback` in Claude Code and paste the content above.
