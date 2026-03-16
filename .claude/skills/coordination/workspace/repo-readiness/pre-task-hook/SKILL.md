---
name: repo-readiness-pre-task-hook
description: 'Sub-skill of repo-readiness: Pre-Task Hook (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Pre-Task Hook (+1)

## Pre-Task Hook


This skill auto-executes as a pre-task hook:

**Hook Configuration:**
```bash
# .claude/hooks/pre-task.sh
#!/bin/bash
# Auto-execute repo-readiness before any task

REPO_PATH="$(pwd)"
SKILL_PATH="$HOME/.claude/skills/workspace-hub/repo-readiness"

*See sub-skills for full details.*

## Post-Task Hook (Optional)


Update readiness state after work:

```bash
# .claude/hooks/post-task.sh
#!/bin/bash
# Update readiness cache after task completion

REPO_PATH="$(pwd)"
TASK_ID="$1"


*See sub-skills for full details.*
