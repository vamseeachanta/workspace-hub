---
title: "feat(stage-exit): self-contained stage-exit-NN.yaml with auto-capture + --decisions flag"
priority: high
category: harness
subcategory: work-queue
complexity: medium
created_at: "2026-03-20T20:00:00Z"
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1244
---

Enhance exit_stage.py to write assets/WRK-NNN/stage-exit-NN.yaml that auto-captures 80% of context (git diff, test results, timing, checklist, hooks) and accepts --decisions and --user-note flags for agent-provided context. Next session loads only this file + micro-skill — zero pollution from memory/rules/conversation history.

Spawned from WRK-1384 Task #44.
