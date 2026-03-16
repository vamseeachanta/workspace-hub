---
name: skill-learner-post-commit-hook
description: 'Sub-skill of skill-learner: Post-Commit Hook.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Post-Commit Hook

## Post-Commit Hook


**Hook Configuration:**
```bash
# .claude/hooks/post-commit.sh
#!/bin/bash
# Auto-execute skill learning after commits

REPO_PATH="$(pwd)"
SKILL_PATH="${HOME}/.claude/skills/workspace-hub/skill-learner"

# Allow bypassing skill learning

*See sub-skills for full details.*
