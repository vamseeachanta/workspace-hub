---
name: work-document-exit-step-4-stage-files
description: "Sub-skill of work-document-exit: Step 4 \u2014 Stage Files."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 4 — Stage Files

## Step 4 — Stage Files


Show the user what will be staged and print the git add command:

```
Files to stage:
  .claude/skills/workspace-hub/work-document-exit/SKILL.md
  .claude/skills/workspace-hub/work-document-exit/README.md
  .claude/work-queue/pending/WRK-392.md

Ready to stage:
  git add <file1> <file2> ...

To commit:
  git commit -m "feat(wrk-392): ..."
```

Do NOT run `git add` or `git commit` automatically. Print the commands only.
The user must paste and run them to preserve the WRK gate.

Exception: if the user explicitly says "stage for me" or "run git add", then
run `git add` for the listed files only (no `-A`, no wildcard).
