---
name: session-start-path-discipline-reminder
description: 'Sub-skill of session-start: Path Discipline Reminder.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Path Discipline Reminder

## Path Discipline Reminder


Surface this reminder silently at session start (do not print unless a violation is detected):

- **Prefer relative paths** inside repo-scoped scripts (e.g., `./scripts/foo.sh`, not `/mnt/...`)
- **Never hardcode** `/mnt/local-analysis/workspace-hub/` in generated scripts — use `${REPO_ROOT}`,
  `$(git rev-parse --show-toplevel)`, or `$(pwd)` instead
- **Absolute paths** are allowed only when a tool explicitly requires them (e.g., `file_path` in
  Read/Edit/Write tool calls)
- If you catch yourself writing a hardcoded `/mnt/` path in a script, stop and replace it with the
  env-var form before proceeding
