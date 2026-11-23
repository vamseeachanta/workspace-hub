---
name: daily-brief
description: "Morning briefing — learning tips, git status, open issues, and today's priorities. Run at the start of each work session."
allowed-tools: Read, Bash, Glob, Grep, Agent(explorer)
---

## Morning Briefing

Run these steps in order and present a consolidated brief:

### 1. Today's Learning Tips
!`uv run scripts/productivity/daily-learning.py 2>/dev/null`

### 2. Git Status
!`cd /mnt/local-analysis/workspace-hub && git log --oneline -5 && echo "---" && git status --short 2>/dev/null`

### 3. Open Issues (recent)
!`cd /mnt/local-analysis/workspace-hub && gh issue list --limit 5 --sort updated 2>/dev/null`

### 4. Priorities
Based on the above, recommend the top 3 things to work on today. Consider:
- Any failing tests or broken builds
- Recently updated issues that need attention
- Unfinished work from yesterday (check git log)
- Learning tips that could be practiced during today's work

Format as a numbered priority list with estimated effort (S/M/L).
