---
name: stage-01-capture
description: "Stage 01: Capture"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 1
invocation: human_interactive
weight: light
human_gate: False
---

Stage 1 · Capture | human_interactive | light | single-thread
Entry: nothing (human initiates)
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Ask human: WRK title, mission, category
2. Write pending/WRK-NNN.md with valid frontmatter (id, title, status:pending, category, github_issue_ref)
3. Run `bash scripts/work-queue/validate-wrk-frontmatter.sh WRK-NNN` — must exit 0
4. Create GitHub issue: `uv run --no-project python scripts/knowledge/update-github-issue.py WRK-NNN --create`
   - Stores github_issue_ref in frontmatter automatically
   - If gh auth fails, log warning and continue — issue can be created later
Exit: pending/WRK-NNN.md with github_issue_ref populated (Stage 1 done)
