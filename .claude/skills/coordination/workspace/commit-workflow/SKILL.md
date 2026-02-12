---
name: commit-workflow
description: Standardized commit-and-push workflow with change summary, conventional commit messages, and safety checks. Prevents autonomous commits and ensures user approval.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - change_summary
  - conventional_commits
  - safety_checks
  - push_confirmation
tools: [Bash, Read]
related_skills: [repo-sync, work-queue]
---

# Commit Workflow Skill

> Standardized commit-and-push workflow with safety checks and user approval gates.

## Quick Start

```bash
# Use via Claude Code
/commit                    # Commit current changes
/commit -m "fix: thing"    # Commit with specific message
```

## Workflow Steps

### 1. Survey Changes

Run in parallel:
```bash
git status                           # Untracked + modified files
git diff --stat                      # Change summary
git log --oneline -5                 # Recent commits for style matching
```

### 2. Draft Commit Message

Follow conventional commits format matching repository history:
```
<type>(<scope>): <description>

[optional body — why, not what]

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 3. Present for Approval

Show the user:
- Files to be staged (list specific files, not `git add -A`)
- Proposed commit message
- Whether push is needed (check `git rev-list --count origin/main..HEAD`)

**Wait for explicit approval before committing.**

### 4. Execute

```bash
git add <specific-files>
git commit -m "<message>"
git status                           # Verify success
```

### 5. Push (only if requested)

```bash
git push origin <branch>
```

## Safety Rules

- NEVER use `git add -A` or `git add .` — stage specific files by name
- NEVER commit `.env`, credentials, or files matching `.gitignore`
- NEVER push without explicit user approval
- NEVER force-push to main/master
- NEVER amend commits unless explicitly requested — always create NEW commits
- If pre-commit hook fails: fix issue, re-stage, create NEW commit (not --amend)
- NEVER skip hooks (--no-verify) unless user explicitly requests it

## Sensitive File Detection

Before staging, check for:
- `.env`, `.env.*` files
- `credentials.json`, `*.pem`, `*.key`
- Files containing API keys or tokens (grep for common patterns)
- Large binaries (> 1MB)

If found, warn user and exclude from staging.

## When to Use

- After completing a work item or feature
- After fixing a bug
- When user says "commit", "push", "save changes"
- End of work session

## When NOT to Use

- No changes to commit (empty working tree)
- User hasn't explicitly requested a commit
- Mid-implementation (wait for logical completion)

---

## Version History

- **1.0.0** (2026-02-12): Initial release — extracted from /insights analysis of 152 commits across 111 sessions
