---
id: TIP-002
type: tip
title: "workspace-hub pre-commit hook takes 5+ min — use TaskOutput with 300s timeout"
category: tooling
tags: [git, pre-commit, hooks, validate-skills, timeout, workspace-hub]
repos: [workspace-hub]
confidence: 0.95
created: "2026-02-22"
last_validated: "2026-02-22"
source_type: manual
related: []
status: active
access_count: 0
---

# workspace-hub Pre-Commit Hook Takes 5+ Minutes

## Observation

The `validate-skills.sh` pre-commit hook in workspace-hub scans 465+ skill files on every commit. This regularly takes **5 or more minutes**.

## Impact

- Bash tool calls to `git commit` in the main context window will time out (default 2-minute timeout)
- The commit silently appears to fail when it is actually still running

## Fix

Always run workspace-hub git commits as a **background Bash task** and use `TaskOutput` with a **300-second (5-minute) timeout**:

```python
# In orchestrator
bash_result = bash("git commit -m '...'", run_in_background=True)
task_id = bash_result["task_id"]
# Then:
output = task_output(task_id, block=True, timeout=300000)
```

## Alternative

If urgency requires it, the hook can be bypassed with `--no-verify` (but only with explicit user permission per workspace rules).
